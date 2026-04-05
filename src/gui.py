import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import sys
import ctypes
from pathlib import Path
from typing import Optional
import webbrowser

# Enable DPI awareness for crisp rendering on high-DPI displays
if sys.platform == 'win32':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# Import core functionality
sys.path.insert(0, str(Path(__file__).parent))
from concat_pdf import process_pdf

# ─── Color Palette ───────────────────────────────────────────────
COLORS = {
    'bg':           '#F8F9FA',
    'surface':      '#FFFFFF',
    'border':       '#E8E8E8',
    'title_bg':     '#FFFFFF',
    'title_border': '#E8E8E8',
    'accent':       '#4A90D9',
    'accent_hover': '#357ABD',
    'text':         '#2D3436',
    'text_sec':     '#95A5A6',
    'danger':       '#E74C3C',
    'hover':        '#F0F0F0',
    'entry_bg':     '#FFFFFF',
    'progress_trough': '#E8E8E8',
}


class PDFConcatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDFConcat")
        self.root.geometry("700x960")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS['bg'])

        # Remove system title bar
        self.root.overrideredirect(True)

        # Track window state
        self._drag_x = 0
        self._drag_y = 0
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.columns = tk.IntVar(value=3)
        self.rows = tk.IntVar(value=2)
        self.dpi = tk.IntVar(value=150)
        self.gap = tk.DoubleVar(value=3)
        self.padding = tk.DoubleVar(value=10)

        self.processing = False

        self.create_title_bar()
        self.create_widgets()

    # ─── Custom Title Bar ────────────────────────────────────────
    def create_title_bar(self):
        title_bar = tk.Frame(self.root, bg=COLORS['title_bg'], height=40)
        title_bar.grid(row=0, column=0, sticky='new')
        title_bar.pack_propagate(False)

        # Left side: icon + title
        left_frame = tk.Frame(title_bar, bg=COLORS['title_bg'])
        left_frame.pack(side='left', padx=(10, 0))

        # App icon
        icon_path = Path(__file__).parent.parent / "icons" / "pdf-red.ico"
        self._title_icon = None
        if icon_path.exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                img = img.resize((20, 20))
                self._title_icon = ImageTk.PhotoImage(img)
                icon_label = tk.Label(left_frame, image=self._title_icon,
                                      bg=COLORS['title_bg'])
                icon_label.pack(side='left', padx=(0, 6))
            except Exception:
                pass

        # App title text
        self._title_text_widget = tk.Label(left_frame, text="PDFConcat",
                              font=('Segoe UI', 11, 'bold'),
                              bg=COLORS['title_bg'], fg=COLORS['text'])
        self._title_text_widget.pack(side='left')

        # Right side: window control buttons
        btn_frame = tk.Frame(title_bar, bg=COLORS['title_bg'])
        btn_frame.pack(side='right')

        BTN_W, BTN_H = 46, 40

        btn_defs = [
            (self._draw_close,    self.on_close,    True),
            (self._draw_minimize, self.on_minimize, False),
        ]

        for draw_fn, cmd, is_close in btn_defs:
            canvas = tk.Canvas(btn_frame, width=BTN_W, height=BTN_H,
                               bg=COLORS['title_bg'], highlightthickness=0,
                               cursor='hand2')
            canvas.pack(side='right')
            draw_fn(canvas, COLORS['text'])
            canvas._draw_fn = draw_fn
            canvas._is_close = is_close
            canvas.bind('<ButtonPress-1>', lambda e, c=cmd: c())
            canvas.bind('<Enter>', self._on_canvas_btn_enter)
            canvas.bind('<Leave>', self._on_canvas_btn_leave)

        # Drag bindings
        for widget in (title_bar, self._title_text_widget):
            widget.bind('<ButtonPress-1>', self.on_title_press)
            widget.bind('<B1-Motion>', self.on_title_drag)

        # Bottom border line
        border_line = tk.Frame(self.root, bg=COLORS['title_border'], height=1)
        border_line.grid(row=1, column=0, sticky='new')

    # ─── Title Bar Button Drawing ─────────────────────────────
    @staticmethod
    def _draw_minimize(canvas, color):
        """Draw ─ centered at (23, 20)"""
        canvas.delete('icon')
        canvas.create_line(16, 20, 30, 20, fill=color, width=2.0, tags='icon')

    @staticmethod
    def _draw_close(canvas, color):
        """Draw ✕ centered at (23, 20)"""
        canvas.delete('icon')
        canvas.create_line(18, 15, 28, 25, fill=color, width=1.5, tags='icon')
        canvas.create_line(28, 15, 18, 25, fill=color, width=1.5, tags='icon')

    def _on_canvas_btn_enter(self, event):
        canvas = event.widget
        if canvas._is_close:
            canvas.configure(bg=COLORS['danger'])
            canvas._draw_fn(canvas, '#FFFFFF')
        else:
            canvas.configure(bg=COLORS['hover'])
            canvas._draw_fn(canvas, COLORS['text'])

    def _on_canvas_btn_leave(self, event):
        canvas = event.widget
        canvas.configure(bg=COLORS['title_bg'])
        canvas._draw_fn(canvas, COLORS['text'])

    def on_title_press(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def on_title_drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def on_minimize(self):
        self.root.iconify()

    def on_close(self):
        self.root.destroy()

    # ─── Main Content ────────────────────────────────────────────
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg=COLORS['bg'], padx=15, pady=10)
        main_frame.grid(row=2, column=0, sticky='nsew')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = tk.Label(main_frame, text="PDFConcat",
                               font=('Segoe UI', 20, 'bold'),
                               bg=COLORS['bg'], fg=COLORS['accent'])
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # File selection area
        file_frame = tk.LabelFrame(main_frame, text="  File Selection  ",
                                   bg=COLORS['surface'], fg=COLORS['text'],
                                   font=('Segoe UI', 10, 'bold'),
                                   bd=1, relief='solid',
                                   highlightbackground=COLORS['border'],
                                   padx=12, pady=10)
        file_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)

        # Input drop zone
        self.drop_zone = tk.Frame(file_frame, bg=COLORS['surface'], height=180,
                                  cursor='hand2', highlightbackground=COLORS['border'],
                                  highlightthickness=2)
        self.drop_zone.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 5))
        self.drop_zone.grid_propagate(False)
        self.drop_zone.columnconfigure(0, weight=1)
        self.drop_zone.rowconfigure(0, weight=1)

        # Drop zone inner content
        self.drop_canvas = tk.Canvas(self.drop_zone, bg=COLORS['surface'],
                                     highlightthickness=0, cursor='hand2')
        self.drop_canvas.grid(row=0, column=0, sticky='nsew')
        self._draw_drop_zone_placeholder()

        # Bindings
        self.drop_canvas.drop_target_register(DND_FILES)
        self.drop_canvas.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_canvas.bind('<Button-1>', lambda e: self.select_input_file())
        self.drop_canvas.bind('<Configure>', lambda e: self._redraw_drop_zone())
        self.drop_canvas.bind('<Enter>', lambda e: self.drop_canvas.configure(bg=COLORS['hover']) or self.drop_zone.configure(highlightbackground=COLORS['accent']))
        self.drop_canvas.bind('<Leave>', lambda e: self.drop_canvas.configure(bg=COLORS['surface']) or self.drop_zone.configure(highlightbackground=COLORS['border']))

        # Output file
        tk.Label(file_frame, text="Output PDF File:",
                 bg=COLORS['surface'], fg=COLORS['text'],
                 font=('Segoe UI', 9)).grid(row=2, column=0, sticky='w', pady=(10, 0))
        self.output_entry = ttk.Entry(file_frame, textvariable=self.output_path, width=50)
        self.output_entry.grid(row=3, column=0, padx=(0, 10), sticky='ew', pady=(10, 0))

        self.output_btn = tk.Button(file_frame, text="Browse...",
                                    command=self.select_output_file,
                                    bg=COLORS['surface'], fg=COLORS['text'],
                                    font=('Segoe UI', 9),
                                    relief='solid', bd=1,
                                    activebackground=COLORS['hover'],
                                    activeforeground=COLORS['text'],
                                    cursor='hand2', padx=12, pady=3)
        self.output_btn.grid(row=3, column=1, padx=(0, 10), pady=(10, 0))



        # Parameter configuration area
        param_frame = tk.LabelFrame(main_frame, text="  Parameters  ",
                                    bg=COLORS['surface'], fg=COLORS['text'],
                                    font=('Segoe UI', 10, 'bold'),
                                    bd=1, relief='solid',
                                    padx=12, pady=10)
        param_frame.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(0, 10))

        # Grid layout
        grid_frame = tk.Frame(param_frame, bg=COLORS['surface'])
        grid_frame.grid(row=0, column=0, columnspan=3, sticky='ew', pady=(0, 10))
        grid_frame.columnconfigure(0, weight=1)

        tk.Label(grid_frame, text="Grid Layout:",
                 bg=COLORS['surface'], fg=COLORS['text'],
                 font=('Segoe UI', 9)).grid(row=0, column=0, sticky='w')
        tk.Label(grid_frame, text="Columns:",
                 bg=COLORS['surface'], fg=COLORS['text'],
                 font=('Segoe UI', 9)).grid(row=0, column=1, padx=(20, 5), sticky='e')
        columns_spin = ttk.Spinbox(grid_frame, from_=1, to=10, width=5,
                                   textvariable=self.columns)
        columns_spin.grid(row=0, column=2, padx=(0, 20))

        tk.Label(grid_frame, text="Rows:",
                 bg=COLORS['surface'], fg=COLORS['text'],
                 font=('Segoe UI', 9)).grid(row=0, column=3, padx=(0, 5), sticky='e')
        rows_spin = ttk.Spinbox(grid_frame, from_=1, to=10, width=5,
                                textvariable=self.rows)
        rows_spin.grid(row=0, column=4, padx=(0, 10))

        auto_calc_btn = tk.Button(grid_frame, text="Auto Calculate Rows",
                                  command=self.auto_calculate_rows,
                                  bg=COLORS['surface'], fg=COLORS['text'],
                                  font=('Segoe UI', 9),
                                  relief='solid', bd=1,
                                  activebackground=COLORS['hover'],
                                  activeforeground=COLORS['text'],
                                  cursor='hand2', padx=8, pady=2)
        auto_calc_btn.grid(row=0, column=5)

        # Quality settings
        quality_frame = tk.Frame(param_frame, bg=COLORS['surface'])
        quality_frame.grid(row=2, column=0, columnspan=3, sticky='ew')
        quality_frame.columnconfigure(0, weight=1)

        tk.Label(quality_frame, text="Quality Settings:",
                 bg=COLORS['surface'], fg=COLORS['text'],
                 font=('Segoe UI', 9)).grid(row=0, column=0, sticky='w')
        tk.Label(quality_frame, text="DPI:",
                 bg=COLORS['surface'], fg=COLORS['text'],
                 font=('Segoe UI', 9)).grid(row=0, column=1, padx=(20, 5), sticky='e')
        dpi_spin = ttk.Spinbox(quality_frame, from_=50, to=600, width=6,
                               textvariable=self.dpi, increment=50)
        dpi_spin.grid(row=0, column=2, padx=(0, 20))

        tk.Label(quality_frame, text="Spacing:",
                 bg=COLORS['surface'], fg=COLORS['text'],
                 font=('Segoe UI', 9)).grid(row=0, column=3, padx=(0, 5), sticky='e')
        gap_spin = ttk.Spinbox(quality_frame, from_=0, to=20, width=5,
                               textvariable=self.gap, increment=0.5)
        gap_spin.grid(row=0, column=4, padx=(0, 20))

        tk.Label(quality_frame, text="Margin:",
                 bg=COLORS['surface'], fg=COLORS['text'],
                 font=('Segoe UI', 9)).grid(row=0, column=5, padx=(0, 5), sticky='e')
        padding_spin = ttk.Spinbox(quality_frame, from_=0, to=50, width=5,
                                   textvariable=self.padding, increment=1)
        padding_spin.grid(row=0, column=6)

        # Action area
        action_frame = tk.LabelFrame(main_frame, text="  Actions  ",
                                     bg=COLORS['surface'], fg=COLORS['text'],
                                     font=('Segoe UI', 10, 'bold'),
                                     bd=1, relief='solid',
                                     padx=12, pady=10)
        action_frame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(0, 10))
        action_frame.columnconfigure(0, weight=1)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(action_frame, variable=self.progress_var,
                                            maximum=100, mode='determinate')
        self.progress_bar.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='ew')

        # Status label
        self.status_label = tk.Label(action_frame, text="Ready",
                                     font=('Segoe UI', 9),
                                     bg=COLORS['surface'], fg=COLORS['text_sec'])
        self.status_label.grid(row=1, column=0, columnspan=2, sticky='w')

        # Buttons
        button_frame = tk.Frame(action_frame, bg=COLORS['surface'])
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        self.process_btn = tk.Button(button_frame, text="  Start Processing  ",
                                     command=self.start_processing,
                                     bg=COLORS['accent'], fg='#FFFFFF',
                                     font=('Segoe UI', 10, 'bold'),
                                     relief='flat', bd=0,
                                     activebackground=COLORS['accent_hover'],
                                     activeforeground='#FFFFFF',
                                     cursor='hand2', padx=20, pady=6)
        self.process_btn.grid(row=0, column=0, padx=(0, 10))

        self.open_btn = tk.Button(button_frame, text="Open Output File",
                                  command=self.open_output_file, state='disabled',
                                  bg=COLORS['surface'], fg=COLORS['text'],
                                  font=('Segoe UI', 10, 'bold'),
                                  relief='solid', bd=1,
                                  activebackground=COLORS['hover'],
                                  activeforeground=COLORS['text'],
                                  cursor='hand2', padx=20, pady=6)
        self.open_btn.grid(row=0, column=1, padx=(0, 10))

        # Preset configurations
        preset_frame = tk.LabelFrame(main_frame, text="  Quick Presets  ",
                                     bg=COLORS['surface'], fg=COLORS['text'],
                                     font=('Segoe UI', 10, 'bold'),
                                     bd=1, relief='solid',
                                     padx=12, pady=8)
        preset_frame.grid(row=4, column=0, columnspan=3, sticky='ew')
        preset_frame.columnconfigure(0, weight=1)

        btn_container = tk.Frame(preset_frame, bg=COLORS['surface'])
        btn_container.grid(row=0, column=0)

        presets = [
            ("3×2 Grid",       lambda: self.apply_preset(3, 2),   0, 0),
            ("4×3 Grid",       lambda: self.apply_preset(4, 3),   0, 1),
            ("5×3 Grid",       lambda: self.apply_preset(5, 3),   0, 2),
            ("Single Row",     self.apply_single_row,             1, 0),
            ("Single Column",  self.apply_single_column,          1, 1),
            ("Auto Layout",    lambda: self.apply_preset(4, None),1, 2),
        ]

        for text, cmd, r, c in presets:
            pady = (5, 0) if r == 1 else (0, 0)
            btn = tk.Button(btn_container, text=text, command=cmd,
                            bg=COLORS['surface'], fg=COLORS['text'],
                            font=('Segoe UI', 9),
                            relief='solid', bd=1,
                            activebackground=COLORS['hover'],
                            activeforeground=COLORS['text'],
                            cursor='hand2', padx=10, pady=3, width=14)
            btn.grid(row=r, column=c, padx=(0 if c == 0 else 5, 0), pady=pady)

    # ─── Business Logic (unchanged) ──────────────────────────────
    def _draw_drop_zone_placeholder(self):
        """Draw dashed border and placeholder text in the drop zone canvas"""
        self.drop_canvas.delete('all')
        w = self.drop_canvas.winfo_width() or 620
        h = self.drop_canvas.winfo_height() or 120

        # Dashed border
        self.drop_canvas.create_rectangle(
            8, 8, w - 8, h - 8,
            outline=COLORS['border'], width=2, dash=(8, 4), tags='border')

        # Upload arrow icon (simple lines)
        cx, cy = w // 2, h // 2 - 12
        self.drop_canvas.create_line(cx, cy - 14, cx, cy + 4,
                                     fill=COLORS['text_sec'], width=2, tags='icon')
        self.drop_canvas.create_line(cx - 8, cy - 6, cx, cy - 14,
                                     fill=COLORS['text_sec'], width=2, tags='icon')
        self.drop_canvas.create_line(cx + 8, cy - 6, cx, cy - 14,
                                     fill=COLORS['text_sec'], width=2, tags='icon')

        # Text
        self.drop_canvas.create_text(
            cx, cy + 22,
            text="Click to select or drag & drop PDF file here",
            fill=COLORS['text_sec'], font=('Segoe UI', 10), tags='text')

    def _draw_drop_zone_filename(self):
        """Draw selected filename in the drop zone"""
        self.drop_canvas.delete('all')
        w = self.drop_canvas.winfo_width() or 620
        h = self.drop_canvas.winfo_height() or 120

        # Solid accent border
        self.drop_canvas.create_rectangle(
            8, 8, w - 8, h - 8,
            outline=COLORS['accent'], width=2, tags='border')

        cx, cy = w // 2, h // 2 - 16
        filename = Path(self.input_path.get()).name

        # PDF icon
        self.drop_canvas.create_text(cx, cy,
                                     text="📄",
                                     font=('Segoe UI', 18), tags='icon')

        # Filename
        self.drop_canvas.create_text(
            cx, cy + 30,
            text=filename,
            fill=COLORS['text'], font=('Segoe UI', 11, 'bold'), tags='text')

        # Subtitle
        self.drop_canvas.create_text(
            cx, cy + 52,
            text="Click to change file",
            fill=COLORS['text_sec'], font=('Segoe UI', 9), tags='subtext')

    def _redraw_drop_zone(self):
        """Redraw drop zone based on current state"""
        if self.input_path.get():
            self._draw_drop_zone_filename()
        else:
            self._draw_drop_zone_placeholder()

    def select_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            if not filename.lower().endswith('.pdf'):
                messagebox.showwarning("Warning", "Only PDF files are supported")
                return
            self.input_path.set(filename)
            input_path = Path(filename)
            output_path = input_path.parent / f"{input_path.stem}_thumbnails.pdf"
            self.output_path.set(str(output_path))
            self._redraw_drop_zone()

    def select_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save Output File",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)

    def auto_calculate_rows(self):
        """Automatically calculate rows based on input file page count"""
        input_file = self.input_path.get()
        if not input_file:
            messagebox.showwarning("Warning", "Please select an input PDF file first")
            return

        try:
            import fitz
            doc = fitz.open(input_file)
            total_pages = len(doc)
            doc.close()

            cols = self.columns.get()
            rows = (total_pages + cols - 1) // cols
            self.rows.set(rows)

            messagebox.showinfo("Auto Calculate",
                              f"File has {total_pages} pages\n"
                              f"{cols} thumbnails per row\n"
                              f"Need {rows} rows")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read PDF file: {str(e)}")

    def apply_preset(self, columns, rows):
        """Apply preset configuration"""
        self.columns.set(columns)
        if rows is not None:
            self.rows.set(rows)

    def _get_page_count(self):
        """Get page count of the input PDF file"""
        input_file = self.input_path.get()
        if not input_file:
            messagebox.showwarning("Warning", "Please select an input PDF file first")
            return None
        try:
            import fitz
            doc = fitz.open(input_file)
            total_pages = len(doc)
            doc.close()
            return total_pages
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read PDF file: {str(e)}")
            return None

    def apply_single_row(self):
        """Set all pages in one row"""
        total_pages = self._get_page_count()
        if total_pages is not None:
            self.columns.set(total_pages)
            self.rows.set(1)
            self.status_label.config(text=f"Single Row: {total_pages} pages in 1 row")

    def apply_single_column(self):
        """Set all pages in one column"""
        total_pages = self._get_page_count()
        if total_pages is not None:
            self.columns.set(1)
            self.rows.set(total_pages)
            self.status_label.config(text=f"Single Column: {total_pages} pages in 1 column")

    def validate_inputs(self):
        """Validate input parameters"""
        if not self.input_path.get():
            messagebox.showwarning("Warning", "Please select an input PDF file")
            return False

        if not self.input_path.get().lower().endswith('.pdf'):
            messagebox.showwarning("Warning", "Input file must be a PDF file")
            return False

        if not self.output_path.get():
            messagebox.showwarning("Warning", "Please select an output PDF file")
            return False

        output_file = Path(self.output_path.get())
        if output_file.exists():
            if not messagebox.askyesno("Confirm",
                    f"File already exists:\n{output_file}\n\nOverwrite?"):
                return False

        if self.columns.get() <= 0:
            messagebox.showwarning("Warning", "Columns must be greater than 0")
            return False

        if self.rows.get() <= 0:
            messagebox.showwarning("Warning", "Rows must be greater than 0")
            return False

        if self.dpi.get() <= 0:
            messagebox.showwarning("Warning", "DPI must be greater than 0")
            return False

        return True

    def start_processing(self):
        """Start PDF processing"""
        if not self.validate_inputs():
            return

        if self.processing:
            messagebox.showwarning("Warning", "Processing in progress, please wait...")
            return

        # Disable controls
        self.processing = True
        self.process_btn.config(state='disabled')
        self.open_btn.config(state='disabled')
        self.progress_var.set(0)
        self.status_label.config(text="Processing...")

        # Process in new thread
        threading.Thread(target=self.process_pdf_thread, daemon=True).start()

    def process_pdf_thread(self):
        """PDF processing thread function"""
        try:
            # Simulate progress update
            self.update_progress(10, "Reading PDF file...")

            # Call core processing function
            process_pdf(
                input_path=Path(self.input_path.get()),
                output_path=Path(self.output_path.get()),
                n=self.columns.get(),
                m=self.rows.get(),
                page_size=None,
                orientation="landscape",
                dpi=self.dpi.get(),
                gap=self.gap.get(),
                padding=self.padding.get()
            )

            self.update_progress(100, "Processing complete!")
            self.root.after(0, lambda: self.on_processing_complete(True))

        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            self.root.after(0, lambda: self.on_processing_complete(False, error_msg))

    def update_progress(self, value, text):
        """Update progress bar and status"""
        self.root.after(0, lambda: (
            self.progress_var.set(value),
            self.status_label.config(text=text)
        ))

    def on_processing_complete(self, success, error_msg=None):
        """Callback after processing completion"""
        self.processing = False
        self.process_btn.config(state='normal')

        if success:
            self.open_btn.config(state='normal')
            messagebox.showinfo("Success", "PDF processing completed!")
        else:
            messagebox.showerror("Error", error_msg)
            self.status_label.config(text="Processing failed")

    def open_output_file(self):
        """Open output file"""
        output_file = self.output_path.get()
        if output_file and Path(output_file).exists():
            if sys.platform == 'win32':
                import os
                os.startfile(output_file)
            else:
                webbrowser.open(f'file://{output_file}')

    def on_drop(self, event):
        """Handle file drag and drop"""
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if file_path.lower().endswith('.pdf'):
                self.input_path.set(file_path)
                input_path = Path(file_path)
                output_path = input_path.parent / f"{input_path.stem}_thumbnails.pdf"
                self.output_path.set(str(output_path))
                self._redraw_drop_zone()
            else:
                messagebox.showwarning("Warning", "Please drag and drop PDF files")


