# CAPP Turning Planner - Testing Checklist

This document provides a comprehensive testing checklist to verify all functionality works correctly.

## Pre-Test Setup

### Environment

- [ ] Python 3.12+ installed and on PATH
- [ ] Virtual environment created: `venv312`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Ollama installed and working
- [ ] Test STEP files available

### Test Files

Use these STEP files for testing (included in repo):
- `head part v1.step` - Standard cylindrical part
- Other STEP files in repo

## Test 1: Basic Application Startup

### Using Direct Python Command

**Test**: `python capp_app.py`

Steps:
1. Open PowerShell in project directory
2. Activate venv: `venv312\Scripts\Activate.ps1`
3. Run: `python capp_app.py`

Expected Results:
- [ ] Application window opens
- [ ] Window title shows "CAPP Turning Planner - Professional Edition"
- [ ] All UI elements visible and responsive
- [ ] No errors in console
- [ ] Status shows "Ready"

### Using Batch Launcher

**Test**: `launch_capp.bat`

Steps:
1. Double-click `launch_capp.bat` from File Explorer
2. Wait for application to launch

Expected Results:
- [ ] Batch file message displays correctly
- [ ] Application window opens
- [ ] Application functions identically to direct Python run
- [ ] Venv is properly activated (batch shows messages)

### Comparison

Expected Results:
- [ ] Both methods launch identical application
- [ ] Both methods display same version/title
- [ ] No functional differences between the two methods

## Test 2: Ollama Health Check

### Ollama Running Normally

**Setup**: Start Ollama with `ollama serve`

Steps:
1. Start application
2. Navigate to "Chat with AI" tab
3. Observe status indicator

Expected Results:
- [ ] Status shows "🟢 Ollama AI is healthy and ready" (or similar green indicator)
- [ ] Chat input is enabled (not grayed out)
- [ ] Available models are accessible

### Ollama Not Running

**Setup**: Stop Ollama before starting app

Steps:
1. Stop Ollama process
2. Start application
3. Navigate to "Chat with AI" tab
4. Observe status indicator

Expected Results:
- [ ] Status shows "🔴 Ollama is not responding" or similar red indicator
- [ ] Chat input is disabled (grayed out)
- [ ] Attempting to send message shows error: "Ollama service is not running"
- [ ] Error message includes instructions to start Ollama

### Health Check Timing

Steps:
1. Start application without Ollama running
2. Wait 5-10 seconds
3. Start Ollama in terminal: `ollama serve`
4. Wait another 5 seconds

Expected Results:
- [ ] Status indicator updates from red to green
- [ ] Chat becomes enabled
- [ ] No need to restart application

## Test 3: File Analysis

### Load STEP File

**Test**: Upload and analyze a STEP file

Steps:
1. Click "📂 Browse & Select STEP File"
2. Select `head part v1.step` from repo
3. Verify file appears in UI
4. Check "✓ Include AI Optimization"
5. Check "💾 Export to JSON"
6. Click "🚀 Analyze & Generate Plan"
7. Wait for analysis to complete

Expected Results:
- [ ] File selection shows filename
- [ ] Status changes to "⏳ Analyzing..."
- [ ] Progress updates appear
- [ ] Analysis completes in <30 seconds
- [ ] Operations table populates with turning operations
- [ ] Tools table shows required tools
- [ ] Summary tab displays analysis results
- [ ] Turning score calculated and displayed
- [ ] AI Recommendations tab shows recommendations (if AI enabled)
- [ ] JSON file created in project directory
- [ ] Chat context updates with file information
- [ ] Initial AI message in Chat tab references analyzed file

### Analyze Without AI Recommendations

Steps:
1. Uncheck "🤖 Include AI Optimization"
2. Repeat analysis

Expected Results:
- [ ] Analysis still completes
- [ ] Operations and tools populated
- [ ] AI Recommendations tab may be empty or show "No recommendations"
- [ ] Analysis time is faster (no AI call)

## Test 4: Chat with AI (Ollama Timeout Testing)

### Normal Response (< 60 seconds)

**Setup**: Ensure Ollama is running with a fast model (e.g., `phi`)

**Test**: Chat with quick question

Steps:
1. Analyze a STEP file first
2. Navigate to Chat tab
3. Type question: "How can I optimize this turning plan?"
4. Click "📤 Send" or press Ctrl+Enter
5. Wait for response

Expected Results:
- [ ] "⏳ Thinking..." appears briefly
- [ ] Response arrives within 60 seconds
- [ ] Chat displays user message and AI response
- [ ] Input field re-enables after response
- [ ] Multiple messages work correctly

