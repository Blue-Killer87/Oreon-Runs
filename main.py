from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core import window
from kivymd.app import MDApp
from kivy.clock import mainthread
from kivy.utils import platform
from plyer import gps
from kivy.properties import StringProperty, ObjectProperty
from kivy_garden.mapview import MapMarker, MapView, MapMarkerPopup, MapLayer
from kivy.animation import Animation
from kivy_garden.mapview import MapSource
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.graphics import Line, Color, InstructionGroup
from kivy.clock import Clock
from kivy.graphics.context_instructions import Translate, Scale, PushMatrix, PopMatrix
from kivy_garden.mapview.utils import clamp
from kivy_garden.mapview.constants import \
    (MIN_LONGITUDE, MAX_LONGITUDE, MIN_LATITUDE, MAX_LATITUDE)
from math import radians, log, tan, cos, pi
import random
import zbarlight
from kivy.uix.camera import Camera
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle

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

class LineDrawLayer(MapLayer):
    def __init__(self, coordinates=[[0, 0], [0, 0]], color=[0, 0, 1, 1], **kwargs):
        super().__init__(**kwargs)
        self._coordinates = coordinates
        self.color = color
        self._line_points = None
        self._line_points_offset = (0, 0)
        self.zoom = 0
        self.lon = 0
        self.lat = 0
        self.ms = 0

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates):
        self._coordinates = coordinates
        self.invalidate_line_points()
        self.clear_and_redraw()

    @property
    def line_points(self):
        if self._line_points is None:
            self.calc_line_points()
        return self._line_points

    @property
    def line_points_offset(self):
        if self._line_points is None:
            self.calc_line_points()
        return self._line_points_offset

    def calc_line_points(self):
        # Offset all points by the coordinates of the first point,
        # to keep coordinates closer to zero.
        # (and therefore avoid some float precision issues when drawing lines)
        self._line_points_offset = (self.get_x(self.coordinates[0][1]),
                                    self.get_y(self.coordinates[0][0]))
        # Since lat is not a linear transform we must compute manually
        self._line_points = [(self.get_x(lon) - self._line_points_offset[0],
                              self.get_y(lat) - self._line_points_offset[1])
                             for lat, lon in self.coordinates]

    def invalidate_line_points(self):
        self._line_points = None
        self._line_points_offset = (0, 0)

    def get_x(self, lon):
        """Get the x position on the map using this map source's projection
        (0, 0) is located at the top left.
        """
        return clamp(lon, MIN_LONGITUDE, MAX_LONGITUDE) * self.ms / 360.0

    def get_y(self, lat):
        """Get the y position on the map using this map source's projection
        (0, 0) is located at the top left.
        """
        lat = radians(clamp(-lat, MIN_LATITUDE, MAX_LATITUDE))
        return (1.0 - log(tan(lat) + 1.0 / cos(lat)) / pi) * self.ms / 2.0

    # Function called when the MapView is moved
    def reposition(self):
        map_view = self.parent

        # Must redraw when the zoom changes
        # as the scatter transform resets for the new tiles
        if self.zoom != map_view.zoom or \
                   self.lon != round(map_view.lon, 7) or \
                   self.lat != round(map_view.lat, 7):
            map_source = map_view.map_source
            self.ms = pow(2.0, map_view.zoom) * map_source.dp_tile_size
            self.invalidate_line_points()
            self.clear_and_redraw()

    def clear_and_redraw(self, *args):
        with self.canvas:
            # Clear old line
            self.canvas.clear()

        self._draw_line()

    def _draw_line(self, *args):
        map_view = self.parent
        self.zoom = map_view.zoom
        self.lon = map_view.lon
        self.lat = map_view.lat

        # When zooming we must undo the current scatter transform
        # or the animation distorts it
        scatter = map_view._scatter
        sx, sy, ss = scatter.x, scatter.y, scatter.scale

        # Account for map source tile size and map view zoom
        vx, vy, vs = map_view.viewport_pos[0], map_view.viewport_pos[1], map_view.scale

        with self.canvas:

            # Save the current coordinate space context
            PushMatrix()

            # Offset by the MapView's position in the window (always 0,0 ?)
            Translate(*map_view.pos)

            # Undo the scatter animation transform
            Scale(1 / ss, 1 / ss, 1)
            Translate(-sx, -sy)

            # Apply the get window xy from transforms
            Scale(vs, vs, 1)
            Translate(-vx, -vy)

            # Apply what we can factor out of the mapsource long, lat to x, y conversion
            Translate(self.ms / 2, 0)

            # Translate by the offset of the line points
            # (this keeps the points closer to the origin)
            Translate(*self.line_points_offset)

            Color(*self.color)
            Line(points=self.line_points, width=2)

            # Retrieve the last saved coordinate space context
            PopMatrix()

class QRScannerLayout(BoxLayout):
    orientation = "vertical"
    pass

