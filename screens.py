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
            gps.stop()
        except NotImplementedError:
            print("Problem with GPS, not implemented on your platform.")
        


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

class ScanQRRun(Screen):
    runpins = []
    def on_enter(self, *args):
        self.ids.preview.connect_camera(enable_analyze_pixels = True,default_zoom=0.0)

    @mainthread
    def got_result(self, result):
        self.ids.ti.text=str(result)
        self.qrdata = result
       
        self.checkpoint()
  
        
    def checkpoint(self):
        app = App.get_running_app()
        mapviewRun = app.root.get_screen('run').ids.mapview
        
        print('Matching checkpoint...')
        Raw_data = self.qrdata
        Proc_data = []
        Proc_data = Raw_data.split()
        self.Checkpoint_num = int(Proc_data[1])
        if self.Checkpoint_num > 0 and self.Checkpoint_num < 99:
            which = self.Checkpoint_num
            chosenpin = self.runpins[which-1]
            chosenpin = chosenpin.replace("-"," ").split()
            print (chosenpin)
            cpinLat = float(chosenpin[1])
            cpinLon = float(chosenpin[2])
            print (f"Checkpoint: {self.Checkpoint_num} Lat: {cpinLat} Lon: {cpinLon}")
        app.root.current = 'run'

        PinToRemove = app.ExistingMarkers[self.Checkpoint_num+1]
        print(f'Existing markers = {app.ExistingMarkers}')
        print(f'removing run pin {PinToRemove}')
        mapviewRun.remove_marker(PinToRemove)
        

        #donepin = MapMarker(lat = cpinLat, lon = cpinLon, source= "data/donepin.png")
        #mapviewRun.add_marker(donepin)
        #app.ExistingMarkers.append(donepin)

        mapviewPreview = app.root.get_screen('preview').ids.mapview
        PinToRemovePreview = app.ExistingMarkersPreview[self.Checkpoint_num+1]
        print(f'Existing markers = {app.ExistingMarkersPreview}')
        print(f'removing preview pin {PinToRemovePreview}')
        mapviewPreview.remove_marker(PinToRemovePreview)

        #donepinpreview = MapMarker(lat = cpinLat, lon = cpinLon, source= "data/donepin.png")
        #mapviewPreview.add_marker(donepinpreview)
        #app.ExistingMarkersPreview.append(donepinpreview)
        #print(f"This is the preview marker list: {app.ExistingMarkersPreview}")
    def on_leave(self, *args):
        try:
            self.ids.preview.disconnect_camera()
        except:
            print('Camera already disconnected')
class ScanQRCreate(Screen):
    
    
    def on_enter(self, *args):
         self.ids.preview.connect_camera(enable_analyze_pixels = True,default_zoom=0.0)

    @mainthread
    def got_result(self,result):
        self.ids.ti.text=str(result)
        self.qrdata = result
        try:
            self.proc_track_string()
        except:
            print('Invalid track QR')
        
        self.load_map()
       
        time.sleep(1)

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
        self.StartLat = float(StartLat)
        Startlon = ArrString[Checkpoints*2+2]
        self.StartLon = float(Startlon)
        print(f"Starting lat is {StartLat} and lon is {Startlon}")

        EndLat = ArrString[Checkpoints*2+3]
        self.EndLat = float(EndLat)
        Endlon = ArrString[Checkpoints*2+4]
        self.EndLon = float(Endlon)
        print(f"Ending lat is {EndLat} and lon is {Endlon}")
        
        try:
            Name = ArrString[Checkpoints*2+5].replace("@", " ")
            Description = ArrString[Checkpoints*2+6].replace("@", " ")
            print(f"Name: {Name}")
            print(f"Description: {Description}")
        except:
            print('Invalid name or description')
        return True
    

    def load_map(self):
        app = App.get_running_app()
        app.ExistingMarkers = []
        app.ExistingMarkersPreview = []
        self.runpins = []
        qr_run = ScanQRRun()

        print('Loading map from QR code')
        app.root.current = 'run'
        mapviewRun = app.root.get_screen('run').ids.mapview
        mapviewPreview = app.root.get_screen('preview').ids.mapview
        RawString = self.qrdata
        ArrString = []
        time.sleep(1)

        Spoint = MapMarker(lat = self.StartLat, lon = self.StartLon, source= "data/startpin.png")
        SpointPreview = MapMarker(lat = self.StartLat, lon = self.StartLon, source= "data/startpin.png")
        mapviewRun.add_marker(Spoint)
        mapviewPreview.add_marker(SpointPreview)
        print('placing startpin')
        mapviewRun.center_on(self.StartLat, self.StartLon)
        mapviewPreview.center_on(self.StartLat, self.StartLon)
        app.ExistingMarkers.append(Spoint)
        app.ExistingMarkersPreview.append(Spoint)


        Epoint = MapMarker(lat = self.EndLat, lon = self.EndLon, source= "data/endpin.png")
        EpointPreview = MapMarker(lat = self.EndLat, lon = self.EndLon, source= "data/endpin.png")
        mapviewRun.add_marker(Epoint)
        mapviewPreview.add_marker(EpointPreview)
        app.ExistingMarkers.append(Epoint)
        app.ExistingMarkersPreview.append(Epoint)

        print('placing Endpin')

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
            string = f"{pointn}-{PinLat}-{PinLon}"
            qr_run.runpins.append(string)
            n += 2
            point = MapMarker(lat = PinLat, lon = PinLon, source= "data/pin.png")
            pointPreview = MapMarker(lat = PinLat, lon = PinLon, source= "data/pin.png")

            print('Placing pin')
            mapviewRun.add_marker(point)
            mapviewPreview.add_marker(pointPreview)
            app.ExistingMarkers.append(point)
            app.ExistingMarkersPreview.append(point)
            print(f"Existing markers list to remove = {app.ExistingMarkers}")

    def on_leave(self, *args):
        try:
            self.ids.preview.disconnect_camera()
        except:
            print('Camera already disconnected')

class GetTrackQR(Screen):
    pass
class Main(ScreenManager):
    pass