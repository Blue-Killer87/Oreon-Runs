from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.utils import platform
from plyer import gps
from kivy.properties import StringProperty, ObjectProperty
from kivy_garden.mapview import MapMarker, MapView, MapMarkerPopup, MapLayer
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
from camera4kivy import Preview
from PIL import Image
from pyzbar.pyzbar import decode
from kivy.uix.label import Label
from kivy.metrics import dp, sp
from kivy_garden.qrcode import QRCodeWidget
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
import os
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
import time

#if platform != "android" or platform != "ios":
 #   Window.size = (900, 800)
  #  Window.minimum_width, Window.minimum_height = Window.size


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

    def clear_canvas(self):
        with self.canvas:
            self.canvas.clear()

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
            Line(points=self.line_points, width=4)

            # Retrieve the last saved coordinate space context
            PopMatrix()



class WelcomeScreen(Screen):
    pass

class ChooseTrackScreen(Screen):
    pass

class RunScreen(Screen):
    pass

class RunResultScreen(Screen):
    pass

class TrackingScreen(Screen):
    
    def on_enter(self, *args):
        app_instance = App.get_running_app()
        app_instance.GPSstart()
        app_instance.waitingforgps = True
        self.TrackPointCounter = 0

    def on_leave(self, *args):
        app_instance = App.get_running_app()
        try:
            gps.stop()
        except NotImplementedError:
            print("Problem with GPS, not implemented on your platform.")
        app_instance.last = True
        


class CreateScreen(Screen):
    pass

class CreateQRScreen(Screen):
    pass

class ScanAnalyze(Preview):
	extracted_data=ObjectProperty(None)


	def analyze_pixels_callback(self, pixels, image_size, image_pos, scale, mirror):
		pimage=Image.frombytes(mode='RGBA',size=image_size,data=pixels)
		list_of_all_barcodes=decode(pimage)
		

		if list_of_all_barcodes:
			first_barcode_data = list_of_all_barcodes[0].data.decode('utf-8')
			if self.extracted_data:
				self.extracted_data(first_barcode_data)
			else:
				print("Not found")


class ScanQRScreen(Screen):


    def on_enter(self, *args):
         self.ids.preview.connect_camera(enable_analyze_pixels = True,default_zoom=0.0)

    @mainthread
    def got_result(self,result):
        self.ids.ti.text=str(result)
        self.qrdata = result
        self.proc_track_string()

    def proc_track_string(self):
        #The function that will process the string of a track into individual data pieces that are:
        #0 - Number of checkpoints (will count by this number to make sure it's real)
        #1 - Checkpoint n lat
        #2 - Checkpoint n lon (n times criss cross)
        #3 - Starting point lat
        #4 - Starting point lon
        #5 - Ending point lat
        #6 - Ending point lon
        #7 - Name of the track
        #8 - Track description

        #Example loaded string: 4-14.7-7.5-14.8-7.9-14.9-8.0-15.0-8.1-15.1-9.2-14.3-8.2-Testing@Track-This@is@a@testing@track@for@loading@a@string

        RawString = self.qrdata
        ArrString = []
  
        RawString=RawString.replace("-", " ").split()
        ArrString = RawString
        n = 0
        pointn = 0
        Checkpoints = int(ArrString[0])

        for i in range(Checkpoints):
            PinLat = ArrString[n+1]
            PinLon = ArrString[n+2]
            pointn += 1
            print(f"Point number {pointn} lattitude is {PinLat} and longitude is {PinLon}")
            n += 2

        StartLat = ArrString[Checkpoints*2+1]
        Startlon = ArrString[Checkpoints*2+2]
        print(f"Starting lat is {StartLat} and lon is {Startlon}")

        EndLat = ArrString[Checkpoints*2+3]
        Endlon = ArrString[Checkpoints*2+4]
        print(f"Ending lat is {EndLat} and lon is {Endlon}")
        try:
            Name = ArrString[Checkpoints*2+5].replace("@", " ")
            Description = ArrString[Checkpoints*2+6].replace("@", " ")
            print(f"Name: {Name}")
            print(f"Description: {Description}")
        except:
            print('Invalid name or description')
    def on_leave(self, *args):
        self.ids.preview.disconnect_camera()

class GetTrackQR(Screen):
    pass
class Main(ScreenManager):
    pass

