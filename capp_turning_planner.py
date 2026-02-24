"""Computer-Aided Process Planner (CAPP) for Turning Operations.

This module generates detailed turning process plans for STEP files that are
suitable for lathe machining. It checks machinability and creates a complete
turning process plan with tool paths, feeds, speeds, and operations.

Author: CAPP System
Date: November 2025

Environment Variables:
- OLLAMA_AI_TIMEOUT: Timeout for AI recommendation queries in seconds (default: 120)
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime

from step_analyzer import analyze_step_file
from chat_ollama import query_ollama, OllamaError, set_model

# Configuration from environment variables
OLLAMA_AI_TIMEOUT = int(os.getenv("OLLAMA_AI_TIMEOUT", "120"))

DEFAULT_MATERIAL_PROFILE = "Aluminum 6061-T6"
DEFAULT_MACHINE_PROFILE = "2-axis CNC turning center (ST-20 class)"

MATERIAL_SPEED_FACTORS = {
    "Aluminum 6061-T6": 1.7,
    "Mild Steel (AISI 1018/1020)": 1.0,
    "Stainless Steel 304": 0.65,
}

MACHINE_RPM_LIMITS = {
    "2-axis CNC turning center (ST-20 class)": 4000,
    "Toolroom CNC lathe (TL-1 class)": 1800,
    "High-speed CNC turning center (ST-10 class)": 6000,
}


class TurningProcessPlan:
    """Represents a turning process plan for a STEP file."""
    
    def __init__(
        self,
        analysis: dict,
        model: str = "phi",
        material_profile: str = DEFAULT_MATERIAL_PROFILE,
        machine_profile: str = DEFAULT_MACHINE_PROFILE,
    ):
        """Initialize the process plan with analysis data.
        
        Args:
            analysis: The analysis dict from analyze_step_file.
            model: LLM model to use for AI recommendations.
        """
        self.analysis = analysis
        self.model = model
        self.material_profile = material_profile
        self.machine_profile = machine_profile
        self.turning_score = self._get_turning_score()
        self.is_machinable = self.turning_score >= 40  # Minimum threshold
        self.operations = []
        self.tools = []
        self.ai_recommendations = {}
    
    def _get_turning_score(self) -> int:
        """Extract turning machinability score from analysis.
        
        Returns:
            The turning score (0-100).
        """
        machinability = self.analysis.get("machinability", {})
        turning_data = machinability.get("3_axis_milling", {})  # Using milling as fallback
        
        # Try to get actual turning score if available
        if "turning" in machinability:
            turning_data = machinability["turning"]
        
        return turning_data.get("score", 0)
    
    def _format_dimensions(self) -> Dict[str, float]:
        """Extract and format part dimensions.
        
        Returns:
            Dictionary with diameter, length, and other dimensions.
        """
        machinability = self.analysis.get("machinability", {})
        dimensions = machinability.get("dimensions", {})
        
        # Extract dimensions with defaults
        x_size = max(dimensions.get("x_size", 20), 0.1)
        y_size = max(dimensions.get("y_size", 20), 0.1)
        z_size = max(dimensions.get("z_size", 50), 0.1)
        
        return {
            "diameter": max(x_size, y_size),
            "length": z_size,
            "volume": max(dimensions.get("volume", 0), 0),
            "x_size": x_size,
            "y_size": y_size,
            "z_size": z_size,
        }
    
    def _get_surface_info(self) -> Dict[str, int]:
        """Extract surface type information.
        
        Returns:
            Dictionary with surface type counts.
        """
        model_info = self.analysis.get("model_info", {})
        return model_info.get("surface_types", {})
    
    def generate_operations(self) -> List[Dict]:
        """Generate turning operations sequence.
        
        Returns:
            List of operation dictionaries.
        """
        if not self.is_machinable:
            return []
        
        dimensions = self._format_dimensions()
        diameter = dimensions["diameter"]
        length = dimensions["length"]
        
        operations = []
        
        # Operation 1: Face & Center
        operations.append({
            "operation_id": 1,
            "name": "Face & Center",
            "description": "Face the part and create center marks for alignment",
            "type": "facing",
            "tool": "Facing insert (CNMG)",
            "spindle_speed": self._calculate_spindle_speed(diameter, "facing"),
            "feed_rate": 0.15,  # mm/rev
            "depth_of_cut": 1.0,  # mm
            "coolant": "flood",
            "estimated_time": 2.0  # minutes
        })
        
        # Operation 2: Rough turning (if diameter > 20mm)
        if diameter > 20:
            operations.append({
                "operation_id": 2,
                "name": "Rough Turning",
                "description": "Remove material from outer diameter",
                "type": "turning",
                "tool": "Turning insert (VNMG)",
                "spindle_speed": self._calculate_spindle_speed(diameter * 0.8, "rough"),
                "feed_rate": 0.20,  # mm/rev
                "depth_of_cut": 2.0,  # mm
                "coolant": "flood",
                "estimated_time": self._estimate_turning_time(diameter, length, 2.0, 0.20)
            })
        
        # Operation 3: Finish turning
        operations.append({
            "operation_id": 3,
            "name": "Finish Turning",
            "description": "Achieve final diameter and surface finish",
            "type": "turning",
            "tool": "Finishing insert (VNMG, R0.4)",
            "spindle_speed": self._calculate_spindle_speed(diameter, "finish"),
            "feed_rate": 0.10,  # mm/rev
            "depth_of_cut": 0.5,  # mm
            "coolant": "flood",
            "estimated_time": self._estimate_turning_time(diameter, length, 0.5, 0.10)
        })
        
        # Operation 4: Boring (if part has holes/internal features)
        cylindrical_faces = self.analysis.get("cylindrical_faces", 0)
        if cylindrical_faces > 2:
            operations.append({
                "operation_id": 4,
                "name": "Boring",
                "description": "Machine internal cylindrical features",
                "type": "boring",
                "tool": "Boring bar with insert",
                "spindle_speed": self._calculate_spindle_speed(diameter * 0.5, "boring"),
                "feed_rate": 0.12,  # mm/rev
                "depth_of_cut": 1.0,  # mm
                "coolant": "flood",
                "estimated_time": 3.0
            })
        
        # Operation 5: Threading (if applicable)
        if length > diameter * 1.5:  # Long part
            operations.append({
                "operation_id": 5,
                "name": "Threading",
                "description": "Cut external threads",
                "type": "threading",
                "tool": "Threading insert (60° diamond)",
                "spindle_speed": self._calculate_spindle_speed(diameter, "threading") // 2,
                "feed_rate": 0.5,  # mm/rev (pitch)
                "depth_of_cut": 0.5,  # mm
                "coolant": "light",
                "estimated_time": 2.5,
                "thread_spec": "M10 x 1.5 (example)"
            })
        
        # Operation 6: Grooving
        operations.append({
            "operation_id": 6,
            "name": "Grooving",
            "description": "Cut grooves for stress relief",
            "type": "grooving",
            "tool": "Grooving insert",
            "spindle_speed": self._calculate_spindle_speed(diameter * 0.7, "grooving"),
            "feed_rate": 0.15,  # mm/rev
            "depth_of_cut": 0.8,  # mm
            "coolant": "flood",
            "estimated_time": 1.5
        })
        
        # Operation 7: Parting off
        operations.append({
            "operation_id": 7,
            "name": "Parting Off",
            "description": "Separate finished part from stock",
            "type": "parting",
            "tool": "Parting blade",
            "spindle_speed": self._calculate_spindle_speed(diameter * 0.9, "parting"),
            "feed_rate": 0.08,  # mm/rev
            "depth_of_cut": diameter * 0.5,
            "coolant": "light",
            "estimated_time": 1.0
        })
        
        self.operations = operations
        return operations
    
    def _calculate_spindle_speed(self, diameter_mm: float, operation_type: str) -> int:
        """Calculate spindle speed based on diameter and operation.
        
        Uses the formula: RPM = (1000 * SFM) / (π * diameter)
        where SFM is Surface Feet per Minute
        
        Args:
            diameter_mm: Part diameter in mm.
            operation_type: Type of operation (rough, finish, etc).
        
        Returns:
            Spindle speed in RPM.
        """
        # Handle zero or invalid diameter
        if diameter_mm <= 0:
            diameter_mm = 20  # Use default diameter of 20mm if invalid
        
        # Surface speeds for different materials/operations (SFM)
        surface_speeds = {
            "facing": 250,      # Steel
            "rough": 200,
            "finish": 300,
            "boring": 180,
            "threading": 100,
            "grooving": 150,
            "parting": 120,
        }
        
        material_factor = MATERIAL_SPEED_FACTORS.get(self.material_profile, 1.0)
        sfm = surface_speeds.get(operation_type, 200) * material_factor
        diameter_inches = diameter_mm / 25.4
        
        # Prevent division by zero
        if diameter_inches <= 0:
            diameter_inches = 0.8  # Default ~20mm
        
        # RPM = (SFM * 12) / (π * D)
        rpm = int((sfm * 12) / (3.14159 * diameter_inches))
        
        # Clamp to selected machine limits.
        machine_rpm_limit = MACHINE_RPM_LIMITS.get(self.machine_profile, 4000)
        rpm = max(100, min(machine_rpm_limit, rpm))
        
        return rpm
    
    def _estimate_turning_time(self, diameter_mm: float, length_mm: float,
                               depth_mm: float, feed_mm_rev: float) -> float:
        """Estimate cutting time for turning operation.
        
        Args:
            diameter_mm: Part diameter.
            length_mm: Part length.
            depth_mm: Depth of cut.
            feed_mm_rev: Feed rate in mm/rev.
        
        Returns:
            Estimated time in minutes.
        """
        if feed_mm_rev == 0 or length_mm == 0:
            return 0
        
        # Number of passes = radius / depth_of_cut
        passes = max(int((diameter_mm / 2) / depth_mm), 1)
        
        # Spindle speed in RPM
        spindle_speed = self._calculate_spindle_speed(diameter_mm, "rough")
        
        # Material removal rate (mm³/min) = spindle_speed * feed * depth
        material_removal_rate = spindle_speed * feed_mm_rev * depth_mm
        
        # Volume to remove per pass = length * feed * depth (approximation)
        # Time per pass (minutes) = length / (feed_rate * spindle_speed) * passes
        if spindle_speed > 0:
            time_per_pass = length_mm / (spindle_speed * feed_mm_rev / 1000)  # Convert feed from mm/rev to m/min equivalent
        else:
            time_per_pass = 5.0  # Default 5 minutes per pass
        
        # Total time including tool changes (0.5 min per change)
        total_time = (time_per_pass * passes) + (max(passes - 1, 0) * 0.5)
        
        # Cap unrealistic values
        if total_time > 100:
            total_time = 10.0  # Cap at 10 minutes for small parts
        
        return round(total_time, 1)
    
    def generate_tool_list(self) -> List[Dict]:
        """Generate list of required turning tools.
        
        Returns:
            List of tool specifications.
        """
        tools = [
            {
                "tool_id": 1,
                "name": "Facing Insert",
                "type": "CNMG 432 M0804",
                "material": "Carbide",
                "coating": "TiAlN",
                "description": "For facing and end turning"
            },
            {
                "tool_id": 2,
                "name": "Turning Insert",
                "type": "VNMG 431",
                "material": "Carbide",
                "coating": "TiAlN",
                "description": "For rough and finish turning"
            },
            {
                "tool_id": 3,
                "name": "Boring Insert",
                "type": "VNMG 331",
                "material": "Carbide",
                "coating": "TiAlN",
                "description": "For boring internal diameters"
            },
            {
                "tool_id": 4,
                "name": "Threading Insert",
                "type": "TT09T304",
                "material": "Carbide",
                "coating": "TiN",
                "description": "For external threading"
            },
            {
                "tool_id": 5,
                "name": "Grooving Insert",
                "type": "MGMN 300-M",
                "material": "Carbide",
                "coating": "TiAlN",
                "description": "For grooving operations"
            },
            {
                "tool_id": 6,
                "name": "Parting Blade",
                "type": "MGHR-3-M",
                "material": "Carbide",
                "coating": "TiN",
                "description": "For parting off finished parts"
            }
        ]
        
        self.tools = tools
        return tools
    
    def generate_ai_recommendations(self, timeout: Optional[int] = None) -> Dict:
        """Generate AI-powered optimization recommendations.
        
        Args:
            timeout: Request timeout in seconds. If None, uses OLLAMA_AI_TIMEOUT env var (default 120s).
                     Use larger values (180s+) for slower models or slower hardware.
        
        Returns:
            Dictionary with AI recommendations.
        """
        if timeout is None:
            timeout = OLLAMA_AI_TIMEOUT
        
        if not self.is_machinable:
            return {"error": "Part not suitable for turning"}
        
        dimensions = self._format_dimensions()
        operations_summary = "\n".join([
            f"  - {op['name']}: {op['description']}"
            for op in self.operations[:3]
        ])
        
        recommendations = {}
        
        print(f"  ⏳ Generating process optimization recommendations (timeout: {timeout}s)...")
        try:
            prompt = f"""Review this turning process plan for a lathe operation:

