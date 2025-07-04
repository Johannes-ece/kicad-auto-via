import pcbnew
import math

class GridGenerator:
    """Generates grid points within PCB zones"""
    
    def __init__(self, board):
        self.board = board
    
    def generate_grid_in_zone(self, zone, origin, spacing, stagger=False):
        """Generate grid points within zone boundaries"""
        points = []
        
        # Get zone bounding box
        bbox = zone.GetBoundingBox()
        x_min = bbox.GetX()
        y_min = bbox.GetY()
        x_max = bbox.GetRight()
        y_max = bbox.GetBottom()
        
        # Generate grid aligned to origin
        origin_x = origin.x
        origin_y = origin.y
        
        # Calculate grid start points
        x_start = origin_x - math.floor((origin_x - x_min) / spacing) * spacing
        y_start = origin_y - math.floor((origin_y - y_min) / spacing) * spacing
        
        # Generate points
        y = y_start
        row = 0
        while y <= y_max:
            x = x_start
            if stagger and row % 2 == 1:
                x += spacing / 2
            
            while x <= x_max:
                point = pcbnew.VECTOR2I(int(x), int(y))
                
                # Check if point is inside zone
                if self.point_in_zone(point, zone):
                    points.append(point)
                
                x += spacing
            
            y += spacing
            row += 1
        
        return points
    
    def point_in_zone(self, point, zone):
        """Check if point is inside zone boundary"""
        # Get zone outline
        outline = zone.Outline()
        
        # KiCad provides built-in collision detection
        return outline.Contains(point)
    
    def get_zone_filled_area(self, zone):
        """Get the filled area polygons for more accurate checking"""
        layer = zone.GetLayer()
        filled_polys = zone.GetFilledPolysList(layer)
        
        # Return the filled polygon set for advanced operations
        return filled_polys