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


kv = '''
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

<Toolbar@BoxLayout>:
    size_hint_y: None
    height: '48dp'
    padding: '4dp'
    spacing: '4dp'

    canvas:
        Color:
            rgba: .1, .1, .1, .5
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
            text: "Load Track"
            icon: "go-kart-track"
            icon_size: "64sp"
            font_size: sp(25)  
            text_color: "white"
            pos_hint: {"center_x": .5, "center_y": .35}
            on_release:
                app.root.current = "run"
        MDFillRoundFlatIconButton:
            text: "Create Track"
            icon: "draw"
            icon_size: "64sp"
            font_size: sp(25)  
            text_color: "white"
            pos_hint: {"center_x": .5, "center_y": .2}
            on_release:
                app.root.current = "create"


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
        text:"Load from local library"
        on_press: app.root.current = "run"
        on_release: app.start(1000, 0)
        font_size: sp(30)
        icon:"library"
        pos_hint: {"center_x": .5, "center_y": .4}

    MDRectangleFlatIconButton:
        text:"Load from internet"
        on_press: app.root.current = "run"
        on_release: app.start(1000, 0)
        font_size: sp(30)
        icon:"library"
        pos_hint: {"center_x": .5, "center_y": .6}

<RunScreen>
    name: "run"

    RelativeLayout:

        MapView:
            id: mapview
            lat: 49.5
            lon: 14.8
            zoom: 6
            map_source: "osm"
            #size_hint: .5, .5
            #pos_hint: {"x": .25, "y": .25}

            #on_map_relocated: mapview2.sync_to(self)
            #on_map_relocated: mapview3.sync_to(self)
            #on_map_relocated: app.restrict_movement


        Toolbar:
            top: root.top
            FloatLayout:
                MDIconButton:

                    on_release: mapview.center_on(GPSlang, GPSlong)
                    halign: 'center'
                    font_size: sp(20)
                    icon:"crosshairs-gps"
                    pos_hint: {"center_x": .15, "center_y": .5}
                    size_hint: (0.3, 0.8)
                    multiline: True
                    md_bg_color: 1,.5,0,.6


                MDIconButton:

                    on_press: app.root.current = "welcome" 
                    font_size: sp(20)
                    icon:"keyboard-backspace"  
                    halign: 'center'
                    pos_hint: {"center_x": .5, "center_y": .5}
                    size_hint: (0.3, 1)
                    multiline: True
                    md_bg_color: 1,.5,0,.6


                MDIconButton:

                    on_press: app.center_on_gps()
                    font_size: sp(20)
                    icon:"map-marker-outline"  
                    halign: 'center'
                    pos_hint: {"center_x": .85, "center_y": .5}
                    size_hint: (0.3, 1)
                    multiline: True
                    md_bg_color: 1,.5,0,.6
            


<CreateScreen>
    name: 'create'
    FloatLayout:
        MDTextField:
            id: text_create_name
            hint_text: "Track name"
            helper_text: "Insert a name that describes your new track"
            helper_text_mode: "on_focus"
            mode: "round"
            required: True
            pos_hint: {"center_x": .5, "center_y": .9}
            size_hint: (.5, .07)

        MDTextField:
            hint_text: ""
            helper_text: ""
            helper_text_mode: "on_focus"
            mode: "round"
            pos_hint: {"center_x": .5, "center_y": .75}
            size_hint: (.5, .07)

        MDTextField:
            hint_text: ""
            helper_text: ""
            helper_text_mode: "on_focus"
            mode: "round"
            pos_hint: {"center_x": .5, "center_y": .6}
            size_hint: (.5, .07)

        MDTextField:
            hint_text: ""
            helper_text: ""
            helper_text_mode: "on_focus"
            mode: "round"
            pos_hint: {"center_x": .5, "center_y": .45}
            size_hint: (.5, .07)
        
        MDFillRoundFlatIconButton:
            text: "Submit"
            icon: "keyboard-return" 
            on_release: app.root.current="welcome"
            font_size: sp(30)  
            size_hint:(.3, .1)
            pos_hint: {"center_x": .5, "center_y": .21}

        MDFillRoundFlatIconButton:
            text: "Go back"
            icon: "keyboard-backspace" 
            on_release: app.root.current="welcome"
            font_size: sp(30)  
            size_hint:(.3, .1)
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
    GPSlan = StringProperty('0')
    GPSlon = StringProperty('0')

class GpsTest(MDApp):
    current_lat = 50  # Default value
    current_lon = 14  # Default value

    # Pokud je platforma Android, zapni GPS a nastav jí na metodu on_gps_location
    if platform == "android":
        def on_start(self):
            gps.configure(on_location=self.on_location)
            gps.start()
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()


        #Hlavní metoda GPS. Provede se vždy když přijde nová GPS zpráva. 
        def on_location(self, **kwargs):
            sm = ScreenManager()
            print(kwargs)
            label_widget = self.root.ids.gps
            label_widget.text = f'Latitude: {kwargs["lat"]}, Longitude: {kwargs["lon"]}'
            sm.GPSlan = kwargs["lat"]
            sm.GPSlon = kwargs["lon"]

            self.center_on_gps(self.current_lat, self.current_lon)

    #Pokud není platforma Android, nezapínej GPS        
    else:
        print("Desktop version starting.")



    #Metoda Build načte kv string
    def build(self):
        self.theme_cls.theme_style = "Dark" #Pozadí
        self.theme_cls.primary_palette = "Orange" #Hlavní barva
        sm = Main()    
        return Builder.load_string(kv) #Načtení kv stringu



    #Žádání o oprávnění
    def request_android_permissions(self):

        from android.permissions import request_permissions, Permission

        def callback(permissions, results):

            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)
    

    def center_on_gps(self):
        mapview = self.root.get_screen('run').ids.mapview  # Accessing the MapView widget
        mapview.center_on(self.current_lat, self.current_lon)  # Specify the desired latitude and longitude

GpsTest().run()
