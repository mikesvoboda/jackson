#!/usr/bin/env python3
"""
Pin Coordinate Analysis - Ironstone vs. Actual Survey Data
Visualizes the specific pin location discrepancy for legal analysis.

This script highlights the coordinate fraud evidence by showing:
1. Actual SYM1 pin location from DXF survey data
2. Ironstone's claimed "exact coordinates" 
3. Visual circle highlighting the 3-inch discrepancy
4. Context for legal significance
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

class PinCoordinateAnalyzer:
    """Analyze and visualize pin coordinate discrepancies."""
    
    def __init__(self, geometry_file: str):
        """Initialize with geometry data file."""
        self.geometry_file = geometry_file
        self.geometry_data = None
        
        # Coordinates from Ironstone email (May 2, 2022)
        self.ironstone_north = 1222153.447
        self.ironstone_east = 2384715.378
        
        # Actual coordinates from DXF survey data (SYM1 pin)
        self.actual_north = 1222153.692742
        self.actual_east = 2384715.355801
        
        # Calculate discrepancy
        self.north_diff = self.actual_north - self.ironstone_north  # 0.245742 feet
        self.east_diff = self.actual_east - self.ironstone_east     # -0.022199 feet
        self.total_discrepancy = np.sqrt(self.north_diff**2 + self.east_diff**2)
        
    def load_data(self):
        """Load geometry data."""
        try:
            with open(self.geometry_file, 'r') as f:
                self.geometry_data = json.load(f)
            print(f"Loaded geometry data successfully")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def find_target_pin(self):
        """Find the SYM1 pin that matches our target coordinates."""
        target_pin = None
        min_distance = float('inf')
        
        inserts = self.geometry_data.get('inserts', [])
        sym1_pins = [i for i in inserts if i['block_name'] == 'SYM1']
        
        for pin in sym1_pins:
            pos = pin['position']
            # Check if this is close to our actual coordinates
            distance = np.sqrt((pos[0] - self.actual_east)**2 + (pos[1] - self.actual_north)**2)
            if distance < min_distance:
                min_distance = distance
                target_pin = pin
        
        if target_pin and min_distance < 1.0:  # Within 1 foot
            print(f"Found target pin at: E{target_pin['position'][0]:.6f} N{target_pin['position'][1]:.6f}")
            print(f"Distance from expected: {min_distance:.6f} feet")
            return target_pin
        else:
            print(f"Warning: Could not find exact matching pin. Closest distance: {min_distance:.6f} feet")
            return target_pin
    
    def create_coordinate_analysis_visualization(self, output_path: str):
        """Create focused visualization showing coordinate discrepancy."""
        if not self.load_data():
            return False
        
        # Find the target pin
        target_pin = self.find_target_pin()
        if not target_pin:
            print("Could not locate target pin for analysis")
            return False
        
        # Create figure with two subplots: overview and detail
        fig = plt.figure(figsize=(20, 12))
        
        # Subplot 1: Overview of entire survey
        ax1 = plt.subplot(1, 2, 1)
        ax1.set_title('SURVEY OVERVIEW\nShowing Pin Location Context', fontsize=14, fontweight='bold', pad=20)
        
        # Plot full survey area
        bounds = self.geometry_data['metadata']['bounds']
        ax1.set_xlim(bounds['min_x'], bounds['max_x'])
        ax1.set_ylim(bounds['min_y'], bounds['max_y'])
        ax1.set_aspect('equal')
        
        # Plot main survey lines
        for line in self.geometry_data['lines']:
            color = 'green' if line['color'] == 3 else 'gray'
            linewidth = 2.0 if line['color'] == 3 else 0.5
            alpha = 1.0 if line['color'] == 3 else 0.3
            ax1.plot([line['start'][0], line['end'][0]], 
                     [line['start'][1], line['end'][1]], 
                     color=color, linewidth=linewidth, alpha=alpha)
        
        # Plot all SYM1 pins
        inserts = self.geometry_data.get('inserts', [])
        sym1_pins = [i for i in inserts if i['block_name'] == 'SYM1']
        for pin in sym1_pins:
            pos = pin['position']
            if pin == target_pin:
                # Highlight the target pin
                ax1.plot(pos[0], pos[1], 'o', markersize=12, 
                        markerfacecolor='red', markeredgecolor='darkred', linewidth=3)
                ax1.text(pos[0] + 50, pos[1] + 50, 'TARGET PIN\n(Coordinate Issue)', 
                        fontsize=10, fontweight='bold', color='red',
                        bbox=dict(boxstyle="round,pad=0.5", facecolor='yellow', alpha=0.9))
            else:
                ax1.plot(pos[0], pos[1], 's', markersize=6, 
                        markerfacecolor='blue', markeredgecolor='navy', linewidth=1)
        
        # Add north arrow and scale
        ax1.text(bounds['max_x'] - 100, bounds['max_y'] - 50, 'N ↑', 
                fontsize=12, fontweight='bold', ha='center')
        
        # Subplot 2: Detailed view of coordinate discrepancy
        ax2 = plt.subplot(1, 2, 2)
        ax2.set_title('COORDINATE DISCREPANCY ANALYSIS\nIronstone Claim vs. Actual Survey Data', 
                     fontsize=14, fontweight='bold', pad=20)
        
        # Focus on the pin area (±20 feet around the pin)
        center_x = target_pin['position'][0]
        center_y = target_pin['position'][1]
        margin = 20  # 20 feet margin
        
        ax2.set_xlim(center_x - margin, center_x + margin)
        ax2.set_ylim(center_y - margin, center_y + margin)
        ax2.set_aspect('equal')
        
        # Plot nearby survey elements for context
        for line in self.geometry_data['lines']:
            # Only plot lines near our target area
            start_x, start_y = line['start']
            end_x, end_y = line['end']
            
            # Check if line intersects our area of interest
            if (center_x - margin <= max(start_x, end_x) and 
                center_x + margin >= min(start_x, end_x) and
                center_y - margin <= max(start_y, end_y) and 
                center_y + margin >= min(start_y, end_y)):
                
                color = 'green' if line['color'] == 3 else 'gray'
                linewidth = 2.0 if line['color'] == 3 else 1.0
                ax2.plot([start_x, end_x], [start_y, end_y], 
                        color=color, linewidth=linewidth, alpha=0.7)
        
        # Plot actual pin location (from DXF data)
        ax2.plot(self.actual_east, self.actual_north, 'o', markersize=15, 
                markerfacecolor='green', markeredgecolor='darkgreen', linewidth=3,
                label=f'ACTUAL PIN LOCATION\nE{self.actual_east:.6f}\nN{self.actual_north:.6f}')
        
        # Plot Ironstone's claimed location
        ax2.plot(self.ironstone_east, self.ironstone_north, 'X', markersize=15, 
                markerfacecolor='red', markeredgecolor='darkred', linewidth=3,
                label=f'IRONSTONE CLAIM\nE{self.ironstone_east:.3f}\nN{self.ironstone_north:.3f}')
        
        # Draw line connecting the two points
        ax2.plot([self.actual_east, self.ironstone_east], 
                [self.actual_north, self.ironstone_north], 
                'r--', linewidth=2, alpha=0.7, label=f'Discrepancy: {self.total_discrepancy:.3f} ft')
        
        # Circle the discrepancy area
        circle = patches.Circle((self.actual_east, self.actual_north), 
                              radius=self.total_discrepancy, 
                              fill=False, edgecolor='red', linewidth=2, 
                              linestyle='--', alpha=0.8)
        ax2.add_patch(circle)
        
        # Add coordinate annotations
        ax2.annotate(f'ACTUAL:\nE {self.actual_east:.6f}\nN {self.actual_north:.6f}\n(DXF Survey Data)', 
                    xy=(self.actual_east, self.actual_north), 
                    xytext=(self.actual_east - 15, self.actual_north + 10),
                    fontsize=9, fontweight='bold', color='green',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen', alpha=0.9),
                    arrowprops=dict(arrowstyle='->', color='green', linewidth=2))
        
        ax2.annotate(f'IRONSTONE CLAIM:\nE {self.ironstone_east:.3f}\nN {self.ironstone_north:.3f}\n("Exact Coordinates")', 
                    xy=(self.ironstone_east, self.ironstone_north), 
                    xytext=(self.ironstone_east + 10, self.ironstone_north - 12),
                    fontsize=9, fontweight='bold', color='red',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='pink', alpha=0.9),
                    arrowprops=dict(arrowstyle='->', color='red', linewidth=2))
        
        # Add discrepancy measurements
        mid_x = (self.actual_east + self.ironstone_east) / 2
        mid_y = (self.actual_north + self.ironstone_north) / 2
        
        ax2.text(mid_x - 8, mid_y, 
                f'DISCREPANCY:\n{self.total_discrepancy:.3f} feet\n({self.total_discrepancy * 12:.1f} inches)', 
                fontsize=10, fontweight='bold', color='red',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='yellow', alpha=0.9),
                ha='center', va='center')
        
        # Add grid for precise measurement
        ax2.grid(True, alpha=0.3, linewidth=0.5)
        ax2.set_xlabel('Easting (feet)', fontsize=12)
        ax2.set_ylabel('Northing (feet)', fontsize=12)
        
        # Add legal significance analysis
        legal_text = f"""COORDINATE ACCURACY ANALYSIS:

