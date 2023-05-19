import omni.ext
from .style import livelink_window_style
from .window import FreeDLiveLinkWindow

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[omni.FreeD.LiveLink] some_public_function was called with x: ", x)
    return x ** x


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
        
    def on_startup(self, ext_id):
        print("[omni.FreeD.LiveLink] omni FreeD LiveLink startup")  
        self._window = FreeDLiveLinkWindow("FreeD Live Link", width=300, height=200)

    def on_shutdown(self):
        self._window.destroy()
        self._window = None
        print("[omni.FreeD.LiveLink] omni FreeD LiveLink shutdown")