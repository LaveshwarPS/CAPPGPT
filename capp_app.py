"""Professional CAPP GUI Application with Table Display.

Interactive GUI application for uploading STEP files and viewing
process plans in a formatted table interface.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from pathlib import Path
import json
from datetime import datetime
from typing import Optional, Dict, List
import os
import sys
import subprocess
from queue import Queue
import hashlib

from step_analyzer import analyze_step_file
from capp_turning_planner import generate_turning_plan

try:
    from chat_ollama import (
        query_ollama,
        OllamaError,
        ollama_health_check,
        get_available_models,
    )
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Configuration from environment variables
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "180"))
OLLAMA_AI_TIMEOUT = int(os.getenv("OLLAMA_AI_TIMEOUT", "120"))
TRAINING_DATA_DIR = Path.home() / ".capp_training_data"


class CAPPApplication:
    """Professional CAPP GUI Application."""
    
    def __init__(self, root):
        """Initialize the application.
        
        Args:
            root: Tkinter root window.
        """
        self.root = root
        self.root.title("CAPP Turning Planner - Professional Edition")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 700)
        
        self.selected_file = None
        self.analysis_result = None
        self.is_processing = False
        self.chat_history = []  # Store conversation history
        self.model_analysis = None  # Store current model analysis
        
        # Thread-safe UI update queue for chat messages
        self.chat_queue = Queue()
        self.ollama_status = "checking"  # checking, healthy, unavailable
        
        # Initialize training data directory
        self._init_training_data_dir()
        
        # Configure style
        self._configure_styles()
        self._setup_ui()
        
        # Start Ollama health check in background
        if OLLAMA_AVAILABLE:
            threading.Thread(target=self._check_ollama_health, daemon=True).start()
    
    def _init_training_data_dir(self):
        """Initialize training data directory."""
        TRAINING_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def _check_ollama_health(self):
        """Check Ollama health in background thread."""
        try:
            if ollama_health_check(timeout=5):
                self.ollama_status = "healthy"
                status_text = "🟢 Ollama AI is healthy and ready"
            else:
                self.ollama_status = "unavailable"
                status_text = "🔴 Ollama is not responding. Click Chat tab for details."
        except Exception:
            self.ollama_status = "unavailable"
            status_text = "🔴 Ollama is not available. Click Chat tab for details."
        
        # Update status label on main thread
        self.root.after(0, lambda: self._update_ollama_status_label(status_text))
    
    def _update_ollama_status_label(self, status_text: str):
        """Update Ollama status label (main thread)."""
        try:
            self.ollama_status_label.config(text=status_text)
        except:
            pass
    
    def _configure_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        bg_color = "#f0f0f0"
        header_color = "#2c3e50"
        accent_color = "#3498db"
        success_color = "#27ae60"
        error_color = "#e74c3c"
        
        style.configure("Header.TFrame", background=header_color)
        style.configure("Header.TLabel", background=header_color, foreground="white")
        style.configure("Content.TFrame", background=bg_color)
        
    def _setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header(main_container)
        
        # Content area with two columns
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Upload and options
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        self._create_upload_panel(left_panel)
        
        # Right panel - Results table
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self._create_results_panel(right_panel)
    
    def _create_header(self, parent):
        """Create header section."""
        header_frame = ttk.Frame(parent, style="Header.TFrame", height=70)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="🔧 CAPP Turning Process Planner",
            style="Header.TLabel",
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Upload STEP files and generate optimized turning process plans",
            style="Header.TLabel",
            font=("Arial", 10)
        )
        subtitle_label.pack(side=tk.LEFT, padx=20, pady=15)
    
    def _create_upload_panel(self, parent):
        """Create upload and options panel."""
        # Main frame
        main_frame = ttk.LabelFrame(parent, text="📁 File & Options", padding=15)
        main_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(file_frame, text="Selected File:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        self.file_label = ttk.Label(
            file_frame,
            text="No file selected",
            font=("Arial", 9),
            foreground="gray"
        )
        self.file_label.pack(anchor=tk.W, pady=5, fill=tk.X)
        
        # Upload button
        upload_frame = ttk.Frame(main_frame)
        upload_frame.pack(fill=tk.X, pady=(0, 15))
        
        upload_btn = ttk.Button(
            upload_frame,
            text="📂 Browse & Select STEP File",
            command=self._browse_file
        )
        upload_btn.pack(fill=tk.X, pady=5)
        
        clear_btn = ttk.Button(
            upload_frame,
            text="✕ Clear Selection",
            command=self._clear_selection
        )
        clear_btn.pack(fill=tk.X, pady=5)
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Analysis options
        ttk.Label(main_frame, text="Analysis Options:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # AI Recommendations
        self.ai_var = tk.BooleanVar(value=True)
        ai_check = ttk.Checkbutton(
            main_frame,
            text="🤖 Include AI Optimization",
            variable=self.ai_var
        )
        ai_check.pack(anchor=tk.W, pady=5)
        
        # Save JSON
        self.save_var = tk.BooleanVar(value=True)
        save_check = ttk.Checkbutton(
            main_frame,
            text="💾 Export to JSON",
            variable=self.save_var
        )
        save_check.pack(anchor=tk.W, pady=5)
        
        # Model selection
        model_frame = ttk.Frame(main_frame)
        model_frame.pack(anchor=tk.W, pady=10, fill=tk.X)
        
        ttk.Label(model_frame, text="AI Model:", font=("Arial", 9)).pack(side=tk.LEFT)
        
        self.model_var = tk.StringVar(value="phi")
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["phi", "llama2", "neural-chat"],
            state="readonly",
            width=15
        )
        model_combo.pack(side=tk.LEFT, padx=10)
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Action buttons
        ttk.Label(main_frame, text="Actions:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        analyze_btn = ttk.Button(
            main_frame,
            text="🚀 Analyze & Generate Plan",
            command=self._analyze_file
        )
        analyze_btn.pack(fill=tk.X, pady=5)
        
        export_btn = ttk.Button(
            main_frame,
            text="📥 Export Results",
            command=self._export_results
        )
        export_btn.pack(fill=tk.X, pady=5)
        
        # Status
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Arial", 9, "italic"),
            foreground="green"
        )
        self.status_label.pack(anchor=tk.W)
    
    def _create_results_panel(self, parent):
        """Create results table panel."""
        # Title
        ttk.Label(parent, text="📊 Process Plan Results", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Operations
        self.operations_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.operations_frame, text="Operations")
        self._create_operations_table(self.operations_frame)
        
        # Tab 2: Tools
        self.tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tools_frame, text="Tools")
        self._create_tools_table(self.tools_frame)
        
        # Tab 3: Summary
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")
        self._create_summary_display(self.summary_frame)
        
        # Tab 4: AI Recommendations
        self.ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_frame, text="AI Recommendations")
        self._create_ai_display(self.ai_frame)
        
        # Tab 5: Chat with AI
        self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="💬 Chat with AI")
        self._create_chat_display(self.chat_frame)
    
    def _create_operations_table(self, parent):
        """Create operations table."""
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        self.operations_tree = ttk.Treeview(
            tree_frame,
            columns=("Op", "Name", "Type", "Tool", "Speed", "Feed", "DOC", "Time"),
            height=20,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.operations_tree.yview)
        hsb.config(command=self.operations_tree.xview)
        
        # Define columns
        self.operations_tree.column("#0", width=0, stretch=tk.NO)
        self.operations_tree.column("Op", width=35, anchor=tk.CENTER, minwidth=35)
        self.operations_tree.column("Name", width=120, anchor=tk.W, minwidth=100)
        self.operations_tree.column("Type", width=80, anchor=tk.W, minwidth=70)
        self.operations_tree.column("Tool", width=140, anchor=tk.W, minwidth=120)
        self.operations_tree.column("Speed", width=70, anchor=tk.CENTER, minwidth=60)
        self.operations_tree.column("Feed", width=70, anchor=tk.CENTER, minwidth=60)
        self.operations_tree.column("DOC", width=60, anchor=tk.CENTER, minwidth=50)
        self.operations_tree.column("Time", width=70, anchor=tk.CENTER, minwidth=60)
        
        # Define headings
        self.operations_tree.heading("#0", text="", anchor=tk.W)
        self.operations_tree.heading("Op", text="Op")
        self.operations_tree.heading("Name", text="Operation Name")
        self.operations_tree.heading("Type", text="Type")
        self.operations_tree.heading("Tool", text="Tool Specification")
        self.operations_tree.heading("Speed", text="Speed\n(RPM)")
        self.operations_tree.heading("Feed", text="Feed\n(mm/rev)")
        self.operations_tree.heading("DOC", text="DOC\n(mm)")
        self.operations_tree.heading("Time", text="Time\n(min)")
        
        # Pack tree and scrollbars
        self.operations_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
    
    def _create_tools_table(self, parent):
        """Create tools table."""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.tools_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Name", "Type", "Material", "Coating", "Purpose"),
            height=20,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tools_tree.yview)
        hsb.config(command=self.tools_tree.xview)
        
        self.tools_tree.column("#0", width=0, stretch=tk.NO)
        self.tools_tree.column("ID", width=35, anchor=tk.CENTER, minwidth=30)
        self.tools_tree.column("Name", width=100, anchor=tk.W, minwidth=90)
        self.tools_tree.column("Type", width=140, anchor=tk.W, minwidth=120)
        self.tools_tree.column("Material", width=100, anchor=tk.W, minwidth=90)
        self.tools_tree.column("Coating", width=100, anchor=tk.W, minwidth=90)
        self.tools_tree.column("Purpose", width=250, anchor=tk.W, minwidth=200)
        
        self.tools_tree.heading("#0", text="", anchor=tk.W)
        self.tools_tree.heading("ID", text="#")
        self.tools_tree.heading("Name", text="Tool Name")
        self.tools_tree.heading("Type", text="Type/Model")
        self.tools_tree.heading("Material", text="Material")
        self.tools_tree.heading("Coating", text="Coating")
        self.tools_tree.heading("Purpose", text="Purpose")
        
        self.tools_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
    
    def _create_summary_display(self, parent):
        """Create summary display."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create text widget with scrollbar
        scrollbar = ttk.Scrollbar(content_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.summary_text = tk.Text(
            content_frame,
            font=("Courier New", 10),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            bg="#f9f9f9"
        )
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.summary_text.yview)
    
    def _create_ai_display(self, parent):
        """Create AI recommendations display."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(content_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ai_text = tk.Text(
            content_frame,
            font=("Courier New", 9),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            bg="#f9f9f9"
        )
        self.ai_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.ai_text.yview)
    
    def _create_chat_display(self, parent):
        """Create chat interface with AI."""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar with health indicator
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Ollama status indicator (will be updated by background check)
        self.ollama_status_label = ttk.Label(
            status_frame,
            text="🟡 Checking Ollama status...",
            font=("Arial", 9, "bold")
        )
        self.ollama_status_label.pack(anchor=tk.W)
        
        # Chat history display
        history_label = ttk.Label(main_frame, text="💬 Conversation History:", font=("Arial", 9, "bold"))
        history_label.pack(anchor=tk.W, pady=(10, 5))
        
        history_frame = ttk.Frame(main_frame)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        history_scrollbar = ttk.Scrollbar(history_frame)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chat_display = tk.Text(
            history_frame,
            font=("Courier New", 9),
            wrap=tk.WORD,
            yscrollcommand=history_scrollbar.set,
            bg="#fafafa",
            state=tk.DISABLED
        )
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.config(command=self.chat_display.yview)
        
        # Input frame
        input_label = ttk.Label(main_frame, text="📝 Ask about your STEP file:", font=("Arial", 9, "bold"))
        input_label.pack(anchor=tk.W, pady=(10, 5))
        
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X)
        
        self.chat_input = tk.Text(input_frame, height=4, font=("Courier New", 9), wrap=tk.WORD)
        self.chat_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Send button
        send_btn = ttk.Button(
            input_frame,
            text="📤 Send\n(Ctrl+Enter)",
            command=self._send_chat_message
        )
        send_btn.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind Ctrl+Enter to send
        self.chat_input.bind("<Control-Return>", lambda e: self._send_chat_message())
        
        # Info text
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = ttk.Label(
            info_frame,
            text="💡 Tip: Analyze a STEP file first to enable contextual AI discussions about your model",
            font=("Arial", 8, "italic"),
            foreground="gray"
        )
        info_text.pack(anchor=tk.W)
        
        # Initial message
        self._append_chat("🤖 AI Assistant", "Hello! I'm your CAPP AI assistant. Upload and analyze a STEP file, then ask me questions about:\n• Process planning\n• Tool selection\n• Machining parameters\n• Design optimization\n\nWaiting for analysis...")
        
        # Start polling chat queue for thread-safe UI updates
        self._process_chat_queue()
    
    def _append_chat(self, sender: str, message: str):
        """Append message to chat display (thread-safe via queue).
        
        This method is safe to call from background threads.
        The actual UI update is scheduled on the main thread.
        """
        self.chat_queue.put((sender, message))
    
    def _process_chat_queue(self):
        """Process queued chat messages on the main thread (called periodically).
        
        This ensures Tkinter widgets are always updated from the main thread,
        which is a hard requirement in Tkinter.
        """
        try:
            while not self.chat_queue.empty():
                sender, message = self.chat_queue.get_nowait()
                self._append_chat_main_thread(sender, message)
        except Exception:
            pass
        
        # Schedule next check
        self.root.after(100, self._process_chat_queue)
    
    def _append_chat_main_thread(self, sender: str, message: str):
        """Actually append message to chat display (main thread only)."""
        self.chat_display.config(state=tk.NORMAL)
        
        if sender == "🤖 AI Assistant":
            self.chat_display.insert(tk.END, f"\n{sender}:\n")
            self.chat_display.insert(tk.END, f"{message}\n", "ai_response")
            self.chat_display.insert(tk.END, "\n" + "─" * 70 + "\n")
        else:
            self.chat_display.insert(tk.END, f"\n{sender}:\n")
            self.chat_display.insert(tk.END, f"{message}\n", "user_query")
            self.chat_display.insert(tk.END, "\n" + "─" * 70 + "\n")
        
        # Configure tags for styling
        self.chat_display.tag_config("ai_response", foreground="#0066cc", font=("Courier New", 9))
        self.chat_display.tag_config("user_query", foreground="#009900", font=("Courier New", 9, "bold"))
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def _send_chat_message(self):
        """Send chat message to AI."""
        if not OLLAMA_AVAILABLE:
            messagebox.showerror("Error", "Ollama is not installed. Please install Ollama to use chat features.")
            return
        
        if self.ollama_status != "healthy":
            messagebox.showerror(
                "Ollama Not Available",
                "Ollama service is not running or not reachable.\n\n"
                "To use chat features:\n"
                "1. Install Ollama: https://ollama.com/download\n"
                "2. Start Ollama: Run 'ollama serve' or use the Ollama app\n"
                "3. Pull a model: 'ollama pull phi'"
            )
            return
        
        if not self.analysis_result:
            messagebox.showwarning("Warning", "Please analyze a STEP file first to enable AI chat")
            return
        
        message = self.chat_input.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a message")
            return
        
        self.chat_input.delete(1.0, tk.END)
        
        # Disable input while processing
        self.chat_input.config(state=tk.DISABLED)
        
        # Show user message
        self._append_chat("👤 You", message)
        
        # Process in background thread (safe for long-running operations)
        thread = threading.Thread(
            target=self._process_chat_message,
            args=(message,),
            daemon=True
        )
        thread.start()
    
    def _process_chat_message(self, user_message: str):
        """Process chat message with AI in background thread.
        
        This runs in a separate thread to avoid blocking the UI.
        All UI updates are queued and processed on the main thread.
        """
        try:
            # Show thinking indicator
            self._append_chat("🤖 AI Assistant", "⏳ Thinking...")
            
            # Build context from analysis
            context = f"""You are an expert manufacturing engineer with deep knowledge of CAPP (Computer-Aided Process Planning) and turning operations.

