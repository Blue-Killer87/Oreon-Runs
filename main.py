from kivymd.app import MDApp
from kivy.clock import mainthread, Clock
from kivy.utils import platform
from plyer import gps, notification
from kivy_garden.mapview import MapMarker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.metrics import dp, sp
from kivy_garden.qrcode import QRCodeWidget
from kivymd.uix.label import MDLabel
from LineDrawLayer import LineDrawLayer
from screens import *
import numpy as np
from kalman import KalmanSmoother
from kivy.core.window import Window
from pathlib import Path
from kivy.uix.boxlayout import BoxLayout
#if platform != "android" or platform != "ios":
 #   Window.size = (900, 800)
  #  Window.minimum_width, Window.minimum_height = Window.size
if platform == 'android':
    import android
import math

def android_start_service(name):  
        from android import mActivity  
        from jnius import autoclass  
        print(f'Starting service {name}')
        context = mActivity.getApplicationContext()  
        service_name = str(context.getPackageName()) + '.Service' + name  
        service = autoclass(service_name)  
        service.start(mActivity, '')  # starts or re-initializes a service  
        print('service started')
        return service



class OreonApp(MDApp):

################################################################################################################
#Základní nastavení na startu:
    
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
            self.observations = []
            self.GPSonBackground = False
            if platform == 'android':
                self.start_service()

            if platform == 'android':
                self.request_android_permissions()


            
        
                
    def on_gps_update(self):
        # Update Kalmanova Filteru (W.I.P)
        observation = [self.gpslat, self.gpslon]
        self.filtered_state_means = self.kalman_filter.filter_update(
            self.filtered_state_means, observation
        )[0]

        # Update s uhlazenými souřadnicemi
        #smooth_lat, smooth_lon = self.filtered_state_means[0], self.filtered_state_means[1]
        #marker = MapMarker(lat=smooth_lat, lon=smooth_lon)
        #self.mapviewRun.add_marker(marker)

    #Servis na pozadí (W.I.P)
    

    def start_service(self):  
        #dprint('entered start_service()')  
        print("Start_Service got called")
        if platform == 'android':  
            print("Android detected, starting android service")
            self.service = android_start_service('Gps')
            #dprint(f'started android service. {self.service}')  

        elif platform in ('linux', 'linux2', 'macos', 'win'):  
            from runpy import run_path  
            from threading import Thread  
            self.service = Thread(  
                target=run_path,  
                args=['./gps.py'],  
                kwargs={'run_name': '__main__'},  
                daemon=True  
            )  
            self.service.start()  
    
        else:  
            raise NotImplementedError(  
                "service start not implemented on this platform"  
            )
################################################################################################################
#GPS konfigurace a inicializace:
                
    if platform == "android":
        def on_start(self):
            gps.configure(on_location=self.on_location)
            
            #gps.start(minTime=5000, minDistance=1)
            print("gps.py: Android detected. Requesting permissions")
            self.oldlat = 0
            self.oldlon = 0
            self.removelat = 0
            self.removelon = 0

        #Hlavní GPS funkce, zavolá se vždy když se obdrží nová GPS telemetrie
        @mainthread
        def on_location(self, **kwargs):
            print("Got location")
            if (kwargs['accuracy'] < 20 or kwargs['accuracy'] > 110):
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

                self.loc = np.array([self.gpslat, self.gpslon])
                self.observations.append(self.loc)

                if self.waitingforgps == True:
                    self.startPin()
                    self.waitingforgps == False
                    print("fetched starting location")
                Clock.schedule_once(self.proc_location, 0)

        def proc_location(self, dt):        
            
            '''     
            Další Kalman funkce (W.I.P)

            initial_state_mean = np.array([0, 0])  # Initial position (latitude, longitude)
            initial_state_covariance = np.eye(2) * 0.1  # Initial covariance matrix
            transition_matrix = np.eye(2)  # Identity matrix for simplicity
            observation_matrix = np.eye(2)  # Identity matrix for simplicity
            observation_covariance = np.eye(2) * 0.1  # Observation covariance matrix
            process_covariance = np.eye(2) * 0.01  # Process covariance matrix
            print(f'Kalman inicialises...')
            kalman_smoother = KalmanSmoother(initial_state_mean, initial_state_covariance, transition_matrix, observation_matrix, observation_covariance, process_covariance)
            smoothed_states = kalman_smoother.smooth(self.observations)
            

            print(f'Smoothened states: {smoothed_states}')
            for state in smoothed_states:
                print(f'State: {state}')
            try:
                self.smoothlatOLD = self.smoothlat
                self.smoothlonOLD = self.smoothlon
            except:
                print("First location, no previous kalman results.")
            '''
       

            if self.oldlat != 0 and self.oldlon != 0:
                # Kreslení čáry
                my_coordinates = [[self.gpslat, self.gpslon], [self.oldlat, self.oldlon]]
                lml3 = LineDrawLayer(coordinates=my_coordinates, color=[0, 0, 1, 1])
                if self.root.current == 'run':
                    self.mapviewRun.add_layer(lml3, mode="scatter")
                else:
                    self.mapviewTrack.add_layer(lml3, mode="scatter")


            else:    
                print("still initializing")
            self.oldlat = self.gpslat
            self.oldlon = self.gpslon

    #Pokud platforma není Android, nezapípen lokaci    
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

    def StaticGPS(self):
        if platform == 'android':
            print('Inicialising GPS and stuff')
            gps.start(minTime= 5000, minDistance=15)
        else:
            print("unsupported platform for GPS")



