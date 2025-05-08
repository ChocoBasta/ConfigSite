import ezdxf
import os

class ProfileManager:
    def __init__(self):
        self.profiles = {}
        self.load_profiles()

    def load_profiles(self):
        """Load all DXF profiles from the assets/dxf directory"""
        dxf_dir = os.path.join('assets', 'dxf')
        print(f"Loading profiles from: {dxf_dir}")
        
        # Create directory if it doesn't exist
        if not os.path.exists(dxf_dir):
            os.makedirs(dxf_dir)
            print(f"Created directory: {dxf_dir}")
            return

        # Load all DXF files
        for filename in os.listdir(dxf_dir):
            if filename.endswith('.dxf'):
                print(f"Found DXF file: {filename}")
                filepath = os.path.join(dxf_dir, filename)
                self.load_profile(filepath)

    def load_profile(self, filepath):
        """Load a single DXF profile from file"""
        try:
            # Read DXF file
            doc = ezdxf.readfile(filepath)
            msp = doc.modelspace()
            
            # Get profile name from filename
            profile_name = os.path.splitext(os.path.basename(filepath))[0]
            print(f"\nLoading profile: {profile_name}")
            
            # Initialize empty profile
            self.profiles[profile_name] = {}
            
            # Process all entities
            print("Processing entities...")
            for entity in msp:
                # Get entity type and layer
                entity_type = entity.dxftype()
                layer = entity.dxf.layer
                
                # Skip if not a polyline
                if entity_type not in ['LWPOLYLINE', 'POLYLINE']:
                    continue
                
                print(f"Found {entity_type} in layer: {layer}")
                
                # Get points based on entity type
                try:
                    if entity_type == 'LWPOLYLINE':
                        points = [(point[0], point[1]) for point in entity.get_points()]
                    else:  # POLYLINE
                        points = [(vertex[0], vertex[1]) for vertex in entity.points()]
                    
                    # Store points in profile
                    if points:
                        self.profiles[profile_name][layer] = points
                        print(f"Added {len(points)} points to layer {layer}")
                        print(f"First point: {points[0]}")
                        print(f"Last point: {points[-1]}")
                except Exception as e:
                    print(f"Error processing points in layer {layer}: {str(e)}")
            
            # Print summary
            print(f"\nProfile {profile_name} loaded with {len(self.profiles[profile_name])} layers:")
            for layer, points in self.profiles[profile_name].items():
                print(f"- {layer}: {len(points)} points")
            
        except Exception as e:
            print(f"Error loading profile {filepath}: {str(e)}")
            import traceback
            traceback.print_exc()

    def scale_profile(self, profile_name, scale_x, scale_y, reference_y=None):
        """Scale a profile's points based on scaling factors"""
        if profile_name not in self.profiles:
            return None
            
        scaled_profile = {}
        original_profile = self.profiles[profile_name]
        
        # First, find the original dimensions and panel positions
        panel_positions = {}
        for layer, points in original_profile.items():
            if not points or 'SLOT' in layer:
                continue
                
            # Get the bounding box of this panel
            min_x = min(p[0] for p in points)
            max_x = max(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_y = max(p[1] for p in points)
            
            # Store panel dimensions and position
            panel_positions[layer] = {
                'min_x': min_x,
                'max_x': max_x,
                'min_y': min_y,
                'max_y': max_y,
                'width': max_x - min_x,
                'height': max_y - min_y
            }
        
        # Calculate the gaps between panels
        left_panels = [p for p in panel_positions.keys() if 'L' in p]
        right_panels = [p for p in panel_positions.keys() if 'R' in p]
        top_panels = [p for p in panel_positions.keys() if 'T' in p]
        bottom_panels = [p for p in panel_positions.keys() if 'B' in p]
        
        # Get the original gaps
        original_horizontal_gap = min(panel_positions[r]['min_x'] for r in right_panels) - max(panel_positions[l]['max_x'] for l in left_panels)
        original_vertical_gap = min(panel_positions[t]['min_y'] for t in top_panels) - max(panel_positions[b]['max_y'] for b in bottom_panels)
        
        # Calculate new gaps based on scaling
        new_horizontal_gap = original_horizontal_gap * scale_x
        new_vertical_gap = original_vertical_gap * scale_y
        
        # Process each layer
        for layer, points in original_profile.items():
            if not points:
                continue
                
            if 'SLOT' in layer:
                # Keep slots in their original position
                scaled_points = points
            else:
                # For panels, keep their shape but move them based on their position
                is_left = 'L' in layer
                is_top = 'T' in layer
                
                # Calculate offset based on panel position
                x_offset = 0 if is_left else new_horizontal_gap - original_horizontal_gap
                y_offset = 0 if is_top else new_vertical_gap - original_vertical_gap
                
                # Move the panel without adding any connecting lines
                scaled_points = [(x + x_offset, y + y_offset) for x, y in points]
            
            scaled_profile[layer] = scaled_points
            
        return scaled_profile

    def get_profile(self, profile_name):
        """Get a profile by name"""
        return self.profiles.get(profile_name)

    def list_profiles(self):
        """List all available profiles"""
        return list(self.profiles.keys()) 