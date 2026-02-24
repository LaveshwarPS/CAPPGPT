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

TOP_MATERIALS_INDIA = [
    "EN8 / EN8D",
    "EN1A (Free-cutting steel)",
    "EN19 / 42CrMo4",
    "C45 / CK45",
    "20MnCr5 / EN353",
    "SS304",
    "SS316 / 316L",
    "SS410",
    "Aluminum 6061 / 6082",
    "Brass (CW614N / CuZn39Pb3)",
]

TOP_MACHINE_PROFILES_INDIA = [
    "ACE Designers CNC Turning Center",
    "Jyoti CNC Turning Center",
    "LMW CNC Turning Center",
    "BFW CNC Turning Center",
    "Haas ST Series",
    "Mazak QUICK TURN Series",
    "Okuma CNC Lathe",
    "DMG MORI Turning Center",
    "DN Solutions Lynx/Puma",
    "HMT CNC Lathe",
]

DEFAULT_MATERIAL_PROFILE = "EN8 / EN8D"
DEFAULT_MACHINE_PROFILE = "ACE Designers CNC Turning Center"

MATERIAL_SPEED_FACTORS = {
    "EN8 / EN8D": 1.0,
    "EN1A (Free-cutting steel)": 1.15,
    "EN19 / 42CrMo4": 0.8,
    "C45 / CK45": 0.95,
    "20MnCr5 / EN353": 0.9,
    "SS304": 0.65,
    "SS316 / 316L": 0.6,
    "SS410": 0.85,
    "Aluminum 6061 / 6082": 1.7,
    "Brass (CW614N / CuZn39Pb3)": 1.8,
}

MACHINE_PROFILES = {
    "ACE Designers CNC Turning Center": {
        "max_rpm": 4000,
        "max_power_kw": 14.9,
        "max_turning_diameter_mm": 262.0,
        "max_turning_length_mm": 572.0,
    },
    "Jyoti CNC Turning Center": {
        "max_rpm": 4000,
        "max_power_kw": 14.9,
        "max_turning_diameter_mm": 260.0,
        "max_turning_length_mm": 600.0,
    },
    "LMW CNC Turning Center": {
        "max_rpm": 4000,
        "max_power_kw": 15.0,
        "max_turning_diameter_mm": 300.0,
        "max_turning_length_mm": 650.0,
    },
    "BFW CNC Turning Center": {
        "max_rpm": 3500,
        "max_power_kw": 12.0,
        "max_turning_diameter_mm": 280.0,
        "max_turning_length_mm": 600.0,
    },
    "Haas ST Series": {
        "max_rpm": 4000,
        "max_power_kw": 14.9,
        "max_turning_diameter_mm": 262.0,
        "max_turning_length_mm": 572.0,
    },
    "Mazak QUICK TURN Series": {
        "max_rpm": 5000,
        "max_power_kw": 18.5,
        "max_turning_diameter_mm": 300.0,
        "max_turning_length_mm": 600.0,
    },
    "Okuma CNC Lathe": {
        "max_rpm": 4500,
        "max_power_kw": 18.5,
        "max_turning_diameter_mm": 300.0,
        "max_turning_length_mm": 600.0,
    },
    "DMG MORI Turning Center": {
        "max_rpm": 5000,
        "max_power_kw": 18.5,
        "max_turning_diameter_mm": 300.0,
        "max_turning_length_mm": 600.0,
    },
    "DN Solutions Lynx/Puma": {
        "max_rpm": 4500,
        "max_power_kw": 15.0,
        "max_turning_diameter_mm": 280.0,
        "max_turning_length_mm": 600.0,
    },
    "HMT CNC Lathe": {
        "max_rpm": 1800,
        "max_power_kw": 11.2,
        "max_turning_diameter_mm": 406.0,
        "max_turning_length_mm": 762.0,
    },
}

