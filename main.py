import os
os.system("py -m pip install boto3")

from kivy.base import runTouchApp
from kivy.lang import Builder

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

root = Builder.load_string(
    """
#:import MapSource kivy_garden.mapview.MapSource

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

RelativeLayout:

    MapView:
        id: mapview
        lat: 49.9
        lon: 14.4
        zoom: 8
        #size_hint: .5, .5
        #pos_hint: {"x": .25, "y": .25}

        #on_map_relocated: mapview2.sync_to(self)
        #on_map_relocated: mapview3.sync_to(self)

        MapMarker:
            lat: 50.6394
            lon: 3.057

        MapMarker
            lat: -33.867
            lon: 151.206

    Toolbar:
        top: root.top
        Button:
            text: "Praha, Česká republika"
            on_release: mapview.center_on(49.9, 14.4)
            on_release: 
        Button:
            text: "Vesnice"
            on_release: mapview.center_on(49.1089, 16.6271)     
        Spinner:
            text: "Výběr Map"
            values: MapSource.providers.keys()
            on_text: mapview.map_source = self.text

    Toolbar:
        Label:
            text: "Longitude: {}".format(mapview.lon)
        Label:
            text: "Latitude: {}".format(mapview.lat)
    """
)
    
runTouchApp(root)
