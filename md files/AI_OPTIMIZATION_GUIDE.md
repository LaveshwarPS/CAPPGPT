# AI Optimization Guide for CAPP Turning Planner

## Quick Start: Enable AI Optimization

### 1. **Basic AI Optimization (Via CLI)**
```powershell
# Generate turning plan WITH AI recommendations
echo "2" | python step_analyzer.py model.step --capp-turning --ai

# Or with saving to JSON
echo "2" | python step_analyzer.py model.step --capp-turning --ai --save
```

### 2. **What the AI Optimizes**
The AI recommendations cover:
- ✅ **Tool Selection Improvements** - Better tool choices for surface finish
- ✅ **Speed/Feed Optimization** - Adjusted RPM and feed rates for better efficiency
- ✅ **Coolant Strategy** - Optimal coolant types and application methods
- ✅ **Setup Considerations** - Better workpiece holding and alignment
- ✅ **Quality Improvements** - Surface finish and dimensional accuracy tips

---

## Advanced: Programmatic AI Optimization

### 3. **Using Python API with Enhanced AI**
```python
from capp_turning_planner import generate_turning_plan

# With AI optimization enabled
result = generate_turning_plan(
    step_file="clo v1 (1).step",
    model="phi",              # Ollama model
    with_ai=True,             # Enable AI recommendations
    save_json=True            # Save to JSON
)

# Print recommendations
if result["success"]:
    print(result["ai_recommendations"])
```

### 4. **Access Detailed AI Recommendations**
```python
from capp_turning_planner import TurningProcessPlan
from step_analyzer import analyze_step_file

# Analyze STEP file
analysis = analyze_step_file("clo v1 (1).step")

# Create process plan
plan = TurningProcessPlan(analysis, model="phi")
plan.generate_operations()
plan.generate_tool_list()

# Generate AI recommendations
recommendations = plan.generate_ai_recommendations(timeout=30)

# Access specific recommendations
optimizations = recommendations.get("optimizations")
print(optimizations)
```

---

## Enhanced AI Optimization Features

### 5. **Custom AI Prompts (Advanced)**
You can modify the AI prompt in `capp_turning_planner.py` to get specific optimizations:

**Current prompt location:** Lines 360-390 in `capp_turning_planner.py`

**Example: Modify for cost optimization**
```python
# In generate_ai_recommendations() method:
prompt = f"""Review this turning process plan for a lathe operation:

Part Specifications:
  - Diameter: {dimensions['diameter']:.1f} mm
  - Length: {dimensions['length']:.1f} mm
  - Cylindrical faces: {self.analysis.get('cylindrical_faces', 0)}
  - Machinability score: {self.turning_score}/100

Planned Operations:
{operations_summary}

FOCUS ON COST REDUCTION:
1. Which operations can be eliminated?
2. Can tool changes be reduced?
3. Suggest faster but acceptable speed/feed combinations
4. Recommend single-tool operations where possible
5. Cost-benefit analysis"""
```

---

## Optimization Results Interpretation

### 6. **Understanding AI Recommendations Output**

The AI will provide recommendations like:

```
🤖 AI OPTIMIZATION RECOMMENDATIONS:
────────────────────────────────────────────────────────────────────────────────
1. Tool Selection Improvements:
   - Consider VNMG carbide inserts for better finish
   - Use specialized facing tools for better flat surfaces

2. Speed/Feed Optimization:
   - Increase spindle speed 15% for same surface finish
   - Reduce feed rate on finish operation for precision

3. Coolant Strategy:
   - Switch to MQL (Minimum Quantity Lubrication) to reduce cost
   - Use through-spindle coolant for boring operation

4. Setup Considerations:
   - Use soft jaws to prevent part marking
   - Implement live center for better stability

5. Quality Improvements:
   - Add super finishing operation for <0.4µm Ra finish
   - Reduce vibration through optimized tool lengths
```

---

## Step-by-Step: Using AI Optimization

### 7. **Complete Workflow**

```powershell
# Step 1: Activate virtual environment
cd "C:\Users\Adm\Desktop\CAPP-AI project"
.\.venv\Scripts\Activate.ps1

# Step 2: Run with AI optimization
echo "2" | python step_analyzer.py model.step --capp-turning --ai --save

# Output includes:
# ✅ Standard process plan (7 operations)
# ✅ AI-generated recommendations
# ✅ JSON file with all data
```

