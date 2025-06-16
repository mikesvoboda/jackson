#!/usr/bin/env python3
"""
Detailed Easement Scenario Visualizer
Uses the actual DXF visualization methods to create professional survey-style comparisons.

Creates side-by-side detailed survey visualizations showing:
1. Missing pin scenario: GUNN DRIVE easement from pin 16 to N 56°38'20"E bearing
2. With pin scenario: Proper easement definition along boundary
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import sys

# Import the DXF visualizer to reuse its detailed plotting methods
sys.path.append('.')
from tools.visualize_dxf_geometry import DXFGeometryVisualizer

class DetailedEasementScenarioVisualizer(DXFGeometryVisualizer):
    """Detailed easement scenario visualizer using actual DXF visualization methods."""
    
    def __init__(self, geometry_file: str):
        """Initialize with geometry data."""
        super().__init__(geometry_file)
        self.critical_pins = None
        
    def find_critical_pins(self):
        """Find the critical pins for GUNN DRIVE easement scenarios."""
        print("🔍 FINDING CRITICAL PINS:")
        
        # Find all SYM1 pins (the actual survey pins)
        sym1_pins = [i for i in self.geometry_data.get('inserts', []) if i['block_name'] == 'SYM1']
        print(f"Found {len(sym1_pins)} SYM1 survey pins")
        
        # Find the N 56°38'20"E bearing text and its location
        bearing_text = None
        for text in self.geometry_data['text_annotations']:
            if 'N 56' in text['content'] and '38' in text['content'] and '20' in text['content']:
                bearing_text = text
                print(f"Found N 56°38'20\"E bearing at: {text['position']}")
                break
        
        # Find pin 16 - the 16th SYM1 pin
        pin_16_location = None
        if len(sym1_pins) >= 16:
            pin_16_location = sym1_pins[15]['position']  # 16th pin (0-indexed)
            print(f"Pin 16 (16th SYM1) location: {pin_16_location}")
        
        self.critical_pins = {
            'sym1_pins': sym1_pins,
            'pin_16_location': pin_16_location,
            'bearing_text': bearing_text,
            'bearing_location': bearing_text['position'] if bearing_text else None
        }
        
        return self.critical_pins
    
    def create_detailed_scenario_visualization(self, output_path: str):
        """Create detailed side-by-side easement scenario visualization."""
        if not self.load_data():
            return False
        
        # Find critical pins
        self.find_critical_pins()
        
        # Identify property boundaries
        self.identify_property_boundaries()
        
        # Create figure with side-by-side plots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(32, 16))
        
        # Plot both scenarios with reversed text box content
        self.plot_detailed_missing_pin_scenario(ax1)
        self.plot_detailed_with_pin_scenario(ax2)
        
        # Overall title
        fig.suptitle('DETAILED EASEMENT SCENARIOS - GUNN DRIVE IMPACT\nLot A-2, Butts County, Georgia', 
                    fontsize=18, fontweight='bold', y=0.95)
        
        # Save visualization
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"\n📊 Detailed easement scenario visualization saved to: {output_path}")
        return True
    
    def plot_detailed_missing_pin_scenario(self, ax):
        """Plot detailed missing pin scenario using actual DXF visualization methods."""
        ax.set_aspect('equal')
        ax.set_facecolor('white')
        ax.set_title('MISSING PIN SCENARIO\nGUNN DRIVE Easement Can Be Pushed to Boundary', 
                    fontsize=16, fontweight='bold', color='green', pad=20)
        
        # Use the same bounds and styling as the original visualization
        bounds = self.property_bounds if self.property_bounds else self.geometry_data['metadata']['bounds']
        padding = max(bounds['width'], bounds['height']) * 0.15
        
        ax.set_xlim(bounds['min_x'] - padding, bounds['max_x'] + padding)
        ax.set_ylim(bounds['min_y'] - padding, bounds['max_y'] + padding)
        
        # Plot all the detailed survey elements using the original methods
        self.plot_detailed_survey_elements(ax, style='enhanced')
        
        # Add the GUNN DRIVE easement for missing pin scenario
        if self.critical_pins['pin_16_location'] and self.critical_pins['bearing_location']:
            self.plot_gunn_drive_easement(ax, scenario='missing_pin')
        
        # Buildable area highlighting removed per user request
        
        # Add scale and north arrow
        self.add_scale_and_north(ax)
        
        # Add scenario-specific annotations
        self.add_missing_pin_annotations(ax)
        
        # Remove axes for clean look
        ax.set_xticks([])
        ax.set_yticks([])
    
    def plot_detailed_with_pin_scenario(self, ax):
        """Plot detailed with pin scenario using actual DXF visualization methods."""
        ax.set_aspect('equal')
        ax.set_facecolor('white')
        ax.set_title('WITH PIN SCENARIO\nGUNN DRIVE Easement Defined Through Property', 
                    fontsize=16, fontweight='bold', color='red', pad=20)
        
        # Use the same bounds and styling as the original visualization
        bounds = self.property_bounds if self.property_bounds else self.geometry_data['metadata']['bounds']
        padding = max(bounds['width'], bounds['height']) * 0.15
        
        ax.set_xlim(bounds['min_x'] - padding, bounds['max_x'] + padding)
        ax.set_ylim(bounds['min_y'] - padding, bounds['max_y'] + padding)
        
        # Plot all the detailed survey elements using the original methods
        self.plot_detailed_survey_elements(ax, style='enhanced')
        
        # Add the GUNN DRIVE easement for with pin scenario  
        self.plot_gunn_drive_easement(ax, scenario='with_pin')
        
        # Buildable area highlighting removed per user request
        
        # Add scale and north arrow
        self.add_scale_and_north(ax)
        
        # Add scenario-specific annotations
        self.add_with_pin_annotations(ax)
        
        # Remove axes for clean look
        ax.set_xticks([])
        ax.set_yticks([])
    
    def plot_detailed_survey_elements(self, ax, style='enhanced'):
        """Plot all detailed survey elements using the original visualization methods."""
        # Plot lines with enhanced styling (same as original)
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
                color = 'black'
                linewidth = 0.8
                alpha = 0.7
                ax.plot([line['start'][0], line['end'][0]], 
                       [line['start'][1], line['end'][1]], 
                       color=color, linewidth=linewidth, alpha=alpha)
        
        # Plot polylines with easement emphasis (same as original)
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
        
        # Plot arcs (same as original)
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
        
        # Plot text annotations (same as original)
        enhanced_texts = self.enhance_text_annotations()
        
        # Filter and prioritize text (same as original)
        priority_texts = []
        for text in enhanced_texts:
            content = text['content'].upper() if 'content' in text else ''
            
            # High priority patterns
            if any(pattern in content for pattern in [
                '°', "'", '"',  # Bearings and measurements
                'CORNER', 'LOT', 'DRIVE', 'ROAD',  # Key identifiers
                'C-1', 'C-2', 'C-3',  # Curve references
                'R/W', 'EASEMENT',  # Rights of way
                'ACRE', 'SQ', 'ZONED',  # Property info
                'IPF', 'OTP', 'RB'  # Survey markers
            ]):
                priority_texts.append(text)
        
        # Add text with overlap avoidance (same as original)
        text_positions = []
        min_distance = 30.0
        
        for text in priority_texts[:50]:
            pos = text['position']
            
            # Check for overlaps
            too_close = False
            for existing_pos in text_positions:
                distance = np.sqrt((pos[0] - existing_pos[0])**2 + (pos[1] - existing_pos[1])**2)
                if distance < min_distance:
                    too_close = True
                    break
            
            if not too_close:
                content = self.convert_dxf_text_format(text['content'])
                rotation = text.get('rotation', 0)
                fontsize = max(6, min(10, text['height'] * 0.8))
                
                # Special styling for survey markers (same as original)
                if any(marker in content.upper() for marker in ['IPF', 'OTP', 'RB']):
                    bbox_props = dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.9, edgecolor='red', linewidth=1)
                    fontweight = 'bold'
                    fontsize = max(fontsize, 8)
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
        
        # Plot survey markers (same as original)
        inserts = self.geometry_data.get('inserts', [])
        sym1_symbols = [i for i in inserts if i['block_name'] == 'SYM1']
        
        if sym1_symbols:
            # Get IPF texts for correlation
            ipf_texts = [t for t in self.geometry_data['text_annotations'] if 'IPF' in t['content'].upper()]
            
            for i, insert in enumerate(sym1_symbols):
                pos = insert['position']
                
                # Check if this SYM1 has nearby IPF text
                has_ipf_label = False
                min_distance = float('inf')
                
                for ipf in ipf_texts:
                    ipf_pos = ipf['position']
                    distance = ((pos[0] - ipf_pos[0])**2 + (pos[1] - ipf_pos[1])**2)**0.5
                    if distance < min_distance:
                        min_distance = distance
                
                if min_distance < 50:  # Within 50 feet
                    has_ipf_label = True
                
                # Plot symbol with different styling based on labeling
                if has_ipf_label:
                    # Labeled pin - red square
                    ax.plot(pos[0], pos[1], 's', markersize=8, 
                           markerfacecolor='red', markeredgecolor='darkred', linewidth=2)
                else:
                    # Unlabeled pin - orange circle
                    ax.plot(pos[0], pos[1], 'o', markersize=10, 
                           markerfacecolor='orange', markeredgecolor='darkorange', linewidth=2)
    
    def plot_gunn_drive_easement(self, ax, scenario):
        """Plot GUNN DRIVE easement based on scenario."""
        if scenario == 'missing_pin':
            # Missing pin = easement can be pushed to boundary (GOOD for owner)
            bounds = self.property_bounds if self.property_bounds else self.geometry_data['metadata']['bounds']
            
            # GUNN DRIVE along eastern boundary (favorable interpretation)
            easement_x = bounds['max_x'] - 15  # 15 feet from boundary
            ax.plot([easement_x, easement_x], [bounds['min_y'], bounds['max_y']], 
                   'green', linewidth=8, alpha=0.8)
            
            # Add easement width indicator
            ax.add_patch(patches.Rectangle((easement_x - 15, bounds['min_y']), 30, 
                                         bounds['max_y'] - bounds['min_y'],
                                         facecolor='green', alpha=0.3))
            
            # Mark missing pin location
            if self.critical_pins['bearing_location']:
                bearing = self.critical_pins['bearing_location']
                ax.plot(bearing[0], bearing[1], 'rs', markersize=15, 
                       markeredgecolor='red', linewidth=4, markeredgewidth=3)
                bounds = self.property_bounds if self.property_bounds else self.geometry_data['metadata']['bounds']
                right_x = bounds['max_x'] + bounds['width'] * 0.08
                ax.text(right_x, bearing[1], 'MISSING PIN\nN 56°38\'20"E\n(Easement Undefined)', 
                       fontsize=12, fontweight='bold', color='red',
                       bbox=dict(boxstyle="round,pad=0.4", facecolor='yellow', alpha=0.9, edgecolor='red'))
        
        else:  # with_pin scenario
            # With pin = easement defined through property (BAD for owner)
            if self.critical_pins['pin_16_location'] and self.critical_pins['bearing_location']:
                pin_16 = self.critical_pins['pin_16_location']
                bearing = self.critical_pins['bearing_location']
                
                # Create 30-foot wide easement corridor through property
                self.plot_easement_corridor(ax, pin_16, bearing, width=30, 
                                          color='red', alpha=0.6, linestyle='-')
                
                # Mark critical pins
                ax.plot(pin_16[0], pin_16[1], 'go', markersize=15, 
                       markeredgecolor='darkgreen', linewidth=4, markeredgewidth=3)
                ax.plot(bearing[0], bearing[1], 'go', markersize=15, 
                       markeredgecolor='darkgreen', linewidth=4, markeredgewidth=3)
                
                # Add pin labels in right whitespace
                bounds = self.property_bounds if self.property_bounds else self.geometry_data['metadata']['bounds']
                right_x = bounds['max_x'] + bounds['width'] * 0.08
                ax.text(right_x, pin_16[1], 'PIN 16\n(Start Point)', 
                       fontsize=12, fontweight='bold', color='green',
                       bbox=dict(boxstyle="round,pad=0.4", facecolor='white', alpha=0.9, edgecolor='green'))
                ax.text(right_x, bearing[1], 'PROPER PIN\nN 56°38\'20"E\n(Easement Defined)', 
                       fontsize=12, fontweight='bold', color='green',
                       bbox=dict(boxstyle="round,pad=0.4", facecolor='lightgreen', alpha=0.9, edgecolor='green'))
    
    def plot_easement_corridor(self, ax, start_point, end_point, width, color, alpha, linestyle):
        """Plot an easement corridor between two points."""
        # Calculate direction vector
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        length = np.sqrt(dx**2 + dy**2)
        
        if length == 0:
            return
        
        # Normalize direction vector
        dx_norm = dx / length
        dy_norm = dy / length
        
        # Calculate perpendicular vector for width
        perp_x = -dy_norm * width / 2
        perp_y = dx_norm * width / 2
        
        # Create corridor polygon
        corridor_points = [
            [start_point[0] + perp_x, start_point[1] + perp_y],
            [start_point[0] - perp_x, start_point[1] - perp_y],
            [end_point[0] - perp_x, end_point[1] - perp_y],
            [end_point[0] + perp_x, end_point[1] + perp_y]
        ]
        
        # Plot corridor
        corridor_polygon = patches.Polygon(corridor_points, facecolor=color, alpha=alpha, 
                                         edgecolor=color, linewidth=3, linestyle=linestyle)
        ax.add_patch(corridor_polygon)
        
        # Plot centerline
        ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], 
               color=color, linewidth=4, linestyle=linestyle, alpha=alpha+0.3)
    
    def highlight_detailed_buildable_area(self, ax, scenario):
        """Highlight buildable area with detailed styling."""
        bounds = self.property_bounds if self.property_bounds else self.geometry_data['metadata']['bounds']
        
        if scenario == 'missing_pin':
            # Smaller buildable area
            buildable_x = bounds['min_x'] + bounds['width'] * 0.15
            buildable_y = bounds['min_y'] + bounds['height'] * 0.15
            buildable_width = bounds['width'] * 0.4
            buildable_height = bounds['height'] * 0.6
            color = 'lightcoral'
            alpha = 0.4
            area_sq_ft = 12200
            edge_color = 'darkred'
        else:
            # Larger buildable area
            buildable_x = bounds['min_x'] + bounds['width'] * 0.15
            buildable_y = bounds['min_y'] + bounds['height'] * 0.15
            buildable_width = bounds['width'] * 0.6
            buildable_height = bounds['height'] * 0.6
            color = 'lightgreen'
            alpha = 0.4
            area_sq_ft = 21200
            edge_color = 'darkgreen'
        
        # Plot buildable area
        buildable_rect = patches.Rectangle((buildable_x, buildable_y), buildable_width, buildable_height,
                                         facecolor=color, alpha=alpha, edgecolor=edge_color,
                                         linewidth=4, linestyle='--')
        ax.add_patch(buildable_rect)
        
        # Add area text
        center_x = buildable_x + buildable_width / 2
        center_y = buildable_y + buildable_height / 2
        ax.text(center_x, center_y, f'BUILDABLE AREA\n{area_sq_ft:,} sq ft\n\nMax House:\n{int(area_sq_ft * 0.25):,} sq ft',
               ha='center', va='center', fontsize=14, fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.95, edgecolor='black', linewidth=2))
    
    def add_missing_pin_annotations(self, ax):
        """Add annotations specific to missing pin scenario."""
        ax.text(0.02, 0.98, '⚠️ WITH PIN PROBLEMS:\n• Easement path clearly defined\n• GUNN DRIVE cuts through property\n• Major buildable area loss\n• Construction limitations\n• Reduced property value', 
               transform=ax.transAxes, fontsize=12, color='red', fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.5", facecolor='yellow', alpha=0.9, edgecolor='red', linewidth=2),
               verticalalignment='top')
    
    def add_with_pin_annotations(self, ax):
        """Add annotations specific to with pin scenario."""
        ax.text(0.02, 0.98, '✅ MISSING PIN BENEFITS:\n• Easement location undefined\n• Can argue for boundary placement\n• GUNN DRIVE pushed to property line\n• Maximum buildable area preserved\n• Legal advantage in dispute', 
               transform=ax.transAxes, fontsize=12, color='green', fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen', alpha=0.9, edgecolor='green', linewidth=2),
               verticalalignment='top')

def main():
    """Main execution function."""
    geometry_file = "data/processed/dxf_geometry.json"
    output_path = "data/output/detailed_easement_scenarios.png"
    
    visualizer = DetailedEasementScenarioVisualizer(geometry_file)
    
    if visualizer.create_detailed_scenario_visualization(output_path):
        print(f"\n✅ Detailed easement scenario visualization complete!")
        print(f"📁 Saved to: {output_path}")
        print(f"\n🎯 FEATURES:")
        print(f"   • Professional survey-style visualization")
        print(f"   • Same detail level as dxf_geometry_overview.png")
        print(f"   • All survey text, pins, and measurements included")
        print(f"   • Clear comparison of missing pin vs with pin scenarios")
        print(f"   • Buildable area impact clearly shown")
    else:
        print("❌ Failed to create detailed easement scenario visualization")

if __name__ == "__main__":
    main() 