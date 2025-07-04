import pcbnew
import os
import wx
import math
from .grid_generator import GridGenerator
from .drc_checker import DRCChecker

class ViaGridPlacerAction(pcbnew.ActionPlugin):
    """
    KiCad 9 plugin for placing vias in a grid pattern within copper zones
    """
    
    def defaults(self):
        """Configure plugin metadata"""
        self.name = "Via Grid Placer"
        self.category = "Modify PCB"
        self.description = "Place vias in a grid pattern within selected copper zones"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.dark_icon_file_name = os.path.join(os.path.dirname(__file__), 'icon_dark.png')
    
    def Run(self):
        """Main plugin execution"""
        board = pcbnew.GetBoard()
        
        # Get selected items
        selected = list(pcbnew.GetCurrentSelection())
        
        # Find zones and vias in selection
        zones = []
        vias = []
        
        for item in selected:
            if item.Type() == pcbnew.PCB_ZONE_T:
                zones.append(item)
            elif item.Type() == pcbnew.PCB_VIA_T:
                vias.append(item)
        
        # Validate selection
        if not zones:
            wx.MessageBox("Please select at least one copper zone", 
                         "No Zone Selected", wx.OK | wx.ICON_WARNING)
            return
        
        if not vias:
            wx.MessageBox("Please select a reference via", 
                         "No Via Selected", wx.OK | wx.ICON_WARNING)
            return
        
        # Use first via as reference
        reference_via = vias[0]
        
        # Show configuration dialog
        dialog = ViaGridConfigDialog(None, board, reference_via)
        if dialog.ShowModal() != wx.ID_OK:
            dialog.Destroy()
            return
        
        grid_spacing = dialog.GetGridSpacing()
        use_stagger = dialog.GetStaggerEnabled()
        check_drc = dialog.GetDRCCheckEnabled()
        dialog.Destroy()
        
        # Create grid generator and DRC checker
        grid_gen = GridGenerator(board)
        drc_check = DRCChecker(board)
        
        # Extract via properties
        via_props = {
            'drill': reference_via.GetDrillValue(),
            'width': reference_via.GetWidth(),
            'via_type': reference_via.GetViaType(),
            'net': reference_via.GetNet()
        }
        
        # Process each zone
        total_placed = 0
        total_skipped = 0
        
        # Progress dialog
        progress = wx.ProgressDialog(
            "Placing Vias",
            "Generating grid points...",
            maximum=100,
            style=wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME
        )
        
        try:
            for zone_idx, zone in enumerate(zones):
                progress.Update(int(zone_idx * 100 / len(zones)), 
                              f"Processing zone {zone_idx + 1} of {len(zones)}")
                
                # Use reference via position as origin
                origin = reference_via.GetPosition()
                
                # Generate grid points
                grid_points = grid_gen.generate_grid_in_zone(
                    zone, origin, grid_spacing, use_stagger
                )
                
                # Place vias
                for i, point in enumerate(grid_points):
                    if i % 10 == 0:  # Update progress every 10 vias
                        cont, _ = progress.Update(
                            int(zone_idx * 100 / len(zones) + (i * 100 / len(grid_points)) / len(zones)),
                            f"Placing via {i + 1} of {len(grid_points)} in zone {zone_idx + 1}"
                        )
                        if not cont:
                            break
                    
                    # Check DRC if enabled
                    if check_drc:
                        clearance_ok = drc_check.check_via_clearance(
                            point, via_props['width'], via_props['net']
                        )
                        if not clearance_ok:
                            total_skipped += 1
                            continue
                    
                    # Create and place via
                    new_via = pcbnew.PCB_VIA(board)
                    new_via.SetPosition(point)
                    new_via.SetDrill(via_props['drill'])
                    new_via.SetWidth(via_props['width'])
                    new_via.SetViaType(via_props['via_type'])
                    new_via.SetNet(via_props['net'])
                    
                    board.Add(new_via)
                    total_placed += 1
            
        finally:
            progress.Destroy()
        
        # Refresh display
        pcbnew.Refresh()
        
        # Report results
        wx.MessageBox(
            f"Via placement complete!\n\n"
            f"Vias placed: {total_placed}\n"
            f"Vias skipped (DRC): {total_skipped}",
            "Operation Complete",
            wx.OK | wx.ICON_INFORMATION
        )


class ViaGridConfigDialog(wx.Dialog):
    """Configuration dialog for via grid parameters"""
    
    def __init__(self, parent, board, reference_via):
        super().__init__(parent, title="Via Grid Configuration", 
                        size=(400, 300))
        
        self.board = board
        self.reference_via = reference_via
        
        # Create UI
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Grid spacing
        grid_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Grid Parameters")
        
        spacing_sizer = wx.BoxSizer(wx.HORIZONTAL)
        spacing_label = wx.StaticText(panel, label="Grid Spacing (mm):")
        self.spacing_ctrl = wx.SpinCtrlDouble(panel, min=0.1, max=50.0, 
                                             initial=5.0, inc=0.1)
        spacing_sizer.Add(spacing_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        spacing_sizer.Add(self.spacing_ctrl, 1, wx.EXPAND)
        grid_box.Add(spacing_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Stagger option
        self.stagger_check = wx.CheckBox(panel, label="Stagger alternate rows")
        grid_box.Add(self.stagger_check, 0, wx.ALL, 5)
        
        sizer.Add(grid_box, 0, wx.EXPAND | wx.ALL, 10)
        
        # DRC options
        drc_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Design Rules")
        self.drc_check = wx.CheckBox(panel, label="Check DRC before placing")
        self.drc_check.SetValue(True)
        drc_box.Add(self.drc_check, 0, wx.ALL, 5)
        
        sizer.Add(drc_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Via info
        info_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Reference Via")
        via_size = pcbnew.ToMM(self.reference_via.GetWidth())
        via_drill = pcbnew.ToMM(self.reference_via.GetDrillValue())
        info_text = f"Size: {via_size:.2f}mm, Drill: {via_drill:.2f}mm"
        info_label = wx.StaticText(panel, label=info_text)
        info_box.Add(info_label, 0, wx.ALL, 5)
        
        sizer.Add(info_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Buttons
        btn_sizer = wx.StdDialogButtonSizer()
        ok_btn = wx.Button(panel, wx.ID_OK)
        cancel_btn = wx.Button(panel, wx.ID_CANCEL)
        btn_sizer.AddButton(ok_btn)
        btn_sizer.AddButton(cancel_btn)
        btn_sizer.Realize()
        
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        
    def GetGridSpacing(self):
        """Return grid spacing in KiCad internal units"""
        return pcbnew.FromMM(self.spacing_ctrl.GetValue())
    
    def GetStaggerEnabled(self):
        return self.stagger_check.GetValue()
    
    def GetDRCCheckEnabled(self):
        return self.drc_check.GetValue()