class FileChooserPopup(Popup):
################################################################################################################
#The save file function:
    file_chooser = ObjectProperty(None)

    def __init__(self, qr_widget, **kwargs):
        super(FileChooserPopup, self).__init__(**kwargs)
        self.qr_widget = qr_widget
        self.file_chooser = FileChooserIconView()
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
        submit_button = Button(text='Submit', size_hint_x=None, width=100, on_press=self.save_qr)
        cancel_button = Button(text='Cancel', size_hint_x=None, width=100, on_press=self.dismiss_popup)
        button_layout.add_widget(submit_button)
        button_layout.add_widget(cancel_button)

        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(self.file_chooser)
        main_layout.add_widget(button_layout)

        self.content = main_layout

    def save_qr(self, instance):
        selected_path = self.file_chooser.path
        image_path = os.path.join(selected_path)

        self.qr_widget.export_as_image('OreonQRcode', image_path)
        print(f"QR code saved as {image_path}")
        self.dismiss_popup()

    def dismiss_popup(self):
        self.dismiss()

class OreonApp(MDApp):

################################################################################################################
#Settings to setup at start:
    
    def build(self):
            self.theme_cls.theme_style = "Dark" #Background
            self.theme_cls.primary_palette = "Blue" #Main color
            self.mapviewRun = self.root.get_screen('run').ids.mapview
            self.mapviewTrack = self.root.get_screen('tracking').ids.mapview
            self.started = False

            self.seconds = 0
            self.minutes = 0
            self.hours = 0  
            self.stopwatch = Label(text='00:00:00', font_size=dp(40), halign='center', valign='middle', color=(0,0,.5,1), markup='True')
            self.stopwatch.size_hint = (None, None)
            self.stopwatch.pos_hint = {'center_x': 0.5, 'center_y': 0.87}
            self.generated = False
            self.QR = None
            self.file_chooser_popup = None
            self.first = True
            self.last = False
            self.gpslat = 0
            self.gpslon = 0
            self.waitingforgps = False
            self.TrackPins = []
            self.TrackPointCounter = 0

            if platform == 'android':
                self.request_android_permissions()


################################################################################################################
#GPS configurations and start:
                
    if platform == "android":
        def on_start(self):
            gps.configure(on_location=self.on_location)
            
            #gps.start(minTime=5000, minDistance=1)
            print("gps.py: Android detected. Requesting permissions")
            self.oldlat = 0
            self.oldlon = 0

        #Main GPS method, calls itself every time the app gets new GPS telemtry
        @mainthread
        def on_location(self, **kwargs):
            print("Got location")
            if (kwargs['accuracy'] < 10 or kwargs['accuracy'] > 99):
                print(kwargs)
                print('Location is bad')
                #self.aproxgpslat = kwargs["lat"]
                #self.aproxgpslon = kwargs["lon"]
                #Clock.schedule_once(self.proc_aprox_location, 5)
            else:
                print(kwargs)
                print('Location is fine')
                self.gpslat = kwargs["lat"]
                self.gpslon = kwargs["lon"]
                if self.waitingforgps == True:
                    self.startPin()
                    self.waitingforgps == False
                    print("fetched starting location")

                if self.last == True:
                    self.endPin()
                    print("Initated ending sequence")
                Clock.schedule_once(self.proc_location, 0)

        def proc_location(self, dt):        
            self.point = MapMarker(lat = self.gpslat, lon = self.gpslon, source= "data/Blank.png")
            #
            #mapview.remove_marker(self.point)
            if self.root.current == 'run':
                self.mapviewRun.add_marker(self.point)
            else:
                self.mapviewTrack.add_marker(self.point)
                
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
                if self.root.current == 'run':
                    self.mapviewRun.add_layer(lml3, mode="scatter")
                else:
                    self.mapviewTrack.add_layer(lml3, mode="scatter")


            else:    
                print("still initializing")
            self.oldlat = self.gpslat
            self.oldlon = self.gpslon

    #If platform is not Android, don't turn GPS on      
    else:
        print("Desktop version starting.")

    def start(self):
           
        self.GPSstart()
        print("Run starting...")

        self.started = True
        try:
            self.root.get_screen('run').add_widget(self.stopwatch)
            Clock.schedule_interval(self.update, 1)
        except:
            print("Stopwatch error: Already existing")

    def GPSstart(self):
        if platform == 'android':
            print('Inicialising GPS and stuff')
            gps.start(minTime= 500, minDistance=5)
        else:
            print("unsupported platform for GPS")


