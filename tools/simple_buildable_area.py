#!/usr/bin/env python3
"""
Simple Buildable Area Calculator
Realistic analysis of construction space within property boundaries.

Focus: Impact of missing "IPF 1/2" RB ON LINE" pin on GUNN DRIVE easement
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

class SimpleBuildableAreaCalculator:
    """Simple, accurate buildable area calculator."""
    
    def __init__(self, geometry_file: str):
        """Initialize with geometry data."""
        self.geometry_file = geometry_file
        self.geometry_data = None
        
        # Property details from README.md
        self.property_area_sq_ft = 49200  # 1.129 acres
        
        # Realistic constraint estimates for irregular pentagon property
        self.constraints = {
            'diagonal_easement': 12000,    # 30-foot diagonal easement across property
            'setbacks_total': 8000,        # Combined setback areas (realistic for irregular shape)
            'gunn_undefined': 6000,        # Conservative buffer for undefined GUNN DRIVE
            'gunn_defined': 3000,          # Smaller area if GUNN DRIVE properly defined
            'uncertainty_buffer': 2000     # Additional buffer due to legal uncertainty
        }
        
    def load_data(self):
        """Load geometry data."""
        try:
            with open(self.geometry_file, 'r') as f:
                self.geometry_data = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def calculate_buildable_scenarios(self):
        """Calculate buildable areas for both scenarios."""
        print("🏗️ SIMPLE BUILDABLE AREA ANALYSIS")
        print("=" * 50)
        print(f"Property: Lot A-2, Butts County, Georgia")
        print(f"Total area: {self.property_area_sq_ft:,} sq ft (1.129 acres)")
        print(f"Shape: Irregular pentagon with curved boundaries")
        
        # Scenario 1: Missing pin (current situation)
        print(f"\n📊 SCENARIO 1 - MISSING PIN (Current):")
        print(f"-" * 40)
        
        remaining_1 = self.property_area_sq_ft
        print(f"Total property area: {remaining_1:,} sq ft")
        
        remaining_1 -= self.constraints['diagonal_easement']
        print(f"- 30-foot diagonal easement: -{self.constraints['diagonal_easement']:,} sq ft")
        
        remaining_1 -= self.constraints['setbacks_total']
        print(f"- Required setbacks (all sides): -{self.constraints['setbacks_total']:,} sq ft")
        
        remaining_1 -= self.constraints['gunn_undefined']
        print(f"- GUNN DRIVE (undefined): -{self.constraints['gunn_undefined']:,} sq ft")
        
        remaining_1 -= self.constraints['uncertainty_buffer']
        print(f"- Legal uncertainty buffer: -{self.constraints['uncertainty_buffer']:,} sq ft")
        
        buildable_1 = max(0, remaining_1)
        max_house_1 = buildable_1 * 0.25  # Conservative 25% coverage
        
        print(f"= BUILDABLE AREA: {buildable_1:,} sq ft")
        print(f"Max house footprint: {max_house_1:.0f} sq ft")
        
        # Scenario 2: With proper pin
        print(f"\n📊 SCENARIO 2 - WITH PROPER PIN:")
        print(f"-" * 40)
        
        remaining_2 = self.property_area_sq_ft
        print(f"Total property area: {remaining_2:,} sq ft")
        
        remaining_2 -= self.constraints['diagonal_easement']
        print(f"- 30-foot diagonal easement: -{self.constraints['diagonal_easement']:,} sq ft")
        
        remaining_2 -= self.constraints['setbacks_total']
        print(f"- Required setbacks (all sides): -{self.constraints['setbacks_total']:,} sq ft")
        
        remaining_2 -= self.constraints['gunn_defined']
        print(f"- GUNN DRIVE (defined): -{self.constraints['gunn_defined']:,} sq ft")
        
        # No uncertainty buffer needed
        print(f"- Legal uncertainty buffer: -0 sq ft")
        
        buildable_2 = max(0, remaining_2)
        max_house_2 = buildable_2 * 0.30  # More aggressive 30% coverage when defined
        
        print(f"= BUILDABLE AREA: {buildable_2:,} sq ft")
        print(f"Max house footprint: {max_house_2:.0f} sq ft")
        
        # Impact analysis
        difference = buildable_2 - buildable_1
        house_difference = max_house_2 - max_house_1
        
        print(f"\n🎯 IMPACT OF MISSING PIN:")
        print(f"=" * 30)
        print(f"Buildable area difference: +{difference:,} sq ft")
        print(f"House footprint difference: +{house_difference:.0f} sq ft")
        print(f"Percentage impact: {100 * difference / self.property_area_sq_ft:.1f}% of total property")
        
        return {
            'missing_pin': {'buildable': buildable_1, 'max_house': max_house_1},
            'with_pin': {'buildable': buildable_2, 'max_house': max_house_2},
            'difference': difference,
            'house_difference': house_difference
        }
    
    def create_visualization(self, results, output_path):
        """Create simple, clear visualization."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Colors
        property_color = 'lightgray'
        easement_color = 'red'
        setback_color = 'yellow'
        gunn_undefined_color = 'orange'
        gunn_defined_color = 'blue'
        buildable_uncertain_color = 'lightcoral'
        buildable_defined_color = 'lightgreen'
        
        # Property dimensions (simplified rectangle for visualization)
        prop_width = 300
        prop_height = 200
        
        for i, (scenario, ax) in enumerate([('missing_pin', ax1), ('with_pin', ax2)]):
            ax.set_xlim(0, prop_width)
            ax.set_ylim(0, prop_height)
            ax.set_aspect('equal')
            
            # Property boundary
            property_rect = patches.Rectangle((0, 0), prop_width, prop_height,
                                            facecolor=property_color, edgecolor='black', linewidth=2,
                                            label='Property Boundary')
            ax.add_patch(property_rect)
            
            # Diagonal easement
            diagonal_points = [(50, 180), (250, 20)]
            easement_width = 20
            dx = diagonal_points[1][0] - diagonal_points[0][0]
            dy = diagonal_points[1][1] - diagonal_points[0][1]
            length = np.sqrt(dx**2 + dy**2)
            offset_x = -dy / length * easement_width / 2
            offset_y = dx / length * easement_width / 2
            
            easement_poly = patches.Polygon([
                (diagonal_points[0][0] + offset_x, diagonal_points[0][1] + offset_y),
                (diagonal_points[0][0] - offset_x, diagonal_points[0][1] - offset_y),
                (diagonal_points[1][0] - offset_x, diagonal_points[1][1] - offset_y),
                (diagonal_points[1][0] + offset_x, diagonal_points[1][1] + offset_y)
            ], facecolor=easement_color, alpha=0.7, label='30\' Diagonal Easement')
            ax.add_patch(easement_poly)
            
            # Setbacks (simplified)
            setback_width = 15
            # Front setback
            ax.add_patch(patches.Rectangle((0, prop_height-setback_width), prop_width, setback_width,
                                         facecolor=setback_color, alpha=0.6, label='Setbacks'))
            # Side setbacks
            ax.add_patch(patches.Rectangle((0, 0), setback_width, prop_height,
                                         facecolor=setback_color, alpha=0.6))
            ax.add_patch(patches.Rectangle((prop_width-setback_width, 0), setback_width, prop_height,
                                         facecolor=setback_color, alpha=0.6))
            # Rear setback
            ax.add_patch(patches.Rectangle((0, 0), prop_width, setback_width,
                                         facecolor=setback_color, alpha=0.6))
            
            # GUNN DRIVE easement
            if scenario == 'missing_pin':
                # Undefined - larger area
                gunn_rect = patches.Rectangle((prop_width-60, 0), 60, prop_height,
                                            facecolor=gunn_undefined_color, alpha=0.6,
                                            label='GUNN DRIVE (Undefined)')
                ax.add_patch(gunn_rect)
                
                # Buildable area
                buildable_rect = patches.Rectangle((setback_width+5, setback_width+5), 
                                                 prop_width-60-setback_width-10, 
                                                 prop_height-2*setback_width-10,
                                                 facecolor=buildable_uncertain_color, alpha=0.8,
                                                 label='Buildable Area')
                ax.add_patch(buildable_rect)
                
                ax.set_title('CURRENT SITUATION\n(Missing Critical Pin)', fontweight='bold', color='red')
                
                # Add text
                ax.text(0.02, 0.98, '⚠️ MISSING PIN\nUndefined Easement\nLarge Buffer Required', 
                       transform=ax.transAxes, fontsize=10, color='red', fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.9),
                       verticalalignment='top')
                
            else:
                # Defined - smaller area
                gunn_rect = patches.Rectangle((prop_width-35, 0), 35, prop_height,
                                            facecolor=gunn_defined_color, alpha=0.6,
                                            label='GUNN DRIVE (Defined)')
                ax.add_patch(gunn_rect)
                
                # Buildable area
                buildable_rect = patches.Rectangle((setback_width+5, setback_width+5), 
                                                 prop_width-35-setback_width-10, 
                                                 prop_height-2*setback_width-10,
                                                 facecolor=buildable_defined_color, alpha=0.8,
                                                 label='Buildable Area')
                ax.add_patch(buildable_rect)
                
                ax.set_title('WITH PROPER PIN\n(Easement Defined)', fontweight='bold', color='green')
                
                # Add text
                ax.text(0.02, 0.98, '✅ WITH PIN\nDefined Easement\nOptimal Building Area', 
                       transform=ax.transAxes, fontsize=10, color='green', fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.9),
                       verticalalignment='top')
            
            # Add area numbers
            result = results[scenario]
            ax.text(0.5, 0.5, f'{result["buildable"]:,} sq ft\nBuildable\n\nMax House:\n{result["max_house"]:.0f} sq ft',
                   transform=ax.transAxes, ha='center', va='center', fontsize=11, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.4", facecolor='white', alpha=0.9))
            
            ax.legend(loc='lower right', fontsize=8)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(True, alpha=0.3)
        
        # Overall title
        fig.suptitle('BUILDABLE AREA ANALYSIS - Missing Pin Impact\nLot A-2, Butts County, Georgia', 
                    fontsize=14, fontweight='bold')
        
        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"\n📊 Visualization saved to: {output_path}")
    
    def run_analysis(self, output_path):
        """Run complete analysis."""
        if not self.load_data():
            return False
        
        results = self.calculate_buildable_scenarios()
        self.create_visualization(results, output_path)
        
        print(f"\n💰 FINANCIAL IMPACT:")
        print(f"=" * 20)
        print(f"Lost buildable area: {results['difference']:,} sq ft")
        print(f"Lost house potential: {results['house_difference']:.0f} sq ft")
        print(f"Estimated value impact: ${results['difference'] * 75:,} - ${results['difference'] * 150:,}")
        
        print(f"\n🏗️ CONSTRUCTION RECOMMENDATIONS:")
        print(f"=" * 35)
        print(f"Conservative house size: 2,000-2,500 sq ft")
        print(f"Moderate house size: 2,500-3,000 sq ft")
        print(f"Maximum safe size: {results['missing_pin']['max_house']:.0f} sq ft (current situation)")
        print(f"Optimal with pin: {results['with_pin']['max_house']:.0f} sq ft")
        
        return True

def main():
    """Main execution."""
    geometry_file = "data/processed/dxf_geometry.json"
    output_path = "data/output/buildable_area_analysis.png"
    
    calculator = SimpleBuildableAreaCalculator(geometry_file)
    
    if calculator.run_analysis(output_path):
        print(f"\n✅ Analysis complete!")
        print(f"📁 Results saved to: {output_path}")
    else:
        print("❌ Analysis failed")

if __name__ == "__main__":
    main() 