Part Specifications:
  - Diameter: {dimensions['diameter']:.1f} mm
  - Length: {dimensions['length']:.1f} mm
  - Cylindrical faces: {self.analysis.get('cylindrical_faces', 0)}
  - Machinability score: {self.turning_score}/100
  - Workpiece material: {self.material_profile}
  - Lathe machine profile: {self.machine_profile}

Planned Operations:
{operations_summary}

Suggest optimizations for:
1. Tool selection improvements
2. Speed/feed optimization
3. Coolant strategy
4. Setup considerations
5. Quality improvements"""
            
            response = query_ollama(prompt, model=self.model, timeout=timeout)
            # Ensure response is not empty
            if response and response.strip():
                recommendations["optimizations"] = response
            else:
                recommendations["optimizations"] = "Ollama returned empty response. Check Ollama connection and try again."
        except OllamaError as e:
            recommendations["optimizations"] = f"Error: {e}"
        
        print("  ✅ AI recommendations generated")
        self.ai_recommendations = recommendations
        return recommendations
    
    def generate_report(self) -> str:
        """Generate a formatted turning process plan report.
        
        Returns:
            Formatted report string.
        """
        report = []
        report.append("═" * 80)
        report.append("TURNING PROCESS PLAN (CAPP SYSTEM)")
        report.append("═" * 80)
        report.append("")
        
        # Header
        report.append("PART INFORMATION:")
        report.append(f"  File: {self.analysis.get('file_path', 'Unknown')}")
        report.append(f"  Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"  Material Profile: {self.material_profile}")
        report.append(f"  Machine Profile: {self.machine_profile}")
        report.append("")
        
        # Machinability
        report.append("TURNING MACHINABILITY:")
        report.append(f"  Score: {self.turning_score}/100")
        report.append(f"  Suitable for Turning: {'YES ✓' if self.is_machinable else 'NO ✗'}")
        report.append("")
        
        if not self.is_machinable:
            report.append("❌ This part is NOT suitable for turning operations.")
            report.append("   Consider alternative manufacturing methods.")
            return "\n".join(report)
        
        # Dimensions
        dimensions = self._format_dimensions()
        report.append("PART DIMENSIONS:")
        report.append(f"  Diameter: {dimensions['diameter']:.2f} mm")
        report.append(f"  Length: {dimensions['length']:.2f} mm")
        report.append(f"  Volume: {dimensions['volume']:.2f} mm³")
        report.append("")
        
        # Operations
        report.append("TURNING OPERATIONS SEQUENCE:")
        report.append("─" * 80)
        
        total_time = 0
        for op in self.operations:
            report.append(f"\nOperation {op['operation_id']}: {op['name']}")
            report.append(f"  Type: {op['type']}")
            report.append(f"  Description: {op['description']}")
            report.append(f"  Tool: {op['tool']}")
            report.append(f"  Spindle Speed: {op['spindle_speed']:,} RPM")
            report.append(f"  Feed Rate: {op['feed_rate']} mm/rev")
            report.append(f"  Depth of Cut: {op['depth_of_cut']} mm")
            report.append(f"  Coolant: {op['coolant']}")
            report.append(f"  Estimated Time: {op['estimated_time']} minutes")
            total_time += op['estimated_time']
        
        report.append("")
        report.append("─" * 80)
        report.append(f"TOTAL ESTIMATED MACHINING TIME: {total_time:.1f} minutes ({total_time/60:.1f} hours)")
        report.append("")
        
        # Tools
        report.append("REQUIRED TURNING TOOLS:")
        report.append("─" * 80)
        for tool in self.tools:
            report.append(f"\n{tool['tool_id']}. {tool['name']} ({tool['type']})")
            report.append(f"   Material: {tool['material']} with {tool['coating']} coating")
            report.append(f"   Purpose: {tool['description']}")
        
        report.append("")
        report.append("─" * 80)
        
        # AI Recommendations
        if self.ai_recommendations.get("optimizations"):
            report.append("\n🤖 AI OPTIMIZATION RECOMMENDATIONS:")
            report.append("─" * 80)
            report.append(self.ai_recommendations.get("optimizations", "No recommendations"))
            report.append("")
        
        # Setup notes
        report.append("SETUP NOTES:")
        report.append("─" * 80)
        report.append("  1. Mount part securely in chuck or collet")
        report.append("  2. Run spindle at low speed before full engagement")
        report.append("  3. Use appropriate coolant for cutting conditions")
        report.append("  4. Check tool alignment before each operation")
        report.append("  5. Monitor surface finish and adjust feeds/speeds as needed")
        report.append("  6. Ensure adequate clearance for each tool and holder")
        report.append("")
        
        report.append("═" * 80)
        report.append("End of Process Plan")
        report.append("═" * 80)
        
        return "\n".join(report)
    
    def save_as_json(self, filepath: Optional[str] = None) -> str:
        """Save process plan as JSON file.
        
        Args:
            filepath: Optional output filepath. If None, generates from part name.
        
        Returns:
            Path to saved file.
        """
        if filepath is None:
            part_name = Path(self.analysis.get("file_path", "plan")).stem
            filepath = f"{part_name}_turning_plan.json"
        
        data = {
            "metadata": {
                "generator": "CAPP Turning Planner",
                "date": datetime.now().isoformat(),
                "part_file": self.analysis.get("file_path"),
                "material_profile": self.material_profile,
                "machine_profile": self.machine_profile,
            },
            "machinability": {
                "score": self.turning_score,
                "suitable_for_turning": self.is_machinable,
            },
            "dimensions": self._format_dimensions(),
            "operations": self.operations,
            "tools": self.tools,
            "ai_recommendations": self.ai_recommendations,
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        return filepath


def generate_turning_plan(
    step_file: str,
    model: str = "phi",
    with_ai: bool = True,
    save_json: bool = False,
    material_profile: str = DEFAULT_MATERIAL_PROFILE,
    machine_profile: str = DEFAULT_MACHINE_PROFILE,
) -> dict:
    """Generate a complete turning process plan for a STEP file.
    
    Args:
        step_file: Path to STEP file.
        model: Ollama model to use.
        with_ai: If True, generate AI recommendations.
        save_json: If True, save plan to JSON file.
        material_profile: Workpiece material profile used for speed logic.
        machine_profile: Lathe machine profile used for RPM limits.
    
    Returns:
        Dictionary with plan results.
    """
    print(f"📊 Analyzing STEP file for turning feasibility: {step_file}")
    
    # Analyze the STEP file
    print("  ⏳ Running geometry analysis...")
    analysis = analyze_step_file(step_file)
    
    if not analysis.get("success"):
        print(f"  ❌ Analysis failed: {analysis.get('error')}")
        return {"success": False, "error": analysis.get("error")}
    
    print("  ✅ Analysis complete")
    
    # Create process plan
    print("\n🔧 Generating turning process plan...")
    plan = TurningProcessPlan(
        analysis,
        model=model,
        material_profile=material_profile,
        machine_profile=machine_profile,
    )
    
    # Check if machinable for turning
    if not plan.is_machinable:
        print(f"  ❌ Part NOT suitable for turning (score: {plan.turning_score}/100)")
        print("  ⚠️  This part is better suited for other manufacturing methods")
        return {
            "success": False,
            "error": "Part not suitable for turning",
            "turning_score": plan.turning_score,
            "recommendation": "Consider 3-axis milling or 3D printing instead"
        }
    
    print(f"  ✅ Part suitable for turning (score: {plan.turning_score}/100)")
    
    # Generate operations
    print("  ⏳ Generating turning operations...")
    plan.generate_operations()
    print(f"  ✅ Generated {len(plan.operations)} operations")
    
    # Generate tool list
    print("  ⏳ Generating required tools...")
    plan.generate_tool_list()
    print(f"  ✅ Listed {len(plan.tools)} turning tools")
    
    # Generate AI recommendations if requested
    if with_ai:
        print("  ⏳ Generating AI optimization recommendations...")
        set_model(model)
        plan.generate_ai_recommendations()
    
    # Save JSON if requested
    json_file = None
    if save_json:
        print("  ⏳ Saving plan to JSON...")
        json_file = plan.save_as_json()
        print(f"  ✅ Saved to: {json_file}")
    
    # Generate report
    report = plan.generate_report()
    
    return {
        "success": True,
        "turning_score": plan.turning_score,
        "material_profile": plan.material_profile,
        "machine_profile": plan.machine_profile,
        "operations": plan.operations,
        "tools": plan.tools,
        "report": report,
        "json_file": json_file,
        "ai_recommendations": plan.ai_recommendations,
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python capp_turning_planner.py <step_file> [--ai] [--save]")
        print("Example: python capp_turning_planner.py model.step --ai --save")
        sys.exit(1)
    
    step_file = sys.argv[1]
    with_ai = "--ai" in sys.argv
    save_json = "--save" in sys.argv
    
    result = generate_turning_plan(step_file, with_ai=with_ai, save_json=save_json)
    
    if result.get("success"):
        print("\n" + result.get("report"))
    else:
        print(f"\n❌ {result.get('error')}")
        print(f"   Turning score: {result.get('turning_score')}/100")
        print(f"   {result.get('recommendation')}")
        sys.exit(1)