SPECIFIC_POWER_KW_PER_CM3_MIN = {
    "EN8 / EN8D": 0.05,
    "EN1A (Free-cutting steel)": 0.045,
    "EN19 / 42CrMo4": 0.065,
    "C45 / CK45": 0.055,
    "20MnCr5 / EN353": 0.06,
    "SS304": 0.07,
    "SS316 / 316L": 0.075,
    "SS410": 0.06,
    "Aluminum 6061 / 6082": 0.03,
    "Brass (CW614N / CuZn39Pb3)": 0.03,
}


class TurningProcessPlan:
    """Represents a turning process plan for a STEP file."""
    
    def __init__(
        self,
        analysis: dict,
        model: str = "phi",
        material_profile: str = DEFAULT_MATERIAL_PROFILE,
        machine_profile: str = DEFAULT_MACHINE_PROFILE,
        tolerance_mm: Optional[float] = None,
        surface_roughness_ra: Optional[float] = None,
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
        self.tolerance_mm = tolerance_mm
        self.surface_roughness_ra = surface_roughness_ra
        turning_data = self.analysis.get("machinability", {}).get("turning", {})
        self.turning_score = self._get_turning_score()
        self.strict_turnable = bool(turning_data.get("strict_turnable", self.turning_score >= 75))
        strict_checks = turning_data.get("strict_checks", {}) or {}
        # Partial turning should be easier to pass: keep strict mode for "full turning",
        # but allow CAPP on clearly rotational subsets of mixed-geometry models.
        if strict_checks:
            self.partial_turnable = bool(
                self.turning_score >= 40
                and strict_checks.get("cylindrical_dominance", False)
                and (
                    strict_checks.get("circular_edge_support", False)
                    or strict_checks.get("reasonable_aspect_ratio", False)
                )
            )
        else:
            # Fallback when strict checks are unavailable (older/demo analyzer output).
            self.partial_turnable = self.turning_score >= 45
        self.is_machinable = self.strict_turnable or self.partial_turnable
        self.operations = []
        self.tools = []
        self.ai_recommendations = {}
        self.feature_detection = {}
        self.validation = {}
    
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

    def _machine_limits(self) -> Dict[str, float]:
        return MACHINE_PROFILES.get(
            self.machine_profile,
            MACHINE_PROFILES[DEFAULT_MACHINE_PROFILE],
        )

    def _detect_features(self, dimensions: Dict[str, float]) -> Dict[str, Dict]:
        surface = self._get_surface_info()
        geometry_stats = self.analysis.get("model_info", {}).get("geometry_stats", {})
        faces = max(int(geometry_stats.get("faces", 0)), 1)
        edges = max(int(geometry_stats.get("edges", 0)), 0)
        edge_face_ratio = edges / faces
        cyl = int(surface.get("Cylinder", 0))
        cone = int(surface.get("Cone", 0))
        torus = int(surface.get("Torus", 0))
        plane = int(surface.get("Plane", 0))
        slenderness = dimensions["length"] / max(dimensions["diameter"], 0.1)

        threading_reasons: List[str] = []
        threading_score = 0
        if cone > 0 and cyl >= 2:
            threading_score += 2
            threading_reasons.append("Cone + multiple cylinder surfaces indicate thread lead-in profile.")
        if edge_face_ratio >= 2.8 and cyl >= 3:
            threading_score += 1
            threading_reasons.append("High edge density on cylindrical geometry suggests helical detail.")
        if slenderness >= 1.2:
            threading_score += 1
            threading_reasons.append("Length/diameter ratio supports external threading access.")

        grooving_reasons: List[str] = []
        grooving_score = 0
        if torus > 0:
            grooving_score += 2
            grooving_reasons.append("Torus surfaces are a strong groove/fillet indicator.")
        if cyl >= 4 and plane >= 4 and edge_face_ratio >= 2.2:
            grooving_score += 1
            grooving_reasons.append("Cylinder-plane transitions and edge density suggest relief grooves.")
        if self.analysis.get("cylindrical_faces", 0) >= 5:
            grooving_score += 1
            grooving_reasons.append("High cylindrical face count indicates stepped OD/ID features.")

        def _feature_result(score: int, reasons: List[str], label: str) -> Dict:
            if score >= 3:
                return {"detected": True, "confidence": "high", "reasons": reasons[:3], "label": label}
            if score == 2:
                return {"detected": True, "confidence": "medium", "reasons": reasons[:3], "label": label}
            return {
                "detected": False,
                "confidence": "low",
                "reasons": reasons[:2] or [f"No strong geometric evidence for {label}."],
                "label": label,
            }

        return {
            "threading": _feature_result(threading_score, threading_reasons, "threading"),
            "grooving": _feature_result(grooving_score, grooving_reasons, "grooving"),
            "metrics": {
                "edge_face_ratio": round(edge_face_ratio, 2),
                "cylinder_surfaces": cyl,
                "cone_surfaces": cone,
                "torus_surfaces": torus,
                "slenderness_ratio": round(slenderness, 2),
            },
        }

    def _needs_finish_pass(self) -> bool:
        if self.tolerance_mm is not None and self.tolerance_mm <= 0.05:
            return True
        if self.surface_roughness_ra is not None and self.surface_roughness_ra <= 1.6:
            return True
        return False
    
    def generate_operations(self) -> List[Dict]:
        """Generate turning operations sequence."""
        if not self.is_machinable:
            return []

        dimensions = self._format_dimensions()
        diameter = dimensions["diameter"]
        length = dimensions["length"]
        features = self._detect_features(dimensions)
        self.feature_detection = features

        operations: List[Dict] = []

        def add_operation(op: Dict) -> None:
            row = dict(op)
            row["operation_id"] = len(operations) + 1
            operations.append(row)

        add_operation({
            "name": "Face & Center",
            "description": "Face the part and create center marks for alignment",
            "type": "facing",
            "tool": "Facing insert (CNMG)",
            "spindle_speed": self._calculate_spindle_speed(diameter, "facing"),
            "feed_rate": 0.15,
            "depth_of_cut": 1.0,
            "coolant": "flood",
            "estimated_time": 2.0,
        })

        if diameter > 20:
            add_operation({
                "name": "Rough Turning",
                "description": "Remove material from outer diameter",
                "type": "turning",
                "tool": "Turning insert (VNMG)",
                "spindle_speed": self._calculate_spindle_speed(diameter * 0.8, "rough"),
                "feed_rate": 0.20,
                "depth_of_cut": 2.0,
                "coolant": "flood",
                "estimated_time": self._estimate_turning_time(diameter, length, 2.0, 0.20),
            })

        finish_desc = "Achieve final diameter and surface finish"
        if self.tolerance_mm is not None or self.surface_roughness_ra is not None:
            tol_text = f"tol +/-{self.tolerance_mm:.3f} mm" if self.tolerance_mm is not None else "tol n/a"
            ra_text = f"Ra {self.surface_roughness_ra:.2f} um" if self.surface_roughness_ra is not None else "Ra n/a"
            finish_desc = f"Achieve final diameter and surface finish ({tol_text}, {ra_text})"

        add_operation({
            "name": "Finish Turning",
            "description": finish_desc,
            "type": "turning",
            "tool": "Finishing insert (VNMG, R0.4)",
            "spindle_speed": self._calculate_spindle_speed(diameter, "finish"),
            "feed_rate": 0.10,
            "depth_of_cut": 0.5,
            "coolant": "flood",
            "estimated_time": self._estimate_turning_time(diameter, length, 0.5, 0.10),
        })

        if self._needs_finish_pass():
            add_operation({
                "name": "Fine Finish Pass",
                "description": "Low-DOC pass for tight tolerance and low roughness target",
                "type": "finishing",
                "tool": "Wiper finishing insert (VNMG, R0.2)",
                "spindle_speed": self._calculate_spindle_speed(diameter, "finish"),
                "feed_rate": 0.05,
                "depth_of_cut": 0.2,
                "coolant": "flood",
                "estimated_time": self._estimate_turning_time(diameter, length, 0.2, 0.05),
            })

        cylindrical_faces = self.analysis.get("cylindrical_faces", 0)
        if cylindrical_faces > 2:
            add_operation({
                "name": "Boring",
                "description": "Machine internal cylindrical features",
                "type": "boring",
                "tool": "Boring bar with insert",
                "spindle_speed": self._calculate_spindle_speed(diameter * 0.5, "boring"),
                "feed_rate": 0.12,
                "depth_of_cut": 1.0,
                "coolant": "flood",
                "estimated_time": 3.0,
            })

        if features["threading"]["detected"]:
            add_operation({
                "name": "Threading",
                "description": "Cut external threads (geometry-detected)",
                "type": "threading",
                "tool": "Threading insert (60 degree diamond)",
                "spindle_speed": self._calculate_spindle_speed(diameter, "threading") // 2,
                "feed_rate": 0.5,
                "depth_of_cut": 0.5,
                "coolant": "light",
                "estimated_time": 2.5,
                "thread_spec": "M10 x 1.5 (example)",
            })

        if features["grooving"]["detected"]:
            add_operation({
                "name": "Grooving",
                "description": "Cut grooves for stress relief (geometry-detected)",
                "type": "grooving",
                "tool": "Grooving insert",
                "spindle_speed": self._calculate_spindle_speed(diameter * 0.7, "grooving"),
                "feed_rate": 0.15,
                "depth_of_cut": 0.8,
                "coolant": "flood",
                "estimated_time": 1.5,
            })

        add_operation({
            "name": "Parting Off",
            "description": "Separate finished part from stock",
            "type": "parting",
            "tool": "Parting blade",
            "spindle_speed": self._calculate_spindle_speed(diameter * 0.9, "parting"),
            "feed_rate": 0.08,
            "depth_of_cut": diameter * 0.5,
            "coolant": "light",
            "estimated_time": 1.0,
        })

        self.operations = operations
        return operations

    def _calculate_spindle_speed(self, diameter_mm: float, operation_type: str) -> int:
        """Calculate spindle speed based on diameter and operation.
        
        Uses the formula: RPM = (1000 * SFM) / (Ï€ * diameter)
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
        
        # RPM = (SFM * 12) / (Ï€ * D)
        rpm = int((sfm * 12) / (3.14159 * diameter_inches))
        
        # Clamp to selected machine limits.
        machine_rpm_limit = int(self._machine_limits().get("max_rpm", 4000))
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
        
        # Material removal rate (mmÂ³/min) = spindle_speed * feed * depth
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

    def run_validation_checks(self) -> Dict:
        """Validate geometry rules, finish logic, and machine limits."""
        dimensions = self._format_dimensions()
        limits = self._machine_limits()
        messages: List[Dict] = []

        threading_detected = bool(self.feature_detection.get("threading", {}).get("detected"))
        grooving_detected = bool(self.feature_detection.get("grooving", {}).get("detected"))
        has_threading_op = any(op.get("type") == "threading" for op in self.operations)
        has_grooving_op = any(op.get("type") == "grooving" for op in self.operations)
        has_fine_finish = any(op.get("type") == "finishing" for op in self.operations)

        if has_threading_op == threading_detected:
            messages.append({
                "level": "pass",
                "title": "Threading Rule",
                "detail": f"Threading op {'added' if has_threading_op else 'skipped'} based on geometry detection.",
            })
        else:
            messages.append({
                "level": "fail",
                "title": "Threading Rule",
                "detail": "Threading operation mismatch against geometry detector.",
            })

        if has_grooving_op == grooving_detected:
            messages.append({
                "level": "pass",
                "title": "Grooving Rule",
                "detail": f"Grooving op {'added' if has_grooving_op else 'skipped'} based on geometry detection.",
            })
        else:
            messages.append({
                "level": "fail",
                "title": "Grooving Rule",
                "detail": "Grooving operation mismatch against geometry detector.",
            })

        finish_needed = self._needs_finish_pass()
        if finish_needed == has_fine_finish:
            messages.append({
                "level": "pass",
                "title": "Tolerance/Ra Rule",
                "detail": f"Fine finish pass {'enabled' if has_fine_finish else 'not required'} for given quality target.",
            })
        else:
            messages.append({
                "level": "fail",
                "title": "Tolerance/Ra Rule",
                "detail": "Finish pass logic did not match tolerance/Ra thresholds.",
            })

        if dimensions["diameter"] > limits["max_turning_diameter_mm"]:
            messages.append({
                "level": "fail",
                "title": "Machine Diameter Limit",
                "detail": f"Part diameter {dimensions['diameter']:.1f} mm exceeds machine limit {limits['max_turning_diameter_mm']:.1f} mm.",
            })
        else:
            messages.append({
                "level": "pass",
                "title": "Machine Diameter Limit",
                "detail": f"Part diameter {dimensions['diameter']:.1f} mm is within machine limit.",
            })

        if dimensions["length"] > limits["max_turning_length_mm"]:
            messages.append({
                "level": "fail",
                "title": "Machine Length Limit",
                "detail": f"Part length {dimensions['length']:.1f} mm exceeds machine limit {limits['max_turning_length_mm']:.1f} mm.",
            })
        else:
            messages.append({
                "level": "pass",
                "title": "Machine Length Limit",
                "detail": f"Part length {dimensions['length']:.1f} mm is within machine limit.",
            })

        max_rpm_limit = int(limits.get("max_rpm", 4000))
        near_limit = [op for op in self.operations if int(op.get("spindle_speed", 0)) >= int(max_rpm_limit * 0.95)]
        if near_limit:
            messages.append({
                "level": "warn",
                "title": "Spindle Speed Margin",
                "detail": f"{len(near_limit)} operation(s) run near machine max RPM ({max_rpm_limit}).",
            })
        else:
            messages.append({
                "level": "pass",
                "title": "Spindle Speed Margin",
                "detail": "All operations are below 95% of machine max RPM.",
            })

        roughing_ops = [op for op in self.operations if op.get("name") == "Rough Turning"]
        estimated_kw = 0.0
        if roughing_ops:
            op = roughing_ops[0]
            d = max(dimensions["diameter"], 1.0)
            rpm = float(op.get("spindle_speed", 0))
            f = float(op.get("feed_rate", 0))
            ap = float(op.get("depth_of_cut", 0))
            mrr_mm3_min = 3.14159 * d * rpm * f * ap
            mrr_cm3_min = mrr_mm3_min / 1000.0
            spec_power = SPECIFIC_POWER_KW_PER_CM3_MIN.get(self.material_profile, 0.05)
            estimated_kw = mrr_cm3_min * spec_power

        usable_power_kw = float(limits.get("max_power_kw", 10.0)) * 0.85
        if estimated_kw > usable_power_kw:
            messages.append({
                "level": "warn",
                "title": "Spindle Power Check",
                "detail": f"Estimated roughing demand {estimated_kw:.1f} kW exceeds 85% usable power ({usable_power_kw:.1f} kW).",
            })
        else:
            messages.append({
                "level": "pass",
                "title": "Spindle Power Check",
                "detail": f"Estimated roughing demand {estimated_kw:.1f} kW is within usable power ({usable_power_kw:.1f} kW).",
            })

        severity = {"pass": 0, "warn": 1, "fail": 2}
        worst = max(messages, key=lambda m: severity[m["level"]])["level"] if messages else "pass"
        self.validation = {
            "status": worst,
            "messages": messages,
            "feature_detection": self.feature_detection,
            "inputs": {
                "material_profile": self.material_profile,
                "machine_profile": self.machine_profile,
                "tolerance_mm": self.tolerance_mm,
                "surface_roughness_ra": self.surface_roughness_ra,
            },
        }
        return self.validation
    
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

        op_types = {op.get("type") for op in self.operations}
        filtered: List[Dict] = []
        for tool in tools:
            name = tool["name"]
            if name == "Threading Insert" and "threading" not in op_types:
                continue
            if name == "Grooving Insert" and "grooving" not in op_types:
                continue
            filtered.append(tool)

        if "finishing" in op_types:
            filtered.append(
                {
                    "tool_id": len(filtered) + 1,
                    "name": "Fine Finishing Insert",
                    "type": "VNMG 331 Wiper",
                    "material": "Carbide",
                    "coating": "TiAlN",
                    "description": "For tight tolerance and Ra finishing pass",
                }
            )

        for idx, tool in enumerate(filtered, start=1):
            tool["tool_id"] = idx

        self.tools = filtered
        return filtered
    
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
        
        print(f"  â³ Generating process optimization recommendations (timeout: {timeout}s)...")
        try:
            prompt = f"""Review this turning process plan for a lathe operation:

Part Specifications:
  - Diameter: {dimensions['diameter']:.1f} mm
  - Length: {dimensions['length']:.1f} mm
  - Cylindrical faces: {self.analysis.get('cylindrical_faces', 0)}
  - Machinability score: {self.turning_score}/100
  - Workpiece material: {self.material_profile}
  - Lathe machine profile: {self.machine_profile}
  - Dimensional tolerance target (mm): {self.tolerance_mm if self.tolerance_mm is not None else 'not specified'}
  - Surface roughness target Ra (um): {self.surface_roughness_ra if self.surface_roughness_ra is not None else 'not specified'}

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
        
        print("  âœ… AI recommendations generated")
        self.ai_recommendations = recommendations
        return recommendations
    
    def generate_report(self) -> str:
        """Generate a formatted turning process plan report.
        
        Returns:
            Formatted report string.
        """
        report = []
        report.append("â•" * 80)
        report.append("TURNING PROCESS PLAN (CAPP SYSTEM)")
        report.append("â•" * 80)
        report.append("")
        
        # Header
        report.append("PART INFORMATION:")
        report.append(f"  File: {self.analysis.get('file_path', 'Unknown')}")
        report.append(f"  Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"  Material Profile: {self.material_profile}")
        report.append(f"  Machine Profile: {self.machine_profile}")
        if self.tolerance_mm is not None:
            report.append(f"  Tolerance Target: +/-{self.tolerance_mm:.3f} mm")
        if self.surface_roughness_ra is not None:
            report.append(f"  Surface Target: Ra {self.surface_roughness_ra:.2f} um")
        report.append("")
        
        # Machinability
        report.append("TURNING MACHINABILITY:")
        report.append(f"  Score: {self.turning_score}/100")
        report.append(f"  Suitable for Turning: {'YES âœ“' if self.is_machinable else 'NO âœ—'}")
        report.append("")
        
        if not self.is_machinable:
            report.append("âŒ This part is NOT suitable for turning operations.")
            report.append("   Consider alternative manufacturing methods.")
            return "\n".join(report)
        
        # Dimensions
        dimensions = self._format_dimensions()
        report.append("PART DIMENSIONS:")
        report.append(f"  Diameter: {dimensions['diameter']:.2f} mm")
        report.append(f"  Length: {dimensions['length']:.2f} mm")
        report.append(f"  Volume: {dimensions['volume']:.2f} mmÂ³")
        report.append("")
        
        # Operations
        report.append("TURNING OPERATIONS SEQUENCE:")
        report.append("â”€" * 80)
        
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
        report.append("â”€" * 80)
        report.append(f"TOTAL ESTIMATED MACHINING TIME: {total_time:.1f} minutes ({total_time/60:.1f} hours)")
        report.append("")
        
        # Tools
        report.append("REQUIRED TURNING TOOLS:")
        report.append("â”€" * 80)
        for tool in self.tools:
            report.append(f"\n{tool['tool_id']}. {tool['name']} ({tool['type']})")
            report.append(f"   Material: {tool['material']} with {tool['coating']} coating")
            report.append(f"   Purpose: {tool['description']}")
        
        report.append("")
        report.append("â”€" * 80)
        
        # AI Recommendations
        if self.ai_recommendations.get("optimizations"):
            report.append("\nðŸ¤– AI OPTIMIZATION RECOMMENDATIONS:")
            report.append("â”€" * 80)
            report.append(self.ai_recommendations.get("optimizations", "No recommendations"))
            report.append("")
        
        # Setup notes
        report.append("SETUP NOTES:")
        report.append("â”€" * 80)
        report.append("  1. Mount part securely in chuck or collet")
        report.append("  2. Run spindle at low speed before full engagement")
        report.append("  3. Use appropriate coolant for cutting conditions")
        report.append("  4. Check tool alignment before each operation")
        report.append("  5. Monitor surface finish and adjust feeds/speeds as needed")
        report.append("  6. Ensure adequate clearance for each tool and holder")
        report.append("")
        
        report.append("â•" * 80)
        report.append("End of Process Plan")
        report.append("â•" * 80)
        
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
                "step_protocol": self.analysis.get("step_protocol", "Unknown"),
                "step_schema": self.analysis.get("step_schema", "Unknown"),
                "material_profile": self.material_profile,
                "machine_profile": self.machine_profile,
                "tolerance_mm": self.tolerance_mm,
                "surface_roughness_ra": self.surface_roughness_ra,
            },
            "machinability": {
                "score": self.turning_score,
                "suitable_for_turning": self.is_machinable,
            },
            "dimensions": self._format_dimensions(),
            "operations": self.operations,
            "tools": self.tools,
            "ai_recommendations": self.ai_recommendations,
            "feature_detection": self.feature_detection,
            "validation": self.validation,
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
    tolerance_mm: Optional[float] = None,
    surface_roughness_ra: Optional[float] = None,
) -> dict:
    """Generate a complete turning process plan for a STEP file.
    
    Args:
        step_file: Path to STEP file.
        model: Ollama model to use.
        with_ai: If True, generate AI recommendations.
        save_json: If True, save plan to JSON file.
        material_profile: Workpiece material profile used for speed logic.
        machine_profile: Lathe machine profile used for RPM limits.
        tolerance_mm: Optional dimensional tolerance target in mm.
        surface_roughness_ra: Optional Ra target in um.
    
    Returns:
        Dictionary with plan results.
    """
    print(f"ðŸ“Š Analyzing STEP file for turning feasibility: {step_file}")
    
    # Analyze the STEP file
    print("  â³ Running geometry analysis...")
    analysis = analyze_step_file(step_file)
    
    if not analysis.get("success"):
        print(f"  âŒ Analysis failed: {analysis.get('error')}")
        return {"success": False, "error": analysis.get("error")}
    
    print("  âœ… Analysis complete")
    
    # Create process plan
    print("\nðŸ”§ Generating turning process plan...")
    plan = TurningProcessPlan(
        analysis,
        model=model,
        material_profile=material_profile,
        machine_profile=machine_profile,
        tolerance_mm=tolerance_mm,
        surface_roughness_ra=surface_roughness_ra,
    )
    
    turning_data = analysis.get("machinability", {}).get("turning", {})
    strict_checks = turning_data.get("strict_checks", {}) or {}
    failing_checks = [k for k, passed in strict_checks.items() if not passed]
    check_reason_map = {
        "axisymmetric_xy": "Part envelope is not axisymmetric enough for full turning-only processing.",
        "cylindrical_dominance": "Cylindrical content is too low for a robust turning workflow.",
        "circular_edge_support": "Circular edge evidence is weak for rotational manufacturing.",
        "limited_complexity": "Freeform/complex surfaces indicate non-turning features (milling/grinding likely needed).",
        "reasonable_aspect_ratio": "Part proportions are outside safe turning-focused envelope.",
    }
    limitation_reasons = [check_reason_map.get(k, k) for k in failing_checks]

    # Check if machinable for turning
    if not plan.is_machinable:
        recommended = analysis.get("recommended_process") or "3_axis_milling"
        recommended_text = str(recommended).replace("_", " ")
        alternatives = analysis.get("alternative_processes", [])
        turning_reasons = analysis.get("machinability", {}).get("turning", {}).get("reasons", [])
        print(f"  âŒ Part NOT strictly suitable for turning (score: {plan.turning_score}/100)")
        print(f"  âš ï¸  Recommended process: {recommended}")
        return {
            "success": False,
            "error": "Part is not strictly turnable for CAPP turning workflow.",
            "turning_score": plan.turning_score,
            "strict_turnable": False,
            "partial_turnable": False,
            "turning_scope": "none",
            "recommended_process": recommended,
            "alternative_processes": alternatives,
            "turning_gate_reasons": turning_reasons,
            "turning_limitations": limitation_reasons,
            "recommendation": f"Use {recommended_text} instead of turning."
        }

    if plan.strict_turnable:
        print(f"  âœ… Part suitable for full turning CAPP (score: {plan.turning_score}/100)")
    else:
        print(f"  âš ï¸ Part is partially turnable; generating limited turning CAPP (score: {plan.turning_score}/100)")
    
    # Generate operations
    print("  â³ Generating turning operations...")
    plan.generate_operations()
    print(f"  âœ… Generated {len(plan.operations)} operations")
    
    # Generate tool list
    print("  â³ Generating required tools...")
    plan.generate_tool_list()
    print(f"  âœ… Listed {len(plan.tools)} turning tools")

    # Run validation checks
    print("  â³ Running rule and machine capability validation...")
    plan.run_validation_checks()
    print(f"  âœ… Validation status: {plan.validation.get('status', 'unknown')}")
    
    # Generate AI recommendations if requested
    if with_ai:
        print("  â³ Generating AI optimization recommendations...")
        set_model(model)
        plan.generate_ai_recommendations()
    
    # Save JSON if requested
    json_file = None
    if save_json:
        print("  â³ Saving plan to JSON...")
        json_file = plan.save_as_json()
        print(f"  âœ… Saved to: {json_file}")
    
    # Generate report
    report = plan.generate_report()
    
    return {
        "success": True,
        "step_protocol": analysis.get("step_protocol", "Unknown"),
        "step_schema": analysis.get("step_schema", "Unknown"),
        "legacy_step": analysis.get("legacy_step", "unknown"),
        "strict_turnable": plan.strict_turnable,
        "partial_turnable": plan.partial_turnable,
        "turning_scope": "full" if plan.strict_turnable else "partial",
        "turning_score": plan.turning_score,
        "recommended_process": analysis.get("recommended_process"),
        "alternative_processes": analysis.get("alternative_processes", []),
        "turning_gate_reasons": turning_data.get("reasons", []),
        "turning_limitations": limitation_reasons,
        "material_profile": plan.material_profile,
        "machine_profile": plan.machine_profile,
        "tolerance_mm": plan.tolerance_mm,
        "surface_roughness_ra": plan.surface_roughness_ra,
        "operations": plan.operations,
        "tools": plan.tools,
        "report": report,
        "json_file": json_file,
        "ai_recommendations": plan.ai_recommendations,
        "feature_detection": plan.feature_detection,
        "validation": plan.validation,
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
        print(f"\nâŒ {result.get('error')}")
        print(f"   Turning score: {result.get('turning_score')}/100")
        print(f"   {result.get('recommendation')}")
        sys.exit(1)