### Long Response (60-180 seconds)

**Test**: Chat with complex question that takes longer

Steps:
1. Type detailed question requiring in-depth analysis
2. Send message
3. Monitor response time

Expected Results (with OLLAMA_TIMEOUT=180):
- [ ] Request doesn't time out at 90 seconds
- [ ] Wait up to 180 seconds for response
- [ ] Response arrives and displays correctly
- [ ] No error messages
- [ ] UI remains responsive (no freezing)

### Response Timeout (> 180 seconds)

**Test**: Set aggressive timeout and trigger timeout error

Steps:
1. Set environment variable: `$env:OLLAMA_TIMEOUT="30"`
2. Restart application
3. Send a complex question
4. Wait for timeout

Expected Results:
- [ ] Request times out after ~30 seconds
- [ ] Error message appears: "❌ Error: ... timed out ..."
- [ ] Error message suggests solutions:
  - Check Ollama is running
  - Try increasing OLLAMA_TIMEOUT
- [ ] Input field re-enables
- [ ] Application doesn't crash

### Thread Safety - Rapid Messages

**Test**: Send multiple messages rapidly

Steps:
1. Type message 1, click Send
2. Immediately type message 2, click Send (before response 1 arrives)
3. Repeat 5-10 times
4. Monitor for freezing or errors

Expected Results:
- [ ] Messages queue correctly
- [ ] UI never freezes
- [ ] Responses arrive in order
- [ ] No Tkinter errors in console
- [ ] No "operation not permitted" errors

## Test 5: Ollama Error Handling

### Connection Error (Ollama Not Running)

**Setup**: Stop Ollama

**Test**: Attempt chat

Steps:
1. Stop Ollama
2. Try to send chat message
3. Observe error

Expected Results:
- [ ] Error appears in chat: "❌ Could not connect to Ollama"
- [ ] Instructions included:
  - Install Ollama
  - Start Ollama: `ollama serve`
  - Pull a model
- [ ] UI doesn't crash
- [ ] Can retry after starting Ollama

### Model Not Found

**Setup**: Switch to non-existent model

**Test**: Chat with missing model

Steps:
1. In model selection, manually edit or select non-existent model
2. Try to send message
3. Observe error

Expected Results:
- [ ] Error shows: "Model not found"
- [ ] Available models listed
- [ ] Instructions to pull model: `ollama pull <model>`
- [ ] User can switch model and retry

### Malformed Ollama Response

**Test**: (Advanced) Simulate malformed JSON response

This is difficult to test in normal usage; check logs if error occurs.

Expected Results:
- [ ] Graceful error message
- [ ] No application crash
- [ ] Suggest checking Ollama logs

## Test 6: UI Responsiveness

### While Analysis Running

**Test**: Keep UI responsive during file analysis

Steps:
1. Start large file analysis
2. While analyzing, try to:
   - Switch tabs
   - Scroll tables
   - Type in chat
   - Resize window

Expected Results:
- [ ] All UI elements remain responsive
- [ ] No freezing during analysis
- [ ] Tab switching works smoothly
- [ ] Window resizes without stalling

### While AI Response Coming In

**Test**: Keep UI responsive during long AI response

Steps:
1. Send chat message to AI
2. While waiting for response, try to:
   - Switch tabs
   - Scroll chat history
   - Type another message
   - Resize window

Expected Results:
- [ ] Tab switching immediate
- [ ] Scrolling smooth
- [ ] Can type next message without waiting
- [ ] Window resizing responsive
- [ ] No UI locks up

## Test 7: Environment Variable Configuration

### OLLAMA_TIMEOUT

**Test**: Configure request timeout

Steps:
1. Set: `$env:OLLAMA_TIMEOUT="240"`
2. Restart app
3. Send chat message
4. Verify it waits up to 240 seconds

Expected Results:
- [ ] Timeout behavior respects env var
- [ ] Long responses work with higher timeout

### OLLAMA_ENDPOINT

**Test**: (Advanced) Point to different Ollama instance

Steps:
1. Set: `$env:OLLAMA_ENDPOINT="http://192.168.1.100:11434/api/generate"`
2. Restart app
3. If Ollama running on remote machine, should work

Expected Results:
- [ ] Application tries to connect to specified endpoint
- [ ] Appropriate error if endpoint unreachable

### OLLAMA_MODEL

**Test**: Change default model

Steps:
1. Set: `$env:OLLAMA_MODEL="llama2"`
2. Restart app
3. Model dropdown should show "llama2"

Expected Results:
- [ ] Model changes in UI
- [ ] Chat uses specified model

## Test 8: Installer Build

### Build Process

