╔════════════════════════════════════════════════════════════════════════════╗
║         CAPP TURNING PROCESS PLANNER - USER GUIDE                         ║
╚════════════════════════════════════════════════════════════════════════════╝

📋 WHAT IS CAPP?
════════════════════════════════════════════════════════════════════════════

CAPP (Computer-Aided Process Planning) is an automated system that:

✓ Analyzes STEP files for turning feasibility
✓ Generates complete turning operation sequences
✓ Recommends optimized cutting parameters (speeds, feeds, depth of cut)
✓ Lists all required turning tools with specifications
✓ Generates AI-powered optimization recommendations (with Ollama)
✓ Exports detailed process plans to JSON format

KEY FEATURE: Only generates process plans for parts that are suitable for
             turning (machinability score >= 40/100). For unsuitable parts,
             it recommends alternative manufacturing methods.


🚀 QUICK START
════════════════════════════════════════════════════════════════════════════

BASIC USAGE:
  python step_analyzer.py model.step --capp-turning

WITH AI RECOMMENDATIONS:
  python step_analyzer.py model.step --capp-turning --ai

SAVE PROCESS PLAN TO JSON:
  python step_analyzer.py model.step --capp-turning --save

COMBINED (AI + Save):
  python step_analyzer.py model.step --capp-turning --ai --save


💻 PYTHON CODE USAGE
════════════════════════════════════════════════════════════════════════════

from capp_turning_planner import generate_turning_plan

# Generate basic process plan
result = generate_turning_plan("model.step")
if result['success']:
    print(result['report'])
else:
    print(f"Not suitable for turning: {result['error']}")
    print(f"Score: {result['turning_score']}/100")

# With AI recommendations
result = generate_turning_plan("model.step", with_ai=True)

# Save to JSON file
result = generate_turning_plan("model.step", with_ai=True, save_json=True)
print(f"Plan saved to: {result['json_file']}")


📊 PROCESS PLAN CONTENTS
════════════════════════════════════════════════════════════════════════════

The generated turning process plan includes:

1. MACHINABILITY ASSESSMENT
   • Turning score (0-100)
   • Suitability determination
   • Score rationale

2. PART DIMENSIONS
   • Diameter (mm)
   • Length (mm)
   • Volume (mm³)

3. OPERATION SEQUENCE (typically 7 operations)
   • Operation #1: Face & Center (alignment)
   • Operation #2: Rough Turning (material removal)
   • Operation #3: Finish Turning (final diameter)
   • Operation #4: Boring (internal features)
   • Operation #5: Threading (if applicable)
   • Operation #6: Grooving (stress relief)
   • Operation #7: Parting Off (separation)

   Each operation includes:
   - Tool specification
   - Spindle speed (RPM)
   - Feed rate (mm/rev)
   - Depth of cut (mm)
   - Coolant type
   - Estimated time (minutes)

4. REQUIRED TOOLS
   • Facing inserts
   • Turning inserts
   • Boring inserts
   • Threading inserts
   • Grooving inserts
   • Parting blades

5. AI RECOMMENDATIONS (if enabled)
   • Process optimizations
   • Tool selection improvements
   • Speed/feed optimization
   • Coolant strategy
   • Setup considerations
   • Quality improvements

6. SETUP NOTES
   • Chuck/collet mounting
   • Spindle spin-up procedure
   • Coolant application
   • Tool alignment
   • Monitoring procedures


⚙️ TURNING MACHINABILITY SCORING
════════════════════════════════════════════════════════════════════════════

The CAPP system evaluates turning suitability based on:

✓ CYLINDRICAL SURFACES (50+ points)
  • High percentage = suitable for rotational machining
  • Each cylindrical face indicates turning potential

✓ CIRCULAR EDGES (20 points)
  • More circular edges = better for spinning operations
  • Linear edges = more difficult to turn

✗ COMPLEX SURFACES (-40 points)
  • Bezier/B-spline surfaces = challenging for traditional turning
  • These surfaces may require 5-axis CNC or other methods

• PART SIZE (10 points)
  • Smaller parts = suitable for standard lathes

SCORING THRESHOLDS:
  • 70+   = High feasibility for turning
  • 40-70 = Medium feasibility (possible with custom setup)
  • <40   = Low feasibility (recommend alternatives)

MINIMUM THRESHOLD: 40/100
  Parts scoring below 40 will NOT generate a turning plan.
  Instead, CAPP recommends alternative processes.


