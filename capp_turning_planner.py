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
import copy
import sys
import builtins
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime

from step_analyzer import analyze_step_file
from chat_ollama import query_ollama, OllamaError, set_model

# Configuration from environment variables
OLLAMA_AI_TIMEOUT = int(os.getenv("OLLAMA_AI_TIMEOUT", "120"))
PLAN_CACHE_MAX = max(1, int(os.getenv("CAPP_PLAN_CACHE_MAX", "12")))
_PLAN_CACHE: Dict[str, Dict] = {}


def _safe_print(*args, **kwargs):
    """Print safely on terminals that cannot encode some Unicode characters."""
    try:
        return builtins.print(*args, **kwargs)
    except UnicodeEncodeError:
        sep = kwargs.get("sep", " ")
        end = kwargs.get("end", "\n")
        flush = kwargs.get("flush", False)
        file = kwargs.get("file", sys.stdout)
        encoding = getattr(file, "encoding", None) or "utf-8"
        text = sep.join(str(arg) for arg in args)
        sanitized = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
        return builtins.print(sanitized, end=end, file=file, flush=flush)


# Module-local print wrapper for robust Windows console behavior.
print = _safe_print

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


def _make_file_signature(step_file: str) -> str:
    path = Path(step_file)
    try:
        stat = path.stat()
        return f"{path.resolve()}::{stat.st_size}::{stat.st_mtime_ns}"
    except Exception:
        return str(path)


def _build_plan_cache_key(
    step_file: str,
    model: str,
    with_ai: bool,
    save_json: bool,
    allow_demo_mode: bool,
    material_profile: str,
    machine_profile: str,
    tolerance_mm: Optional[float],
    surface_roughness_ra: Optional[float],
) -> str:
    payload = {
        "file": _make_file_signature(step_file),
        "model": model,
        "with_ai": bool(with_ai),
        "save_json": bool(save_json),
        "allow_demo_mode": bool(allow_demo_mode),
        "material_profile": material_profile,
        "machine_profile": machine_profile,
        "tolerance_mm": tolerance_mm,
        "surface_roughness_ra": surface_roughness_ra,
    }
    return json.dumps(payload, sort_keys=True, default=str)


def _cache_get(cache_key: str) -> Optional[Dict]:
    cached = _PLAN_CACHE.get(cache_key)
    if cached is None:
        return None
    return copy.deepcopy(cached)


