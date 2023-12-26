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



KV = '''
#:import MapSource kivy_garden.mapview.MapSource
#:import utils kivy.utils

ScreenManager:
    WelcomeScreen:
    ChooseScreen:
    RunScreen:
    TrackingScreen:
    CreateScreen:
    ScanQRScreen:
    CreateQRScreen:
    ChooseTrackScreen:

<GpsBlinker>:
    default_blink_size: 25
    blink_size: 25
    source: 'kivymd/images/transparent.png'
    outer_opacity: 1
 
    canvas.before:
        # Outer circle
        Color:
            rgba: app.theme_cls.primary_color[:3] + [root.outer_opacity]
 
        RoundedRectangle:
            radius: [root.blink_size/2.0, ]
            size: [root.blink_size, root.blink_size]
            pos: [root.pos[0] + root.size[0]/2.0 - root.blink_size/2.0, root.pos[1] + root.size[1]/2.0 - root.blink_size/2.0]
 
        # Inner Circle
        Color:
            rgb: 1,1,1
        RoundedRectangle:
            radius: [root.default_blink_size/2.0, ]
            size: [root.default_blink_size, root.default_blink_size]
            pos: [root.pos[0] + root.size[0]/2.0 - root.default_blink_size/2.0, root.pos[1] + root.size[1]/2.0 - root.default_blink_size/2.0]

            
<Toolbar@BoxLayout>:
    size_hint_y: None
    height: '48dp'
    padding: '4dp'
    spacing: '4dp'

    canvas:
        Color:
            rgba: .2, .2, .2, .6
        Rectangle:
            pos: self.pos
            size: self.size

<ShadedLabel@Label>:
    size: self.texture_size
    canvas.before:
        Color:
            rgba: .2, .2, .2, .6
        Rectangle:
            pos: self.pos
            size: self.size

<WelcomeScreen>
    name: "welcome"
    canvas:
        Color:
            rgba: 0.11, 0.11, 0.11, 0.2
        Rectangle:
            pos: self.pos
            size: self.size


    FloatLayout:

           
        MDLabel:
            font_size: sp(60)
            text: "Oreon"
            halign: 'center'
            pos_hint: {'center_y': .7}
            bold: True
            canvas:
                
                Color:
                    rgba: 0.11, 0.11, 0.11, 0.2
                Rectangle:
                    pos: self.center_x - 250, self.center_y - 300
                    size: sp(512),sp(512)
                    source: 'data/BackgroundOreon.png'

        MDFillRoundFlatIconButton:
            text: "Start"
            icon: "walk"
            icon_size: "98sp"
            font_size: sp(30)  
            text_color: "white"
            pos_hint: {"center_x": .5, "center_y": .4}
            on_release:
                app.root.current = "choose"
                root.manager.transition.direction = "left"



<ChooseScreen>
    name: "choose"

    canvas.before:
        Color:
            rgba: 0.11, 0.11, 0.11, 0.8
        Rectangle:
            pos: self.pos
            size: self.size


    BoxLayout:
        Button:
            text: "Load Track"
            on_release: app.root.current = "choosetrack"
            background_color: 0, 0, 0, .1
            markup: True
            font_size: sp(50)
            color: 1,1,1,1
            multiline: True
            text_size: self.width, None
            height: self.texture_size[1]
            halign: 'center'


        Button:
            text: "Create track"
            on_press: app.root.current = "create"
            background_color: 0, 0, 0, .1
            markup: True
            font_size: sp(50)
            color: 1,1,1,1
            multiline: True
            text_size: self.width, None
            height: self.texture_size[1]
            halign: 'center'

<ChooseTrackScreen>
    name: "choosetrack"

    MDRectangleFlatIconButton:
        text: "Load from library"
        on_press: app.root.current = "run"
        on_release: app.start(1000, 0)
        font_size: sp(30)
        icon:"library"
        pos_hint: {"center_x": .5, "center_y": .5}

<RunScreen>
    name: "run"

    RelativeLayout:

        MapView:
            id: mapview
            lat: 49.5
            lon: 14.8
            zoom: 6
            #size_hint: .5, .5
            #pos_hint: {"x": .25, "y": .25}

            #on_map_relocated: mapview2.sync_to(self)
            #on_map_relocated: mapview3.sync_to(self)
            #on_map_relocated: app.restrict_movement


        Toolbar:
            top: root.top
            Button:
                text: "Your location"
                on_release: mapview.set_zoom_at(10,1,1)
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'center'

            Spinner:
                text: "Chose map"
                values: MapSource.providers.keys()
                on_text: mapview.map_source = self.text
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'center'
            Button:
                text: "Back to menu"
                on_press: app.root.current = "choose" 
                on_release: app.stop()
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'center'
        Toolbar:
            Label:
                text: "Longitude: {}".format(mapview.lon)
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'center'
            Label:
                text: "Latitude: {}".format(mapview.lat)
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'center'
            Label:
                text: app.gps_location
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'center'

<CreateScreen>
    name: 'create'
    FloatLayout:
        Label:
            text: "Work in Progress... maybe"
            font_size: sp(35)
            pos_hint: {"center_x": .5, "center_y": .6}

        Button:
            text: "Go back"
            on_release: app.root.current="choose"
            font_size: sp(30)  
            size_hint:(.4, .25)
            pos_hint: {"center_x": .5, "center_y": .1}

                    
'''

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
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        window.bind(on_keyboard = self.keyboard)