################################################################################################################
#Stopwatch functions:

    def update(self, *args):
        self.seconds += 1

        if self.seconds == 60:
            self.seconds = 0
            self.minutes += 1

            if self.minutes == 60:
                self.minutes = 0
                self.hours += 1

        # Update the label text with leading zeros
        self.stopwatch.text = f'{self.format_digit(self.hours)}:{self.format_digit(self.minutes)}:{self.format_digit(self.seconds)}'


    def format_digit(self, value):
        # Helper function to add leading zero if value is less than 10
        return f'{value:02}'

    def toggle_counter(self, on):
        # Turn on/off the counter label by adjusting its opacity
        self.stopwatch.opacity = 1.0 if on else 0.0

    def stop_counter(self):
        # Stop the counter by canceling the scheduled updates
        self.root.get_screen('run').remove_widget(self.stopwatch)
        self.root.get_screen('preview').add_widget(self.stopwatch)

        counter_data = self.get_counter_data()

        self.stopwatch.text = f"Time: {self.format_digit(counter_data['hours'])}:{self.format_digit(counter_data['minutes'])}:{self.format_digit(counter_data['seconds'])}"
        print(counter_data)
        
        Clock.unschedule(self.update)

    def get_counter_data(self):
        # Return the current counter data
        return {'hours': self.hours, 'minutes': self.minutes, 'seconds': self.seconds}
    

################################################################################################################
#QR generation functions:
    
    def submit_create(self):
        try:
            if int(self.root.get_screen('create').ids.tcheckpoints.text) > 0:
            
                self.root.current = "createqr"
                self.a = 0
                self.checkpoints = int(self.root.get_screen('create').ids.tcheckpoints.text)
                self.infoLabel = MDLabel(text='You can create and download your QR codes here, one by one.', font_size=sp(60), color=(1,1,1,1), markup='True', halign='center')
                self.infoLabel.pos_hint = {"center_x": .5, "center_y": .7}
                self.root.get_screen('createqr').ids.floatqr.add_widget(self.infoLabel)
                self.WhichQR = Label(text='', font_size=dp(25), halign='center', valign='middle', color=(1,1,1,1), markup='True')
                self.WhichQR.pos_hint = {'center_x': 0.5, 'center_y': 0.95}
                self.root.get_screen('createqr').ids.floatqr.add_widget(self.WhichQR)
                if self.generated == True:
                    self.root.get_screen('createqr').ids.floatqr.remove_widget(self.infoLabel)
                else:
                    pass
                self.generated = False
        except:
            print("Invalid value")




    def gen_qr(self):  
        if self.root.current == 'createqr':
            self.root.get_screen('createqr').ids.floatqr.remove_widget(self.infoLabel)
            self.a += 1 
            if self.a <= self.checkpoints:
                self.remaining = self.checkpoints - 1
                self.root.get_screen('createqr').ids.floatqr.add_widget(QRCodeWidget(data=f"QRcodeCheckpoint {self.a}"))
                QRCodeWidget.size_hint=(.9, .6)
                QRCodeWidget.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
                self.WhichQR.text=f'Checkpoint #{self.a}'
                self.generated = True
                self.QR = QRCodeWidget()
                
            else:
                self.root.current = "tracking"
                self.WhichQR.text=''
        else:
            self.root.get_screen('trackqr').ids.floatqr.add_widget(QRCodeWidget(data=self.String))
            QRCodeWidget.size_hint=(.9, .6)
            QRCodeWidget.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
            self.QR = QRCodeWidget()

    def downloadQR(self):
        if hasattr(self, 'QR'):
            self.file_chooser_popup = FileChooserPopup(self.QR)
            self.file_chooser_popup.open()
            print('Exported the image')


################################################################################################################
#Permissions:
    
    def request_android_permissions(self):

        from android.permissions import request_permissions, Permission

        def callback(permissions, results):

            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.INTERNET, Permission.ACCESS_FINE_LOCATION, Permission.WRITE_EXTERNAL_STORAGE,Permission.CAMERA], callback)
    