CURRENT ANALYSIS CONTEXT:
{self._build_chat_context()}

User's Question: {user_message}

Provide a detailed, technical response based on the analyzed part and your expertise in turning operations."""
            
            # Query Ollama with configurable timeout
            response = query_ollama(
                prompt=context,
                model=self.model_var.get(),
                timeout=OLLAMA_TIMEOUT
            )
            
            # Remove the thinking message placeholder
            # (Note: We can't directly edit from worker thread, so we'll replace with actual response)
            # The queue will handle the UI update safely
            
            self._append_chat("🤖 AI Assistant", response)
            self.chat_history.append((user_message, response))
            
        except OllamaError as e:
            error_msg = f"""❌ Error: {str(e)}

To fix this:
1. Check that Ollama is running
2. Run: ollama serve (if not running)
3. Ensure a model is installed: ollama pull phi
4. For slow models, increase OLLAMA_TIMEOUT environment variable"""
            self._append_chat("🤖 AI Assistant", error_msg)
        
        except Exception as e:
            self._append_chat("🤖 AI Assistant", f"❌ Unexpected error: {str(e)}")
        
        finally:
            # Re-enable input when done
            self.root.after(0, lambda: self.chat_input.config(state=tk.NORMAL))
    
    def _build_chat_context(self) -> str:
        """Build context string from analysis results."""
        if not self.analysis_result:
            return "No analysis available"
        
        result = self.analysis_result
        ops = result.get("operations", [])
        tools = result.get("tools", [])
        total_time = sum(op.get('estimated_time', 0) for op in ops)
        
        context = f"""