class GpsBlinker(MapMarker):
    def blink(self):
        # Animation that changes the blink size and opacity
        anim = Animation(outer_opacity=0, blink_size=50)
         
        # When the animation completes, reset the animation, then repeat
        anim.bind(on_complete = self.reset)
        anim.start(self)
 
    def reset(self, *args):
        self.outer_opacity = 1
        self.blink_size = self.default_blink_size
        self.blink()
 
    # blink --> outer_opacity = 0, blink_size = 50
    # reset --> outer_opacity = 1, blink_size = default = 25

            
class Oreon(MDApp):

    gps_lan = float()
    gps_lon = float()
    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')

    def request_android_permissions(self):

        from android.permissions import request_permissions, Permission

        def callback(permissions, results):

            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)
        # # To request permissions without a callback, do:
        # request_permissions([Permission.ACCESS_COARSE_LOCATION,
        #                      Permission.ACCESS_FINE_LOCATION])

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'

        if platform == "android":
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()

        return Builder.load_string(KV)

    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()

    @mainthread

    def onLocationChanged(self, location):
        self.root.on_location(
            lat=location.getLatitude(),
            lon=location.getLongitude())
        
    def on_location(self, **kwargs):
        self.gps_location = f'Latitude: {kwargs["lat"]}, Longitude: {kwargs["lon"]}'

        if (kwargs['accuracy'] < 40 or kwargs['accuracy'] > 100):
            return
        else:
            self.lat = kwargs['lat']
            self.lon = kwargs['lon']
            self.mapview.center_on(kwargs['lat'], kwargs['lon'])
            self.marker = MapMarker(lat=kwargs['lat'], lon=kwargs['lon'])
            self.mapview.add_marker(self.marker)


    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def on_pause(self):
        gps.stop()
        return True

    def on_resume(self):
        gps.start(1000, 0)
        pass

    def keyboard(self,window,key,*args):
        if key == 27 and self.sm.current != "welcome":
            self.current = 'choose'
            return True   # key event consumed by app
        else:           
            return False  # key event passed to Android

    def restrict_movement(self):
        if MapView.lon > 179 or MapView.lon < -179:
            MapView.set_zoom_at(10,1,1)
Oreon().run()
# Required dependencies for Ubuntu:
# sudo apt-get install gettext
# sudo apt-get install zbar-tools
