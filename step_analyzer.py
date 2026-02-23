#!/usr/bin/env python3
"""
STEP File Analyzer - Cylindrical Face Counter

This script analyzes STEP files and counts cylindrical faces in 3D CAD models.
It uses OpenCASCADE libraries through the OCP (cadquery-ocp) binding.

Author: Final Year Project
Date: September 2025
"""

import sys
from pathlib import Path
import traceback


def safe_input(prompt: str):
    """Wrapper for input() that handles KeyboardInterrupt/EOFError.

    Returns the user's input string, or None if the user cancelled the prompt.
    """
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print()
        return None

def setup_imports():
    """Import OpenCASCADE libraries using OCP (pip package)."""
    try:
        from OCP.STEPControl import STEPControl_Reader
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.TopAbs import TopAbs_FACE
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopoDS import TopoDS  # Import TopoDS class for casting
        from OCP.BRep import BRep_Tool
        from OCP.GeomAdaptor import GeomAdaptor_Surface
        from OCP.GeomAbs import GeomAbs_Cylinder
        
        print("✅ Successfully imported OCP libraries")
        return {
            'STEPControl_Reader': STEPControl_Reader,
            'IFSelect_RetDone': IFSelect_RetDone,
            'TopAbs_FACE': TopAbs_FACE,
            'TopExp_Explorer': TopExp_Explorer,
            'TopoDS': TopoDS,
            'BRep_Tool': BRep_Tool,
            'GeomAdaptor_Surface': GeomAdaptor_Surface,
            'GeomAbs_Cylinder': GeomAbs_Cylinder,
            'binding': 'OCP'
        }
    except ImportError as e:
        print(f"❌ Failed to import OCP libraries: {e}")
        print("Make sure to install cadquery-ocp: pip install cadquery-ocp")
        print("Running in demo mode with mock data for testing purposes.")
        return None


def read_step_file(path: str, ocp_modules):
    """Read a STEP file and return the shape."""
    if not ocp_modules:
        print("📄 Using mock data for STEP file reading (demo mode)")
        return "MOCK_SHAPE"
        
    STEPControl_Reader = ocp_modules['STEPControl_Reader']
    IFSelect_RetDone = ocp_modules['IFSelect_RetDone']
    
    reader = STEPControl_Reader()
    status = reader.ReadFile(path)
    if status != IFSelect_RetDone:
        raise RuntimeError("STEP read failed")
    reader.TransferRoots()
    return reader.OneShape()


def count_cylindrical_faces(shape, ocp_modules) -> int:
    """Count cylindrical faces in the shape."""
    if not ocp_modules:
        print("🔍 Using mock data for cylindrical face counting (demo mode)")
        return 8  # Mock data for testing
        
    TopExp_Explorer = ocp_modules['TopExp_Explorer']
    TopAbs_FACE = ocp_modules['TopAbs_FACE']
    TopoDS = ocp_modules['TopoDS']
    BRep_Tool = ocp_modules['BRep_Tool']
    GeomAdaptor_Surface = ocp_modules['GeomAdaptor_Surface']
    GeomAbs_Cylinder = ocp_modules['GeomAbs_Cylinder']
    
    it = TopExp_Explorer(shape, TopAbs_FACE)
    count = 0
    
    while it.More():
        face = TopoDS.Face_s(it.Current())  # Use TopoDS.Face_s() for proper casting in OCP
        surface = BRep_Tool.Surface_s(face)  # Use Surface_s method in OCP
        adaptor = GeomAdaptor_Surface(surface)
        if adaptor.GetType() == GeomAbs_Cylinder:
            count += 1
        it.Next()
    
    return count


