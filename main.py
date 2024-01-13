from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core import window
from kivymd.app import MDApp
from kivy.clock import mainthread
from kivy.utils import platform
from plyer import gps
from kivy.properties import StringProperty
from kivy_garden.mapview import MapMarker, MapView, MapMarkerPopup
from kivy.animation import Animation
from kivy_garden.mapview import MapSource
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.graphics import Line
from kivy.clock import Clock


#if platform != "android" or platform != "ios":
 #   Window.size = (900, 800)
  #  Window.minimum_width, Window.minimum_height = Window.size



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
    
    
    def build(self):
        self.theme_cls.theme_style = "Dark" #Background
        self.theme_cls.primary_palette = "Blue" #Main color
        self.mapviewRun = self.root.get_screen('run').ids.mapview

        prague = (50.0755, 14.4378)
        initial_position = (50.0755, 14.4378)

        self.lines=[]

        with self.mapviewRun.canvas:
            line = Line(points=(prague[0], prague[1], initial_position[0], initial_position[1]), width=2)
            self.lines.append(line)

        # Schedule movement updates every 5 seconds
        Clock.schedule_interval(self.update_movement, 5)

    # If platform is android, turn GPS on and set it to method on_location
    if platform == "android":
        def on_start(self):
            gps.configure(on_location=self.on_location)
            gps.start(minTime=1000, minDistance=0)
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()


        @mainthread
        #Main GPS method, calls itself every time the app gets new GPS telemtry
        def on_location(self, **kwargs):
            if (kwargs['accuracy'] < 60 or kwargs['accuracy'] > 100):
                return
            else:
                print(kwargs)
                self.gpslat = kwargs["lat"]
                self.gpslon = kwargs["lon"]
                self.point = MapMarker(lat = self.gpslat, lon = self.gpslon)
                #mapview.remove_marker(self.point)
                self.mapviewRun.add_marker(self.point)
                
        

        

        

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
            lat=50
            lon=14
            testpoint = MapMarker(lat=lat,lon=lon,source="data/down.png")
            self.mapviewRun.add_marker(testpoint)
        def startRun(self):

            with self.mapviewRun.canvas:
               Line(points=[50, 14, 55, 18], width=2)
        
        

    def update_movement(self, dt):
        # New position for the updated line
        prague = (50.0755, 14.4378)
        new_position = (50.0765, 14.4388)

        # Draw a new line connecting the previous position to the updated position
        with self.mapviewRun.canvas:
            line = Line(points=(prague[0], prague[1], new_position[0], new_position[1]), width=2)
            self.lines.append(line)


    def request_android_permissions(self):

        from android.permissions import request_permissions, Permission

        def callback(permissions, results):

            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                            Permission.ACCESS_FINE_LOCATION], callback)
    
    @mainthread
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


'''
Otázky:

Musí být sledování polohy? Je to správné?
- Poloha skrytá, jen pro systémové využití. Trackování zobrazit až po ukončení.

QR tisk na místě? Místo toho proximity checker?
- Vytvořit předem QR kódy s číslem stanoviště. Přiřadit zahashované číslo k stanovišti na mapě. Proximity checkem zkontrolovat že tam vážně jsi.
'''