**Test**: Build the installer

Steps:
```powershell
cd installer
.\build.ps1
```

Expected Results:
- [ ] Script runs without errors
- [ ] Build messages are clear
- [ ] EXE created in `dist\CAPP_Turning_Planner\`
- [ ] EXE size is reasonable (~100-200 MB)
- [ ] Installer created (if Inno Setup available)

### Test Built EXE

**Test**: Run the built executable

Steps:
1. Navigate to `dist\CAPP_Turning_Planner\`
2. Run `CAPP_Turning_Planner.exe`
3. Verify it works identically to source version

Expected Results:
- [ ] EXE launches without errors
- [ ] All functionality works
- [ ] Performance is acceptable
- [ ] Can analyze STEP files
- [ ] Can chat with AI (if Ollama running)

### Test Installer (if created)

**Test**: Run the Windows installer

Steps:
1. Run `dist\CAPP_Turning_Planner_Setup_1.0.0.exe`
2. Follow installer steps
3. Launch from Start Menu or desktop shortcut

Expected Results:
- [ ] Installer runs without errors
- [ ] Application installs to Program Files
- [ ] Start Menu shortcut created
- [ ] Installed EXE launches correctly
- [ ] Uninstall option works

## Test 9: Error Recovery

### Corrupt STEP File

**Test**: Load invalid STEP file

Steps:
1. Try to analyze a text file or corrupt STEP file
2. Observe error handling

Expected Results:
- [ ] Clear error message shown
- [ ] UI shows error in status
- [ ] Application doesn't crash
- [ ] Can try another file

### Out of Memory (Large File)

**Test**: Analyze very large STEP file

Steps:
1. Use large 3D model (> 100 MB)
2. Try to analyze

Expected Results:
- [ ] Reasonable error message if out of memory
- [ ] Application handles gracefully
- [ ] Doesn't cause system freeze

## Test 10: Documentation

### README Files

**Test**: Verify documentation

Steps:
1. Check [README.md](../README.md)
2. Check [installer/README_build_installer.md](README_build_installer.md)
3. Check [installer/versioning.md](versioning.md)

Expected Results:
- [ ] All README files exist and are readable
- [ ] Instructions are clear and accurate
- [ ] Build steps work as documented
- [ ] Troubleshooting section helpful

## Test Summary Report

Use this template to document test results:

```
CAPP Turning Planner - Test Report
Date: YYYY-MM-DD
Tester: [Name]
Version: [Version Number]

Environment:
- Windows: [10/11]
- Python: [3.12.x]
- Ollama: [Version if installed]

Test Results:
- [ ] Test 1: Application Startup - PASS / FAIL / N/A
- [ ] Test 2: Ollama Health Check - PASS / FAIL / N/A
- [ ] Test 3: File Analysis - PASS / FAIL / N/A
- [ ] Test 4: Chat with AI - PASS / FAIL / N/A
- [ ] Test 5: Error Handling - PASS / FAIL / N/A
- [ ] Test 6: UI Responsiveness - PASS / FAIL / N/A
- [ ] Test 7: Environment Config - PASS / FAIL / N/A
- [ ] Test 8: Installer Build - PASS / FAIL / N/A
- [ ] Test 9: Error Recovery - PASS / FAIL / N/A
- [ ] Test 10: Documentation - PASS / FAIL / N/A

Issues Found:
1. [Description]
2. [Description]

Recommendations:
1. [Suggestion]
2. [Suggestion]

Overall Result: PASS / FAIL
```

## Continuous Testing

For ongoing testing:

1. **Before each release**: Run full checklist
2. **After code changes**: Run affected test sections
3. **On new Python version**: Test full suite
4. **On Ollama update**: Test Chat features
5. **On Windows update**: Test installer compatibility

## Automated Testing (Future)

Consider adding:

- Unit tests for `chat_ollama.py` functions
- Integration tests for file analysis
- UI tests with PyAutoGUI
- Performance benchmarks
- Regression testing

```python
# Example: Test health check
import unittest
from chat_ollama import ollama_health_check

class TestOllamaIntegration(unittest.TestCase):
    def test_health_check_running(self):
        # Requires Ollama to be running
        assert ollama_health_check() == True
    
    def test_health_check_timeout(self):
        # Should not hang
        result = ollama_health_check(timeout=2)
        assert isinstance(result, bool)
```

## Support

If tests fail:

1. Check error messages carefully
2. Review relevant documentation
3. Check console output for stack traces
4. Ensure all prerequisites are installed
5. Try restarting Ollama and application
6. Check GitHub issues for similar problems
7. Create detailed bug report with test results