def get_model_description(path: str, ocp_modules) -> dict:
    """
    Extract detailed description and metadata from a STEP file.
    
    Returns a dictionary containing:
    - File information (name, size, creation date)
    - Model metadata (author, organization, description)
    - Geometry statistics (faces, edges, vertices, etc.)
    - Surface types breakdown
    """
    import os
    import datetime
    
    # Handle missing dependencies
    if not ocp_modules:
        print("📊 Using mock data for model description (demo mode)")
        file_path = Path(path) if path else Path("demo.step")
        return {
            "file_info": {
                "filename": file_path.name,
                "size_kb": round(os.path.getsize(file_path) / 1024, 2) if os.path.exists(file_path) else 250.45,
                "last_modified": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            "header_data": {"root_entities": 5},
            "geometry_stats": {
                "faces": 403,
                "edges": 1878,
                "vertices": 3756
            },
            "surface_types": {
                "Plane": 225,
                "Cylinder": 178,
                "Cone": 0,
                "Sphere": 0,
                "Torus": 0,
                "BezierSurface": 0,
                "BSplineSurface": 0,
                "Other": 0
            }
        }
    
    from OCP.STEPControl import STEPControl_Reader
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    from OCP.BRep import BRep_Tool
    from OCP.GeomAdaptor import GeomAdaptor_Surface
    from OCP.GeomAbs import (GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Sphere, 
                            GeomAbs_Cone, GeomAbs_Torus, GeomAbs_BezierSurface,
                            GeomAbs_BSplineSurface)
    
    # File information
    file_path = Path(path)
    file_info = {
        "filename": file_path.name,
        "size_kb": round(os.path.getsize(file_path) / 1024, 2),
        "last_modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Read STEP file
    reader = STEPControl_Reader()
    status = reader.ReadFile(str(file_path))
    if status != IFSelect_RetDone:
        raise RuntimeError("STEP read failed")
    
    # Extract header information
    header_data = {}
    try:
        # Get number of roots
        nb_roots = reader.NbRootsForTransfer()
        header_data["root_entities"] = nb_roots
        
        # Transfer roots
        reader.TransferRoots()
        shape = reader.OneShape()
        
        # Count geometry elements
        geometry_stats = {}
        geometry_stats["faces"] = count_explorer_items(shape, TopAbs_FACE, TopExp_Explorer)
        geometry_stats["edges"] = count_explorer_items(shape, TopAbs_EDGE, TopExp_Explorer)
        geometry_stats["vertices"] = count_explorer_items(shape, TopAbs_VERTEX, TopExp_Explorer)
        
        # Count surface types
        surface_types = count_surface_types(shape, TopoDS, BRep_Tool, GeomAdaptor_Surface)
        
    except Exception as e:
        return {
            "file_info": file_info,
            "error": str(e)
        }
    
    return {
        "file_info": file_info,
        "header_data": header_data,
        "geometry_stats": geometry_stats,
        "surface_types": surface_types
    }


def count_explorer_items(shape, item_type, TopExp_Explorer):
    """Helper function to count items of a specific type in a shape."""
    explorer = TopExp_Explorer(shape, item_type)
    count = 0
    while explorer.More():
        count += 1
        explorer.Next()
    return count


def count_surface_types(shape, TopoDS, BRep_Tool, GeomAdaptor_Surface):
    """Count different types of surfaces in the shape."""
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.GeomAbs import (GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Sphere, 
                            GeomAbs_Cone, GeomAbs_Torus, GeomAbs_BezierSurface,
                            GeomAbs_BSplineSurface)
    
    surface_types = {
        "Plane": 0,
        "Cylinder": 0,
        "Sphere": 0,
        "Cone": 0,
        "Torus": 0,
        "BezierSurface": 0,
        "BSplineSurface": 0,
        "Other": 0
    }
    
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current())
        surface = BRep_Tool.Surface_s(face)
        adaptor = GeomAdaptor_Surface(surface)
        
        surface_type = adaptor.GetType()
        
        if surface_type == GeomAbs_Plane:
            surface_types["Plane"] += 1
        elif surface_type == GeomAbs_Cylinder:
            surface_types["Cylinder"] += 1
        elif surface_type == GeomAbs_Sphere:
            surface_types["Sphere"] += 1
        elif surface_type == GeomAbs_Cone:
            surface_types["Cone"] += 1
        elif surface_type == GeomAbs_Torus:
            surface_types["Torus"] += 1
        elif surface_type == GeomAbs_BezierSurface:
            surface_types["BezierSurface"] += 1
        elif surface_type == GeomAbs_BSplineSurface:
            surface_types["BSplineSurface"] += 1
        else:
            surface_types["Other"] += 1
            
        explorer.Next()
    
    return surface_types


def analyze_machinability(shape, ocp_modules):
    """
    Analyze the machinability of a 3D model for different manufacturing processes.
    
    Returns a dictionary with machining process types as keys and their feasibility scores.
    """
    # Check if OCP modules are available
    if not ocp_modules:
        # Return mock data for testing when OCP is not available
        return {
            'dimensions': {
                'x_size': 100.0,
                'y_size': 75.0,
                'z_size': 50.0,
                'volume': 375000.0
            },
            'surface_types': {
                "Plane": 12,
                "Cylinder": 8,
                "Sphere": 2,
                "Cone": 1,
                "Torus": 0,
                "BezierSurface": 0,
                "BSplineSurface": 3,
                "Other": 0
            },
            'edge_types': {
                "Line": 24,
                "Circle": 16,
                "Other": 4
            },
            'machinability': {
                '3_axis_milling': {
                    'feasibility': 'High',
                    'score': 85,
                    'reasons': [
                        'High percentage of planar surfaces',
                        '8 cylindrical surfaces detected',
                        'Size suitable for standard milling machines'
                    ]
                },
                'turning': {
                    'feasibility': 'Medium',
                    'score': 45,
                    'reasons': [
                        'Moderate percentage of cylindrical surfaces',
                        'Predominance of circular edges',
                        '3 complex surfaces not suitable for turning'
                    ]
                },
                '3d_printing': {
                    'feasibility': 'High',
                    'score': 95,
                    'reasons': [
                        '3 complex surfaces well-suited for 3D printing',
                        'Size suitable for standard 3D printers',
                        '4 different surface types detected'
                    ]
                }
            }
        }
    from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    from OCP.BRep import BRep_Tool
    from OCP.GeomAdaptor import GeomAdaptor_Surface, GeomAdaptor_Curve
    from OCP.GeomAbs import (GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Sphere, 
                            GeomAbs_Cone, GeomAbs_Torus, GeomAbs_BezierSurface,
                            GeomAbs_BSplineSurface, GeomAbs_Line, GeomAbs_Circle)
    from OCP.BRepBndLib import BRepBndLib
    from OCP.Bnd import Bnd_Box
    import math
    
    # Get surface types
    surface_types = count_surface_types(shape, TopoDS, BRep_Tool, GeomAdaptor_Surface)
    
    # Get bounding box to determine overall size
    bbox = Bnd_Box()
    BRepBndLib.Add_s(shape, bbox)
    x_min, y_min, z_min, x_max, y_max, z_max = bbox.Get()
    
    # Calculate dimensions
    dimensions = {
        "x_size": x_max - x_min,
        "y_size": y_max - y_min,
        "z_size": z_max - z_min,
        "volume": (x_max - x_min) * (y_max - y_min) * (z_max - z_min)
    }
    
    # Count edge types
    edge_types = {
        "Line": 0,
        "Circle": 0,
        "Other": 0
    }
    
    edge_explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    while edge_explorer.More():
        edge = TopoDS.Edge_s(edge_explorer.Current())
        try:
            # Handle curve data safely - some curves might not unpack correctly
            curve_data = BRep_Tool.Curve_s(edge, 0, 1)
            if isinstance(curve_data, tuple):
                curve, first, last = curve_data
            else:
                # Handle case where curve is returned directly without unpacking
                curve = curve_data
                first, last = 0, 1
                
            if curve:
                adaptor = GeomAdaptor_Curve(curve)
                curve_type = adaptor.GetType()
                
                if curve_type == GeomAbs_Line:
                    edge_types["Line"] += 1
                elif curve_type == GeomAbs_Circle:
                    edge_types["Circle"] += 1
                else:
                    edge_types["Other"] += 1
        except Exception as e:
            print(f"Warning: Could not process edge: {str(e)}")
                
        edge_explorer.Next()
    
    # Analyze machinability for different processes
    machinability = {}
    
    # 3-Axis Milling
    milling_score = 0
    milling_reasons = []
    
    # Milling favors planar and cylindrical surfaces
    planar_ratio = surface_types["Plane"] / sum(surface_types.values()) if sum(surface_types.values()) > 0 else 0
    if planar_ratio > 0.5:
        milling_score += 30
        milling_reasons.append("High percentage of planar surfaces")
    elif planar_ratio > 0.3:
        milling_score += 20
        milling_reasons.append("Moderate percentage of planar surfaces")
    
    # Cylindrical features are good for milling
    if surface_types["Cylinder"] > 0:
        milling_score += min(20, surface_types["Cylinder"] / 10)
        milling_reasons.append(f"{surface_types['Cylinder']} cylindrical surfaces detected")
    
    # Complex surfaces reduce machinability
    complex_surfaces = surface_types["BezierSurface"] + surface_types["BSplineSurface"]
    if complex_surfaces > 0:
        penalty = min(30, complex_surfaces * 2)
        milling_score -= penalty
        milling_reasons.append(f"{complex_surfaces} complex surfaces may require 5-axis milling")
    
    # Size considerations
    if max(dimensions["x_size"], dimensions["y_size"], dimensions["z_size"]) < 500:
        milling_score += 10
        milling_reasons.append("Size suitable for standard milling machines")
    
    # Normalize score
    milling_score = max(0, min(100, milling_score + 40))  # Base score of 40
    
    machinability["3_axis_milling"] = {
        "score": milling_score,
        "feasibility": "High" if milling_score > 70 else "Medium" if milling_score > 40 else "Low",
        "reasons": milling_reasons
    }
    
    # Turning (Lathe) - IMPROVED scoring for rotational parts like bottles
    turning_score = 0
    turning_reasons = []
    
    # Turning requires rotational symmetry - check for cylindrical dominance
    cylindrical_ratio = surface_types["Cylinder"] / sum(surface_types.values()) if sum(surface_types.values()) > 0 else 0
    if cylindrical_ratio > 0.5:
        turning_score += 50
        turning_reasons.append("High percentage of cylindrical surfaces suggests rotational symmetry")
    elif cylindrical_ratio > 0.2:  # LOWERED threshold from 0.3 to 0.2 (bottles ~30-40%)
        turning_score += 30  # INCREASED from 25
        turning_reasons.append("Moderate percentage of cylindrical surfaces (suitable for turning)")
    elif surface_types["Cylinder"] > 3:  # NEW: Check absolute count for small parts
        turning_score += 25
        turning_reasons.append(f"{surface_types['Cylinder']} cylindrical surfaces detected - rotational part")
    
    # Circular edges are STRONG indicators for turning (bottles have many)
    if edge_types["Circle"] > 0:
        # IMPROVED: Give credit for circular edges, not just dominance
        edge_credit = min(35, edge_types["Circle"] * 3)
        turning_score += edge_credit
        turning_reasons.append(f"{edge_types['Circle']} circular edges detected (typical of rotational/bottle parts)")
    
    # Complex surfaces are difficult for turning - but less penalty for small details
    # (bottles have ribs, threads - still turnable)
    if complex_surfaces > 0:
        penalty = min(20, complex_surfaces * 1.5)  # REDUCED from complex*3 to *1.5
        turning_score -= penalty
        if complex_surfaces <= 3:
            turning_reasons.append(f"{complex_surfaces} minor complex surfaces (fine details turnable)")
        else:
            turning_reasons.append(f"{complex_surfaces} complex surfaces (moderate turning difficulty)")
    
    # Aspect ratio check - more lenient for rotational parts
    # Bottles aren't always long vs diameter, check if reasonable proportions
    length = dimensions["z_size"]
    max_diameter = max(dimensions["x_size"], dimensions["y_size"])
    
    if length > 0 and max_diameter > 0:
        aspect_ratio = length / max_diameter
        if aspect_ratio > 0.5:  # RELAXED: was > 2.0, now accepts wider range
            turning_score += 20
            turning_reasons.append(f"Length to diameter ratio {aspect_ratio:.1f}:1 suitable for turning")
    
    # NEW: Add points for rotational geometry indicators
    # Parts with few planes are likely rotational (bottles, shafts, etc.)
    plane_count = surface_types.get("Plane", 0)
    if plane_count <= 3:  # Few planes = rotational part
        turning_score += 15
        turning_reasons.append("Rotational geometry detected (excellent turning candidate)")
    
    # INCREASED base score from 20 to 35 (recognition that turning is viable for many parts)
    turning_score = max(0, min(100, turning_score + 35))
    
    machinability["turning"] = {
        "score": turning_score,
        "feasibility": "High" if turning_score > 70 else "Medium" if turning_score > 40 else "Low",
        "reasons": turning_reasons
    }
    
    # 3D Printing
    printing_score = 0
    printing_reasons = []
    
    # 3D printing handles complex geometries well
    if complex_surfaces > 0:
        printing_score += min(40, complex_surfaces * 2)
        printing_reasons.append(f"{complex_surfaces} complex surfaces well-suited for 3D printing")
    
    # Size considerations
    if max(dimensions["x_size"], dimensions["y_size"], dimensions["z_size"]) < 250:
        printing_score += 30
        printing_reasons.append("Size suitable for standard 3D printers")
    
    # More diverse surface types favor 3D printing
    unique_surfaces = sum(1 for count in surface_types.values() if count > 0)
    if unique_surfaces >= 4:
        printing_score += 20
        printing_reasons.append(f"{unique_surfaces} different surface types detected")
    
    # Normalize score
    printing_score = max(0, min(100, printing_score + 30))  # Base score of 30
    
    machinability["3d_printing"] = {
        "score": printing_score,
        "feasibility": "High" if printing_score > 70 else "Medium" if printing_score > 40 else "Low",
        "reasons": printing_reasons
    }
    
    # Determine recommended manufacturing process
    scores = {
        "3_axis_milling": machinability["3_axis_milling"]["score"],
        "turning": machinability["turning"]["score"],
        "3d_printing": machinability["3d_printing"]["score"]
    }
    recommended_process = max(scores, key=scores.get)
    
    # Generate machining requirements based on the recommended process
    machining_requirements = []
    
    if recommended_process == "3_axis_milling":
        machining_requirements = [
            f"Workpiece material: Select based on hardness and machinability",
            f"Machine: 3-axis CNC mill with minimum work envelope of {dimensions['x_size']:.1f} x {dimensions['y_size']:.1f} x {dimensions['z_size']:.1f} mm",
            f"Tooling: End mills for flat surfaces, ball nose for contoured surfaces",
            f"Fixturing: Design fixtures to secure part during machining",
            f"Finishing: Plan for {surface_types.get('Plane', 0)} flat surfaces and {surface_types.get('Cylinder', 0) + surface_types.get('Cone', 0)} curved surfaces"
        ]
    elif recommended_process == "turning":
        machining_requirements = [
            f"Workpiece material: Round stock with diameter ≥ {max(dimensions['y_size'], dimensions['z_size']):.1f} mm",
            f"Machine: CNC lathe with minimum length capacity of {dimensions['x_size']:.1f} mm",
            f"Tooling: External turning tools, boring bars for internal features",
            f"Fixturing: Standard chuck with appropriate jaws",
            f"Operations: Facing, turning, and potentially milling for non-axisymmetric features"
        ]
    else:  # 3D printing
        machining_requirements = [
            f"Printer type: FDM for simple parts, SLA/SLS for complex geometries",
            f"Build volume: Minimum {dimensions['x_size']:.1f} x {dimensions['y_size']:.1f} x {dimensions['z_size']:.1f} mm",
            f"Material: Select based on mechanical requirements",
            f"Layer height: 0.1-0.2mm for balance of detail and print time",
            f"Post-processing: Support removal and surface finishing"
        ]
    
    return {
        "machinability": machinability,
        "surface_types": surface_types,
        "edge_types": edge_types,
        "dimensions": dimensions,
        "recommended_process": recommended_process,
        "machining_requirements": machining_requirements
    }


def upload_step_file() -> str:
    """Upload a STEP file and save it to the current directory."""
    import os
    import shutil
    
    print("📤 Please enter the full path to the STEP file you want to upload:")
    print("   (Example: C:\\Users\\YourName\\Downloads\\example.step)")
    
    file_path_raw = safe_input("File path: ")
    if file_path_raw is None:
        print("❌ Upload cancelled by user.")
        return None
    file_path = file_path_raw.strip('"')  # Remove quotes if user included them
    
    if not file_path or not os.path.exists(file_path):
        print("❌ File not found. Please check the path and try again.")
        return None
    
    # Check if it's a STEP file
    if not Path(file_path).suffix.lower() in {".stp", ".step"}:
        print("❌ The selected file is not a STEP file (.stp or .step).")
        return None
    
    # Copy the file to the current directory
    dest_path = Path(".") / Path(file_path).name
    try:
        shutil.copy2(file_path, dest_path)
        print(f"✅ File uploaded successfully: {dest_path}")
        return str(dest_path)
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None


def find_step_file(path: str = None) -> str:
    """Find a STEP file to analyze, with user input if needed."""
    # If a valid path was provided as an argument, use it
    if path and Path(path).suffix.lower() in {".stp", ".step"} and Path(path).exists():
        return path
    
    # Look for STEP files in the current directory
    current_dir = Path(".")
    step_files = list(current_dir.glob("*.step")) + list(current_dir.glob("*.stp"))
    
    if step_files:
        # If STEP files are found, list them and ask the user to choose
        print("\n📁 Available STEP files:")
        for i, file in enumerate(step_files, 1):
            print(f"  {i}. {file}")
        
        # Ask user to select a file or upload a new one
        while True:
            try:
                print("\n🔍 Options:")
                print("  • Enter a number to select a file from the list")
                print("  • Type 'upload' to upload a new file")
                print("  • Type a custom file path")
                choice = safe_input("\nYour choice: ")
                if choice is None:
                    print("❌ Selection cancelled by user.")
                    return None

                # Check if user wants to upload a file
                if choice.lower() == 'upload':
                    uploaded_file = upload_step_file()
                    if uploaded_file:
                        return uploaded_file
                    else:
                        continue

                # Check if the input is a number (file selection from list)
                elif choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(step_files):
                        step_path = str(step_files[index])
                        print(f"✅ Selected: {step_path}")
                        return step_path
                    else:
                        print(f"❌ Invalid selection. Please enter a number between 1 and {len(step_files)}.")

                # Check if the input is a custom file path
                elif Path(choice).exists():
                    if Path(choice).suffix.lower() in {".stp", ".step"}:
                        print(f"✅ Selected custom file: {choice}")
                        return choice
                    else:
                        print("❌ The selected file is not a STEP file (.stp or .step).")
                else:
                    print("❌ File not found. Please enter a valid number, 'upload', or a file path.")

            except ValueError:
                print("❌ Invalid input. Please enter a number, 'upload', or a valid file path.")
    else:
        # No STEP files found, ask for a custom path or upload
        print("❌ No STEP files found in current directory.")
        available_files = [f.name for f in current_dir.iterdir() if f.is_file()]
        print("Available files:", available_files)
        
        while True:
            print("\n🔍 Options:")
            print("  • Type 'upload' to upload a new file")
            print("  • Enter a path to an existing STEP file")
            choice = safe_input("\nYour choice: ")
            if choice is None:
                print("❌ Selection cancelled by user.")
                return None
            # Check if user wants to upload a file
            if choice.lower() == 'upload':
                uploaded_file = upload_step_file()
                if uploaded_file:
                    return uploaded_file
                else:
                    continue

            # Check if the input is a custom file path
            elif Path(choice).exists():
                if Path(choice).suffix.lower() in {".stp", ".step"}:
                    print(f"✅ Selected custom file: {choice}")
                    return choice
                else:
                    print("❌ The selected file is not a STEP file (.stp or .step).")
            else:
                print("❌ File not found. Please enter 'upload' or a valid file path.")


def analyze_step_file(file_path: str = None):
    """Main function to analyze a STEP file and count cylindrical faces."""
    print("🔧 STEP File Analyzer - Cylindrical Face Counter")
    print("=" * 50)
    
    try:
        # Setup imports
        ocp_modules = setup_imports()
        if ocp_modules is None:
            print("⚠️ Running in DEMO MODE with mock data (OCP libraries not available)")
        else:
            print(f"✅ Successfully imported OCP libraries")
            print(f"🔗 Using OpenCASCADE binding: OCP")
        
        # Find STEP file
        step_file_path = find_step_file(file_path)
        if not step_file_path:
            print("❌ No STEP file selected. Exiting.")
            return {'success': False, 'error': 'No STEP file selected'}
        
        # Read STEP file
        print(f"📖 Reading STEP file: {step_file_path}")
        shape = read_step_file(step_file_path, ocp_modules)
        
        # Analyze cylindrical faces
        print("🔍 Analyzing geometry...")
        cylinder_count = count_cylindrical_faces(shape, ocp_modules)
        
        # Get detailed model description
        print("\n📋 Extracting model description and metadata...")
        model_info = get_model_description(step_file_path, ocp_modules)
        
        # Analyze machinability
        print("\n🔧 Analyzing machinability for different manufacturing processes...")
        machinability_info = analyze_machinability(shape, ocp_modules)
        
        # Display results
        print("\n" + "=" * 50)
        print("📊 ANALYSIS RESULTS")
        print("=" * 50)
        print(f"📄 STEP File: {step_file_path}")
        
        # Print file information
        print("\n📁 FILE INFORMATION:")
        print(f"  • Filename: {model_info['file_info']['filename']}")
        print(f"  • Size: {model_info['file_info']['size_kb']} KB")
        print(f"  • Last Modified: {model_info['file_info']['last_modified']}")
        
        # Print geometry statistics
        print("\n📐 GEOMETRY STATISTICS:")
        print(f"  • Faces: {model_info['geometry_stats']['faces']}")
        print(f"  • Edges: {model_info['geometry_stats']['edges']}")
        print(f"  • Vertices: {model_info['geometry_stats']['vertices']}")
        
        # Print surface types
        print("\n🔍 SURFACE TYPES:")
        for surface_type, count in model_info['surface_types'].items():
            if count > 0:
                print(f"  • {surface_type}: {count}")
        
        # Print dimensions
        print("\n📏 DIMENSIONS:")
        print(f"  • X: {machinability_info['dimensions']['x_size']:.2f} mm")
        print(f"  • Y: {machinability_info['dimensions']['y_size']:.2f} mm")
        print(f"  • Z: {machinability_info['dimensions']['z_size']:.2f} mm")
        print(f"  • Volume: {machinability_info['dimensions']['volume']:.2f} mm³")
        
        # Print machinability analysis
        print("\n🏭 MACHINABILITY ANALYSIS:")
        
        # 3-Axis Milling
        milling = machinability_info['machinability']['3_axis_milling']
        print(f"\n  3-AXIS MILLING:")
        print(f"  • Feasibility: {milling['feasibility']} (Score: {milling['score']}/100)")
        print(f"  • Reasons:")
        for reason in milling['reasons']:
            print(f"    - {reason}")
        
        # Turning
        turning = machinability_info['machinability']['turning']
        print(f"\n  TURNING (LATHE):")
        print(f"  • Feasibility: {turning['feasibility']} (Score: {turning['score']}/100)")
        print(f"  • Reasons:")
        for reason in turning['reasons']:
            print(f"    - {reason}")
        
        # 3D Printing
        printing = machinability_info['machinability']['3d_printing']
        print(f"\n  3D PRINTING:")
        print(f"  • Feasibility: {printing['feasibility']} (Score: {printing['score']}/100)")
        print(f"  • Reasons:")
        for reason in printing['reasons']:
            print(f"    - {reason}")
        
        # Recommended manufacturing process
        processes = machinability_info['machinability']
        best_process = max(processes.items(), key=lambda x: x[1]['score'])
        print(f"\n✅ RECOMMENDED MANUFACTURING PROCESS: {best_process[0].replace('_', ' ').upper()}")
        
        # Print machining requirements
        print("\n📋 MACHINING REQUIREMENTS:")
        if 'machining_requirements' in machinability_info:
            for requirement in machinability_info['machining_requirements']:
                print(f"  • {requirement}")
        else:
            print("  • Material selection based on part requirements")
            print("  • Tooling selection based on geometry features")
            print("  • Fixturing design for optimal part stability")
            print("  • Finishing operations based on surface requirements")
            
        print(f"\n🔵 Cylindrical Faces: {cylinder_count}")
        print("✅ Analysis completed successfully!")
        
        return {
            'file_path': step_file_path,
            'cylindrical_faces': cylinder_count,
            'model_info': model_info,
            'machinability': machinability_info['machinability'],
            'success': True
        }
        
    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
        return {'success': False, 'error': str(e)}
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def print_system_info():
    """Print system and environment information."""
    import os
    print("🖥️  SYSTEM INFORMATION")
    print("=" * 30)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()


def show_help():
    """Display help message with available options."""
    print("""
STEP File Analyzer - Enhanced with AI & CAPP
=============================================

Usage: python step_analyzer.py [OPTIONS] [STEP_FILE]

OPTIONS:
  --help              Show this help message
  --ai-analysis       Analyze with AI recommendations (requires Ollama)
  --cad-chat          Interactive CAD chatbot (requires Ollama)
  --capp-turning      Generate CAPP turning process plan (if machinable)
  --model <name>      Specify Ollama model to use (default: phi)
  --save              Save AI analysis/plan report to JSON file

EXAMPLES:
  # Basic analysis
  python step_analyzer.py
  python step_analyzer.py model.step

  # AI-enhanced analysis
  python step_analyzer.py model.step --ai-analysis
  python step_analyzer.py model.step --ai-analysis --save

  # Interactive CAD chatbot
  python step_analyzer.py model.step --cad-chat
  python step_analyzer.py model.step --cad-chat --model phi

  # Generate CAPP turning process plan (NEW!)
  python step_analyzer.py model.step --capp-turning
  python step_analyzer.py model.step --capp-turning --ai --save

REQUIREMENTS:
  - For basic analysis: cadquery-ocp
  - For AI features: Ollama must be installed and running on localhost:11434
  - Download Ollama: https://ollama.ai
  - Pull models: ollama pull phi  (or ollama pull llama2, etc)

NOTE:
  CAPP turning planner will only generate a process plan if the part
  has a turning machinability score >= 40/100. Otherwise it recommends
  alternative manufacturing methods.
""")


if __name__ == "__main__":
    print_system_info()
    
    # Parse command line arguments
    file_path = None
    ai_analysis = False
    cad_chat = False
    capp_turning = False
    model = "phi"
    save_report = False
    
    # Process arguments
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg == "--help" or arg == "-h":
            show_help()
            sys.exit(0)
        
        elif arg == "--ai-analysis":
            ai_analysis = True
        
        elif arg == "--cad-chat":
            cad_chat = True
        
        elif arg == "--capp-turning":
            capp_turning = True
        
        elif arg == "--save":
            save_report = True
        
        elif arg == "--model" and i + 1 < len(args):
            model = args[i + 1]
            i += 1
        
        elif not arg.startswith("--"):
            file_path = arg
        
        i += 1
    
    # Determine which mode to run
    if cad_chat:
        # Interactive CAD chatbot mode
        try:
            from cad_chatbot import interactive_cad_chat
            
            if not file_path:
                step_result = analyze_step_file(None)
                if step_result.get('success'):
                    file_path = step_result.get('file_path')
            
            if file_path:
                interactive_cad_chat(file_path, model=model)
        except ImportError:
            print("❌ CAD chatbot module not found. Please ensure cad_chatbot.py is in the same directory.")
            sys.exit(1)
    
    elif ai_analysis:
        # AI analysis mode
        try:
            from cad_ai_analyzer import analyze_with_ai
            
            if not file_path:
                step_result = analyze_step_file(None)
                if step_result.get('success'):
                    file_path = step_result.get('file_path')
            
            if file_path:
                result = analyze_with_ai(file_path, model=model, save_report=save_report)
                if result.get('success'):
                    print(result.get('summary'))
                else:
                    print(f"❌ Analysis failed: {result.get('error')}")
                    sys.exit(1)
        except ImportError:
            print("❌ AI analyzer module not found. Please ensure cad_ai_analyzer.py is in the same directory.")
            sys.exit(1)
    
    elif capp_turning:
        # CAPP Turning Process Planner mode
        try:
            from capp_turning_planner import generate_turning_plan
            
            if not file_path:
                step_result = analyze_step_file(None)
                if step_result.get('success'):
                    file_path = step_result.get('file_path')
            
            if file_path:
                with_ai = "--ai" in sys.argv
                result = generate_turning_plan(file_path, model=model, with_ai=with_ai, save_json=save_report)
                if result.get('success'):
                    print("\n" + result.get('report'))
                else:
                    print(f"\n❌ {result.get('error')}")
                    print(f"   Turning machinability score: {result.get('turning_score')}/100")
                    if result.get('recommendation'):
                        print(f"   💡 {result.get('recommendation')}")
                    sys.exit(1)
        except ImportError:
            print("❌ CAPP module not found. Please ensure capp_turning_planner.py is in the same directory.")
            sys.exit(1)
    
    else:
        # Standard analysis mode
        result = analyze_step_file(file_path)
        
        # Keep console window open for user to see results
        print("\n" + "="*60)
        if result['success']:
            print("✅ Analysis completed successfully!")
            print("\n💡 TIPS:")
            print("  • Use --ai-analysis flag for AI-powered recommendations")
            print("  • Use --cad-chat flag to ask questions about your model")
            print("  • Use --capp-turning flag for turning process planning")
            print(f"  • Example: python step_analyzer.py {file_path} --ai-analysis")
        else:
            print("❌ Analysis failed. Please check the error messages above.")
        
        print("\nPress Enter to close this window...")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            # Handle cases where input might not be available
            pass