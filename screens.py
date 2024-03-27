from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
from kivy.clock import mainthread
from plyer import gps
from kivy.properties import StringProperty, ObjectProperty
from kivy_garden.mapview import MapMarker
from kivy.clock import time

from camera4kivy import Preview
from PIL import Image
from pyzbar.pyzbar import decode


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
            if app_instance.GPSonBackground == False:
                gps.stop()
            else:
                pass
        except NotImplementedError:
            print("Problem with GPS, not implemented on your platform.")
        


class CreateScreen(Screen):
    pass

class CreateQRScreen(Screen):
    pass

class ScanAnalyze(Preview): #Analýza QR kódu
    extracted_data=ObjectProperty(None) 
    def analyze_pixels_callback(self, pixels, image_size, image_pos, scale, mirror): #Funkce pro analýzu
        try:
            pimage=Image.frombytes(mode='RGBA',size=image_size,data=pixels) #Rozeber obrázek na bitovou strukturu
            list_of_all_barcodes=decode(pimage) #Ze struktury dekókuj QR pattern
            

            if list_of_all_barcodes: #Pokud se jedná o QR kód
                first_barcode_data = list_of_all_barcodes[0].data.decode('utf-8') #Zapiš data do listu ve formátu UTF8
                if self.extracted_data: #Pokud máš kam
                    self.extracted_data(first_barcode_data) #Ulož data do univerzální proměnné
                else:
                    print("Not found")
        except:
            print('Invalid code')



class ScanQRRun(Screen):
    checkpoints = 0
    runpins = []
    startpin = []
    endpin = []
    
    def on_enter(self, *args):
        self.ids.preview.connect_camera(enable_analyze_pixels = True,default_zoom=0.0)
        self.done = False
    
    @mainthread
    def got_result(self, result):
        try:
            self.ids.ti.text=str(result)
            self.qrdata = result
            result = None
            if self.done == False:
                try:
                    self.checkpoint()
                except:
                    print('Something is wrong with checking for checkpoint')
            else: 
                print("Already marked checkpoint.")
        except:
            print('Wrong QR code')
        
    def checkpoint(self):
        try:
            scanQRcreate = ScanQRCreate()
            app = App.get_running_app()
            mapviewRun = app.root.get_screen('run').ids.mapview
            mapviewPreview = app.root.get_screen('preview').ids.mapview
            try:
                self.donepoints= []
                StartLat = self.startpin[0]
                StartLon = self.startpin[1]
                EndLat = self.endpin[0]
                EndLon = self.endpin[1]
                self.ids.preview.disconnect_camera()
            except:
                pass
            


            Raw_data = self.qrdata
            Proc_data = []
            Proc_data = Raw_data.split()
            self.Checkpoint_num = int(Proc_data[1])
            if self.Checkpoint_num > 0 and self.Checkpoint_num < 99:
                numberofpoints = len(self.runpins)
                m = 0
                for i in range(numberofpoints):
                    
                    chosenpin = self.runpins[m]
                    chosenpin = chosenpin.replace("-"," ").split()
                
                    which = int(chosenpin[0])
                    if which == self.Checkpoint_num:
                        cpinLat = float(chosenpin[1])
                        cpinLon = float(chosenpin[2])
                        self.runpins.pop(m)
                        self.donepoints.append(cpinLat)
                        self.donepoints.append(cpinLon)
                        DonePin = MapMarker(lat = cpinLat, lon = cpinLon, source= "data/donepin.png")
                        mapviewRun.add_marker(DonePin)
                        app.ExistingMarkers.append(DonePin)

                        DonePinP = MapMarker(lat = cpinLat, lon = cpinLon, source= "data/donepin.png")
                        mapviewPreview.add_marker(DonePinP)
                        app.ExistingMarkersPreview.append(DonePinP)

                    else:
                        m += 1
                    app.root.current = 'run'

            for marker in app.ExistingMarkers:
                mapviewRun.remove_marker(marker)
            
            for marker in app.ExistingMarkersPreview:
                mapviewPreview.remove_marker(marker)
            
            app.ExistingMarkers = []
            app.ExistingMarkersPreview = []
            
            howmanypins = len(self.runpins)
            n = 0
            for i in range(howmanypins):
                npin = self.runpins[n]
                npin = npin.replace("-"," ").split()
                npinLat = npin[1]
                npinLon = npin[2]
                npoint = MapMarker(lat = npinLat, lon = npinLon, source= "data/pin.png")
                npointP = MapMarker(lat = npinLat, lon = npinLon, source= "data/pin.png")
                mapviewRun.add_marker(npoint)
                mapviewPreview.add_marker(npointP)
                npin = []
                n += 1
                app.ExistingMarkers.append(npoint)
                app.ExistingMarkersPreview.append(npointP)
            
            Spoint = MapMarker(lat = StartLat, lon = StartLon, source= "data/startpin.png")
            Epoint = MapMarker(lat = EndLat, lon = EndLon, source= "data/finish.png")
            mapviewRun.add_marker(Spoint)
            app.ExistingMarkers.append(Spoint)
            mapviewRun.add_marker(Epoint)
            app.ExistingMarkers.append(Epoint)

            SpointP = MapMarker(lat = StartLat, lon = StartLon, source= "data/startpin.png")
            EpointP = MapMarker(lat = EndLat, lon = EndLon, source= "data/finish.png")
            mapviewPreview.add_marker(SpointP)
            app.ExistingMarkersPreview.append(SpointP)
            mapviewPreview.add_marker(EpointP)
            app.ExistingMarkersPreview.append(EpointP)

            self.done = True
        
        except:
            print('Problem with loading map')
            
