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
from .style import scatter_window_style
from .utils import get_selection
from .combo_box_model import ComboBoxModel
from .scatter import scatter
from .utils import duplicate_prims

LABEL_WIDTH = 120
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 80
SPACING = 4

class FreeDLiveLinkWindow(ui.Window):
    """The class that represents the window"""
    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = LABEL_WIDTH
        super().__init__(title, **kwargs)

    def destroy(self):
        # It will destroy all the children
        super().destroy()
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


    def _build_fn(self):
        """
        The method that is called to build all the UI once the window is
        visible.
        """
        with ui.ScrollingFrame():
            with ui.VStack(height=0):
                self._build_camera_source()
                self._build_livelink()
        

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

                with ui.HStack():
                    ui.Label("UDP Port", name="attribute_name", width=self.label_width)