class ScannerScreen(Screen):
    def __init__(self, **kwargs):
        super(ScannerScreen, self).__init__(**kwargs)
        self.camera = Camera(resolution=(960, 720), play=True)
        self.label = Label(text="Scan a QR code")
        self.layout = QRScannerLayout()

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.camera)
        self.add_widget(self.layout)

    def scan(self, dt):
        camera_texture = self.camera.texture

        if camera_texture:
            data = camera_texture.pixels
            width, height = camera_texture.size

            codes = zbarlight.scan_codes(['qrcode'], data, width, height)

            if codes:
                self.label.text = f"QR Code: {codes[0].decode('utf-8')}"

class OreonApp(MDApp):
    
    def build(self):
            self.theme_cls.theme_style = "Dark" #Background
            self.theme_cls.primary_palette = "Blue" #Main color
            self.mapviewRun = self.root.get_screen('run').ids.mapview
            sm = ScreenManager()

            welcome_screen = WelcomeScreen(name='welcome')
            sm.add_widget(welcome_screen)

            choose_track_screen = ChooseTrackScreen(name='choosetrack')
            sm.add_widget(choose_track_screen)

            run_screen = RunScreen(name='run')
            sm.add_widget(run_screen)

            tracking_screen = TrackingScreen(name='tracking')
            sm.add_widget(tracking_screen)

            create_screen = CreateScreen(name='create')
            sm.add_widget(create_screen)

            scanner_screen = ScannerScreen(name='scan')
            sm.add_widget(scanner_screen)

            return sm



    # Schedule movement updates every 5 seconds
    # Clock.schedule_interval(self.update_movement, 5)
  
    
   


    
    # If platform is android, turn GPS on and set it to method on_location
    if platform == "android":
        def on_start(self):
            gps.configure(on_location=self.on_location)
            gps.start(minTime=5000, minDistance=1)
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()
            self.oldlat = 0
            self.oldlon = 0
            

        @mainthread
        #Main GPS method, calls itself every time the app gets new GPS telemtry
        def on_location(self, **kwargs):
            if (kwargs['accuracy'] < 80 or kwargs['accuracy'] > 100):
                print(kwargs)
                self.aproxgpslat = kwargs["lat"]
                self.aproxgpslon = kwargs["lon"]
                Clock.schedule_once(self.proc_aprox_location, 5)
            else:
                print(kwargs)
                self.gpslat = kwargs["lat"]
                self.gpslon = kwargs["lon"]
                Clock.schedule_once(self.proc_location, 5)

        def proc_aprox_location(self, dt):        
            self.aproxpoint = MapMarker(lat = self.aproxgpslat, lon = self.aproxgpslon, source="data/Blank.png")
            #mapview.remove_marker(self.point)
            self.mapviewRun.add_marker(self.aproxpoint)

        def proc_location(self, dt):        
            self.point = MapMarker(lat = self.gpslat, lon = self.gpslon)
            #mapview.remove_marker(self.point)
            self.mapviewRun.add_marker(self.point)
                
            # You can import JSON data here or:
            my_coordinates = [[51.505807, -0.128513], [51.126251, 1.327067],
                            [50.959086, 1.827652], [48.85519, 2.35021]]

            # Red Route (multiple routes)
            lml1 = LineDrawLayer(coordinates=my_coordinates, color=[1, 0, 0, 1])
            self.mapviewRun.add_layer(lml1, mode="scatter")
            
            if self.oldlat != 0 and self.oldlon != 0:
                # Blue route (two points)
                my_coordinates = [[self.oldlat, self.oldlon], [self.gpslat, self.gpslon]]
                lml3 = LineDrawLayer(coordinates=my_coordinates, color=[0, 0, 1, 1])
                self.mapviewRun.add_layer(lml3, mode="scatter")
                
            else:
                print("still initializing")
            self.oldlat = self.gpslat
            self.oldlon = self.gpslon

    #If platform is not Android, don't turn GPS on      
    else:
        print("Desktop version starting.")

        def center_on_gps(self):
            print("Not implemented in desktop version")
 
        
        
    
    def update_movement(self, dt):
        pass


    def request_android_permissions(self):

        from android.permissions import request_permissions, Permission

        def callback(permissions, results):

            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([#Permission.ACCESS_COARSE_LOCATION,
                            Permission.ACCESS_FINE_LOCATION], callback)
    
    dialog = None

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


if __name__ == '__main__':
    OreonApp().run()


'''
Otázky:

Musí být sledování polohy? Je to správné?
- Poloha skrytá, jen pro systémové využití. Trackování zobrazit až po ukončení.

QR tisk na místě? Místo toho proximity checker?
- Vytvořit předem QR kódy s číslem stanoviště. Přiřadit zahashované číslo k stanovišti na mapě. Proximity checkem zkontrolovat že tam vážně jsi.
'''