🔧 CUTTING PARAMETERS (Auto-Calculated)
════════════════════════════════════════════════════════════════════════════

SPINDLE SPEED (RPM) Formula:
  RPM = (1000 × SFM) / (π × diameter_mm)
  
  Where SFM (Surface Feet per Minute) varies by operation:
  • Facing:    250 SFM
  • Rough:     200 SFM
  • Finish:    300 SFM
  • Boring:    180 SFM
  • Threading:  100 SFM
  • Grooving:   150 SFM
  • Parting:    120 SFM

FEED RATE (mm/rev) - Set by operation type:
  • Facing:    0.15 mm/rev
  • Rough:     0.20 mm/rev
  • Finish:    0.10 mm/rev
  • Boring:    0.12 mm/rev
  • Threading: 0.5 mm/rev (pitch-dependent)
  • Grooving:  0.15 mm/rev
  • Parting:   0.08 mm/rev

DEPTH OF CUT (mm) - Material removal per pass:
  • Rough:     2.0 mm (aggressive removal)
  • Finish:    0.5 mm (light finishing)
  • Boring:    1.0 mm (controlled internal machining)


📈 ESTIMATED MACHINING TIME
════════════════════════════════════════════════════════════════════════════

Formula:
  Total Time = Σ(length / (RPM × feed) + tool_change_time)

Factors affecting time:
  • Part diameter (affects RPM)
  • Part length (more material = more time)
  • Depth of cut (multiple passes = more time)
  • Feed rate (lower = more time)
  • Number of operations (tool changes add time)

Typical times:
  • Small turning (10-20mm dia, 50mm long): 10-20 minutes
  • Medium turning (30-50mm dia, 100mm long): 30-60 minutes
  • Large turning (100mm dia, 200mm long): 60-120+ minutes

Note: Times are estimates. Actual times depend on machine and operator skill.


🎯 WHEN TO USE CAPP TURNING
════════════════════════════════════════════════════════════════════════════

✅ IDEAL PARTS FOR TURNING:
  • Cylindrical shafts
  • Sleeve components
  • Disk-like parts
  • Parts with circular edges
  • Rotational features
  • Parts with 60%+ cylindrical surfaces

⚠️ MARGINAL PARTS (Medium score 40-70):
  • Parts with mixed features
  • Cylindrical + flat surfaces
  • Parts requiring secondary operations
  • Parts with some complex surfaces

❌ NOT SUITABLE FOR TURNING:
  • Parts with complex 3D surfaces
  • Highly rectangular/boxy parts
  • Parts with <30% cylindrical surfaces
  • Parts with many sharp angles
  • Freeform surfaces


🤖 AI OPTIMIZATION (With --ai Flag)
════════════════════════════════════════════════════════════════════════════

When using --ai flag, the CAPP system:

1. Analyzes the process plan with Ollama (phi model)
2. Generates optimization recommendations for:
   • Tool selection improvements
   • Feed/speed optimization for better finish
   • Coolant strategy (flood vs. mist vs. dry)
   • Setup efficiency improvements
   • Quality monitoring tips

Example:
  python step_analyzer.py model.step --capp-turning --ai

This provides expert-level manufacturing recommendations based on
the specific geometry of your part.


📄 JSON REPORT FORMAT
════════════════════════════════════════════════════════════════════════════

With --save flag, generates JSON file with structure:

{
  "metadata": {
    "generator": "CAPP Turning Planner",
    "date": "2025-11-12T10:30:00.000000",
    "part_file": "model.step"
  },
  "machinability": {
    "score": 75,
    "suitable_for_turning": true
  },
  "dimensions": {
    "diameter": 50.5,
    "length": 100.2,
    "volume": 200000.0,
    "x_size": 50.5,
    "y_size": 50.5,
    "z_size": 100.2
  },
  "operations": [
    {
      "operation_id": 1,
      "name": "Face & Center",
      "type": "facing",
      "tool": "Facing insert (CNMG)",
      "spindle_speed": 3500,
      "feed_rate": 0.15,
      "depth_of_cut": 1.0,
      "coolant": "flood",
      "estimated_time": 2.0
    },
    ...
  ],
  "tools": [
    {
      "tool_id": 1,
      "name": "Facing Insert",
      "type": "CNMG 432 M0804",
      "material": "Carbide",
      "coating": "TiAlN"
    },
    ...
  ],
  "ai_recommendations": {
    "optimizations": "Based on the geometry..."
  }
}


