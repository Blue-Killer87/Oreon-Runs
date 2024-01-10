from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core import window
from kivymd.app import MDApp
from kivy.clock import mainthread
from kivy.utils import platform
from plyer import gps
from kivy.properties import StringProperty
from kivy_garden.mapview import MapMarker, MapView
from kivy.animation import Animation
from kivy_garden.mapview import MapSource
from kivy.core.window import Window

#Window.size = (900, 800)
#Window.minimum_width, Window.minimum_height = Window.size
#Window.maximum_width, Window.maximum_height = (1800, 1600)

class WelcomeScreen(Screen):
    pass

class ChooseScreen(Screen):
    pass

class RunScreen(Screen):
    pass

class TrackingScreen(Screen):
    pass

class CreateScreen(Screen):
    pass

class ScanQRScreen(Screen):
    pass

class CreateQRScreen(Screen):
    pass

class ChooseTrackScreen(Screen):
    pass

class Main(ScreenManager):
    pass


class OreonApp(MDApp):
    # If platform is android, turn GPS on and set it to method on_location
    if platform == "android":
        def on_start(self):
            gps.configure(on_location=self.on_location)
            gps.start(minTime=1000, minDistance=0)
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()


        #Main GPS method, calls itself every time the app gets new GPS telemtry
        def on_location(self, **kwargs):
            print(kwargs)
            gpslan = kwargs["lat"]
            gpslon = kwargs["lon"]
            return gpslan, gpslon
            

        


    #If platform is not Android, don't turn GPS on      
    else:
        print("Desktop version starting.")


    def build(self):
        self.theme_cls.theme_style = "Dark" #Background
        self.theme_cls.primary_palette = "Blue" #Main color


    def request_android_permissions(self):

        from android.permissions import request_permissions, Permission

        def callback(permissions, results):

            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                            Permission.ACCESS_FINE_LOCATION], callback)
        
    def center_on_gps(self, gpslan, gpslon):
        print("Fuck")
        #print(f"Lan:{gpslan}, Lon:{gpslon}")
        #mapview = self.root.get_screen('run').ids.mapview
        #mapview.center_on(gpslan, gpslon)
    
OreonApp().run()

