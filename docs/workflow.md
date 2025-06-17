# Order of Operations for Survey Data Extraction and Visualization

1. **Extract Geometry from DXF**
   - Script: `tools/extract_dxf_geometry.py`
   - Output: `data/processed/dxf_geometry.json`
   - Description: Extracts all geometric entities (lines, polylines, arcs, circles, text, etc.) from the DXF survey file and saves them in a structured format for further processing.

2. **Visualize Extracted Geometry**
   - Script: `tools/visualize_dxf_geometry.py`
   - Output: `data/output/dxf_geometry_overview.png`
   - Description: Plots all extracted geometry for validation and reference, optionally overlaying on the original survey image for scale alignment.

3. **Generate Zoomed-In Buildable Area Images**
   - Script: `tools/generate_zoomed_buildable_area.py`
   - Output: `data/output/buildable_area_zoomed.png`
   - Description: Focuses on the buildable area between easements, generating detailed images for planning and analysis.

# (Add further steps as the project evolves) 