File: {Path(self.selected_file).name}
Analysis Complete: Yes

Process Plan Summary:
- Total Operations: {len(ops)}
- Required Tools: {len(tools)}
- Total Machining Time: {total_time:.1f} min
- Turning Score: {result.get('turning_score', 'N/A')}/100

Operations:
{self._format_ops_for_chat(ops)}

Tools Required:
{self._format_tools_for_chat(tools)}
"""
        return context
    
    def _format_ops_for_chat(self, operations: List[Dict]) -> str:
        """Format operations for chat context."""
        if not operations:
            return "  • No operations defined"
        
        text = ""
        for i, op in enumerate(operations, 1):
            spindle_speed = op.get('spindle_speed', 'N/A')
            feed_rate = op.get('feed_rate', 'N/A')
            depth_of_cut = op.get('depth_of_cut', 'N/A')
            estimated_time = op.get('estimated_time', 'N/A')
            
            spindle_str = f"{spindle_speed} RPM" if spindle_speed != 'N/A' else 'N/A'
            feed_str = f"{feed_rate} mm/rev" if feed_rate != 'N/A' else 'N/A'
            doc_str = f"{depth_of_cut} mm" if depth_of_cut != 'N/A' else 'N/A'
            time_str = f"{estimated_time:.1f} min" if estimated_time != 'N/A' else 'N/A'
            
            text += f"  {i}. {op.get('name', 'Unknown')} - {op.get('type', 'Unknown')}: {spindle_str}, Feed {feed_str}, DOC {doc_str}, Time {time_str}\n"
        return text
    
    def _format_tools_for_chat(self, tools: List[Dict]) -> str:
        """Format tools for chat context."""
        if not tools:
            return "  • No tools defined"
        
        text = ""
        for i, tool in enumerate(tools, 1):
            text += f"  {i}. {tool.get('name', 'Unknown')} ({tool.get('type', 'Unknown')})\n"
        return text
    
    def _browse_file(self):
        """Open file browser dialog."""
        file_path = filedialog.askopenfilename(
            title="Select a STEP File",
            filetypes=[
                ("STEP Files", "*.step *.stp"),
                ("All Files", "*.*")
            ],
            initialdir=str(Path.home())
        )
        
        if file_path:
            self.selected_file = file_path
            file_name = Path(file_path).name
            self.file_label.config(text=f"✓ {file_name}")
            self.status_var.set(f"Ready - {file_name} selected")
    
    def _clear_selection(self):
        """Clear file selection."""
        self.selected_file = None
        self.file_label.config(text="No file selected")
        self.status_var.set("Ready")
        self._clear_tables()
    
    def _clear_tables(self):
        """Clear all result tables."""
        # Clear operations tree
        for item in self.operations_tree.get_children():
            self.operations_tree.delete(item)
        
        # Clear tools tree
        for item in self.tools_tree.get_children():
            self.tools_tree.delete(item)
        
        # Clear text displays
        self.summary_text.delete(1.0, tk.END)
        self.ai_text.delete(1.0, tk.END)
    
    def _analyze_file(self):
        """Analyze the selected file."""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a STEP file first")
            return
        
        if self.is_processing:
            messagebox.showwarning("Processing", "Analysis already in progress...")
            return
        
        # Run analysis in background thread
        thread = threading.Thread(target=self._run_analysis, daemon=True)
        thread.start()
    
    def _run_analysis(self):
        """Run analysis in background thread."""
        self.is_processing = True
        self.status_var.set("⏳ Analyzing...")
        self.root.update()
        
        try:
            file_name = Path(self.selected_file).name
            
            # Generate turning plan
            result = generate_turning_plan(
                step_file=self.selected_file,
                model=self.model_var.get(),
                with_ai=self.ai_var.get(),
                save_json=self.save_var.get()
            )
            
            if result["success"]:
                # Store result for chat context
                self.analysis_result = result
                self.chat_history = []  # Reset chat history
                
                # Check if this is a unique case and add to training data
                self._check_and_train_unique_case(result)
                
                # Populate tables and displays
                self._populate_operations(result["operations"])
                self._populate_tools(result["tools"])
                self._populate_summary(result)
                
                if result.get("ai_recommendations"):
                    self._populate_ai(result["ai_recommendations"])
                
                # Reset chat
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete(1.0, tk.END)
                self.chat_display.config(state=tk.DISABLED)
                self._append_chat("🤖 AI Assistant", f"✅ Analysis complete! I now have context about '{file_name}'.\n\nAsk me anything about:\n• Process optimization\n• Tool recommendations\n• Machining parameters\n• Design improvements")
                
                self.status_var.set(f"✓ Complete - {file_name}")
                messagebox.showinfo("Success", "Analysis complete! Check the tables for details.\nGo to the Chat tab to discuss your part with AI.")
            else:
                error = result.get("error", "Unknown error")
                self.status_var.set(f"✗ Failed - {error}")
                messagebox.showerror("Analysis Failed", f"Error: {error}")
        
        except Exception as e:
            self.status_var.set(f"✗ Error: {str(e)[:30]}")
            messagebox.showerror("Exception", f"Error: {str(e)}")
        
        finally:
            self.is_processing = False
    
    def _populate_operations(self, operations: List[Dict]):
        """Populate operations table.
        
        Args:
            operations: List of operations.
        """
        # Clear existing
        for item in self.operations_tree.get_children():
            self.operations_tree.delete(item)
        
        # Add operations
        for op in operations:
            spindle_speed = op.get('spindle_speed', '-')
            spindle_speed_str = f"{spindle_speed} RPM" if spindle_speed != '-' else '-'
            
            feed_rate = op.get('feed_rate', '-')
            feed_rate_str = f"{feed_rate} mm/rev" if feed_rate != '-' else '-'
            
            depth_of_cut = op.get('depth_of_cut', '-')
            depth_of_cut_str = f"{depth_of_cut} mm" if depth_of_cut != '-' else '-'
            
            estimated_time = op.get('estimated_time', '-')
            estimated_time_str = f"{estimated_time:.1f} min" if estimated_time != '-' else '-'
            
            values = (
                op.get("operation_id", "-"),
                op.get("name", ""),
                op.get("type", ""),
                op.get("tool", ""),
                spindle_speed_str,
                feed_rate_str,
                depth_of_cut_str,
                estimated_time_str
            )
            self.operations_tree.insert("", tk.END, values=values)
    
    def _populate_tools(self, tools: List[Dict]):
        """Populate tools table.
        
        Args:
            tools: List of tools.
        """
        # Clear existing
        for item in self.tools_tree.get_children():
            self.tools_tree.delete(item)
        
        # Add tools
        for tool in tools:
            values = (
                tool.get("tool_id", "-"),
                tool.get("name", ""),
                tool.get("type", ""),
                tool.get("material", ""),
                tool.get("coating", ""),
                tool.get("description", "")
            )
            self.tools_tree.insert("", tk.END, values=values)
    
    def _populate_summary(self, result: Dict):
        """Populate summary display.
        
        Args:
            result: Analysis result.
        """
        self.summary_text.delete(1.0, tk.END)
        
        total_time = sum(op.get('estimated_time', 0) for op in result.get('operations', []))
        
        summary = f"""