################################################################################################################
#The exit dialog function:
    dialog = None

    def show_alert_dialog(self):
        if self.root.current == "run" and self.started == True:
            #Debug in case dialog switch fails
            #print(self.started)
            #print(self.root.current)
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

        else:
            #Debug in case dialog switch fails
            #print(self.started)
            #print(self.root.current)
            if not self.dialog:
                self.dialog = MDDialog(
                    text="Are you sure you want to go back?",
                    buttons=[
                        MDFlatButton(
                            text="Stay here",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_press=self.cancelcall,

                        ),
                        MDFlatButton(
                            text="Go back",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_press=self.discardcall,
                        ),
                    ],
                )
            self.dialog.open()

            
    def cancelcall(self, instance):
        self.dialog.dismiss()
        self.dialog = None
    def discardcall(self, instance):
        if self.root.current != "run":
            self.root.current = "welcome"
            self.seconds = 0
            self.minutes = 0
            self.hours = 0
            self.stopwatch.text = '00:00:00'
            self.dialog.dismiss()
            try:
                self.root.get_screen('preview').remove_widget(self.stopwatch)
                self.root.get_screen('run').remove_widget(self.stopwatch)
            except:
                print("No stopwatches existed")
        elif self.started == True:
            self.root.current = "preview"
            try:
                gps.stop()
            except NotImplementedError:
                print("Problem with GPS, not implemented on your platform.")
            self.dialog.dismiss()
            self.started = False
            self.dialog = None
            self.stop_counter()
            try:
                self.mapviewRun.remove_marker(self.point)
            except:
                print("Something went wrong with removing the pins")


        else: 
            self.root.current = "welcome"
            self.dialog.dismiss()
            self.dialog = None
            self.seconds = 0
            self.minutes = 0
            self.hours = 0
            self.stopwatch.text = '00:00:00'

            try:
                self.root.get_screen('preview').remove_widget(self.stopwatch)
                self.root.get_screen('run').remove_widget(self.stopwatch)
            except:
                print("No stopwatches existed")

################################################################################################################
#Track create pin functions:
    def placePin(self):
        if platform == 'android':
            try:
                if self.gpslat == 0:
                    print('Waiting for first location to place a pin.')

                else:
                    if self.TrackPointCounter < self.checkpoints:
                        try:
                            self.a = self.gpslat
                            while self.a != self.oldlat:
                                print("Waiting for location update...")
                            self.PinLat = self.gpslat
                            self.PinLon = self.gpslon
                            self.Pin = MapMarker(lat=self.PinLat, lon=self.PinLon, source= "data/pin.png")
                            self.mapviewTrack.add_marker(self.Pin)
                            print("Pin placed")
                            self.TrackPins.append(self.PinLat)
                            self.TrackPins.append(self.PinLon)
                            self.TrackPointCounter += 1
                            print(f"Added pin to list: {self.TrackPins}, Number of total points place is now: {self.TrackPointCounter}")

                    
                        except:
                            print('Problem with getting location while placing pin.')
                    else:
                        print("Can't add another pin")
            
            except: 
                print("uknown error while placing pin")
        else:
            print('unsupported platform for GPS')
        #print(f"Last? {self.last}")
        #print(f"First? {self.first}")
        #self.mapview.center_on(kwargs['lat'], kwargs['lon'])
            
    def startPin(self, dt=None):
        if platform == 'android':
            try:
                if self.gpslat == 0:
                    self.waitingforgps = True
                else:      
                    self.SPinLat = self.gpslat
                    self.SPinLon = self.gpslon
                    self.SPin = MapMarker(lat=self.SPinLat, lon=self.SPinLon, source= "data/startpin.png")
                    self.mapviewTrack.add_marker(self.SPin)
                    print("Starter Pin added")
                    self.first = False
                    self.mapviewTrack.center_on(self.gpslat, self.gpslon)
                    self.waitingforgps = False
            except:
                print("Waiting for initial location to place starting pin.")
                self.waitingforgps = True
                
        else:
            print('unsupported platform for GPS')

    def endPin(self):
        if platform == 'android':
            try:
                self.EPinLat = self.gpslat
                self.EPinLon = self.gpslon
                self.EPin = MapMarker(lat=self.EPinLat, lon=self.EPinLon, source= "data/endpin.png")
                self.mapviewTrack.add_marker(self.EPin)
                print("End pin added")
                

                self.last = False
            except:
                print("Uknown error while placing end pin")
        else:
            print('unsupported platform for GPS')

################################################################################################################
            
    def ASSET(self): #Advanced Sequential String Encryption Technology
        self.endPin()
        print(f"EpinLat: {self.EPinLat}")
        print(f"EpinLon: {self.EPinLon}")
        self.PinString = "-".join(str(element) for element in self.TrackPins)

        self.String =  f"{self.TrackPointCounter}-{self.PinString}-{self.SPinLat}-{self.SPinLon}-{self.EPinLat}-{self.EPinLon}-sgdgdg-{self.checkpoints}"

        self.root.current = "trackqr"
        print(self.String)


if __name__ == '__main__':
    OreonApp().run()