################################################################################################################
#Funkce pro stopky:

    def update(self, *args):
        self.seconds += 1

        if self.seconds == 60:
            self.seconds = 0
            self.minutes += 1

            if self.minutes == 60:
                self.minutes = 0
                self.hours += 1

        # Updatuj labely na počáteční nuly (01,02...)
        self.stopwatch.text = f'{self.format_digit(self.hours)}:{self.format_digit(self.minutes)}:{self.format_digit(self.seconds)}'


    def format_digit(self, value):
        # Pomocná funkce pro počáteční nuly
        return f'{value:02}'

    def toggle_counter(self, on):
        # Vypínání a zapínání stopek (Jen widgetu, né funkce) 
        self.stopwatch.opacity = 1.0 if on else 0.0

    def stop_counter(self):
        # Ukončení počítání stopek
        self.root.get_screen('run').remove_widget(self.stopwatch)
        self.root.get_screen('preview').add_widget(self.stopwatch)

        counter_data = self.get_counter_data()

        self.stopwatch.text = f"Time: {self.format_digit(counter_data['hours'])}:{self.format_digit(counter_data['minutes'])}:{self.format_digit(counter_data['seconds'])}"
        print(counter_data)
        
        Clock.unschedule(self.update)

    def get_counter_data(self):
        # Návrat dat ze stopek
        return {'hours': self.hours, 'minutes': self.minutes, 'seconds': self.seconds}
    

