#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Via Grid Generator Action Plugin for KiCad
Main plugin class that integrates with KiCad UI
"""

import pcbnew
import wx
import os
from .via_grid_dialog import ViaGridDialog
from .via_grid_generator import ViaGridGenerator


class ViaGridGeneratorAction(pcbnew.ActionPlugin):
    """
    Main action plugin class for KiCad integration
    """
    
    def __init__(self):
        super(ViaGridGeneratorAction, self).__init__()
        self.name = "Via Grid Generator"
        self.category = "Modify PCB"
        self.description = "Generate a grid of vias with DRC compliance"
        self.show_toolbar_button = True
        self.icon_file_name = self._get_icon_path()
    
    def _get_icon_path(self):
        """Get the path to the icon file"""
        # Try different possible locations
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check in resources folder (PCM installation)
        icon_paths = [
            os.path.join(plugin_dir, '..', 'resources', 'icon.png'),
            os.path.join(plugin_dir, '..', '..', 'resources', 'icon.png'),
            os.path.join(plugin_dir, 'icon.png'),
            os.path.join(plugin_dir, '..', 'icon.png')
        ]
        
        for path in icon_paths:
            if os.path.isfile(path):
                return os.path.abspath(path)
        
        return ""  # No icon found
    
    def defaults(self):
        """
        Set default values - required by KiCad
        """
        # Defaults are set in __init__
        pass
    
    def Run(self):
        """
        Main entry point when user clicks the plugin
        """
        # Get the current board
        board = pcbnew.GetBoard()
        if not board:
            wx.MessageBox(
                "No board loaded!",
                "Error",
                wx.OK | wx.ICON_ERROR
            )
            return
        
        # Check if board has been saved
        board_path = board.GetFileName()
        if not board_path:
            wx.MessageBox(
                "Please save the board before using this plugin.",
                "Board Not Saved",
                wx.OK | wx.ICON_WARNING
            )
            return
        
        # Create and show dialog
        frame = wx.GetTopLevelWindows()[0]
        dialog = ViaGridDialog(frame)
        
        try:
            if dialog.ShowModal() == wx.ID_OK:
                # Get parameters from dialog
                params = dialog.get_parameters()
                
                # Create progress dialog
                progress = wx.ProgressDialog(
                    "Via Grid Generator",
                    "Initializing...",
                    maximum=100,
                    parent=frame,
                    style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_SMOOTH
                )
                
                # Create generator
                generator = ViaGridGenerator(board, progress)
                
                try:
                    # Generate the via grid
                    result = generator.generate_grid(
                        spacing_mm=params['spacing'],
                        via_size_mm=params['via_size'],
                        via_drill_mm=params['via_drill'],
                        net_name=params['net_name'],
                        use_selected_area=params['use_selected_area']
                    )
                    
                    if result['success']:
                        # Refresh the board view
                        pcbnew.Refresh()
                        
                        # Show results
                        wx.MessageBox(
                            f"Successfully placed {result['vias_placed']} vias.\n"
                            f"Skipped {result['vias_skipped']} positions due to DRC constraints.\n\n"
                            f"Please run DRC check to verify the result.",
                            "Success",
                            wx.OK | wx.ICON_INFORMATION
                        )
                    else:
                        wx.MessageBox(
                            f"Via grid generation failed:\n{result['error']}",
                            "Error",
                            wx.OK | wx.ICON_ERROR
                        )
                
                finally:
                    progress.Destroy()
                    
        finally:
            dialog.Destroy()