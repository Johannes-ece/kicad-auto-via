import pcbnew
import math

class DRCChecker:
    """Handles Design Rule Checking for via placement"""
    
    def __init__(self, board):
        self.board = board
        self.min_clearance = self._get_min_clearance()
    
    def _get_min_clearance(self):
        """Get minimum clearance from board design rules"""
        # Get design settings
        settings = self.board.GetDesignSettings()
        
        # Get minimum clearance (returns internal units)
        return settings.GetSmallestClearanceValue()
    
    def check_via_clearance(self, position, via_width, net):
        """Check if via at position would violate clearance rules"""
        # Create search area
        search_radius = via_width // 2 + self.min_clearance * 2
        search_area = pcbnew.BOX2I(position, pcbnew.VECTOR2I(0, 0))
        search_area.Inflate(search_radius)
        
        # Get items in search area
        collector = pcbnew.GENERAL_COLLECTOR()
        guide = pcbnew.COLLECTORS_GUIDE()
        guide.SetIgnoreMTextsMarkedNoShow(True)
        guide.SetIgnoreMTextsOnBack(True)
        guide.SetIgnoreMTextsOnFront(True)
        guide.SetIgnoreModulesOnBack(False)
        guide.SetIgnoreModulesOnFront(False)
        
        # Collect items
        self.board.Collect(collector, [pcbnew.PCB_TRACE_T, pcbnew.PCB_VIA_T, 
                                      pcbnew.PCB_PAD_T], position, guide)
        
        # Check clearances
        via_radius = via_width // 2
        
        for i in range(collector.GetCount()):
            item = collector[i]
            
            # Skip items on same net
            if hasattr(item, 'GetNet') and item.GetNet() == net:
                continue
            
            # Calculate required clearance
            item_clearance = self._get_item_clearance(item)
            required_clearance = max(self.min_clearance, item_clearance)
            
            # Check distance
            if self._check_collision(position, via_radius, item, required_clearance):
                return False
        
        return True
    
    def _get_item_clearance(self, item):
        """Get clearance requirement for specific item"""
        # This is simplified - real implementation would check net classes
        return self.min_clearance
    
    def _check_collision(self, via_pos, via_radius, item, clearance):
        """Check if via would collide with item"""
        if item.Type() == pcbnew.PCB_VIA_T:
            # Via to via check
            item_pos = item.GetPosition()
            item_radius = item.GetWidth() // 2
            
            distance = math.sqrt((via_pos.x - item_pos.x)**2 + 
                               (via_pos.y - item_pos.y)**2)
            
            return distance < (via_radius + item_radius + clearance)
        
        elif item.Type() == pcbnew.PCB_TRACE_T:
            # Via to track check
            track_start = item.GetStart()
            track_end = item.GetEnd()
            track_width = item.GetWidth()
            
            # Simple distance check to track
            dist = self._point_to_line_distance(via_pos, track_start, track_end)
            
            return dist < (via_radius + track_width // 2 + clearance)
        
        elif item.Type() == pcbnew.PCB_PAD_T:
            # Via to pad check
            pad_pos = item.GetPosition()
            pad_bbox = item.GetBoundingBox()
            
            # Simplified - check bounding box
            test_box = pcbnew.BOX2I(via_pos, pcbnew.VECTOR2I(0, 0))
            test_box.Inflate(via_radius + clearance)
            
            return test_box.Intersects(pad_bbox)
        
        return False
    
    def _point_to_line_distance(self, point, line_start, line_end):
        """Calculate distance from point to line segment"""
        # Vector from start to end
        dx = line_end.x - line_start.x
        dy = line_end.y - line_start.y
        
        # Vector from start to point
        px = point.x - line_start.x
        py = point.y - line_start.y
        
        # Project point onto line
        if dx == 0 and dy == 0:
            # Line is actually a point
            return math.sqrt(px**2 + py**2)
        
        t = max(0, min(1, (px * dx + py * dy) / (dx * dx + dy * dy)))
        
        # Closest point on line
        closest_x = line_start.x + t * dx
        closest_y = line_start.y + t * dy
        
        # Distance to closest point
        return math.sqrt((point.x - closest_x)**2 + (point.y - closest_y)**2)