################################################################################################################
#Funkce generátoru QR kódů:
    
    def submit_create(self):
        try:
            if int(self.root.get_screen('create').ids.tcheckpoints.text) > 0 and self.root.get_screen('create').ids.tname.text != "":
            
                self.root.current = "createqr"
                self.a = 0
                self.checkpoints = int(self.root.get_screen('create').ids.tcheckpoints.text)
                self.trackname = self.root.get_screen('create').ids.tname.text
                self.trackdesc = self.root.get_screen('create').ids.tdesc.text
                self.infoLabel = MDLabel(text='Zde si můžete vytvořit a stáhnout QR kódy jeden po druhém .', font_size=sp(60), color=(1,1,1,1), markup='True', halign='center')
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
            self.fade = 1
            self.error = Label(text='Prosím zadejte název trasy a počet stanovišť (Musí být čislo)', font_size=dp(15), halign='center', valign='middle', color=(1,0,0,1), markup='True')
            self.error.pos_hint ={'center_x': 0.5, 'center_y': 0.25}
            self.root.get_screen('create').ids.floatcr.add_widget(self.error)
            Clock.schedule_once(self.fadecreatelabel, 5)

    def removecreatelabel(self):
        self.root.get_screen('create').ids.floatcr.remove_widget(self.error)

    def fadecreatelabel(self, dt):
        self.error.opacity = self.fade
        self.fade -= 0.05
        self.fade = round(self.fade,2)
        if self.fade <= 0:
            self.removecreatelabel()
        else:
            Clock.schedule_once(self.fadecreatelabel, .05)


    def gen_qr(self):  
        if self.root.current == 'createqr':
            self.root.get_screen('createqr').ids.floatqr.remove_widget(self.infoLabel)
            self.a += 1 
            if self.a <= self.checkpoints:
                self.remaining = self.checkpoints - 1
                self.root.get_screen('createqr').ids.floatqr.add_widget(QRCodeWidget(data=f"OreonQRcodeCheckpoint {self.a}"))
                QRCodeWidget.size_hint=(.9, .6)
                QRCodeWidget.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
                QRCodeWidget.show_border = False
                self.WhichQR.text=f'Stanovišťě #{self.a}'
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
            self.QR.size_hint = (.7, .7)
            self.QR
       

    def downloadQR(self):
        if platform == 'android':
            from android.storage import primary_external_storage_path
            dir = primary_external_storage_path()
            download_dir_path = os.path.join(dir, 'Download')

            if self.root.current == 'createqr':
                print(f'Exporting checkpoint QR code as {download_dir_path}/{self.trackname}-QRCheckpoint{self.a}.png')
                self.QR.export_to_png(filename= f'{download_dir_path}/{self.trackname}-QRCheckpoint{self.a}.png', scale=5)
            
            else:
                try:
                    print(f'Exporting track QR code as {download_dir_path}/{self.trackname}-QR.png')
                    self.QR.export_to_png(filename= f'{download_dir_path}/{self.trackname}-QR.png', scale=5)
                                   
                except:
                    print('Something went wrong with exporting track QR')

        else:
            path = str(Path.home() / "Downloads")
            if self.root.current == 'createqr':
                print(f'Exporting checkpoint QR code as {path}/{self.trackname}-QRCheckpoint{self.a}.png')
                self.QR.export_to_png(filename= f'{path}/{self.trackname}-QRCheckpoint{self.a}.png', scale=5)
                notification.notify(
                    title = "QR downloaded",
                    message=" You can find your QR in your downloads folder" ,
                    timeout=2
                )
            
            else:
                try:
                    print(f'Exporting track QR code as {path}/{self.trackname}-QR.png')
                    self.QR.export_to_png(filename= f'{path}/{self.trackname}-QR.png', scale=5)
                    notification.notify(
                        title = "QR downloaded",
                        message=" You can find your QR in your downloads folder" ,
                        timeout=2
                    )                    
                except:
                    print('Something went wrong with exporting track QR')

################################################################################################################
#Oprávnění:
    
    def request_android_permissions(self):

        from android.permissions import request_permissions, Permission

        def callback(permissions, results):

            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.INTERNET, Permission.ACCESS_FINE_LOCATION, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE, Permission.CAMERA], callback)
    

################################################################################################################
#Funkce dialogu:
    dialog = None

    def show_alert_dialog(self):
        if self.root.current == "run" and self.started == True:
            #Debug v případě, že přepínač dialogu selže
            #print(self.started)
            #print(self.root.current)
            if not self.dialog:
                self.dialog = MDDialog(
                    text="Chcete ukončit běh? (Běh nelze obnovit)",
                    buttons=[
                        MDFlatButton(
                            text="Pokračovat",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_press=self.cancelcall,

                        ),
                        MDFlatButton(
                            text="Ukončit",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_press=self.discardcall,
                        ),
                    ],
                )
            self.dialog.open()


        else:
            #Debug v případě, že přepínač dialogu selže
            #print(self.started)
            #print(self.root.current)
            if not self.dialog:
                self.dialog = MDDialog(
                    text="Opravdu se chcete vrátit?",
                    buttons=[
                        MDFlatButton(
                            text="Zůstat zde",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_press=self.cancelcall,

                        ),
                        MDFlatButton(
                            text="Jít zpět",
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
#Vytváření pinů pro trasování:
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

        self.String =-f"{self.TrackPointCounter}-{self.PinString}-{self.SPinLat}-{self.SPinLon}-{self.EPinLat}-{self.EPinLon}-{self.trackname}-{self.trackdesc}"

        self.root.current = "trackqr"
        print(self.String)

        for marker in self.CreateExistingMarkers:
            self.mapviewTrack.remove_marker(marker)
        self.CreateExistingMarkers = []
        print('Removing pins')
        self.LineDraw.unload()


if __name__ == '__main__':
    OreonApp().run()