def _cache_put(cache_key: str, result: Dict) -> None:
    _PLAN_CACHE[cache_key] = copy.deepcopy(result)
    while len(_PLAN_CACHE) > PLAN_CACHE_MAX:
        oldest = next(iter(_PLAN_CACHE))
        _PLAN_CACHE.pop(oldest, None)


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
        axis_analysis = turning_data.get("axis_analysis", {}) or {}
        axis_relaxed_ratio = float(axis_analysis.get("aligned_ratio_15deg", 0.0) or 0.0)
        # Partial turning should be easier to pass: keep strict mode for "full turning",
        # but allow CAPP on clearly rotational subsets of mixed-geometry models.
        if strict_checks:
            self.partial_turnable = bool(
                self.turning_score >= 55
                and strict_checks.get("cylindrical_dominance", False)
                and strict_checks.get("circular_edge_support", False)
                and strict_checks.get("limited_complexity", False)
                and strict_checks.get("reasonable_aspect_ratio", False)
                and (
                    strict_checks.get("axisymmetric_xy", False)
                    or strict_checks.get("turnable_majority", False)
                    or axis_relaxed_ratio >= 0.72
                )
            )
        else:
            # Fallback when strict checks are unavailable (older/demo analyzer output).
            self.partial_turnable = self.turning_score >= 60
        self.is_machinable = self.strict_turnable or self.partial_turnable
        self.operations = []
        self.tools = []
        self.ai_recommendations = {}
        self.feature_detection = {}
        self.operation_profile = {}
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
        dimensions = self.analysis.get("dimensions", {}) or {}
        if not dimensions:
            # Backward compatibility with older analyzer payloads.
            dimensions = self.analysis.get("machinability", {}).get("dimensions", {}) or {}

        x_size = max(float(dimensions.get("x_size", 20)), 0.1)
        y_size = max(float(dimensions.get("y_size", 20)), 0.1)
        z_size = max(float(dimensions.get("z_size", 50)), 0.1)
        size_sorted = sorted([x_size, y_size, z_size])

        # Orientation-agnostic lathe approximation:
        # use the largest span as turning length, and radial envelope from the other two spans.
        length = size_sorted[2]
        diameter = (size_sorted[0] + size_sorted[1]) / 2.0

        return {
            "diameter": diameter,
            "length": length,
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
        cone_to_cyl_ratio = cone / max(cyl, 1)

        drill_like = bool(
            slenderness >= 4.0
            and cyl >= 4
            and cone >= 2
            and cone_to_cyl_ratio >= 0.2
            and torus <= 1
            and plane <= 4
        )

        threading_reasons: List[str] = []
        threading_score = 0
        if cone > 0 and cyl >= 3 and plane >= 3:
            threading_score += 2
            threading_reasons.append("Cone + cylinder + shoulder transitions indicate possible thread lead-in.")
        if edge_face_ratio >= 3.2 and cyl >= 4 and plane >= 3:
            threading_score += 1
            threading_reasons.append("High edge density with shoulder features suggests helical detail.")
        if 0.8 <= slenderness <= 6.0:
            threading_score += 1
            threading_reasons.append("Length/diameter ratio is typical for thread-turning access.")
        if torus > 0:
            threading_score += 1
            threading_reasons.append("Relief-like toroidal transitions support thread termination geometry.")
        thread_hard_cue = cone > 0 or torus > 0
        if threading_score > 1 and not thread_hard_cue:
            threading_score = 1
            threading_reasons.append("No lead-in/relief cue found (cone/torus), suppressing likely threading false positive.")
        if drill_like:
            threading_score = 0
            threading_reasons = ["Drill-like profile detected; suppressing external threading false positive."]

        grooving_reasons: List[str] = []
        grooving_score = 0
        if torus > 0:
            grooving_score += 2
            grooving_reasons.append("Torus surfaces are a strong groove/fillet indicator.")
        if cyl >= 4 and plane >= 4 and edge_face_ratio >= 2.2:
            grooving_score += 1
            grooving_reasons.append("Cylinder-plane transitions and edge density suggest relief grooves.")
        if max(int(self.analysis.get("cylindrical_faces", 0)), cyl) >= 5:
            grooving_score += 1
            grooving_reasons.append("High cylindrical face count indicates stepped OD/ID features.")

        boring_reasons: List[str] = []
        boring_score = 0
        if cyl >= 8 and plane >= 8 and slenderness <= 3.5:
            boring_score += 1
            boring_reasons.append("High cylinder-plane transitions suggest stepped internal/external turning features.")
        if torus >= 1:
            boring_score += 1
            boring_reasons.append("Toroidal transitions can indicate internal reliefs/chamfers.")
        if edge_face_ratio >= 3.5 and plane >= 6:
            boring_score += 1
            boring_reasons.append("Dense edge network with planar transitions suggests internal feature complexity.")
        if cyl >= 6 and edge_face_ratio >= 2.2 and slenderness <= 6.0:
            boring_score += 1
            boring_reasons.append("Cylindrical density with moderate edge complexity suggests bore-like geometry.")
        if drill_like:
            boring_score = 0
            boring_reasons = ["Drill-like profile detected; suppressing internal boring false positive."]

        taper_reasons: List[str] = []
        taper_score = 0
        if cone >= 1 and cyl >= 2:
            taper_score += 2
            taper_reasons.append("Cone surfaces with adjacent cylinders indicate taper turning regions.")
        if cone_to_cyl_ratio >= 0.05 and cone >= 1:
            taper_score += 1
            taper_reasons.append("Cone-to-cylinder ratio supports explicit taper geometry.")
        if edge_face_ratio >= 2.5 and cone >= 1:
            taper_score += 1
            taper_reasons.append("Edge density around conical surfaces suggests stepped taper transitions.")

        undercut_reasons: List[str] = []
        undercut_score = 0
        if torus >= 1:
            undercut_score += 2
            undercut_reasons.append("Toroidal transitions indicate undercut/relief geometry.")
        if torus >= 2:
            undercut_score += 1
            undercut_reasons.append("Multiple toroidal zones support dedicated undercut passes.")

        chamfer_reasons: List[str] = []
        chamfer_score = 0
        if cone >= 1:
            chamfer_score += 2
            chamfer_reasons.append("Conical transitions indicate chamfered edge finishing.")
        if plane >= 4 and cyl >= 4 and edge_face_ratio >= 2.0:
            chamfer_score += 1
            chamfer_reasons.append("High shoulder count suggests post-finish edge break/chamfering.")
        if torus >= 1:
            chamfer_score += 1
            chamfer_reasons.append("Relief transitions suggest final deburring/chamfer cleanup.")

        drilling_reasons: List[str] = []
        drilling_score = 0
        if drill_like:
            drilling_score += 3
            drilling_reasons.append("Drill-like slender profile indicates axial drilling operation.")
        elif slenderness >= 3.0 and cyl >= 2 and cone >= 1:
            drilling_score += 2
            drilling_reasons.append("Slender axisymmetric profile with cone lead-in suggests drilling.")
        elif slenderness >= 2.2 and cyl >= 6 and edge_face_ratio >= 2.0:
            drilling_score += 2
            drilling_reasons.append("High cylindrical density with elongated profile suggests axial drilling/through-hole.")
        elif cone >= 2 and plane <= 4 and cyl >= 2:
            drilling_score += 1
            drilling_reasons.append("Conical lead-ins with cylindrical support suggest center drilling.")

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
            "boring": _feature_result(boring_score, boring_reasons, "boring"),
            "taper_turning": _feature_result(taper_score, taper_reasons, "taper_turning"),
            "undercut": _feature_result(undercut_score, undercut_reasons, "undercut"),
            "chamfering": _feature_result(chamfer_score, chamfer_reasons, "chamfering"),
            "drilling": _feature_result(drilling_score, drilling_reasons, "drilling"),
            "metrics": {
                "edge_face_ratio": round(edge_face_ratio, 2),
                "cylinder_surfaces": cyl,
                "cone_surfaces": cone,
                "plane_surfaces": plane,
                "torus_surfaces": torus,
                "slenderness_ratio": round(slenderness, 2),
                "cone_to_cylinder_ratio": round(cone_to_cyl_ratio, 2),
                "drill_like": drill_like,
            },
        }

    def _needs_finish_pass(self) -> bool:
        if self.tolerance_mm is not None and self.tolerance_mm <= 0.05:
            return True
        if self.surface_roughness_ra is not None and self.surface_roughness_ra <= 1.6:
            return True
        return False

    @staticmethod
    def _confidence_rank(confidence: str) -> int:
        ranks = {"low": 1, "medium": 2, "high": 3}
        return ranks.get(str(confidence or "low").lower(), 1)

    def _build_operation_profile(self, dimensions: Dict[str, float]) -> Dict[str, object]:
        """Decide core turning operations based on turning scope and quality needs."""
        turning_data = self.analysis.get("machinability", {}).get("turning", {}) or {}
        axis_analysis = turning_data.get("axis_analysis", {}) or {}
        axis_relaxed_ratio = float(axis_analysis.get("aligned_ratio_15deg", 0.0) or 0.0)
        slenderness_ratio = dimensions["length"] / max(dimensions["diameter"], 0.1)
        tight_quality = self._needs_finish_pass()
        semi_finish_for_partial = bool(
            not self.strict_turnable
            and (
                self.turning_score >= 70
                or axis_relaxed_ratio >= 0.85
                or tight_quality
            )
        )
        use_between_centers = bool(slenderness_ratio >= 3.5)
        return {
            "scope": "full" if self.strict_turnable else "partial",
            "include_rough": bool(self.strict_turnable),
            "include_semi_finish": bool(self.strict_turnable or semi_finish_for_partial),
            "include_parting": bool(self.strict_turnable),
            "use_between_centers": use_between_centers,
            "facing_name": "Face & Center" if use_between_centers else "Facing",
            "axis_relaxed_ratio": round(axis_relaxed_ratio, 3),
            "slenderness_ratio": round(slenderness_ratio, 2),
            "tight_quality_target": tight_quality,
            "diameter_mm": round(float(dimensions.get("diameter", 0.0)), 2),
            "length_mm": round(float(dimensions.get("length", 0.0)), 2),
        }

    def _should_include_feature_operation(self, feature_name: str, features: Dict[str, Dict]) -> bool:
        feature = features.get(feature_name, {}) or {}
        if not feature.get("detected"):
            return False

        confidence_rank = self._confidence_rank(feature.get("confidence", "low"))
        metrics = features.get("metrics", {}) or {}

        if feature_name == "threading":
            # Threading false positives are common when there is no lead-in/relief cue.
            hard_cue = int(metrics.get("cone_surfaces", 0)) > 0 or int(metrics.get("torus_surfaces", 0)) > 0
            min_rank = 2 if self.strict_turnable else 3
            return bool(hard_cue and confidence_rank >= min_rank)

        if feature_name == "grooving":
            min_rank = 2 if self.strict_turnable else 3
            return confidence_rank >= min_rank

        if feature_name == "boring":
            # Allow boring in partial scope when geometry evidence is strong.
            drill_like = bool(metrics.get("drill_like", False))
            if drill_like:
                return False
            cyl = int(metrics.get("cylinder_surfaces", 0))
            plane = int(metrics.get("plane_surfaces", 0))
            edge_ratio = float(metrics.get("edge_face_ratio", 0.0) or 0.0)
            if self.strict_turnable:
                return bool(confidence_rank >= 2 and (cyl >= 6 or plane >= 6 or edge_ratio >= 2.6))
            return bool(confidence_rank >= 2 and (cyl >= 8 or edge_ratio >= 3.0))

        if feature_name == "taper_turning":
            min_rank = 2 if self.strict_turnable else 3
            return confidence_rank >= min_rank

        if feature_name == "undercut":
            min_rank = 2 if self.strict_turnable else 3
            return confidence_rank >= min_rank

        if feature_name == "drilling":
            # Drilling is generally a pre-finish stock-removal op.
            drill_like = bool(metrics.get("drill_like", False))
            cyl = int(metrics.get("cylinder_surfaces", 0))
            slenderness = float(metrics.get("slenderness_ratio", 0.0) or 0.0)
            edge_ratio = float(metrics.get("edge_face_ratio", 0.0) or 0.0)
            if drill_like:
                return True
            if confidence_rank >= 2:
                return True
            return bool(cyl >= 8 and slenderness >= 2.2 and edge_ratio >= 2.4)

        if feature_name == "chamfering":
            # Chamfer/deburr is a finishing-stage operation.
            return confidence_rank >= 2

        return False

    def _build_feature_operation(
        self,
        feature_name: str,
        diameter: float,
    ) -> Optional[Dict]:
        op_map = {
            "drilling": {
                "name": "Drilling",
                "description": "Drill axial hole/center based on detected internal feature",
                "type": "drilling",
                "tool": "Carbide twist drill / center drill",
                "spindle_speed": self._calculate_spindle_speed(max(diameter * 0.35, 2.0), "drilling"),
                "feed_rate": 0.10,
                "depth_of_cut": 1.2,
                "coolant": "flood",
                "estimated_time": 1.8,
            },
            "boring": {
                "name": "Boring",
                "description": "Machine internal cylindrical features",
                "type": "boring",
                "tool": "Boring bar with insert",
                "spindle_speed": self._calculate_spindle_speed(diameter * 0.5, "boring"),
                "feed_rate": 0.12,
                "depth_of_cut": 1.0,
                "coolant": "flood",
                "estimated_time": 3.0,
            },
            "taper_turning": {
                "name": "Taper Turning",
                "description": "Generate conical/tapered sections before final finishing",
                "type": "taper_turning",
                "tool": "Profiling insert (VNMG)",
                "spindle_speed": self._calculate_spindle_speed(diameter * 0.9, "taper_turning"),
                "feed_rate": 0.12,
                "depth_of_cut": 0.6,
                "coolant": "flood",
                "estimated_time": 2.2,
            },
            "grooving": {
                "name": "Grooving",
                "description": "Cut grooves for relief and profile definition",
                "type": "grooving",
                "tool": "Grooving insert",
                "spindle_speed": self._calculate_spindle_speed(diameter * 0.7, "grooving"),
                "feed_rate": 0.15,
                "depth_of_cut": 0.8,
                "coolant": "flood",
                "estimated_time": 1.5,
            },
            "undercut": {
                "name": "Undercut",
                "description": "Machine undercut/relief region before thread or shoulder finishing",
                "type": "undercut",
                "tool": "Narrow grooving/undercut insert",
                "spindle_speed": self._calculate_spindle_speed(diameter * 0.65, "undercut"),
                "feed_rate": 0.10,
                "depth_of_cut": 0.6,
                "coolant": "flood",
                "estimated_time": 1.3,
            },
            "threading": {
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
            },
            "chamfering": {
                "name": "Chamfering / Deburring",
                "description": "Break sharp edges and apply finishing chamfers after final turning",
                "type": "chamfering",
                "tool": "Chamfer tool / profiling insert",
                "spindle_speed": self._calculate_spindle_speed(diameter, "chamfering"),
                "feed_rate": 0.08,
                "depth_of_cut": 0.2,
                "coolant": "light",
                "estimated_time": 1.0,
            },
        }
        return dict(op_map[feature_name]) if feature_name in op_map else None
    
    def generate_operations(self) -> List[Dict]:
        """Generate turning operations sequence."""
        if not self.is_machinable:
            return []

        dimensions = self._format_dimensions()
        diameter = dimensions["diameter"]
        length = dimensions["length"]
        features = self._detect_features(dimensions)
        self.feature_detection = features
        self.operation_profile = self._build_operation_profile(dimensions)

        operations: List[Dict] = []

        def add_operation(op: Dict) -> None:
            row = dict(op)
            row["operation_id"] = len(operations) + 1
            operations.append(row)

        facing_name = str(self.operation_profile.get("facing_name", "Facing"))
        facing_desc = (
            "Face datum and center-drill for between-centers setup"
            if facing_name == "Face & Center"
            else "Face datum surface for chuck/collet setup"
        )
        facing_tool = "Facing insert + center drill" if facing_name == "Face & Center" else "Facing insert (CNMG)"
        add_operation({
            "name": facing_name,
            "description": facing_desc,
            "type": "facing",
            "tool": facing_tool,
            "spindle_speed": self._calculate_spindle_speed(diameter, "facing"),
            "feed_rate": 0.15,
            "depth_of_cut": 1.0,
            "coolant": "flood",
            "estimated_time": 2.0,
        })

        if self.operation_profile.get("include_rough"):
            rough_depth = 2.0 if diameter > 20 else 1.0
            rough_feed = 0.20 if diameter > 20 else 0.14
            add_operation({
                "name": "Rough Turning",
                "description": "Primary stock removal from outer diameter before any finish passes",
                "type": "turning",
                "tool": "Turning insert (VNMG)",
                "spindle_speed": self._calculate_spindle_speed(diameter * 0.8, "rough"),
                "feed_rate": rough_feed,
                "depth_of_cut": rough_depth,
                "coolant": "flood",
                "estimated_time": self._estimate_turning_time(diameter, length, rough_depth, rough_feed),
            })

        if self.operation_profile.get("include_semi_finish"):
            add_operation({
                "name": "Semi-Finish Turning",
                "description": "Stabilize geometry and leave uniform stock for finish turning",
                "type": "turning",
                "tool": "Semi-finish insert (VNMG, R0.4)",
                "spindle_speed": self._calculate_spindle_speed(diameter * 0.95, "finish"),
                "feed_rate": 0.14,
                "depth_of_cut": 0.8 if diameter > 20 else 0.4,
                "coolant": "flood",
                "estimated_time": self._estimate_turning_time(diameter, length, 0.8 if diameter > 20 else 0.4, 0.14),
            })

        # Major feature machining must occur before finish turning.
        pre_finish_order = ["drilling", "boring", "taper_turning", "grooving", "undercut", "threading"]
        for feature_name in pre_finish_order:
            if self._should_include_feature_operation(feature_name, features):
                op = self._build_feature_operation(feature_name, diameter)
                if op:
                    add_operation(op)

        finish_desc = "Achieve final diameter and surface finish after all major profile features"
        if not self.strict_turnable:
            finish_desc = "Localized final finish on turnable regions after feature passes"
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

        if self._should_include_feature_operation("chamfering", features):
            op = self._build_feature_operation("chamfering", diameter)
            if op:
                add_operation(op)

        if self.operation_profile.get("include_parting"):
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
            "drilling": 160,
            "threading": 100,
            "grooving": 150,
            "undercut": 140,
            "taper_turning": 220,
            "chamfering": 240,
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

        feature_types = {
            "threading": "Threading",
            "grooving": "Grooving",
            "boring": "Boring",
            "drilling": "Drilling",
            "taper_turning": "Taper Turning",
            "undercut": "Undercut",
            "chamfering": "Chamfering / Deburring",
        }
        expected_feature_ops = {
            key: self._should_include_feature_operation(key, self.feature_detection)
            for key in feature_types
        }
        has_feature_ops = {
            key: any(op.get("type") == key for op in self.operations)
            for key in feature_types
        }
        has_fine_finish = any(op.get("type") == "finishing" for op in self.operations)
        has_rough = any(op.get("name") == "Rough Turning" for op in self.operations)
        has_semi = any(op.get("name") == "Semi-Finish Turning" for op in self.operations)
        has_finish = any(op.get("name") == "Finish Turning" for op in self.operations)
        has_parting = any(op.get("name") == "Parting Off" for op in self.operations)
        op_index = {op.get("name"): idx for idx, op in enumerate(self.operations)}
        operation_names = [op.get("name", "") for op in self.operations]
        for key, label in feature_types.items():
            has_op = has_feature_ops[key]
            expected_op = expected_feature_ops[key]
            if has_op == expected_op:
                messages.append({
                    "level": "pass",
                    "title": f"{label} Rule",
                    "detail": f"{label} op {'added' if has_op else 'skipped'} based on geometry detection.",
                })
            else:
                messages.append({
                    "level": "fail",
                    "title": f"{label} Rule",
                    "detail": f"{label} operation mismatch against geometry detector.",
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

        facing_first = bool(operation_names and operation_names[0] in {"Facing", "Face & Center"})
        finish_idx = op_index.get("Finish Turning", -1)
        fine_finish_idx = op_index.get("Fine Finish Pass", finish_idx)
        core_sequence = [name for name in ("Rough Turning", "Semi-Finish Turning", "Finish Turning") if name in op_index]
        rough_before_finish = ("Rough Turning" not in op_index) or (op_index["Rough Turning"] < finish_idx)
        semi_before_finish = ("Semi-Finish Turning" not in op_index) or (op_index["Semi-Finish Turning"] < finish_idx)
        core_order_ok = bool(
            has_finish
            and core_sequence == sorted(core_sequence, key=lambda name: op_index[name])
            and rough_before_finish
            and semi_before_finish
        )
        pre_finish_feature_names = {"Drilling", "Boring", "Taper Turning", "Grooving", "Undercut", "Threading"}
        post_finish_feature_names = {"Chamfering / Deburring"}
        pre_feature_indices = [idx for name, idx in op_index.items() if name in pre_finish_feature_names]
        post_feature_indices = [idx for name, idx in op_index.items() if name in post_finish_feature_names]
        pre_features_before_finish = all(idx < finish_idx for idx in pre_feature_indices) if finish_idx >= 0 else False
        post_features_after_finish = all(idx > fine_finish_idx for idx in post_feature_indices) if post_feature_indices else True
        parting_last = ("Parting Off" not in op_index) or (op_index["Parting Off"] == len(self.operations) - 1)

        if facing_first and core_order_ok and pre_features_before_finish and post_features_after_finish and parting_last:
            messages.append({
                "level": "pass",
                "title": "Operation Sequence",
                "detail": "Sequence follows facing -> rough/semi -> feature machining -> finish -> chamfer/deburr -> parting.",
            })
        else:
            messages.append({
                "level": "fail",
                "title": "Operation Sequence",
                "detail": "Operation order violates turning rules (facing first, pre-finish features before finish, chamfer after finish, parting last).",
            })

        expected_rough = bool(self.operation_profile.get("include_rough"))
        expected_semi = bool(self.operation_profile.get("include_semi_finish"))
        expected_parting = bool(self.operation_profile.get("include_parting"))
        expected_facing_name = str(self.operation_profile.get("facing_name", "Facing"))
        facing_mode_ok = bool(operation_names and operation_names[0] == expected_facing_name)
        if (
            has_rough == expected_rough
            and has_semi == expected_semi
            and has_parting == expected_parting
            and facing_mode_ok
        ):
            messages.append({
                "level": "pass",
                "title": "Scope Profile",
                "detail": f"Operation profile matches {self.operation_profile.get('scope', 'unknown')} turning scope.",
            })
        else:
            messages.append({
                "level": "fail",
                "title": "Scope Profile",
                "detail": "Core operation set does not match computed full/partial turning scope profile.",
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
            },
            {
                "tool_id": 7,
                "name": "Drill Tool",
                "type": "Carbide Twist / Center Drill",
                "material": "Carbide",
                "coating": "TiAlN",
                "description": "For center drilling and axial drilling operations"
            },
            {
                "tool_id": 8,
                "name": "Chamfer Tool",
                "type": "45 Degree Chamfer Insert",
                "material": "Carbide",
                "coating": "TiN",
                "description": "For chamfering and deburring finishing edges"
            }
        ]

        op_types = {op.get("type") for op in self.operations}
        filtered: List[Dict] = []
        for tool in tools:
            name = tool["name"]
            if name == "Boring Insert" and "boring" not in op_types:
                continue
            if name == "Threading Insert" and "threading" not in op_types:
                continue
            if name == "Grooving Insert" and "grooving" not in op_types:
                continue
            if name == "Drill Tool" and "drilling" not in op_types:
                continue
            if name == "Chamfer Tool" and "chamfering" not in op_types:
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
            "operation_profile": self.operation_profile,
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
    allow_demo_mode: bool = False,
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
        allow_demo_mode: If True, allow mock analysis when OCP is unavailable.
        material_profile: Workpiece material profile used for speed logic.
        machine_profile: Lathe machine profile used for RPM limits.
        tolerance_mm: Optional dimensional tolerance target in mm.
        surface_roughness_ra: Optional Ra target in um.
    
    Returns:
        Dictionary with plan results.
    """
    cache_key = _build_plan_cache_key(
        step_file=step_file,
        model=model,
        with_ai=with_ai,
        save_json=save_json,
        allow_demo_mode=allow_demo_mode,
        material_profile=material_profile,
        machine_profile=machine_profile,
        tolerance_mm=tolerance_mm,
        surface_roughness_ra=surface_roughness_ra,
    )
    cached = _cache_get(cache_key)
    if cached is not None:
        print(f"Using cached turning plan: {Path(step_file).name}")
        return cached

    print(f"Analyzing STEP file for turning feasibility: {step_file}")

    # Analyze the STEP file.
    print("  Running geometry analysis...")
    analysis = analyze_step_file(step_file, allow_demo_mode=allow_demo_mode)

    if not analysis.get("success"):
        print(f"  Analysis failed: {analysis.get('error')}")
        failed = {
            "success": False,
            "error": analysis.get("error"),
            "demo_mode": bool(analysis.get("demo_mode", False)),
        }
        _cache_put(cache_key, failed)
        return failed

    print("  Analysis complete")

    # Create process plan.
    print("\nGenerating turning process plan...")
    plan = TurningProcessPlan(
        analysis,
        model=model,
        material_profile=material_profile,
        machine_profile=machine_profile,
        tolerance_mm=tolerance_mm,
        surface_roughness_ra=surface_roughness_ra,
    )

    turning_data = analysis.get("machinability", {}).get("turning", {})
    dimensions = plan._format_dimensions()
    strict_checks = turning_data.get("strict_checks", {}) or {}
    failing_checks = [k for k, passed in strict_checks.items() if not passed]
    check_reason_map = {
        "axisymmetric_xy": "Part envelope is not axisymmetric enough for full turning-only processing.",
        "turnable_majority": "Rotational features are not dominant enough to justify turning-first process planning.",
        "small_asymmetry_ok": "Asymmetric/freeform detail is too high for a clean turning route.",
        "cylindrical_dominance": "Cylindrical content is too low for a robust turning workflow.",
        "circular_edge_support": "Circular edge evidence is weak for rotational manufacturing.",
        "limited_complexity": "Freeform/complex surfaces indicate non-turning features (milling/grinding likely needed).",
        "reasonable_aspect_ratio": "Part proportions are outside safe turning-focused envelope.",
    }
    limitation_reasons = [check_reason_map.get(k, k) for k in failing_checks]

    # Check if machinable for turning.
    if not plan.is_machinable:
        recommended = analysis.get("recommended_process") or "3_axis_milling"
        recommended_text = str(recommended).replace("_", " ")
        alternatives = analysis.get("alternative_processes", [])
        turning_reasons = analysis.get("machinability", {}).get("turning", {}).get("reasons", [])
        print(f"  Part NOT strictly suitable for turning (score: {plan.turning_score}/100)")
        print(f"  Recommended process: {recommended}")
        failed = {
            "success": False,
            "error": "Part is not strictly turnable for CAPP turning workflow.",
            "demo_mode": bool(analysis.get("demo_mode", False)),
            "turning_score": plan.turning_score,
            "strict_turnable": False,
            "partial_turnable": False,
            "turning_scope": "none",
            "recommended_process": recommended,
            "alternative_processes": alternatives,
            "turning_gate_reasons": turning_reasons,
            "turning_limitations": limitation_reasons,
            "dimensions": dimensions,
            "recommendation": f"Use {recommended_text} instead of turning.",
        }
        _cache_put(cache_key, failed)
        return failed

    if plan.strict_turnable:
        print(f"  Part suitable for full turning CAPP (score: {plan.turning_score}/100)")
    else:
        print(f"  Part is partially turnable; generating limited turning CAPP (score: {plan.turning_score}/100)")

    # Generate operations.
    print("  Generating turning operations...")
    plan.generate_operations()
    print(f"  Generated {len(plan.operations)} operations")

    # Generate tool list.
    print("  Generating required tools...")
    plan.generate_tool_list()
    print(f"  Listed {len(plan.tools)} turning tools")

    # Run validation checks.
    print("  Running rule and machine capability validation...")
    plan.run_validation_checks()
    print(f"  Validation status: {plan.validation.get('status', 'unknown')}")

    # Generate AI recommendations if requested.
    if with_ai:
        print("  Generating AI optimization recommendations...")
        set_model(model)
        plan.generate_ai_recommendations()

    # Save JSON if requested.
    json_file = None
    if save_json:
        print("  Saving plan to JSON...")
        json_file = plan.save_as_json()
        print(f"  Saved to: {json_file}")

    # Generate report.
    report = plan.generate_report()

    result = {
        "success": True,
        "step_protocol": analysis.get("step_protocol", "Unknown"),
        "step_schema": analysis.get("step_schema", "Unknown"),
        "legacy_step": analysis.get("legacy_step", "unknown"),
        "demo_mode": bool(analysis.get("demo_mode", False)),
        "strict_turnable": plan.strict_turnable,
        "partial_turnable": plan.partial_turnable,
        "turning_scope": "full" if plan.strict_turnable else "partial",
        "turning_score": plan.turning_score,
        "recommended_process": analysis.get("recommended_process"),
        "alternative_processes": analysis.get("alternative_processes", []),
        "turning_gate_reasons": turning_data.get("reasons", []),
        "turning_limitations": limitation_reasons,
        "strict_checks": turning_data.get("strict_checks", {}),
        "dimensions": dimensions,
        "model_info": analysis.get("model_info", {}),
        "axis_analysis": turning_data.get("axis_analysis", {}),
        "axis_cue_count": turning_data.get("axis_cue_count"),
        "rotational_evidence_ratio": turning_data.get("rotational_evidence_ratio"),
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
        "operation_profile": plan.operation_profile,
        "validation": plan.validation,
    }
    _cache_put(cache_key, result)
    return result


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

