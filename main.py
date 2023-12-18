from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from random import randint

from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '400')

# Changing the audioplayer library since the default audio_sdl2 does not provide seek operation

import os
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
os.environ['KIVY_AUDIO'] = 'ffpyplayer'

# =================================================================

class PongPaddle(Widget):
    score = NumericProperty(0)

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = 1.4*Vector(*self.velocity) + self.pos

class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    player1_score_label = ObjectProperty(None)
    player2_score_label = ObjectProperty(None)
    commandForBall = StringProperty("serve ball")
    

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self.collision_sound_player_hit = SoundLoader().load('tennis_ball_hit_player.mp3')  
        self.collision_sound_computer_hit = SoundLoader().load('tennis_ball_hit_computer.mp3')  
        self.miss_sound = SoundLoader.load('fail_sound.wav')
        self.score_sound = SoundLoader.load('score_sound.wav')
        self.anim  = Animation(color=(1,0,1,1), duration=0.1) + Animation(color=(1,1,0,1), duration=0.1)
        self.anim += Animation(color=(1,1,1,1), duration=0.1) + Animation(color=(0,0,0,1), duration=1)
        self.scheduledObject = Clock.schedule_interval(self.update, 1.0 / 60.0)
    

    def serve_ball(self, *args):
        self.ball.center = self.center
        self.ball.velocity = Vector(4, 0).rotate(randint(180-30, 180+30))

    def update(self, dt):
        
        self.ball.move()

        # Bounce off paddles
        self.player1_bounce()
        self.player2_bounce()

        # Bounce off top and bottom
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1

        # Score points
        if self.ball.x < self.x:
            self.miss_sound.play()
            self.player2.score += 1
            self.update_score_labels()
            self.anim.start(self.player2_score_label)
            if self.player2.score >= 10:
                self.serve_ball()
                Clock.unschedule(self.scheduledObject)
                self.show_winner("Computer")
            else:
                # Clock.schedule_once( self.serve_ball, 2)
                self.serve_ball()

        if self.ball.x > self.width:
            self.score_sound.play()
            self.player1.score += 1
            self.update_score_labels()
            self.anim.start(self.player1_score_label)
            if self.player1.score >= 10:
                self.serve_ball()
                Clock.unschedule(self.scheduledObject)
                self.show_winner("Player")
            else:
                # Clock.schedule_once( self.serve_ball, 2)
                self.serve_ball()

        # Computer-controlled paddle movement
        self.move_computer_paddle()
    
    def move_computer_paddle(self):
        if self.ball.y < self.player2.center_y:
            self.player2.center_y -= min(6, abs(self.ball.y - self.player2.center_y))
        elif self.ball.y > self.player2.center_y:
            self.player2.center_y += min(6, abs(self.ball.y - self.player2.center_y))


    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y

    def player1_bounce(self):
        if self.ball.collide_widget(self.player1):
            self.collision_sound_player_hit.play()
            vx, vy = self.ball.velocity
            offset = (self.ball.center_y - self.player1.center_y) / (self.player1.height / 2)
            bounced = Vector(-vx, vy)
            vel = bounced * 1.05
            self.ball.velocity = vel.x, vel.y + 3*offset
        
    def player2_bounce(self):
        if self.ball.collide_widget(self.player2):
            self.collision_sound_computer_hit.play()
            vx, vy = self.ball.velocity
            offset = (self.ball.center_y - self.player2.center_y) / (self.player2.height / 2)
            bounced = Vector(-vx, vy)
            vel = bounced * 1.05
            self.ball.velocity = vel.x, vel.y + 3*offset
            
    def update_score_labels(self):
        self.player1_score_label.text = f"Player: {self.player1.score}"
        self.player2_score_label.text = f"Computer: {self.player2.score}"

    def reset_scores(self):
        self.player1.score = 0
        self.player2.score = 0
        self.update_score_labels()

    def show_winner(self, winner):
        if winner == "Computer":
            App.get_running_app().lose_dialog.open()
        elif winner == "Player":
            App.get_running_app().win_dialog.open()

    def replay_game(self, *args):
        self.scheduledObject = Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.reset_scores()
        try:
            App.get_running_app().lose_dialog.dismiss()
        except:
            pass
        try:
            App.get_running_app().win_dialog.dismiss()
        except:
            pass

class PongApp(App):

    def build(self):        
        self.game = PongGame()
        self.game.serve_ball()
        
        win_box = FloatLayout()
        win_box.add_widget(Image(source="winner.zip", size_hint= (0.75, 0.75), pos_hint= {"center_x": 0.5, "center_y": 0.6}, anim_delay= 0.1,
            allow_stretch= True))
        win_box.add_widget(Button(text="Exit Game", size_hint=(0.35, 0.15), pos_hint= {"center_x": 0.3, "center_y": 0.09}, on_release=(lambda x: App.get_running_app().stop())))
        win_box.add_widget(Button(text="Reset", size_hint=(0.3, 0.15), pos_hint= {"center_x": 0.7, "center_y": 0.09}, on_release=App.get_running_app().game.replay_game))
        
        self.win_dialog = Popup(background="court2.jpg", title='Hurray! You Won', title_align="center",
            title_color=(1,1,1,1), title_font="FlatlineSerif-Bold.otf", title_size=25, content=win_box,
            size_hint=(None, None), size=(400, 400), auto_dismiss=False)
        
        lose_box = FloatLayout()
        lose_box.add_widget(Image(source="gameover.zip", size_hint= (0.75, 0.75), pos_hint= {"center_x": 0.5, "center_y": 0.6}, anim_delay= 0.1,
            allow_stretch= True))
        lose_box.add_widget(Button(text="Exit Game", size_hint=(0.35, 0.15), pos_hint= {"center_x": 0.3, "center_y": 0.09}, on_release=(lambda x: App.get_running_app().stop())))
        lose_box.add_widget(Button(text="Reset", size_hint=(0.3, 0.15), pos_hint= {"center_x": 0.7, "center_y": 0.09}, on_release=App.get_running_app().game.replay_game))

        self.lose_dialog = Popup(background_color=(0,0,0,0.7), title='Better Luck Next Time!', title_align="center",
            title_color=(1,1,1,1), title_font="FlatlineSerif-Bold.otf", title_size=25, content=lose_box,
            size_hint=(None, None), size=(400, 400), auto_dismiss=False, separator_color="green")

    
        return self.game

if __name__ == '__main__':
    PongApp().run()