class ScanQRCreate(Screen):
    
    
    def on_enter(self, *args):
         self.Loaded = False
         self.ids.preview.connect_camera(enable_analyze_pixels = True,default_zoom=0.0)

    @mainthread
    def got_result(self,result):
        self.ids.ti.text=str(result)
        self.qrdata = result
        try:
            self.proc_track_string()
        except:
            print('Invalid track QR')
        
        if self.Loaded == False:
            try:
                self.load_map()
            except:
                print('Wrong code')
        else:
            print("Map already loaded")
       

    def proc_track_string(self):
        try:
            #Funkce na rozkládání řetězce na jednotlivé údaje
            #Příklad načteného řetezce: 4-14.7-7.5-14.8-7.9-14.9-8.0-15.0-8.1-15.1-9.2-14.3-8.2-Testing@Track-Description

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
        
            try:
                StartLat = ArrString[Checkpoints*2+1]
                self.StartLat = float(StartLat)
                
                Startlon = ArrString[Checkpoints*2+2]
                self.StartLon = float(Startlon)
                print(f"Starting lat is {StartLat} and lon is {Startlon}")

                EndLat = ArrString[Checkpoints*2+3]
                self.EndLat = float(EndLat)
                Endlon = ArrString[Checkpoints*2+4]
                self.EndLon = float(Endlon)
                print(f"Ending lat is {EndLat} and lon is {Endlon}")
            except:
                pass
            
            try:
                Name = ArrString[Checkpoints*2+5].replace("@", " ")
                Description = ArrString[Checkpoints*2+6].replace("@", " ")
                print(f"Name: {Name}")
                print(f"Description: {Description}")
            except:
                print('Invalid name or description')
            return True
        except:
            pass
    

    def load_map(self):
        try:
            app = App.get_running_app()
            app.ExistingMarkers = []
            app.ExistingMarkersPreview = []
            self.runpins = []
            qr_run = ScanQRRun()
            self.Loaded = True
            

            print('Loading map from QR code')
            app.root.current = 'run'
            mapviewRun = app.root.get_screen('run').ids.mapview
            mapviewPreview = app.root.get_screen('preview').ids.mapview
            RawString = self.qrdata
            ArrString = []

            Spoint = MapMarker(lat = self.StartLat, lon = self.StartLon, source= "data/startpin.png")
            SpointPreview = MapMarker(lat = self.StartLat, lon = self.StartLon, source= "data/startpin.png")
            qr_run.startpin.append(self.StartLat)
            qr_run.startpin.append(self.StartLon)
            mapviewRun.add_marker(Spoint)
            mapviewPreview.add_marker(SpointPreview)
            print('placing startpin')
            mapviewRun.center_on(self.StartLat, self.StartLon)
            mapviewPreview.center_on(self.StartLat, self.StartLon)
            app.ExistingMarkers.append(Spoint)
            app.ExistingMarkersPreview.append(SpointPreview)


            Epoint = MapMarker(lat = self.EndLat, lon = self.EndLon, source= "data/finish.png")
            EpointPreview = MapMarker(lat = self.EndLat, lon = self.EndLon, source= "data/finish.png")
            qr_run.endpin.append(self.EndLat)
            qr_run.endpin.append(self.EndLon)
            mapviewRun.add_marker(Epoint)
            mapviewPreview.add_marker(EpointPreview)
            app.ExistingMarkers.append(Epoint)
            app.ExistingMarkersPreview.append(EpointPreview)

            print('placing Endpin')

            RawString=RawString.replace("-", " ").split()
            ArrString = RawString
            n = 0
            pointn = 0
            Checkpoints = int(ArrString[0])
            qr_run.checkpoints = Checkpoints
            for i in range(Checkpoints):
                PinLat = ArrString[n+1]
                PinLon = ArrString[n+2]
                pointn += 1
                print(f"Point number {pointn} lattitude is {PinLat} and longitude is {PinLon}")
                string = f"{pointn}-{PinLat}-{PinLon}"
                qr_run.runpins.append(string)
                n += 2
                point = MapMarker(lat = PinLat, lon = PinLon, source= "data/pin.png")
                pointPreview = MapMarker(lat = PinLat, lon = PinLon, source= "data/pin.png")

                print('Placing pin')
                mapviewRun.add_marker(point)
                mapviewPreview.add_marker(pointPreview)
                app.ExistingMarkers.append(point)
                app.ExistingMarkersPreview.append(pointPreview)
                print(f"Existing markers list to remove = {app.ExistingMarkers}")
        except:
            pass
            

    def build_startend_points(self):
        try:
            app = App.get_running_app()
            mapviewRun = app.root.get_screen('run').ids.mapview

            Spoint = MapMarker(lat = self.StartLat, lon = self.StartLon, source= "data/startpin.png")
            Epoint = MapMarker(lat = self.EndLat, lon = self.EndLon, source= "data/endpin.png")
            mapviewRun.add_marker(Spoint)
            app.ExistingMarkers.append(Spoint)
            mapviewRun.add_marker(Epoint)
            app.ExistingMarkers.append(Epoint)
        except:
            pass


    def on_leave(self, *args):
        try:
            self.ids.preview.disconnect_camera()
        except:
            print('Camera already disconnected')

class GetTrackQR(Screen):
    pass
class Main(ScreenManager):
    pass
