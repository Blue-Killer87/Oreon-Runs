from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core import window
from kivymd.app import MDApp
from kivy.clock import mainthread
from kivy.utils import platform
from plyer import gps
from kivy.properties import StringProperty
from kivy_garden.mapview import MapMarker, MapView, MapMarkerPopup, MapLayer
from kivy.animation import Animation
from kivy_garden.mapview import MapSource
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.graphics.context_instructions import Translate, Scale
from kivy.graphics import Color, Line, SmoothLine, MatrixInstruction


if platform != "android" or platform != "ios":
    Window.size = (900, 800)
    Window.minimum_width, Window.minimum_height = Window.size

else: 
    pass


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
    dialog = None
    
    

    # If platform is android, turn GPS on and set it to method on_location
    if platform == "android":
        def on_start(self):
            pins = []
            gps.configure(on_location=self.on_location)
            gps.start(minTime=2000, minDistance=0)
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()


        @mainthread
        #Main GPS method, calls itself every time the app gets new GPS telemtry
        def on_location(self, pins, **kwargs):
            mapview = self.root.get_screen('run').ids.mapview
            if (kwargs['accuracy'] < 40 or kwargs['accuracy'] > 100):
                return
            else:
                print(kwargs)
                gpslat = kwargs["lat"]
                gpslon = kwargs["lon"]
                self.point = MapMarker(lat = gpslat, lon = gpslon)
                pins.append(gpslat, gpslon)
                #mapview.remove_marker(self.point)
                mapview.add_marker(self.point)

        def startRun(self, pins):
            pass

        

        #def center_on_gps(self, gpslan, gpslon):
         #   print("GPS CENTER LOCATION")

          #  print(f"Lan:{gpslan}, Lon:{gpslon}")
           # mapview = self.root.get_screen('run').ids.mapview
           # mapview.center_on(gpslan, gpslon)
           # return gpslan, gpslon   

    #If platform is not Android, don't turn GPS on      
    else:
        print("Desktop version starting.")

        def center_on_gps(self):
            print("Not implemented in desktop version")
            mapview = self.root.get_screen('run').ids.mapview
            lat=50
            lon=14
            testpoint = MapMarker(lat=lat,lon=lon,source="data/down.png")
            mapview.add_marker(testpoint)
        
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
    
    
    def show_alert_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Are you sure you want to stop the run? (You can't resume it later')",
                buttons=[
                    MDFlatButton(
                        text="CONTINUE",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.cancelcall,

                    ),
                    MDFlatButton(
                        text="STOP",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.discardcall,
                    ),
                ],
            )
        self.dialog.open()
    def cancelcall(self, instance):
        self.dialog.dismiss()

    def discardcall(self, instance):
        self.root.current = "welcome"
        self.dialog.dismiss()

OreonApp().run()
