import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
from pathlib import Path
from typing import Optional
import webbrowser

# Import core functionality
sys.path.insert(0, str(Path(__file__).parent))
from concat_pdf import process_pdf


class PDFThumbnailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Thumbnail Grid Tool v0.9.9")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        # Set application icon (if available)
        try:
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass

        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.columns = tk.IntVar(value=3)
        self.rows = tk.IntVar(value=2)
        self.dpi = tk.IntVar(value=150)
        self.gap = tk.DoubleVar(value=3)
        self.padding = tk.DoubleVar(value=10)

        self.processing = False

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="PDF Thumbnail Grid Tool",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # File selection area
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Input file
        ttk.Label(file_frame, text="Input PDF File:").grid(row=0, column=0, sticky=tk.W)
        self.input_entry = ttk.Entry(file_frame, textvariable=self.input_path, width=50)
        self.input_entry.grid(row=1, column=0, padx=(0, 10), sticky=(tk.W, tk.E))

        self.input_btn = ttk.Button(file_frame, text="Browse...", command=self.select_input_file)
        self.input_btn.grid(row=1, column=1, padx=(0, 10))

        # Output file
        ttk.Label(file_frame, text="Output PDF File:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.output_entry = ttk.Entry(file_frame, textvariable=self.output_path, width=50)
        self.output_entry.grid(row=3, column=0, padx=(0, 10), sticky=(tk.W, tk.E), pady=(10, 0))

        self.output_btn = ttk.Button(file_frame, text="Browse...", command=self.select_output_file)
        self.output_btn.grid(row=3, column=1, padx=(0, 10), pady=(10, 0))

        # File drag and drop tip
        drag_label = ttk.Label(file_frame, text="Tip: You can drag and drop PDF files to the input box",
                               font=('Arial', 9), foreground='gray')
        drag_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))

        # Parameter configuration area
        param_frame = ttk.LabelFrame(main_frame, text="Parameters", padding="10")
        param_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Grid layout
        grid_frame = ttk.Frame(param_frame)
        grid_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(grid_frame, text="Grid Layout:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(grid_frame, text="Columns:").grid(row=0, column=1, padx=(20, 5))
        columns_spin = ttk.Spinbox(grid_frame, from_=1, to=10, width=5, textvariable=self.columns)
        columns_spin.grid(row=0, column=2, padx=(0, 20))

        ttk.Label(grid_frame, text="Rows:").grid(row=0, column=3, padx=(0, 5))
        rows_spin = ttk.Spinbox(grid_frame, from_=1, to=10, width=5, textvariable=self.rows)
        rows_spin.grid(row=0, column=4, padx=(0, 10))

        auto_calc_btn = ttk.Button(grid_frame, text="Auto Calculate Rows",
                                   command=self.auto_calculate_rows)
        auto_calc_btn.grid(row=0, column=5)

        # Page size is automatically calculated to fit the content

        # Quality settings
        quality_frame = ttk.Frame(param_frame)
        quality_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E))

        ttk.Label(quality_frame, text="Quality Settings:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(quality_frame, text="DPI:").grid(row=0, column=1, padx=(20, 5))
        dpi_spin = ttk.Spinbox(quality_frame, from_=50, to=600, width=6,
                               textvariable=self.dpi, increment=50)
        dpi_spin.grid(row=0, column=2, padx=(0, 20))

        ttk.Label(quality_frame, text="Spacing:").grid(row=0, column=3, padx=(0, 5))
        gap_spin = ttk.Spinbox(quality_frame, from_=0, to=20, width=5,
                              textvariable=self.gap, increment=0.5)
        gap_spin.grid(row=0, column=4, padx=(0, 20))

        ttk.Label(quality_frame, text="Margin:").grid(row=0, column=5, padx=(0, 5))
        padding_spin = ttk.Spinbox(quality_frame, from_=0, to=50, width=5,
                                  textvariable=self.padding, increment=1)
        padding_spin.grid(row=0, column=6)

        # Action area
        action_frame = ttk.LabelFrame(main_frame, text="Actions", padding="10")
        action_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(action_frame, variable=self.progress_var,
                                           maximum=100, length=650)
        self.progress_bar.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))

        # Status label
        self.status_label = ttk.Label(action_frame, text="Ready", font=('Arial', 9))
        self.status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)

        # Buttons
        button_frame = ttk.Frame(action_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        self.process_btn = ttk.Button(button_frame, text="Start Processing",
                                      command=self.start_processing,
                                      style='Accent.TButton')
        self.process_btn.grid(row=0, column=0, padx=(0, 10))

        self.open_btn = ttk.Button(button_frame, text="Open Output File",
                                  command=self.open_output_file, state='disabled')
        self.open_btn.grid(row=0, column=1, padx=(0, 10))

        # Preset configurations
        preset_frame = ttk.Frame(main_frame)
        preset_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))

        ttk.Label(preset_frame, text="Quick Presets:").grid(row=0, column=0, sticky=tk.W)
        ttk.Button(preset_frame, text="3×2 Grid",
                  command=lambda: self.apply_preset(3, 2)).grid(row=0, column=1, padx=(10, 5))
        ttk.Button(preset_frame, text="4×3 Grid",
                  command=lambda: self.apply_preset(4, 3)).grid(row=0, column=2, padx=(5, 5))
        ttk.Button(preset_frame, text="5×3 Grid",
                  command=lambda: self.apply_preset(5, 3)).grid(row=0, column=3, padx=(5, 5))
        ttk.Button(preset_frame, text="Auto Layout",
                  command=lambda: self.apply_preset(4, None)).grid(row=0, column=4, padx=(5, 0))

    def select_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            # Auto generate output filename
            input_path = Path(filename)
            output_path = input_path.parent / f"{input_path.stem}_thumbnails.pdf"
            self.output_path.set(str(output_path))

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

    def validate_inputs(self):
        """Validate input parameters"""
        if not self.input_path.get():
            messagebox.showwarning("Warning", "Please select an input PDF file")
            return False

        if not self.output_path.get():
            messagebox.showwarning("Warning", "Please select an output PDF file")
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
            # Page size is automatically calculated to fit the content
            process_pdf(
                input_path=Path(self.input_path.get()),
                output_path=Path(self.output_path.get()),
                n=self.columns.get(),
                m=self.rows.get(),
                page_size=None,  # Auto-calculate page size to fit content
                orientation="landscape",  # Not used when page_size is None
                dpi=self.dpi.get(),
                gap=self.gap.get(),
                padding=self.padding.get()
            )

            self.update_progress(100, "Processing complete!")

            # Show completion message
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
            messagebox.showinfo("Success", "PDF thumbnail grid completed!")
        else:
            messagebox.showerror("Error", error_msg)
            self.status_label.config(text="Processing failed")

    def open_output_file(self):
        """Open output file"""
        output_file = self.output_path.get()
        if output_file and Path(output_file).exists():
            # Open with system default program
            if sys.platform == 'win32':
                import os
                os.startfile(output_file)
            else:
                webbrowser.open(f'file://{output_file}')

    def on_drop(self, event):
        """Handle file drag and drop"""
        files = self.root.tk.splitlist(event.data)
        if files:
            # Take only the first file
            file_path = files[0]
            if file_path.lower().endswith('.pdf'):
                self.input_path.set(file_path)
                # Auto generate output filename
                input_path = Path(file_path)
                output_path = input_path.parent / f"{input_path.stem}_thumbnails.pdf"
                self.output_path.set(str(output_path))
            else:
                messagebox.showwarning("Warning", "Please drag and drop PDF files")


def main():
    root = tk.Tk()

    # Set up style
    style = ttk.Style(root)

    # Select theme based on system
    if sys.platform == 'win32':
        try:
            style.theme_use('vista')
        except:
            try:
                style.theme_use('winnative')
            except:
                style.theme_use('default')

    # Create app
    app = PDFThumbnailApp(root)

    # Set up drag and drop (requires additional implementation)
    root.mainloop()


if __name__ == "__main__":
    main()