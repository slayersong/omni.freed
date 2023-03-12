import omni.ext
import omni.ui as ui
from .utils import get_selection
from .style import livelink_window_style
import socket
import threading

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[omni.FreeD.LiveLink] some_public_function was called with x: ", x)
    return x ** x

LABEL_WIDTH = 120
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 80
SPACING = 4

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class OmniFreedLivelinkExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    
    def __init__(self):
        super().__init__()

    def on_shutdown(self):
        if self._window:
            self._window.destroy()
            self._window = None
            
        self._connect_staus = False
        self._freeD_thread.join()
        print("[omni.FreeD.LiveLink] omni FreeD LiveLink shutdown")
        

    def on_startup(self, ext_id):
        print("[omni.FreeD.LiveLink] omni FreeD LiveLink startup")

        self._window = ui.Window("FreeD Live Link", width=300, height=200)

        self._source_prim_model_a = ui.SimpleStringModel()

        self._udp_ip = ui.SimpleStringModel()
        self._udp_port = ui.SimpleIntModel()

        self._udp_ip.as_string = "127.0.0.1"
        self._udp_port.as_int = 40001
        self._bufferSize = 1024
        self._connect_staus = False

        self.__label_width = LABEL_WIDTH
        self.__button_width = BUTTON_WIDTH
        self.__button_height = BUTTON_HEIGHT
        
        #self._freeD_thread = _thread.start_new_thread(target = self._updThread， args=(self))

        with self._window.frame:
            with ui.VStack():
                self._build_widget()
                
                # label = ui.Label("")
                # def on_click():
                #     self._count += 1
                #     label.text = f"count: {self._count}"

                # def on_reset():
                #     self._count = 0
                #     label.text = "empty"
        
        self._freeD_thread = threading.Thread(target = self._udpThread)
        self._freeD_thread.start()

    def on_start_listener(self):
        #self._updThread()
        print("on_start_listener")

    def on_stop_listener(self):
        print("on_stop_listener")

    def _build_fn(self):
        print("build_fn")

    def _on_get_selection(self, model):
        """Called when the user presses the "Get From Selection" button"""
        model.as_string = ", ".join(get_selection())
        print('model name is:{}'.format(model.as_string))

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
                    ui.Button("Start", clicked_fn=self.on_start_listener, width=self.button_width)
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
        

    def _udpThread(self):
        msgFromClient       = "Hello From OV Livelink UDP Client"
        bytesToSend         = str.encode(msgFromClient)
        #serverAddressPort   = (self._udp_ip, self._udp_port)
        serverAddressPort   = ("127.0.0.1", 20001)
        self._connect_staus = True
        # Create a UDP socket at client side
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
        # Send to server using created UDP socket
        #while(true):
        while (self._connect_staus):
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            msgFromServer = UDPClientSocket.recvfrom(self._bufferSize)
            msg = "Message from Server {}".format(msgFromServer[0])
            self._update_tips(msg)
          
        UDPClientSocket.close()
        

    def _update_camera(self, freeD):
        #Parse the FreeDinfo
        pass

    def _update_tips(self, textinfo):
        self._tipslabel.text = textinfo

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