def configure_styles(root):
    """Configure ttk widget styles for modern light theme"""
    style = ttk.Style(root)
    style.theme_use('clam')

    # General
    style.configure('.', background=COLORS['bg'], foreground=COLORS['text'])

    # Frames
    style.configure('TFrame', background=COLORS['bg'])
    style.configure('TLabel', background=COLORS['bg'], foreground=COLORS['text'],
                    font=('Segoe UI', 9))

    # Entry
    style.configure('TEntry',
                    fieldbackground=COLORS['entry_bg'],
                    bordercolor=COLORS['border'],
                    lightcolor=COLORS['border'],
                    darkcolor=COLORS['border'],
                    insertcolor=COLORS['text'])
    style.map('TEntry',
              bordercolor=[('focus', COLORS['accent'])],
              lightcolor=[('focus', COLORS['accent'])],
              darkcolor=[('focus', COLORS['accent'])])

    # Spinbox
    style.configure('TSpinbox',
                    fieldbackground=COLORS['entry_bg'],
                    bordercolor=COLORS['border'],
                    lightcolor=COLORS['border'],
                    darkcolor=COLORS['border'],
                    arrowcolor=COLORS['text'],
                    insertcolor=COLORS['text'])
    style.map('TSpinbox',
              bordercolor=[('focus', COLORS['accent'])],
              lightcolor=[('focus', COLORS['accent'])],
              darkcolor=[('focus', COLORS['accent'])])

    # Progressbar
    style.configure('Horizontal.TProgressbar',
                    troughcolor=COLORS['progress_trough'],
                    background='#81C784',
                    bordercolor=COLORS['border'],
                    lightcolor='#81C784',
                    darkcolor='#81C784',
                    thickness=20)


def main():
    root = TkinterDnD.Tk()

    # Configure styles
    configure_styles(root)

    # Create app
    app = PDFConcatApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
