#!/usr/bin/env python3
"""
DXF Geometry Extraction Tool
Extracts geometric entities from survey DXF files for property analysis.

Author: Senior Architect Analysis System
Date: 2024
"""

import ezdxf
import json
import numpy as np
from typing import Dict, List, Tuple, Any
import os
from pathlib import Path

class DXFGeometryExtractor:
    """Extract and process geometric data from DXF survey files."""
    
    def __init__(self, dxf_path: str):
        """Initialize with DXF file path."""
        self.dxf_path = dxf_path
        self.doc = None
        self.geometry_data = {
            'property_boundaries': [],
            'easements': [],
            'curves': [],
            'lines': [],
            'polylines': [],
            'circles': [],
            'arcs': [],
            'text_annotations': [],
            'dimensions': [],
            'points': [],
            'inserts': [],  # Block insertions
            'metadata': {}
        }
        
    def load_dxf(self):
        """Load the DXF document."""
        try:
            self.doc = ezdxf.readfile(self.dxf_path)
            print(f"Successfully loaded DXF file: {self.dxf_path}")
            print(f"DXF version: {self.doc.dxfversion}")
            return True
        except Exception as e:
            print(f"Error loading DXF file: {e}")
            return False
    
    def extract_lines(self):
        """Extract all LINE entities."""
        lines = []
        msp = self.doc.modelspace()
        
        for entity in msp.query('LINE'):
            line_data = {
                'start': [entity.dxf.start.x, entity.dxf.start.y],
                'end': [entity.dxf.end.x, entity.dxf.end.y],
                'layer': entity.dxf.layer,
                'color': entity.dxf.color,
                'linetype': entity.dxf.linetype,
                'length': np.sqrt((entity.dxf.end.x - entity.dxf.start.x)**2 + 
                                (entity.dxf.end.y - entity.dxf.start.y)**2)
            }
            lines.append(line_data)
        
        self.geometry_data['lines'] = lines
        print(f"Extracted {len(lines)} lines")
        
    def extract_polylines(self):
        """Extract all POLYLINE and LWPOLYLINE entities."""
        polylines = []
        msp = self.doc.modelspace()
        
        # Extract POLYLINE entities
        for entity in msp.query('POLYLINE'):
            vertices = []
            for vertex in entity.vertices:
                vertices.append([vertex.dxf.location.x, vertex.dxf.location.y])
            
            polyline_data = {
                'type': 'POLYLINE',
                'vertices': vertices,
                'layer': entity.dxf.layer,
                'color': entity.dxf.color,
                'linetype': entity.dxf.linetype,
                'closed': entity.is_closed,
                'vertex_count': len(vertices)
            }
            polylines.append(polyline_data)
        
        # Extract LWPOLYLINE entities
        for entity in msp.query('LWPOLYLINE'):
            vertices = []
            for point in entity:
                vertices.append([point[0], point[1]])
            
            polyline_data = {
                'type': 'LWPOLYLINE',
                'vertices': vertices,
                'layer': entity.dxf.layer,
                'color': entity.dxf.color,
                'linetype': entity.dxf.linetype,
                'closed': entity.closed,
                'vertex_count': len(vertices)
            }
            polylines.append(polyline_data)
        
        self.geometry_data['polylines'] = polylines
        print(f"Extracted {len(polylines)} polylines")
    
    def extract_arcs(self):
        """Extract all ARC entities."""
        arcs = []
        msp = self.doc.modelspace()
        
        for entity in msp.query('ARC'):
            arc_data = {
                'center': [entity.dxf.center.x, entity.dxf.center.y],
                'radius': entity.dxf.radius,
                'start_angle': entity.dxf.start_angle,
                'end_angle': entity.dxf.end_angle,
                'layer': entity.dxf.layer,
                'color': entity.dxf.color,
                'arc_length': entity.dxf.radius * np.radians(abs(entity.dxf.end_angle - entity.dxf.start_angle))
            }
            arcs.append(arc_data)
        
        self.geometry_data['arcs'] = arcs
        print(f"Extracted {len(arcs)} arcs")
    
    def extract_circles(self):
        """Extract all CIRCLE entities."""
        circles = []
        msp = self.doc.modelspace()
        
        for entity in msp.query('CIRCLE'):
            circle_data = {
                'center': [entity.dxf.center.x, entity.dxf.center.y],
                'radius': entity.dxf.radius,
                'layer': entity.dxf.layer,
                'color': entity.dxf.color,
                'circumference': 2 * np.pi * entity.dxf.radius,
                'area': np.pi * entity.dxf.radius**2
            }
            circles.append(circle_data)
        
        self.geometry_data['circles'] = circles
        print(f"Extracted {len(circles)} circles")
    
    def extract_text(self):
        """Extract all TEXT and MTEXT entities."""
        texts = []
        msp = self.doc.modelspace()
        
        # Extract TEXT entities
        for entity in msp.query('TEXT'):
            text_data = {
                'type': 'TEXT',
                'content': entity.dxf.text,
                'position': [entity.dxf.insert.x, entity.dxf.insert.y],
                'height': entity.dxf.height,
                'rotation': entity.dxf.rotation,
                'layer': entity.dxf.layer,
                'color': entity.dxf.color
            }
            texts.append(text_data)
        
        # Extract MTEXT entities
        for entity in msp.query('MTEXT'):
            text_data = {
                'type': 'MTEXT',
                'content': entity.text,
                'position': [entity.dxf.insert.x, entity.dxf.insert.y],
                'height': entity.dxf.char_height,
                'rotation': entity.dxf.rotation,
                'layer': entity.dxf.layer,
                'color': entity.dxf.color
            }
            texts.append(text_data)
        
        self.geometry_data['text_annotations'] = texts
        print(f"Extracted {len(texts)} text annotations")
    
    def extract_dimensions(self):
        """Extract dimension entities."""
        dimensions = []
        msp = self.doc.modelspace()
        
        for entity in msp.query('DIMENSION'):
            dim_data = {
                'type': entity.dxftype(),
                'layer': entity.dxf.layer,
                'color': entity.dxf.color,
                'measurement': getattr(entity.dxf, 'actual_measurement', None)
            }
            
            # Try to get dimension points
            try:
                if hasattr(entity.dxf, 'defpoint'):
                    dim_data['defpoint'] = [entity.dxf.defpoint.x, entity.dxf.defpoint.y]
                if hasattr(entity.dxf, 'defpoint2'):
                    dim_data['defpoint2'] = [entity.dxf.defpoint2.x, entity.dxf.defpoint2.y]
                if hasattr(entity.dxf, 'defpoint3'):
                    dim_data['defpoint3'] = [entity.dxf.defpoint3.x, entity.dxf.defpoint3.y]
            except:
                pass
            
            dimensions.append(dim_data)
        
        self.geometry_data['dimensions'] = dimensions
        print(f"Extracted {len(dimensions)} dimensions")
    
    def extract_points(self):
        """Extract POINT entities."""
        points = []
        msp = self.doc.modelspace()
        
        for entity in msp.query('POINT'):
            point_data = {
                'position': [entity.dxf.location.x, entity.dxf.location.y],
                'layer': entity.dxf.layer,
                'color': entity.dxf.color
            }
            points.append(point_data)
        
        self.geometry_data['points'] = points
        print(f"Extracted {len(points)} points")
    
    def extract_inserts(self):
        """Extract INSERT entities (block insertions)."""
        inserts = []
        msp = self.doc.modelspace()
        
        for entity in msp.query('INSERT'):
            insert_data = {
                'block_name': entity.dxf.name,
                'position': [entity.dxf.insert.x, entity.dxf.insert.y],
                'layer': entity.dxf.layer,
                'color': entity.dxf.color,
                'rotation': getattr(entity.dxf, 'rotation', 0.0),
                'scale_x': getattr(entity.dxf, 'xscale', 1.0),
                'scale_y': getattr(entity.dxf, 'yscale', 1.0),
                'scale_z': getattr(entity.dxf, 'zscale', 1.0)
            }
            inserts.append(insert_data)
        
        self.geometry_data['inserts'] = inserts
        print(f"Extracted {len(inserts)} block insertions")
    
    def analyze_layers(self):
        """Analyze layer information to identify property boundaries and easements."""
        layer_analysis = {}
        
        # Analyze all entities by layer
        msp = self.doc.modelspace()
        for entity in msp:
            layer = entity.dxf.layer
            if layer not in layer_analysis:
                layer_analysis[layer] = {
                    'entity_types': set(),
                    'entity_count': 0,
                    'colors': set()
                }
            
            layer_analysis[layer]['entity_types'].add(entity.dxftype())
            layer_analysis[layer]['entity_count'] += 1
            layer_analysis[layer]['colors'].add(entity.dxf.color)
        
        # Convert sets to lists for JSON serialization
        for layer in layer_analysis:
            layer_analysis[layer]['entity_types'] = list(layer_analysis[layer]['entity_types'])
            layer_analysis[layer]['colors'] = list(layer_analysis[layer]['colors'])
        
        self.geometry_data['metadata']['layers'] = layer_analysis
        print(f"Analyzed {len(layer_analysis)} layers")
    
    def identify_property_features(self):
        """Identify specific property features based on geometry and text."""
        # Look for easement-related text
        easement_keywords = ['easement', 'right', 'way', 'utility', 'ingress', 'egress']
        curve_keywords = ['curve', 'radius', 'delta', 'chord', 'arc']
        
        for text in self.geometry_data['text_annotations']:
            content_lower = text['content'].lower()
            
            # Check for easement references
            if any(keyword in content_lower for keyword in easement_keywords):
                text['feature_type'] = 'easement_annotation'
            
            # Check for curve references
            elif any(keyword in content_lower for keyword in curve_keywords):
                text['feature_type'] = 'curve_annotation'
            
            # Check for property corner references
            elif any(corner in content_lower for corner in ['corner', 'point', 'p.o.b', 'beginning']):
                text['feature_type'] = 'corner_annotation'
            
            # Check for bearing/distance information
            elif '°' in content_lower or "'" in content_lower or '"' in content_lower:
                text['feature_type'] = 'survey_measurement'
    
    def calculate_bounds(self):
        """Calculate overall bounds of the survey."""
        all_x = []
        all_y = []
        
        # Collect all coordinates
        for line in self.geometry_data['lines']:
            all_x.extend([line['start'][0], line['end'][0]])
            all_y.extend([line['start'][1], line['end'][1]])
        
        for polyline in self.geometry_data['polylines']:
            for vertex in polyline['vertices']:
                all_x.append(vertex[0])
                all_y.append(vertex[1])
        
        for arc in self.geometry_data['arcs']:
            # Approximate arc bounds
            center_x, center_y = arc['center']
            radius = arc['radius']
            all_x.extend([center_x - radius, center_x + radius])
            all_y.extend([center_y - radius, center_y + radius])
        
        for circle in self.geometry_data['circles']:
            center_x, center_y = circle['center']
            radius = circle['radius']
            all_x.extend([center_x - radius, center_x + radius])
            all_y.extend([center_y - radius, center_y + radius])
        
        if all_x and all_y:
            bounds = {
                'min_x': min(all_x),
                'max_x': max(all_x),
                'min_y': min(all_y),
                'max_y': max(all_y),
                'width': max(all_x) - min(all_x),
                'height': max(all_y) - min(all_y)
            }
            self.geometry_data['metadata']['bounds'] = bounds
            print(f"Survey bounds: {bounds['width']:.2f} x {bounds['height']:.2f}")
    
    def extract_all_geometry(self):
        """Extract all geometric entities from the DXF file."""
        if not self.load_dxf():
            return False
        
        print("Extracting geometry from DXF file...")
        
        # Extract all entity types
        self.extract_lines()
        self.extract_polylines()
        self.extract_arcs()
        self.extract_circles()
        self.extract_text()
        self.extract_dimensions()
        self.extract_points()
        self.extract_inserts()
        
        # Analyze and identify features
        self.analyze_layers()
        self.identify_property_features()
        self.calculate_bounds()
        
        # Add metadata
        self.geometry_data['metadata']['source_file'] = self.dxf_path
        self.geometry_data['metadata']['extraction_summary'] = {
            'total_lines': len(self.geometry_data['lines']),
            'total_polylines': len(self.geometry_data['polylines']),
            'total_arcs': len(self.geometry_data['arcs']),
            'total_circles': len(self.geometry_data['circles']),
            'total_text': len(self.geometry_data['text_annotations']),
            'total_dimensions': len(self.geometry_data['dimensions']),
            'total_points': len(self.geometry_data['points']),
            'total_inserts': len(self.geometry_data['inserts'])
        }
        
        return True
    
    def save_geometry_data(self, output_path: str):
        """Save extracted geometry data to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.geometry_data, f, indent=2)
        
        print(f"Geometry data saved to: {output_path}")
        return True

def main():
    """Main execution function."""
    # Set up paths
    dxf_path = "data/raw/210309.DXF"
    output_path = "data/processed/dxf_geometry.json"
    
    # Create output directory
    os.makedirs("data/processed", exist_ok=True)
    
    # Extract geometry
    extractor = DXFGeometryExtractor(dxf_path)
    
    if extractor.extract_all_geometry():
        extractor.save_geometry_data(output_path)
        print("\n=== Extraction Complete ===")
        print(f"Summary:")
        summary = extractor.geometry_data['metadata']['extraction_summary']
        for key, value in summary.items():
            print(f"  {key}: {value}")
    else:
        print("Failed to extract geometry from DXF file")

if __name__ == "__main__":
    main() 