# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["FreeDLiveLinkWindow"]
import omni.ui as ui
from .style import livelink_window_style
from .utils import get_selection
import omni.usd
import socket
import threading
import carb.events

LABEL_WIDTH = 120
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 80
SPACING = 4
FREED_DATA_LENGTH = 29
BUFFERSIZE = 1024

class FreeDLiveLinkWindow(ui.Window):
    
    WINDOW_NAME = "FreeDLiveLink Window"
    MENU_PATH = f"Window/{WINDOW_NAME}"
    
    """The class that represents the window"""
    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = LABEL_WIDTH
        super().__init__(title, **kwargs)

    def destroy(self):
        
        self._connect_staus = False
        if self._freeD_thread.is_alive():
            self._freeD_thread.join()

        self._UDPServerSocket.close()
        print("[omni.FreeD.LiveLink] omni FreeD LiveLink shutdown")
        # It will destroy all the children
        super().destroy()

    def _init_var(self):

        self._source_prim_model_a = ui.SimpleStringModel()
        self._udp_ip = ui.SimpleStringModel()
        self._udp_port = ui.SimpleIntModel()

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
        self._udp_ip.as_string = "127.0.0.1"
        self._udp_port.as_int = 40001
        self._bufferSize = 1024
        self._connect_staus = False

        self._UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self._UDPServerSocket.bind((self._udp_ip.as_string, self._udp_port.as_int))
        
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
        while (self._connect_staus):
                bytesAddressPair = self._UDPServerSocket.recvfrom(BUFFERSIZE)

                message = bytesAddressPair[0]
                address = bytesAddressPair[1]
                msg = "Message from Client {}".format(address)
                self._update_tips(msg)
                self._calculate_camera(message)

        #TODO:  block in recvfrom
        self._UDPServerSocket.shutdown(socket.SHUT_RDWR)
        #UDPServerSocket.close()

    def _calculate_camera(self, freeD):
        #Parse the FreeDinfo
        bit24 = (1 << 23)
        frame_pos_header = str(freeD[0:2])
        camera_id = int(freeD[2:4],16)

        #Rotate: Yaw, Pitch, Roll
        _sign = -1 if int(freeD[4:10], 16) & bit24 == 1 else 1
        camera_pitch = _sign * (int(freeD[4:10], 16) & (bit24 - 1)) / 32678

        _sign = -1 if int(freeD[10:16], 16) & bit24 == 1 else 1
        camera_yaw = _sign * (int(freeD[10:16], 16) & (bit24 - 1)) / 32678

        _sign = -1 if int(freeD[16:22], 16) & bit24 == 1 else 1
        camera_roll = _sign * (int(freeD[16:22], 16) & (bit24 - 1)) / 32678

        new_rotate = (camera_yaw, camera_pitch, camera_roll)
        # Translate X,Y,Z
        _sign = -1 if int(freeD[22:28], 16) & bit24 == 1 else 1
        camera_pos_x = _sign * (int(freeD[22:28], 16) & (bit24 - 1)) / 64

        _sign = -1 if int(freeD[28:34], 16) & bit24 == 1 else 1
        camera_pos_y = _sign * (int(freeD[28:34], 16) & (bit24 - 1)) / 64

        _sign = -1 if int(freeD[34:40], 16) & bit24 == 1 else 1
        camera_pos_z = _sign * (int(freeD[34:40], 16) & (bit24 - 1)) / 64

        # RotateYXZ
        new_translate = (camera_pos_y, camera_pos_x, camera_pos_z)
        #Zoon Focus
        camera_zoom = int(freeD[40:46], 16)
        camera_focus = int(freeD[46:52], 16)

        reserve_ = int(freeD[52:56], 16)
        freed_crc = int(freeD[56:58], 16)
        #check crc further sum all then = crc?

        camare_update_data = {'rotate': new_rotate, 'pos': new_translate, 'zoom': camera_zoom, 'focus': camera_focus}

        self._bus.push(self._Udp_update_EVENT, payload=camare_update_data)

    def _update_tips(self, textinfo):
        self._tipslabel.text = "FreeD Data Update:"+textinfo

    @property
    def label_width(self):
        """The width of the attribute label"""
        return self.__label_width
    @label_width.setter
    
    def label_width(self, value):
        """The width of the attribute label"""
        self.__label_width = value
        self.frame.rebuild()
        
    def _on_get_selection(self, model):
        """Called when the user presses the "Get From Selection" button"""
        model.as_string = ", ".join(get_selection())