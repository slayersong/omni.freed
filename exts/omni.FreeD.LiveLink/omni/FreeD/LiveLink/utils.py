# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["get_selection"]

from typing import List
import omni.usd
import omni.kit.commands
from pxr import Sdf
from pxr import Gf


def get_selection() -> List[str]:
    """Get the list of currently selected prims"""
    return omni.usd.get_context().get_selection().get_selected_prim_paths()