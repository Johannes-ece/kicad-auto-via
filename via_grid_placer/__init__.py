"""
Via Grid Placer Plugin for KiCad 9
Places vias in a grid pattern within selected copper zones
"""

from .via_grid_placer_action import ViaGridPlacerAction

# Register the action plugin
ViaGridPlacerAction().register()

__version__ = "1.0.0"
__author__ = "Johannes v."