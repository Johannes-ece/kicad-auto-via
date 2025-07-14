#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Via Grid Generator Core Logic
Handles the actual via placement with DRC checking
"""

import pcbnew
import wx
import math
import uuid
import re


class ViaGridGenerator:
    """
    Core generator class that handles via placement
    """
    
    def __init__(self, board, progress_dialog=None):
        self.board = board
        self.progress = progress_dialog
        self.min_clearance = 0.2
        self.via_to_via_clearance = 0.1
        
    def generate_grid(self, spacing_mm, via_size_mm, via_drill_mm, 
                     net_name, use_selected_area=False):
        """
        Generate the via grid
        
        Returns dict with:
            - success: bool
            - vias_placed: int
            - vias_skipped: int
            - error: str (if any)
        """
        try:
            # Find the net
            net = self._find_net(net_name)
            if not net:
                return {
                    'success': False,
                    'error': f"Net '{net_name}' not found",
                    'vias_placed': 0,
                    'vias_skipped': 0
                }
            
            # Get placement area
            if use_selected_area:
                area = self._get_selected_area()
                if not area:
                    return {
                        'success': False,
                        'error': "No valid area selected",
                        'vias_placed': 0,
                        'vias_skipped': 0
                    }
            else:
                area = self._get_board_area()
            
            # Convert to internal units
            spacing = pcbnew.FromMM(spacing_mm)
            via_size = pcbnew.FromMM(via_size_mm)
            via_drill = pcbnew.FromMM(via_drill_mm)
            
            # Get existing board items
            self._update_progress("Loading board items...", 10)
            existing_vias = self._get_existing_vias()
            pads = self._get_all_pads()
            tracks = self._get_all_tracks()
            
            # Generate grid positions
            self._update_progress("Calculating grid positions...", 20)
            positions = self._generate_grid_positions(area, spacing)
            total_positions = len(positions)
            
            # Place vias
            placed = 0
            skipped = 0
            new_vias = []
            
            for idx, pos in enumerate(positions):
                # Update progress
                if idx % 10 == 0:
                    progress = 20 + int((idx / total_positions) * 70)
                    self._update_progress(
                        f"Placing vias... ({placed} placed, {skipped} skipped)",
                        progress
                    )
                
                # Check clearances
                if self._check_clearances(pos, via_size, net.GetNetCode(),
                                        existing_vias + new_vias, pads, tracks):
                    # Create and place via
                    via = self._create_via(pos, via_size, via_drill, net)
                    self.board.Add(via)
                    new_vias.append({
                        'pos': pos,
                        'size': via_size,
                        'net': net.GetNetCode()
                    })
                    placed += 1
                else:
                    skipped += 1
            
            self._update_progress("Completed", 100)
            
            return {
                'success': True,
                'vias_placed': placed,
                'vias_skipped': skipped,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'vias_placed': 0,
                'vias_skipped': 0
            }
    
    def _find_net(self, net_name):
        """Find net by name"""
        return self.board.FindNet(net_name)
    
    def _get_board_area(self):
        """Get the board bounding box from edge cuts"""
        bbox = self.board.GetBoardEdgesBoundingBox()
        return bbox
    
    def _get_selected_area(self):
        """Get bounding box of selected items"""
        # Implementation depends on how selection is done
        # For now, return None to use board area
        return None
    
    def _get_existing_vias(self):
        """Get all existing vias on the board"""
        vias = []
        for track in self.board.GetTracks():
            if track.GetClass() == 'PCB_VIA':
                vias.append({
                    'pos': track.GetPosition(),
                    'size': track.GetWidth(),
                    'net': track.GetNetCode()
                })
        return vias
    
    def _get_all_pads(self):
        """Get all pads from all footprints"""
        pads = []
        for footprint in self.board.GetFootprints():
            for pad in footprint.Pads():
                pads.append({
                    'pos': pad.GetPosition(),
                    'size': max(pad.GetSize()[0], pad.GetSize()[1]),
                    'net': pad.GetNetCode()
                })
        return pads
    
    def _get_all_tracks(self):
        """Get all track segments"""
        tracks = []
        for track in self.board.GetTracks():
            if track.GetClass() == 'PCB_TRACK':
                tracks.append({
                    'start': track.GetStart(),
                    'end': track.GetEnd(),
                    'width': track.GetWidth(),
                    'net': track.GetNetCode()
                })
        return tracks
    
    def _generate_grid_positions(self, area, spacing):
        """Generate grid positions within the given area"""
        positions = []
        
        # Get area bounds
        min_x = area.GetX()
        min_y = area.GetY()
        max_x = area.GetX() + area.GetWidth()
        max_y = area.GetY() + area.GetHeight()
        
        # Add margin
        margin = pcbnew.FromMM(1.0)
        min_x += margin
        min_y += margin
        max_x -= margin
        max_y -= margin
        
        # Generate grid
        x = min_x
        while x <= max_x:
            y = min_y
            while y <= max_y:
                pos = pcbnew.VECTOR2I(int(x), int(y))
                
                # Check if position is inside board outline
                if self._is_inside_board(pos):
                    positions.append(pos)
                
                y += spacing
            x += spacing
        
        return positions
    
    def _is_inside_board(self, pos):
        """Check if position is inside board outline"""
        # Simple implementation - just check bounding box
        # Could be improved to check actual outline
        bbox = self.board.GetBoardEdgesBoundingBox()
        return bbox.Contains(pos)
    
    def _check_clearances(self, pos, via_size, net_code, 
                         vias, pads, tracks):
        """Check if via placement would violate clearances"""
        via_radius = via_size / 2
        min_clear = pcbnew.FromMM(self.min_clearance)
        via_clear = pcbnew.FromMM(self.via_to_via_clearance)
        
        # Check against vias
        for via in vias:
            dist = self._distance(pos, via['pos'])
            if via['net'] == net_code:
                # Same net - use smaller clearance
                if dist < (via_radius + via['size']/2 + via_clear):
                    return False
            else:
                # Different net
                if dist < (via_radius + via['size']/2 + min_clear):
                    return False
        
        # Check against pads
        for pad in pads:
            if pad['net'] != net_code:
                dist = self._distance(pos, pad['pos'])
                if dist < (via_radius + pad['size']/2 + min_clear):
                    return False
        
        # Check against tracks
        for track in tracks:
            if track['net'] != net_code:
                dist = self._distance_to_segment(
                    pos, track['start'], track['end']
                )
                if dist < (via_radius + track['width']/2 + min_clear):
                    return False
        
        return True
    
    def _distance(self, pos1, pos2):
        """Calculate distance between two positions"""
        dx = pos1.x - pos2.x
        dy = pos1.y - pos2.y
        return math.sqrt(dx*dx + dy*dy)
    
    def _distance_to_segment(self, pos, start, end):
        """Calculate distance from point to line segment"""
        # Vector from start to end
        dx = end.x - start.x
        dy = end.y - start.y
        
        # Vector from start to point
        px = pos.x - start.x
        py = pos.y - start.y
        
        # Project point onto line
        if dx == 0 and dy == 0:
            # Degenerate segment
            return self._distance(pos, start)
        
        t = (px * dx + py * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        
        # Closest point on segment
        closest = pcbnew.VECTOR2I(
            int(start.x + t * dx),
            int(start.y + t * dy)
        )
        
        return self._distance(pos, closest)
    
    def _create_via(self, pos, size, drill, net):
        """Create a new via"""
        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition(pos)
        via.SetWidth(size)
        via.SetDrill(drill)
        via.SetNet(net)
        via.SetViaType(pcbnew.VIATYPE_THROUGH)
        
        # Set layer pair
        via.SetLayerPair(
            self.board.GetLayerID("F.Cu"),
            self.board.GetLayerID("B.Cu")
        )
        
        # Generate unique ID
        # In KiCad v9, SetTimeStamp might not exist, try without it first
        try:
            via.SetTimeStamp(int(uuid.uuid4().int & 0xFFFFFFFF))
        except AttributeError:
            # Method doesn't exist in this KiCad version
            pass
        
        return via
    
    def _update_progress(self, message, value):
        """Update progress dialog if available"""
        if self.progress:
            wx.CallAfter(self.progress.Update, value, message)