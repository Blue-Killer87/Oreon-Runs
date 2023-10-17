from kivy.base import runTouchApp
from kivy.lang import Builder
import kivy
from plyer import gps
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivy.clock import mainthread
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
import os

#os.system("py -m pip install boto3")

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

class WelcomeScreen(Screen):
    pass

class CreateScreen(Screen):
    pass

class ChooseScreen(Screen):
    pass

class RunScreen(Screen):
    pass

class TrackingScreen(Screen):
    pass

class WindowManager(ScreenManager):
    pass


class MyApp(App):
    def build(self):
        pass

if __name__ == '__main__':
    MyApp().run()
