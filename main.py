from kivymd.app import MDApp
from kivy.clock import mainthread, Clock
from kivy.utils import platform
from plyer import gps
from kivy_garden.mapview import MapMarker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.metrics import dp, sp
from kivy_garden.qrcode import QRCodeWidget
from kivymd.uix.label import MDLabel
from LineDrawLayer import LineDrawLayer
from plyer import filechooser
from screens import *


#if platform != "android" or platform != "ios":
 #   Window.size = (900, 800)
  #  Window.minimum_width, Window.minimum_height = Window.size


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
            self.gpslat = 0
            self.gpslon = 0
            self.waitingforgps = False
            self.TrackPins = []
            self.TrackPointCounter = 0
            self.ExistingMarkers = []
            self.CreateExistingMarkers = []
            self.ExistingMarkersPreview = []
            self.LineDraw = LineDrawLayer()

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
            self.removelat = 0
            self.removelon = 0

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
                Clock.schedule_once(self.proc_location, 0)

        def proc_location(self, dt):        
            #self.point = MapMarker(lat = self.gpslat, lon = self.gpslon, source= "data/Blank.png")
            #
            #mapview.remove_marker(self.point)
            #if self.root.current == 'run':
                #self.mapviewRun.add_marker(self.point)
            #else:
               # self.mapviewTrack.add_marker(self.point)
                
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
            gps.start(minTime= 5000, minDistance=15)
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
                self.root.get_screen('createqr').ids.floatqr.add_widget(QRCodeWidget(data=f"OreonQRcodeCheckpoint {self.a}"))
                QRCodeWidget.size_hint=(.9, .6)
                QRCodeWidget.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
                self.WhichQR.text=f'Checkpoint #{self.a}'
                self.generated = True
                self.QR = QRCodeWidget(data=f"QRcodeCheckpoint {self.a}")
                
            else:
                self.root.current = "tracking"
                self.WhichQR.text=''
        else:
            self.root.get_screen('trackqr').ids.floatqr.add_widget(QRCodeWidget(data=self.String))
            QRCodeWidget.size_hint=(.9, .6)
            QRCodeWidget.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
            self.QR = QRCodeWidget(data=self.String)



    def file_chooser(self):
        filechooser.choose_dir(on_selection=self.selected)

    def selected(self, selection):
        print(selection)
        if selection:
            self.qrpath = selection[0]
            self.downloadQR()

    def downloadQR(self):
        if self.root.current == 'createqr':
            print(f'Exporting checkpoint QR code as {self.qrpath}/QRCheckpoint{self.a}.png')
            self.QR.export_to_png(f'{self.qrpath}/QRCheckpoint{self.a}.png')
            
        else:
            try:
                self.QR.export_to_png(f'{self.qrpath}/QRTrack-{self.trackname}')
                                      
            except:
                print('Something went wrong with exporting track QR')

################################################################################################################
#Permissions:
    
    def request_android_permissions(self):

        from android.permissions import request_permissions, Permission

        def callback(permissions, results):

            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.INTERNET, Permission.ACCESS_FINE_LOCATION, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE, Permission.CAMERA], callback)
    

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
                for marker in self.ExistingMarkers:
                    self.mapviewRun.remove_marker(marker)
                self.ExistingMarkers = []
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
                            self.CreateExistingMarkers.append(self.Pin)
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
                    self.CreateExistingMarkers.append(self.SPin)
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
                self.CreateExistingMarkers.append(self.EPin)
                

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

        for marker in self.CreateExistingMarkers:
            self.mapviewTrack.remove_marker(marker)
        self.CreateExistingMarkers = []
        print('Removing pins')
        self.LineDraw.unload()


if __name__ == '__main__':
    OreonApp().run()