🔍 EXAMPLES
════════════════════════════════════════════════════════════════════════════

EXAMPLE 1: Generate basic plan
  $ python step_analyzer.py shaft.step --capp-turning
  
  Output:
  ✅ Part suitable for turning (score: 85/100)
  ✅ Generated 7 operations
  ✅ Listed 6 turning tools
  [Full process plan displayed]

EXAMPLE 2: Plan + AI + Save
  $ python step_analyzer.py bushing.step --capp-turning --ai --save
  
  Output:
  ✅ Part suitable for turning (score: 75/100)
  ✅ Generated 7 operations
  ✅ Listed 6 turning tools
  ⏳ Generating AI optimization recommendations...
  ✅ AI recommendations generated
  ⏳ Saving plan to JSON...
  ✅ Saved to: bushing_turning_plan.json
  [Full process plan displayed]

EXAMPLE 3: Not suitable for turning
  $ python step_analyzer.py complex.step --capp-turning
  
  Output:
  ❌ Part NOT suitable for turning (score: 25/100)
  ⚠️  This part is better suited for other manufacturing methods
  💡 Consider 3-axis milling or 3D printing instead


⚡ PERFORMANCE
════════════════════════════════════════════════════════════════════════════

Time to generate process plan:
  • Analysis: 2-5 seconds
  • Operations generation: <1 second
  • Tool list: <1 second
  • With AI (--ai): 30-60 seconds additional
  • Save to JSON: <1 second

Total: 2-5 seconds (basic) or 35-65 seconds (with AI)


🛠️ ADVANCED USAGE
════════════════════════════════════════════════════════════════════════════

PROGRAMMATIC API:

from capp_turning_planner import TurningProcessPlan
from step_analyzer import analyze_step_file

# Manual process plan creation
analysis = analyze_step_file("model.step")
plan = TurningProcessPlan(analysis, model="phi")

# Check if machinable
if plan.is_machinable:
    plan.generate_operations()
    plan.generate_tool_list()
    
    # Access plan data
    for op in plan.operations:
        print(f"{op['name']}: {op['spindle_speed']} RPM")
    
    # Generate recommendations
    plan.generate_ai_recommendations()
    
    # Save plan
    json_file = plan.save_as_json()
    
    # Get report
    report = plan.generate_report()
    print(report)


📊 COMPARISON WITH ALTERNATIVES
════════════════════════════════════════════════════════════════════════════

METHOD              | SCORE | TIME | COST | COMPLEXITY
─────────────────────────────────────────────────────
Turning (CAPP)      | ★★★★★ | Fast | Low  | Low
3-Axis Milling      | ★★★☆☆ | Med  | Med  | Medium
5-Axis CNC          | ★★★★☆ | Slow | High | High
3D Printing         | ★★★★☆ | Slow | Med  | Low
Manual Planning     | ★★☆☆☆ | Very | Low  | Very High


❓ FREQUENTLY ASKED QUESTIONS
════════════════════════════════════════════════════════════════════════════

Q: Why is my part getting a low turning score?
A: Low scores indicate complex surfaces not suitable for traditional turning.
   Consider: 3-axis milling, 5-axis CNC, or 3D printing.

Q: Can I modify the generated operations?
A: Yes! Edit the JSON file or modify capp_turning_planner.py for customization.

Q: How accurate are the spindle speeds?
A: Speeds are calculated using standard machining formulas for steel. Adjust
   based on your specific material and machine capabilities.

Q: Why is AI generating different recommendations each time?
A: The Ollama model generates varied responses based on probability. This is
   normal for AI systems. The recommendations are good starting points.

Q: Can I use this for other materials besides steel?
A: Yes, but adjust the SFM values in capp_turning_planner.py:
   - Aluminum: 1.5x speed
   - Titanium: 0.5x speed
   - Stainless: 0.75x speed


📞 SUPPORT
════════════════════════════════════════════════════════════════════════════

For issues or questions:
  1. Check turning machinability score (must be >= 40)
  2. Verify STEP file is valid (try basic analysis first)
  3. Ensure all modules are in the same directory
  4. Try with --ai flag for optimization recommendations
  5. Save JSON file for detailed inspection


═════════════════════════════════════════════════════════════════════════════

🎉 Ready to automate your turning process planning! 🎉

═════════════════════════════════════════════════════════════════════════════
