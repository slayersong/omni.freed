import omni.ext
import omni.usd
import omni.ui as ui
import socket
import threading
import carb.events
import omni.kit.app
import os
import asyncio
import time
import json
from datetime import datetime
from .utils import get_selection
from .style import livelink_window_style
from .window import FreeDLiveLinkWindow

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[omni.FreeD.LiveLink] some_public_function was called with x: ", x)
    return x ** x

LABEL_WIDTH = 120
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 80
SPACING = 4
BUFFERSIZE  = 1024
FREED_DATA_LENGTH = 29

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class OmniFreedLivelinkExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    WINDOW_NAME = "FreeD LiveLink Window"
    MENU_PATH = f"Window/{WINDOW_NAME}"
    
    def __init__(self):
        super().__init__()

    def on_shutdown(self):
        if self._window:
            self.save_config("freed.json")
            self._window.destroy()
            self._window = None

        if self._connect_staus == True:
            self._connect_staus = False
            #time.sleep(3)
            self._freeD_thread.join()

            if self._UDPServerSocket:
                self._UDPServerSocket.close()
        
        print("[omni.FreeD.LiveLink] omni FreeD LiveLink shutdown")

    def _init_var(self):
        self._source_prim_model_a = ui.SimpleStringModel()
        self._udp_ip = ui.SimpleStringModel()
        self._udp_port = ui.SimpleIntModel()
        self._bEncodeCameraLens = ui.SimpleBoolModel(True)
        self._config_dict = {"udp_ip": self._udp_ip.as_string, "udp_port": self._udp_port.as_int, "bEncoude": self._bEncodeCameraLens.as_bool}

        self.__label_width = LABEL_WIDTH
        self.__button_width = BUTTON_WIDTH
        self.__button_height = BUTTON_HEIGHT
        self._stage = omni.usd.get_context().get_stage()

    def _register_event(self):
        # Event is unique integer id. Create it from string by hashing, using helper function.
        # [ext name].[event name] is a recommended naming convention:
        self._Udp_update_EVENT = carb.events.type_from_string("omni.freelink.extension.udp_update")
        self._bus = omni.kit.app.get_app().get_message_bus_event_stream()
        
        # Pop is called on next update, while push is excute immediately  
        # elf.sub1 = self._bus.create_subscription_to_push_by_type(self._Udp_update_EVENT, self.on_event)
        self.sub2 = self._bus.create_subscription_to_pop_by_type(self._Udp_update_EVENT, self.on_event)

    def _init_udp_server(self):
        self._udp_ip.as_string = self._config_dict['udp_ip']
        self._udp_port.as_int = self._config_dict['udp_port']
        self._bEncodeCameraLens.as_bool = self._config_dict['bEncoude']
        self._bufferSize = 1024
        self._connect_staus = False


    def on_startup(self, ext_id):
        print("[omni.FreeD.LiveLink] omni FreeD LiveLink startup")  
        self._window = ui.Window("FreeD Live Link", width=300, height=200)

        with self._window.frame:
            with ui.VStack():
                self._init_var()
                self.load_config("freed.json")
                self._build_widget()
                self._init_udp_server()
                self._register_event()
                

    def on_event(self, e):
        self._update_camera(e.payload)
    
    def load_config(self, filename):
        current_path = os.path.abspath(__file__)
        fran_file_path = os.path.join(os.path.abspath(os.path.dirname(current_path)+os.path.sep), filename)

        with open(fran_file_path) as fl:
            self._config_dict = json.loads(fl.read())
            fl.close()
            #return True

    def save_config(self, filename):
        current_path = os.path.abspath(__file__)
        fran_file_path = os.path.join(os.path.abspath(os.path.dirname(current_path)+os.path.sep), filename)

        self._config_dict['udp_ip'] = self._udp_ip.as_string
        self._config_dict['udp_port'] = self._udp_port.as_int
        self._config_dict['bEncoude'] = self._bEncodeCameraLens.as_bool
        outputjson = json.dumps(self._config_dict)

        outputfile = open(fran_file_path, 'w')
        outputfile.write(outputjson)
        outputfile.close()

    def _update_camera(self, camera_payload):
        if len(self._source_prim_model_a.as_string) != 0:
            #{'rotate': new_rotate, 'pos': new_translate, 'zoom': camera_zoom, 'focus': camera_focus}
            self._cameraPrim.GetAttribute('xformOp:translate').Set(camera_payload['pos'])
            self._cameraPrim.GetAttribute('xformOp:rotateYXZ').Set(camera_payload['rotate'])

            if self._bEncodeCameraLens.as_bool:
                self._cameraPrim.GetAttribute('focalLength').Set(camera_payload['zoom'])
                self._cameraPrim.GetAttribute('focusDistance').Set(camera_payload['focus'])

    def on_start_listener(self):
        if not self._connect_staus:
            self._freeD_thread = threading.Thread(target=self._startUPDServer)
            self._connect_staus = True
            self._freeD_thread.start()
            self._tipslabel.text = "Start Listening socket {}".format(self._udp_port.as_int)
            self._startbtn.text = "Stop"
        else:
            self._connect_staus = False
            self._tipslabel.text = "Waiting 3 seconds to close UPD socket"
            #time.sleep(4)
            self._freeD_thread.join()
            self._UDPServerSocket.close()
            self._startbtn.text = "Start"
            self._tipslabel.text = "Socket closed"
            #
            #self._tipslabel.text = "Send just one byte via UDP to close the Socket"
            #just 

        # else:
        #     self._UDPServerSocket.shutdown(socket.SHUT_RDWR)
        #     self._startbtn.text = "Start"
        #     self._connect_staus = False

        #self._updThread()
        print("on_start_listener")

    def on_stop_listener(self):
        print("on_stop_listener")

    def _build_fn(self):
        print("build_fn")

    def _on_get_selection(self, model):
        """Called when the user presses the "Get From Selection" button"""
        model.as_string = ", ".join(get_selection())
        self._cameraPrim = omni.usd.get_context().get_stage().GetPrimAtPath(self._source_prim_model_a.as_string)
        print('_cameraPrim name is:{}'.format(self._cameraPrim))

    def _build_camera_source(self):
        with ui.CollapsableFrame("Source", name="group"):
            with ui.VStack(height=0, spacing=SPACING):
                with ui.HStack():
                    ui.Label("Live Link Camera", name="attribute_name", width=self.label_width)
                    ui.StringField(model=self._source_prim_model_a)
                    # Button that puts the selection to the string field
                    ui.Button(
                        " S ",
                        width=0,
                        height=0,
                        style={"margin": 0},
                        clicked_fn=lambda:self._on_get_selection(self._source_prim_model_a),
                        tooltip="Get Camera From Selection",
                    )
    
    def _build_livelink(self):
        with ui.CollapsableFrame("LiveLink", name="group"):
            with ui.VStack(height=0, spacing=SPACING):
                with ui.HStack():
                    ui.Label("UDP Server", name="attribute_name", width=self.label_width)
                    ui.StringField(model=self._udp_ip)

                with ui.HStack():
                    ui.Label("UDP Port", name="attribute_name", width=self.label_width)
                    ui.IntDrag(self._udp_port, min=0, max=65535)
                with ui.HStack():
                    ui.CheckBox(model=self._bEncodeCameraLens, width=10)
                    ui.Label("Encode Camera Lens", name="attribute_name", width=self.label_width)

                with ui.HStack():
                    self._startbtn = ui.Button("Start", clicked_fn=self.on_start_listener, width=self.button_width)
                    self._tipslabel = ui.Label("disconected", name="livelink_tips", width=self.label_width)
                    #ui.Label(model=self._connect_tips, name="livelink_tips",width=self.label_width)
                    #ui.Button("Stop", clicked_fn=self.on_stop_listener, width=self.button_width, enabled=False)

    def _build_widget(self):
        """
        The method that is called to build all the UI once the window is
        visible.
        """
        self._window.frame.style = livelink_window_style
        with ui.ScrollingFrame():
            with ui.VStack(height=0):
                self._build_camera_source()
                self._build_livelink()
        
    def _startUPDServer(self):
        ## Should I run in a thread? seems that will cause a hang and cant get the right prim...
        self._UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self._UDPServerSocket.bind((self._udp_ip.as_string, self._udp_port.as_int))
        self._UDPServerSocket.settimeout(3)

        while (self._connect_staus):
            try:
                bytesAddressPair = self._UDPServerSocket.recvfrom(BUFFERSIZE)
            except socket.timeout:
                continue

            message = bytesAddressPair[0]
            address = bytesAddressPair[1]
            msg = "Message from Client {}".format(address)
            self._update_tips(message)
            #print ("Message type is:{}".format(type(message)))
            #send a byte the UPD server will close
            #Should use epoll to handle udp server, TODO later
            if len(message) == 1:
                self._connect_staus = False
                self._tipslabel.text = "Receive 1byte disconnected"
                self._startbtn.text = "Start"
            else:
                if int(len(message)) != FREED_DATA_LENGTH:
                    print("FreeD data size must euqal size 29 ")
                    #self._calculate_camera(message)
                else:
                    self._calculate_camera29(message)

        #TODO:  block in recvfrom
        #self._UDPServerSocket.shutdown(socket.SHUT_RDWR)
        #self._UDPServerSocket.close()

    def _calculate_camera29(self, freeD):
        #Parse the FreeDinfo
        bit24 = (1 << 23)
        frame_pos_header = str(freeD[0:1])
        camera_id = int.from_bytes(freeD[1:2], "big")

        #Rotate: Yaw, Pitch, Roll
        _sign = -1 if (int.from_bytes(freeD[2:5], "big") & bit24) != 0 else 1
        if _sign > 0: 
            camera_yaw = _sign * (int.from_bytes(freeD[2:5], "big") & (bit24 - 1)) / 32768
        else:# if < 0  (1) Data = complement(~)   (2) then Data & 7FFFFF + 1
            camera_yaw = _sign * ((~int.from_bytes(freeD[2:5], "big") & (bit24 - 1)) + 1) / 32768
        
        # Camera pan is clockwise, while in OV raw is anti-clockwise
        camera_yaw *= -1
        
        _sign = -1 if (int.from_bytes(freeD[5:8], "big") & bit24) != 0 else 1
        if _sign > 0:
            camera_pitch = _sign * (int.from_bytes(freeD[5:8], "big") & (bit24 - 1)) / 32768
        else:
            camera_pitch = _sign * ((~int.from_bytes(freeD[5:8], "big") & (bit24 - 1)) + 1) / 32768
        #A positive value indicates an upwards tilt so no need to inverse
        camera_pitch *= -1

        _sign = -1 if (int.from_bytes(freeD[8:11], "big") & bit24) != 0 else 1
        if _sign > 0:
            camera_roll = _sign * (int.from_bytes(freeD[8:11], "big") & (bit24 - 1)) / 32768
        else: # if < 0  1 st complement(~)  then Data & 7FFFFF + 1
            camera_roll = _sign * ((~int.from_bytes(freeD[8:11], "big") & (bit24 - 1)) + 1) / 32768
        camera_roll *= -1
        
        # Y X Z
        new_rotate = (camera_pitch, camera_yaw, camera_roll)
        # Translate X,Y,Z
        _sign = -1 if (int.from_bytes(freeD[11:14], "big") & bit24) != 0 else 1
        if _sign > 0:
            camera_pos_x = _sign * (int.from_bytes(freeD[11:14], "big") & (bit24 - 1)) / 64000
        else:
            camera_pos_x = _sign * ((~int.from_bytes(freeD[11:14], "big") & (bit24 - 1)) + 1) / 64000

        _sign = -1 if (int.from_bytes(freeD[14:17], "big") & bit24) != 0 else 1
        if _sign > 0:
            camera_pos_y = _sign * (int.from_bytes(freeD[14:17], "big") & (bit24 - 1)) / 64000
        else:
            camera_pos_y = _sign * ((~int.from_bytes(freeD[14:17], "big") & (bit24 - 1)) + 1) / 64000

        _sign = -1 if (int.from_bytes(freeD[17:20], "big") & bit24) != 0 else 1
        if _sign > 0:
            camera_pos_z = _sign * (int.from_bytes(freeD[17:20], "big") & (bit24 - 1) + 1) / 64000
        else:
            camera_pos_z = _sign * ((~int.from_bytes(freeD[17:20], "big") & (bit24 - 1)) + 1) / 64000

        # RotateYXZ
        new_translate = (camera_pos_y, camera_pos_x, camera_pos_z)
        #Zoon Focus
        camera_zoom = int.from_bytes(freeD[20:23], "big")
        camera_focus = int.from_bytes(freeD[23:26], "big")

        reserve_ = int.from_bytes(freeD[26:28], "big")
        freed_crc = int.from_bytes(freeD[28:29], "big")
        #check crc further sum all then = crc?

        # Still pack zoom and focus while not update
        camare_update_data = {'rotate': new_rotate, 'pos': new_translate, 'zoom': camera_zoom, 'focus': camera_focus}

        self._bus.push(self._Udp_update_EVENT, payload=camare_update_data)

    def _calculate_camera(self, freeD):
        #Parse the FreeDinfo
        bit24 = (1 << 23)
        frame_pos_header = str(freeD[0:2])
        camera_id = int(freeD[2:4],16)

        #Rotate: Yaw, Pitch, Roll
        _sign = -1 if (int(freeD[4:10], 16) & bit24) != 0 else 1
        if _sign > 0:
            camera_yaw = _sign * (int(freeD[4:10], 16) & (bit24 - 1)) / 32768
        else:# if < 0  (1) Data = complement(~)   (2) then Data & 7FFFFF + 1
            camera_yaw = _sign * ((~int(freeD[4:10], 16) & (bit24 - 1)) + 1) / 32768
        camera_yaw *= -1
        
        _sign = -1 if (int(freeD[10:16], 16) & bit24) != 0 else 1
        if _sign > 0:
            camera_pitch = _sign * (int(freeD[10:16], 16) & (bit24 - 1)) / 32768
        else:
            camera_pitch = _sign * ((~int(freeD[10:16], 16) & (bit24 - 1)) + 1) / 32768
        camera_pitch *= -1
        
        _sign = -1 if (int(freeD[16:22], 16) & bit24) != 0 else 1
        if _sign > 0:
            camera_roll = _sign * (int(freeD[16:22], 16) & (bit24 - 1)) / 32768
        else: # if < 0  1 st complement(~)  then Data & 7FFFFF + 1
            camera_roll = _sign * ((~int(freeD[16:22], 16) & (bit24 - 1)) + 1) / 32768
        
        camera_roll *= -1
        
        new_rotate = (camera_pitch, camera_yaw, camera_roll)
        # Translate X,Y,Z
        _sign = -1 if (int(freeD[22:28], 16) & bit24) != 0 else 1
        if _sign > 0:
            camera_pos_x = _sign * (int(freeD[22:28], 16) & (bit24 - 1)) / (64000)
        else:
            camera_pos_x = _sign * (~int(freeD[22:28], 16) & (bit24 - 1) + 1) / (64000)

        _sign = -1 if (int(freeD[28:34], 16) & bit24) != 0 else 1
        if _sign > 0:
            camera_pos_y = _sign * (int(freeD[28:34], 16) & (bit24 - 1)) / (64000)    
        else:
            camera_pos_y = _sign * (~int(freeD[28:34], 16) & (bit24 - 1) + 1) / (64000)

        _sign = -1 if (int(freeD[34:40], 16) & bit24) != 0 else 1
        if _sign > 0:
            camera_pos_z = _sign * (int(freeD[34:40], 16) & (bit24 - 1)) / (64000)
        else:
            camera_pos_z = _sign * (~int(freeD[34:40], 16) & (bit24 - 1)) / (64000)   

        # RotateYXZ
        new_translate = (camera_pos_y, camera_pos_x, camera_pos_z)
        #Zoon Focus
        #TODO: Depends on Camera HW
        camera_zoom = int(freeD[40:46], 16)
        camera_focus = int(freeD[46:52], 16)

        reserve_ = int(freeD[52:56], 16)
        freed_crc = int(freeD[56:58], 16)
        #check crc further sum all then = crc?

        camare_update_data = {'rotate': new_rotate, 'pos': new_translate, 'zoom': camera_zoom, 'focus': camera_focus}

        self._bus.push(self._Udp_update_EVENT, payload=camare_update_data)

    def _update_tips(self, textinfo):
        #self._tipslabel.text = "FreeD:" + str(datetime.hour) + ":" + str(datetime.minute) + ":" + str(datetime.second) + " " + textinfo
        self._tipslabel.text = "FreeD:" + str(textinfo)

    @property
    def label_width(self):
        """The width of the attribute label"""
        return self.__label_width
    
    @property
    def button_width(self):
        """The width of the attribute label"""
        return self.__label_width

    @property
    def button_height(self):
        """The width of the attribute label"""
        return self.__button_height
  
    def _visiblity_changed_fn(self, visible):
        # Called when the user pressed "X"
        self._set_menu(visible)
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def show_window(self, menu, value):
        if value:
            self._window = FreeDLiveLinkWindow(OmniFreedLivelinkExtension.WINDOW_NAME, width=300, height=500)
            self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
        elif self._window:
            self._window.visible = False