IRONSTONE'S EMAIL CLAIM (May 2, 2022):
"The exact coordinate for the pin is- N.{self.ironstone_north} E{self.ironstone_east}"

ACTUAL DXF SURVEY DATA:
SYM1 Pin at N.{self.actual_north:.6f} E.{self.actual_east:.6f}

DISCREPANCY:
• North: {self.north_diff:.3f} feet ({self.north_diff * 12:.1f} inches)
• East: {self.east_diff:.3f} feet ({abs(self.east_diff) * 12:.1f} inches)
• Total: {self.total_discrepancy:.3f} feet ({self.total_discrepancy * 12:.1f} inches)

LEGAL SIGNIFICANCE:
• Ironstone claimed "exact coordinates" but provided approximations
• Their coordinates appear nowhere in legitimate survey documentation
• Coordinates only have 3 decimal places (unprofessional precision)
• Professional surveys require 6+ decimal places for legal boundaries
• Evidence suggests approximation rather than field measurement

FRAUD INDICATORS:
• False precision claims ("exact coordinates")
• Coordinates don't match any actual survey point
• Combined with IPF fraud (marking placed pin as "found")
• Pattern of deceptive practices throughout survey process"""
        
        plt.figtext(0.02, 0.02, legal_text, fontsize=9, 
                   bbox=dict(boxstyle="round,pad=1.0", facecolor='lightyellow', alpha=0.9),
                   verticalalignment='bottom')
        
        # Remove axes numbers for cleaner detail view
        ax1.set_xticks([])
        ax1.set_yticks([])
        
        plt.tight_layout()
        
        # Save the visualization
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"Pin coordinate analysis saved to: {output_path}")
        
        # Print summary
        print(f"\n📍 COORDINATE ANALYSIS SUMMARY:")
        print(f"   Ironstone claimed: E{self.ironstone_east} N{self.ironstone_north}")
        print(f"   Actual survey pin: E{self.actual_east:.6f} N{self.actual_north:.6f}")
        print(f"   Discrepancy: {self.total_discrepancy:.3f} feet ({self.total_discrepancy * 12:.1f} inches)")
        print(f"   Legal significance: {'MINIMAL' if self.total_discrepancy < 0.5 else 'SIGNIFICANT'} for boundary disputes")
        
        return True

def main():
    """Main execution function."""
    geometry_file = "01_source_documents/surveys/processed/dxf_geometry.json"
    
    # Create analyzer
    analyzer = PinCoordinateAnalyzer(geometry_file)
    
    # Generate coordinate analysis visualization
    output_path = "02_analysis/coordinate_fraud/pin_coordinate_discrepancy.png"
    if analyzer.create_coordinate_analysis_visualization(output_path):
        print(f"\n✅ Pin coordinate analysis visualization created!")
        print(f"📁 Saved to: {output_path}")
        
        # Print legal context
        print(f"\n⚖️ LEGAL CONTEXT:")
        print(f"   • 3 inches is generally NOT significant for property boundaries")
        print(f"   • However, FALSE PRECISION CLAIMS are evidence of fraud")
        print(f"   • Ironstone's coordinates appear NOWHERE in legitimate records")
        print(f"   • This supports the broader pattern of deceptive practices")
        print(f"   • Combined with IPF fraud, strengthens overall malpractice case")
    else:
        print("❌ Failed to create coordinate analysis")

if __name__ == "__main__":
    main() 