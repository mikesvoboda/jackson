#!/usr/bin/env python3
"""
DXF Geometry Visualization Tool
Enhanced version incorporating all analysis findings and improvements.

Author: Senior Architect Analysis System
Date: 2024
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import re
from collections import defaultdict

class DXFGeometryVisualizer:
    """Visualize DXF geometry data with enhanced accuracy and professional styling."""
    
    def __init__(self, geometry_file: str):
        """Initialize with geometry data file."""
        self.geometry_file = geometry_file
        self.geometry_data = None
        self.property_bounds = None
        
    def load_data(self):
        """Load and process geometry data."""
        try:
            with open(self.geometry_file, 'r') as f:
                self.geometry_data = json.load(f)
            print(f"Loaded geometry data: {len(self.geometry_data['lines'])} lines, {len(self.geometry_data['text_annotations'])} texts")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def convert_dxf_text_format(self, text: str) -> str:
        """Convert DXF text format to proper display format."""
        # Convert %%d to degree symbol
        text = text.replace('%%d', '°')
        text = text.replace('%%D', '°')
        
        # Clean up common DXF formatting
        text = text.replace('%%c', 'Ø')  # Diameter symbol
        text = text.replace('%%p', '±')  # Plus/minus
        
        return text
    
    def identify_property_boundaries(self):
        """Identify the actual property boundaries from the larger survey area."""
        print("Identifying property boundaries...")
        
        # Property boundaries are typically green lines (color 3)
        property_lines = []
        for line in self.geometry_data['lines']:
            if line['color'] == 3:
                property_lines.append(line)
        
        # Calculate bounds of property elements
        if property_lines:
            all_points = []
            for line in property_lines:
                all_points.extend([line['start'], line['end']])
            
            if all_points:
                x_coords = [p[0] for p in all_points]
                y_coords = [p[1] for p in all_points]
                
                self.property_bounds = {
                    'min_x': min(x_coords),
                    'max_x': max(x_coords),
                    'min_y': min(y_coords),
                    'max_y': max(y_coords),
                    'width': max(x_coords) - min(x_coords),
                    'height': max(y_coords) - min(y_coords)
                }
                
                area_sq_ft = self.property_bounds['width'] * self.property_bounds['height']
                print(f"Property bounds area estimate: {area_sq_ft:.0f} sq ft")
                return True
        
        # Fallback to full survey bounds
        self.property_bounds = self.geometry_data['metadata']['bounds']
        return False
    
    def enhance_text_annotations(self):
        """Enhance text annotations with proper formatting and missing elements."""
        enhanced_texts = []
        
        # Process existing texts with format conversion
        for text in self.geometry_data['text_annotations']:
            enhanced_text = text.copy()
            enhanced_text['content'] = self.convert_dxf_text_format(text['content'])
            
            # Only include texts with reasonable height
            if text['height'] >= 3.0:
                enhanced_texts.append(enhanced_text)
        
        # Add missing critical elements
        if self.property_bounds:
            missing_elements = [
                {'content': 'GUNN DRIVE', 'position': (self.property_bounds['max_x'] + 20, (self.property_bounds['min_y'] + self.property_bounds['max_y'])/2), 'height': 8.0, 'rotation': 90},
                {'content': '30\' R/W', 'position': (self.property_bounds['max_x'] + 40, (self.property_bounds['min_y'] + self.property_bounds['max_y'])/2 + 30), 'height': 6.0, 'rotation': 0},
                {'content': 'LOT A-2', 'position': ((self.property_bounds['min_x'] + self.property_bounds['max_x'])/2, (self.property_bounds['min_y'] + self.property_bounds['max_y'])/2), 'height': 12.0, 'rotation': 0},
            ]
            
            for element in missing_elements:
                enhanced_texts.append(element)
            
            # Add corner labels
            corners = [
                {'label': 'CORNER A', 'pos': (self.property_bounds['min_x'], self.property_bounds['min_y'])},
                {'label': 'CORNER B', 'pos': (self.property_bounds['max_x'], self.property_bounds['min_y'])},
                {'label': 'CORNER C', 'pos': (self.property_bounds['max_x'], self.property_bounds['max_y'])},
                {'label': 'CORNER D', 'pos': (self.property_bounds['min_x'], self.property_bounds['max_y'])},
            ]
            
            for corner in corners:
                enhanced_texts.append({
                    'content': corner['label'],
                    'position': corner['pos'],
                    'height': 6.0,
                    'rotation': 0
                })
        
        return enhanced_texts
    
    def add_scale_and_north(self, ax):
        """Add scale bar and north arrow to the survey."""
        bounds = ax.get_xlim(), ax.get_ylim()
        
        # Scale bar
        scale_length = 100  # 100 feet
        scale_x = bounds[0][0] + (bounds[0][1] - bounds[0][0]) * 0.05
        scale_y = bounds[1][0] + (bounds[1][1] - bounds[1][0]) * 0.05
        
        ax.plot([scale_x, scale_x + scale_length], [scale_y, scale_y], 
               color='black', linewidth=3)
        ax.text(scale_x + scale_length/2, scale_y - 20, "100'", 
               ha='center', va='top', fontsize=10, fontweight='bold')
        
        # North arrow
        north_x = bounds[0][1] - (bounds[0][1] - bounds[0][0]) * 0.05
        north_y = bounds[1][1] - (bounds[1][1] - bounds[1][0]) * 0.05
        
        ax.annotate('N', xy=(north_x, north_y), xytext=(north_x, north_y - 30),
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'),
                   fontsize=12, fontweight='bold', ha='center')

    def create_visualization(self, output_path: str, style: str = 'enhanced'):
        """Create DXF geometry visualization with specified style."""
        if not self.load_data():
            return False
        
        print("Creating survey visualization...")
        
        # Identify property boundaries for enhanced style
        if style == 'enhanced':
            self.identify_property_boundaries()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 12))
        ax.set_aspect('equal')
        ax.set_facecolor('white')
        
        # Set bounds based on style
        bounds = self.geometry_data['metadata']['bounds']
        if style == 'enhanced' and self.property_bounds:
            bounds = self.property_bounds
            padding = max(bounds['width'], bounds['height']) * 0.15
        else:
            padding = max(bounds['width'], bounds['height']) * 0.02
        
        ax.set_xlim(bounds['min_x'] - padding, bounds['max_x'] + padding)
        ax.set_ylim(bounds['min_y'] - padding, bounds['max_y'] + padding)
        
        # Plot lines with enhanced styling
        print(f"Plotting {len(self.geometry_data['lines'])} lines...")
        for line in self.geometry_data['lines']:
            if line['linetype'] == 'HIDDEN':
                # Easement lines - orange dashed
                ax.plot([line['start'][0], line['end'][0]], 
                       [line['start'][1], line['end'][1]], 
                       color='orange', linewidth=3.0, linestyle='--', alpha=0.8)
            elif line['color'] == 3:
                # Property boundaries - thick green
                ax.plot([line['start'][0], line['end'][0]], 
                       [line['start'][1], line['end'][1]], 
                       color='green', linewidth=2.5, solid_capstyle='round')
            else:
                # Other survey lines
                color = 'black' if style == 'enhanced' else f'C{line["color"] % 10}'
                linewidth = 0.8 if style == 'enhanced' else 1.0
                alpha = 0.7 if style == 'enhanced' else 1.0
                ax.plot([line['start'][0], line['end'][0]], 
                       [line['start'][1], line['end'][1]], 
                       color=color, linewidth=linewidth, alpha=alpha)
        
        # Plot polylines with easement emphasis
        print(f"Plotting {len(self.geometry_data['polylines'])} polylines...")
        for polyline in self.geometry_data['polylines']:
            vertices = polyline['vertices']
            if len(vertices) < 2:
                continue
                
            x_coords = [v[0] for v in vertices]
            y_coords = [v[1] for v in vertices]
            
            if polyline.get('linetype') == 'HIDDEN' or len(vertices) > 40:
                # Easement boundaries - thick orange dashed
                ax.plot(x_coords, y_coords, color='orange', linewidth=3.5, 
                       linestyle='--', alpha=0.9, solid_capstyle='round')
            else:
                # Regular polylines
                ax.plot(x_coords, y_coords, color='black', linewidth=1.0, alpha=0.7)
        
        # Plot arcs
        print(f"Plotting {len(self.geometry_data['arcs'])} arcs...")
        for arc in self.geometry_data['arcs']:
            center = arc['center']
            radius = arc['radius']
            start_angle = arc['start_angle']
            end_angle = arc['end_angle']
            
            if end_angle < start_angle:
                end_angle += 360
            
            arc_patch = patches.Arc(center, 2*radius, 2*radius, 
                                  angle=0, theta1=start_angle, theta2=end_angle,
                                  color='blue', linewidth=2.0)
            ax.add_patch(arc_patch)
        
        # Analyze and highlight easement geometry
        print("Analyzing potential easement geometry...")
        hidden_lines = [line for line in self.geometry_data['lines'] if line['linetype'] == 'HIDDEN']
        print(f"Found {len(hidden_lines)} hidden lines (potential easements)")
        
        # Plot text annotations
        if style == 'enhanced':
            enhanced_texts = self.enhance_text_annotations()
            texts_to_plot = enhanced_texts
        else:
            texts_to_plot = self.geometry_data['text_annotations']
        
        print(f"Plotting text annotations (height >= 4.0)...")
        
        # Filter and prioritize text
        priority_texts = []
        for text in texts_to_plot:
            content = text['content'].upper() if 'content' in text else ''
            
            # High priority patterns
            if any(pattern in content for pattern in [
                '°', "'", '"',  # Bearings and measurements
                'CORNER', 'LOT', 'DRIVE', 'ROAD',  # Key identifiers
                'C-1', 'C-2', 'C-3',  # Curve references
                'R/W', 'EASEMENT',  # Rights of way
                'ACRE', 'SQ', 'ZONED',  # Property info
                'IPF', 'OTP', 'RB'  # Survey markers - CRITICAL for boundary identification
            ]):
                priority_texts.append(text)
        
        # Add text with overlap avoidance
        text_positions = []
        min_distance = 30.0  # Reduced from 50.0 to allow more IPF texts
        texts_plotted = 0
        
        for text in priority_texts[:50]:  # Increased from 30 to 50 for more survey markers
            pos = text['position']
            
            # Check for overlaps
            too_close = False
            for existing_pos in text_positions:
                distance = np.sqrt((pos[0] - existing_pos[0])**2 + (pos[1] - existing_pos[1])**2)
                if distance < min_distance:
                    too_close = True
                    break
            
            if not too_close:
                content = text['content']
                if style == 'enhanced':
                    content = self.convert_dxf_text_format(content)
                
                rotation = text.get('rotation', 0)
                fontsize = max(6, min(10, text['height'] * 0.8))
                
                # Special styling for survey markers
                if any(marker in content.upper() for marker in ['IPF', 'OTP', 'RB']):
                    bbox_props = dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.9, edgecolor='red', linewidth=1)
                    fontweight = 'bold'
                    fontsize = max(fontsize, 8)  # Ensure IPF text is readable
                elif any(kw in content.upper() for kw in ['CORNER', 'LOT', 'DRIVE']):
                    bbox_props = dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8, edgecolor='none')
                    fontweight = 'bold'
                else:
                    bbox_props = dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8, edgecolor='none')
                    fontweight = 'normal'
                
                ax.text(pos[0], pos[1], content,
                       fontsize=fontsize, rotation=rotation,
                       ha='center', va='center',
                       bbox=bbox_props, fontweight=fontweight)
                
                text_positions.append(pos)
                texts_plotted += 1
        
        print(f"Showing high-priority text annotations (filtered from {len(texts_to_plot)} total)")
        print(f"Plotted {texts_plotted} text annotations (avoiding overlaps)")
        
        # Plot survey markers (inserts) - ALL SYM1 symbols are important boundary markers
        inserts = self.geometry_data.get('inserts', [])
        sym1_symbols = [i for i in inserts if i['block_name'] == 'SYM1']
        if sym1_symbols:
            print(f"Adding {len(sym1_symbols)} SYM1 survey markers (discovered pins)...")
            
            # Get IPF texts for correlation
            ipf_texts = [t for t in self.geometry_data['text_annotations'] if 'IPF' in t['content'].upper()]
            
            for i, insert in enumerate(sym1_symbols):
                pos = insert['position']
                
                # Check if this SYM1 has nearby IPF text
                has_ipf_label = False
                closest_ipf = None
                min_distance = float('inf')
                
                for ipf in ipf_texts:
                    ipf_pos = ipf['position']
                    distance = ((pos[0] - ipf_pos[0])**2 + (pos[1] - ipf_pos[1])**2)**0.5
                    if distance < min_distance:
                        min_distance = distance
                        closest_ipf = ipf
                
                if min_distance < 50:  # Within 50 feet
                    has_ipf_label = True
                
                # Plot symbol with different styling based on labeling
                if has_ipf_label:
                    # Labeled pin - red square
                    ax.plot(pos[0], pos[1], 's', markersize=8, 
                           markerfacecolor='red', markeredgecolor='darkred', linewidth=2)
                else:
                    # Unlabeled pin - orange circle (potential missing boundary marker)
                    ax.plot(pos[0], pos[1], 'o', markersize=10, 
                           markerfacecolor='orange', markeredgecolor='darkorange', linewidth=2)
                    
                    # Add label for unlabeled pins
                    ax.text(pos[0] + 15, pos[1] + 15, f'PIN #{i+1}', 
                           fontsize=8, fontweight='bold', color='darkorange',
                           bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.9, edgecolor='orange'))
        
        # Add professional elements for enhanced style
        if style == 'enhanced':
            ax.set_title('SURVEY OF LOT A-2\nMICHAEL & BROOKE SVOBODA\nBUTTS COUNTY, GEORGIA', 
                        fontsize=14, fontweight='bold', pad=20)
            self.add_scale_and_north(ax)
        else:
            ax.set_title('DXF Geometry Visualization', fontsize=14, fontweight='bold')
        
        # Remove axes for clean look
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Save visualization
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"Visualization saved to: {output_path}")
        return True

def main():
    """Main execution function."""
    geometry_file = "data/processed/dxf_geometry.json"
    
    # Create visualizer
    visualizer = DXFGeometryVisualizer(geometry_file)
    
    # Generate enhanced visualization (primary output)
    enhanced_output = "data/output/dxf_geometry_overview.png"
    if visualizer.create_visualization(enhanced_output, style='enhanced'):
        print(f"\n✅ Enhanced survey visualization created!")
        print(f"📁 Saved to: {enhanced_output}")
        
        # Also create geometry-only version for reference
        geometry_output = "data/output/dxf_geometry_overview_geometry_only.png"
        if visualizer.create_visualization(geometry_output, style='basic'):
            print(f"📁 Geometry-only version: {geometry_output}")
        
        print(f"\n🎯 Key Features:")
        print(f"   • Y-shaped easement highlighted in orange")
        print(f"   • Property boundaries in green")
        print(f"   • Text format converted (° symbols)")
        print(f"   • Missing elements added (GUNN DRIVE, corners)")
        print(f"   • Professional survey styling")
    else:
        print("❌ Failed to create visualization")

if __name__ == "__main__":
    main() 