#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Via Grid Generator Dialog
User interface for the via grid generator plugin
"""

import wx
import pcbnew


class ViaGridDialog(wx.Dialog):
    """
    Configuration dialog for via grid parameters
    """
    
    def __init__(self, parent):
        super(ViaGridDialog, self).__init__(
            parent,
            title="Via Grid Generator",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        
        self.board = pcbnew.GetBoard()
        self._init_ui()
        self.Centre()
    
    def _init_ui(self):
        """Initialize the user interface"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header
        header = wx.StaticText(
            self,
            label="Generate a grid of vias with automatic DRC compliance"
        )
        header_font = header.GetFont()
        header_font.SetWeight(wx.FONTWEIGHT_BOLD)
        header.SetFont(header_font)
        main_sizer.Add(header, 0, wx.ALL | wx.EXPAND, 10)
        
        # Main panel with notebook for organization
        notebook = wx.Notebook(self)
        
        # Grid settings page
        grid_panel = wx.Panel(notebook)
        grid_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Grid spacing
        spacing_box = wx.StaticBoxSizer(
            wx.HORIZONTAL,
            grid_panel,
            "Grid Spacing"
        )
        
        self.spacing_ctrl = wx.SpinCtrlDouble(
            grid_panel,
            min=0.1,
            max=50.0,
            inc=0.1
        )
        self.spacing_ctrl.SetValue(2.54)
        spacing_box.Add(self.spacing_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        
        self.spacing_unit = wx.Choice(
            grid_panel,
            choices=["mm", "mils"]
        )
        self.spacing_unit.SetSelection(0)
        spacing_box.Add(self.spacing_unit, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        grid_sizer.Add(spacing_box, 0, wx.ALL | wx.EXPAND, 5)
        
        # Via parameters
        via_box = wx.StaticBoxSizer(wx.VERTICAL, grid_panel, "Via Parameters")
        via_grid = wx.FlexGridSizer(3, 2, 5, 5)
        via_grid.AddGrowableCol(1)
        
        # Via size
        via_grid.Add(
            wx.StaticText(grid_panel, label="Via Size (mm):"),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT
        )
        self.via_size_ctrl = wx.SpinCtrlDouble(
            grid_panel,
            min=0.1,
            max=10.0,
            inc=0.05
        )
        self.via_size_ctrl.SetValue(0.5)
        via_grid.Add(self.via_size_ctrl, 1, wx.EXPAND)
        
        # Drill size
        via_grid.Add(
            wx.StaticText(grid_panel, label="Drill Size (mm):"),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT
        )
        self.drill_size_ctrl = wx.SpinCtrlDouble(
            grid_panel,
            min=0.1,
            max=10.0,
            inc=0.05
        )
        self.drill_size_ctrl.SetValue(0.3)
        via_grid.Add(self.drill_size_ctrl, 1, wx.EXPAND)
        
        # Net selection
        via_grid.Add(
            wx.StaticText(grid_panel, label="Net:"),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT
        )
        
        # Get net names from board
        net_names = self._get_net_names()
        self.net_choice = wx.Choice(grid_panel, choices=net_names)
        
        # Try to select GND by default
        try:
            gnd_index = net_names.index("GND")
            self.net_choice.SetSelection(gnd_index)
        except ValueError:
            if net_names:
                self.net_choice.SetSelection(0)
        
        via_grid.Add(self.net_choice, 1, wx.EXPAND)
        
        via_box.Add(via_grid, 0, wx.ALL | wx.EXPAND, 5)
        grid_sizer.Add(via_box, 0, wx.ALL | wx.EXPAND, 5)
        
        # Area selection
        area_box = wx.StaticBoxSizer(wx.VERTICAL, grid_panel, "Placement Area")
        
        self.area_board_radio = wx.RadioButton(
            grid_panel,
            label="Entire board",
            style=wx.RB_GROUP
        )
        self.area_selection_radio = wx.RadioButton(
            grid_panel,
            label="Selected area only"
        )
        
        area_box.Add(self.area_board_radio, 0, wx.ALL, 5)
        area_box.Add(self.area_selection_radio, 0, wx.ALL, 5)
        
        # Check if there's a selection
        if not self._has_selection():
            self.area_selection_radio.Enable(False)
            self.area_board_radio.SetValue(True)
        
        grid_sizer.Add(area_box, 0, wx.ALL | wx.EXPAND, 5)
        
        grid_panel.SetSizer(grid_sizer)
        notebook.AddPage(grid_panel, "Grid Settings")
        
        # DRC settings page
        drc_panel = wx.Panel(notebook)
        drc_sizer = wx.BoxSizer(wx.VERTICAL)
        
        drc_info = wx.StaticText(
            drc_panel,
            label="The plugin automatically checks clearances to avoid DRC violations."
        )
        drc_sizer.Add(drc_info, 0, wx.ALL, 10)
        
        # Clearance settings
        clear_box = wx.StaticBoxSizer(wx.VERTICAL, drc_panel, "Clearance Settings")
        
        clear_grid = wx.FlexGridSizer(2, 2, 5, 5)
        clear_grid.AddGrowableCol(1)
        
        clear_grid.Add(
            wx.StaticText(drc_panel, label="Minimum Clearance (mm):"),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT
        )
        self.clearance_ctrl = wx.SpinCtrlDouble(
            drc_panel,
            min=0.0,
            max=5.0,
            inc=0.05
        )
        self.clearance_ctrl.SetValue(0.2)
        clear_grid.Add(self.clearance_ctrl, 1, wx.EXPAND)
        
        clear_grid.Add(
            wx.StaticText(drc_panel, label="Via-to-Via Spacing (mm):"),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT
        )
        self.via_spacing_ctrl = wx.SpinCtrlDouble(
            drc_panel,
            min=0.0,
            max=5.0,
            inc=0.05
        )
        self.via_spacing_ctrl.SetValue(0.1)
        clear_grid.Add(self.via_spacing_ctrl, 1, wx.EXPAND)
        
        clear_box.Add(clear_grid, 0, wx.ALL | wx.EXPAND, 5)
        drc_sizer.Add(clear_box, 0, wx.ALL | wx.EXPAND, 5)
        
        drc_panel.SetSizer(drc_sizer)
        notebook.AddPage(drc_panel, "DRC Settings")
        
        main_sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        
        # Buttons
        btn_sizer = wx.StdDialogButtonSizer()
        
        ok_btn = wx.Button(self, wx.ID_OK, "Generate")
        ok_btn.SetDefault()
        btn_sizer.AddButton(ok_btn)
        
        cancel_btn = wx.Button(self, wx.ID_CANCEL)
        btn_sizer.AddButton(cancel_btn)
        
        btn_sizer.Realize()
        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        
        self.SetSizer(main_sizer)
        self.SetMinSize((400, 450))
        self.Fit()
    
    def _get_net_names(self):
        """Get list of net names from the board"""
        nets = []
        board_nets = self.board.GetNetInfo()
        
        for net_code in range(board_nets.GetNetCount()):
            net = board_nets.GetNetItem(net_code)
            if net and net.GetNetname():
                nets.append(net.GetNetname())
        
        return sorted(nets)
    
    def _has_selection(self):
        """Check if user has selected an area"""
        # Check for selected drawings that could define an area
        for drawing in self.board.GetDrawings():
            if drawing.IsSelected():
                return True
        return False
    
    def get_parameters(self):
        """Get the configured parameters"""
        spacing = self.spacing_ctrl.GetValue()
        
        # Convert mils to mm if needed
        if self.spacing_unit.GetSelection() == 1:  # mils
            spacing = spacing * 0.0254
        
        return {
            'spacing': spacing,
            'via_size': self.via_size_ctrl.GetValue(),
            'via_drill': self.drill_size_ctrl.GetValue(),
            'net_name': self.net_choice.GetStringSelection(),
            'use_selected_area': self.area_selection_radio.GetValue(),
            'min_clearance': self.clearance_ctrl.GetValue(),
            'via_to_via_spacing': self.via_spacing_ctrl.GetValue()
        }