### 8. **Extract AI Recommendations from JSON**
```powershell
# After running with --save, parse the JSON:
# File will be: "clo v1 (1)_turning_plan.json"

python -c "
import json
with open('clo v1 (1)_turning_plan.json') as f:
    plan = json.load(f)
    print('AI RECOMMENDATIONS:')
    print(plan['ai_recommendations'].get('optimizations', 'N/A'))
"
```

---

## Command Reference

| Command | Purpose |
|---------|---------|
| `python step_analyzer.py model.step --capp-turning` | Generate basic plan (NO AI) |
| `python step_analyzer.py model.step --capp-turning --ai` | Generate plan WITH AI recommendations |
| `python step_analyzer.py model.step --capp-turning --ai --save` | Generate plan, AI recommendations, AND save JSON |
| `python step_analyzer.py model.step --capp-turning --save` | Generate plan and save JSON (no AI) |

---

## Troubleshooting AI Optimization

### 9. **AI Not Responding**

**Problem:** "Error: timeout" or Ollama connection errors

**Solution:**
```powershell
# 1. Check if Ollama is running
# 2. Increase timeout in command:
echo "2" | python step_analyzer.py model.step --capp-turning --ai

# 3. Or modify timeout in code (capp_turning_planner.py, line ~385):
# Change: timeout=30  →  timeout=60
```

### 10. **AI Recommendations are Generic**

**Problem:** Recommendations are not specific enough

**Solution:**
Edit the AI prompt in `capp_turning_planner.py` (lines 375-390) to be more specific:

```python
# Add material specifications
prompt = f"""Review this turning process plan for {material_type} material:

Part Specifications:
  - Material: Aluminum 6061-T6  # <-- Add material
  - Diameter: {dimensions['diameter']:.1f} mm
  - Length: {dimensions['length']:.1f} mm
  
Prioritize:
1. Chip evacuation challenges for this material
2. Thermal management requirements
3. Tool wear considerations"""
```

---

## Using AI for Multi-Part Optimization

### 11. **Batch Process Multiple Parts with AI**

Create `optimize_batch.py`:

```python
from capp_turning_planner import generate_turning_plan
from pathlib import Path
import json

step_files = [
    "clo v1 (1).step",
    "head part v1 (1).step",
    "smol gear v1.step"
]

results = []

for step_file in step_files:
    print(f"\n📊 Processing: {step_file}")
    result = generate_turning_plan(
        step_file=step_file,
        model="phi",
        with_ai=True,
        save_json=True
    )
    
    if result["success"]:
        results.append({
            "file": step_file,
            "score": result["turning_score"],
            "ai_recommendations": result["ai_recommendations"],
            "operations_count": len(result["operations"])
        })
        
        # Print AI recommendations
        print("\n🤖 AI Recommendations:")
        print(result["ai_recommendations"].get("optimizations"))

# Save batch results
with open("batch_optimization_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✅ Batch optimization complete!")
```

Run it:
```powershell
python optimize_batch.py
```

---

## Performance Tips

### 12. **Optimization Best Practices**

1. **Use appropriate model**: phi is fast, but llama2 might be more detailed
2. **Set timeout wisely**: 30 seconds for phi, 60 for larger models
3. **Cache results**: Save JSON output to avoid re-analysis
4. **Batch similar parts**: Run similar parts together for faster AI processing

---

## Output Examples

### 13. **Real AI Recommendations (Examples)**

For a small cylindrical part:
```
Speed/Feed Optimization:
- Current: 1,455 RPM at 0.1 mm/rev
- Suggested: 1,600 RPM at 0.15 mm/rev (25% faster)
- Benefit: Reduces machining time by 20% with similar finish
```

For a part with threading:
```
Tool Selection:
- Current: Generic threading insert
- Suggested: Specialized solid carbide threading tool
- Benefit: Improves thread accuracy to ±0.05 mm tolerance
```

---

## Next Steps

1. ✅ Run a CAPP analysis with `--ai` flag
2. ✅ Review AI recommendations in the console output
3. ✅ Save results with `--save` to JSON for documentation
4. ✅ Modify prompts in `capp_turning_planner.py` for specific optimization goals
5. ✅ Create batch optimization scripts for multiple parts

---

**Questions?** Check the console output for specific AI recommendations for your part.