╔════════════════════════════════════════════════════════════════════╗
║                  TURNING PROCESS PLAN SUMMARY                     ║
╚════════════════════════════════════════════════════════════════════╝

📄 File: {Path(self.selected_file).name}
📍 Path: {self.selected_file}
🕐 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MACHINABILITY ANALYSIS:
  • Turning Score: {result.get('turning_score', 'N/A')}/100
  • Suitable for Turning: {'✓ YES' if result.get('success') else '✗ NO'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 PROCESS PLAN DETAILS:
  • Total Operations: {len(result.get('operations', []))}
  • Required Tools: {len(result.get('tools', []))}
  • Total Machining Time: {total_time:.1f} min

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 Export Options:
  • JSON File: {result.get('json_file', 'Not saved')}
  • AI Recommendations: {'Included' if self.ai_var.get() else 'Not included'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View detailed information in the other tabs:
  • Operations: Complete operation sequence with parameters
  • Tools: Tool specifications and purposes
  • AI Recommendations: Optimization suggestions from AI model
"""
        self.summary_text.insert(tk.END, summary)
    
    def _populate_ai(self, ai_recommendations: Dict):
        """Populate AI recommendations display.
        
        Args:
            ai_recommendations: AI recommendations.
        """
        self.ai_text.delete(1.0, tk.END)
        
        # Get optimizations or use fallback message
        optimizations = ai_recommendations.get('optimizations', '').strip()
        if not optimizations:
            optimizations = 'No recommendations available. Please check Ollama connection and try again.'
        
        content = f"""
Generated by: {self.model_var.get()} Model
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{optimizations}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Tips:
  • Review the optimization suggestions and implement where applicable
  • Test recommendations on non-critical parts first
  • Document any process changes for future reference
"""
        self.ai_text.insert(tk.END, content)
    
    def _export_results(self):
        """Export results to file."""
        if not self.analysis_result:
            messagebox.showwarning("Warning", "No analysis results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt"),
                ("JSON Files", "*.json"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, "w") as f:
                        json.dump(self.analysis_result, f, indent=2)
                else:
                    content = self.summary_text.get(1.0, tk.END)
                    with open(file_path, "w") as f:
                        f.write(content)
                
                messagebox.showinfo("Success", f"Results exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _check_and_train_unique_case(self, result: Dict):
        """Train LLM on every analysis case automatically.
        
        Args:
            result: Analysis result to train on.
        """
        try:
            # Generate case identifier
            case_hash = self._generate_case_hash(result)
            
            # Always train on every case (not just unique ones)
            training_entry = self._create_training_entry(result, case_hash)
            
            # Add to training history
            existing_cases = self._load_training_cases()
            
            # Use timestamp as key for each case to allow duplicates
            case_key = f"{case_hash}_{datetime.now().timestamp()}"
            existing_cases[case_key] = training_entry
            
            # Save updated training data
            self._save_training_cases(existing_cases)
            
            # Schedule async training (non-blocking)
            thread = threading.Thread(
                target=self._train_on_new_case,
                args=(training_entry,),
                daemon=True
            )
            thread.start()
            
            print(f"✓ Training queued for case: {case_hash[:8]} at {datetime.now().strftime('%H:%M:%S')}")
        
        except Exception as e:
            print(f"⚠️  Warning: Could not process training data: {str(e)}")
    
    def _generate_case_hash(self, result: Dict) -> str:
        """Generate hash from key parameters to identify unique cases.
        
        Args:
            result: Analysis result.
            
        Returns:
            Hash string of case characteristics.
        """
        operations = result.get("operations", [])
        
        # Extract key characteristics
        characteristics = {
            "num_operations": len(operations),
            "operation_types": sorted([op.get("type", "") for op in operations]),
            "turning_score": result.get("turning_score", 0),
            "total_time": sum(op.get('estimated_time', 0) for op in operations),
        }
        
        # Create hash from these characteristics
        char_str = json.dumps(characteristics, sort_keys=True)
        return hashlib.sha256(char_str.encode()).hexdigest()
    
    def _load_training_cases(self) -> Dict:
        """Load existing training cases from disk.
        
        Returns:
            Dictionary of training cases.
        """
        training_file = TRAINING_DATA_DIR / "training_cases.json"
        
        if training_file.exists():
            try:
                with open(training_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_training_cases(self, cases: Dict):
        """Save training cases to disk.
        
        Args:
            cases: Dictionary of training cases.
        """
        training_file = TRAINING_DATA_DIR / "training_cases.json"
        
        try:
            with open(training_file, "w") as f:
                json.dump(cases, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Warning: Could not save training data: {str(e)}")
    
    def _create_training_entry(self, result: Dict, case_hash: str) -> Dict:
        """Create training entry from analysis result.
        
        Args:
            result: Analysis result.
            case_hash: Hash identifying this case.
            
        Returns:
            Training entry dictionary.
        """
        operations = result.get("operations", [])
        total_time = sum(op.get('estimated_time', 0) for op in operations)
        
        entry = {
            "case_hash": case_hash,
            "timestamp": datetime.now().isoformat(),
            "file_name": Path(self.selected_file).name if self.selected_file else "unknown",
            "turning_score": result.get("turning_score", 0),
            "num_operations": len(operations),
            "total_machining_time_min": round(total_time, 1),
            "operation_summary": [
                {
                    "name": op.get("name", ""),
                    "type": op.get("type", ""),
                    "spindle_speed_rpm": op.get("spindle_speed", ""),
                    "feed_rate_mm_per_rev": op.get("feed_rate", ""),
                    "depth_of_cut_mm": op.get("depth_of_cut", ""),
                    "estimated_time_min": op.get("estimated_time", "")
                }
                for op in operations
            ],
            "tools_required": len(result.get("tools", [])),
            "ai_recommendations": result.get("ai_recommendations", {}).get("optimizations", "") if result.get("ai_recommendations") else ""
        }
        
        return entry
    
    def _train_on_new_case(self, training_entry: Dict):
        """Train LLM on new unique case asynchronously.
        
        Args:
            training_entry: Training data for the new case.
        """
        try:
            if not OLLAMA_AVAILABLE or self.ollama_status != "healthy":
                return
            
            # Create training prompt
            training_prompt = f"""Learn from this new CAPP turning process case:

FILE: {training_entry['file_name']}
TURNING SCORE: {training_entry['turning_score']}/100
TOTAL MACHINING TIME: {training_entry['total_machining_time_min']} min
OPERATIONS: {training_entry['num_operations']}
TOOLS REQUIRED: {training_entry['tools_required']}

OPERATION DETAILS:
"""
            
            for i, op in enumerate(training_entry['operation_summary'], 1):
                training_prompt += f"""
Operation {i}: {op['name']}
- Type: {op['type']}
- Spindle Speed: {op['spindle_speed_rpm']} RPM
- Feed Rate: {op['feed_rate_mm_per_rev']} mm/rev
- Depth of Cut: {op['depth_of_cut_mm']} mm
- Estimated Time: {op['estimated_time_min']} min
"""
            
            if training_entry['ai_recommendations']:
                training_prompt += f"\nAI RECOMMENDATIONS:\n{training_entry['ai_recommendations']}\n"
            
            training_prompt += """
Analyze this turning process and remember:
1. The operation sequence and parameter relationships
2. The time estimates for similar feature types
3. Tool selection patterns
4. Design-to-manufacturability insights

This data will help improve future process planning recommendations."""
            
            # Query model to "learn" from this case (contextual learning)
            response = query_ollama(
                prompt=training_prompt,
                model=self.model_var.get(),
                timeout=OLLAMA_AI_TIMEOUT
            )
            
            # Save the learned insights
            insights_file = TRAINING_DATA_DIR / f"insights_{training_entry['case_hash'][:8]}.json"
            insights = {
                "case_hash": training_entry['case_hash'],
                "learned_at": datetime.now().isoformat(),
                "model": self.model_var.get(),
                "model_response": response,
                "source_file": training_entry['file_name']
            }
            
            with open(insights_file, "w") as f:
                json.dump(insights, f, indent=2)
            
            print(f"✓ Training complete for case: {training_entry['case_hash'][:8]}")
            
            # Update UI with learning notification (less obtrusive)
            self.root.after(0, lambda: self._append_chat(
                "🤖 AI Assistant",
                f"📚 Learned from analysis:\n"
                f"• File: {training_entry['file_name']}\n"
                f"• Score: {training_entry['turning_score']}/100\n"
                f"• Operations: {training_entry['num_operations']}\n"
                f"→ This data improves my future recommendations"
            ))
        
        except Exception as e:
            print(f"⚠️  Training error: {str(e)}")


def main():
    """Launch the CAPP application.
    
    This is the canonical entry point for the application.
    Ensures all necessary initialization is done on startup.
    """
    # Ensure venv and environment are properly set up
    _ensure_environment()
    
    root = tk.Tk()
    app = CAPPApplication(root)
    root.mainloop()


def _ensure_environment():
    """Ensure Python environment is properly configured.
    
    Checks and sets up necessary environment variables and paths.
    """
    # Check if running from venv
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        return

    project_root = Path(__file__).resolve().parent
    venv_python = project_root / "venv312" / "Scripts" / "python.exe"

    # Auto-relaunch from venv for one-click startup reliability.
    if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
        print("ℹ️  Not running in venv. Relaunching with venv312 Python...")
        env = os.environ.copy()
        env["CAPP_RELAUNCHED_FROM_VENV"] = "1"
        subprocess.Popen(
            [str(venv_python), str(project_root / "capp_app.py")],
            cwd=str(project_root),
            env=env,
        )
        raise SystemExit(0)

    print("⚠️  Warning: Virtual environment not found at venv312\\Scripts\\python.exe")
    print("   Create it with: python -m venv venv312")
    print("   Then install deps: venv312\\Scripts\\python.exe -m pip install -r requirements.txt")


if __name__ == "__main__":
    main()
