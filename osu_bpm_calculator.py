import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def calculate_new_bpm(original_bpm, desired_snap):
    """Calculates the new BPM based on the given formula."""
    try:
        original_bpm_float = float(original_bpm)
        desired_snap_float = float(desired_snap)

        if original_bpm_float <= 0 or desired_snap_float <= 0:
            messagebox.showerror("Input Error", "BPM and Desired Snap must be positive numbers.")
            return None

        new_bpm = original_bpm_float * desired_snap_float / 4
        return round(new_bpm, 3) # Round to 3 decimal places for precision
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for Original BPM and Desired Snap.")
        return None

def load_bpm_from_osu():
    """Opens a file dialog to select an .osu file and extracts its BPM."""
    filepath = filedialog.askopenfilename(
        title="Select an .osu file",
        filetypes=[("osu! beatmaps", "*.osu")]
    )
    if not filepath:
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex to find the [TimingPoints] section
        timing_points_match = re.search(r"\[TimingPoints\]\n([\s\S]*?)(?=\n\[|\Z)", content)

        if not timing_points_match:
            messagebox.showwarning("Parsing Error", "Could not find [TimingPoints] section in the .osu file.")
            return

        timing_points_section = timing_points_match.group(1)
        
        # Split lines and find the first uninherited timing point
        # An uninherited timing point has '1' as the 7th value (index 6, 0-indexed)
        # or it's implicitly 1 if the value is missing.
        # Format: time,beatLength,meter,sampleSet,sampleIndex,volume,uninherited,kiai,omitted
        
        # Look for lines that are not green lines (negative beatLength)
        # and where uninherited is 1 (or implied 1)
        
        # Example line: 1000,250,4,1,0,100,1,0,0
        # beatLength is 250 (milliseconds per beat)
        # BPM = 60000 / beatLength
        
        bpm_found = False
        for line in timing_points_section.splitlines():
            line = line.strip()
            if not line or line.startswith("//"): # Skip empty lines and comments
                continue
            
            parts = line.split(',')
            if len(parts) >= 7: # Ensure enough parts for 'uninherited' flag
                try:
                    beat_length = float(parts[1])
                    uninherited = int(parts[6]) if len(parts) > 6 else 1 # Default to 1 if not specified

                    if beat_length > 0 and uninherited == 1: # Found an uninherited (red) timing point
                        original_bpm = 60000 / beat_length
                        original_bpm_entry.delete(0, tk.END)
                        original_bpm_entry.insert(0, str(round(original_bpm, 3)))
                        messagebox.showinfo("BPM Loaded", f"Original BPM loaded: {round(original_bpm, 3)}")
                        bpm_found = True
                        break # Found the first uninherited BPM, exit loop
                except ValueError:
                    # Skip lines that don't have valid numbers
                    continue
        
        if not bpm_found:
            messagebox.showwarning("BPM Not Found", "Could not find a valid uninherited BPM in the .osu file's [TimingPoints] section.")

    except FileNotFoundError:
        messagebox.showerror("File Error", "Selected .osu file not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading the .osu file: {e}")

def calculate_and_copy():
    """Calculates New BPM and copies it to clipboard."""
    original_bpm = original_bpm_entry.get()
    desired_snap = desired_snap_entry.get()

    new_bpm = calculate_new_bpm(original_bpm, desired_snap)
    
    if new_bpm is not None:
        new_bpm_label.config(text=f"New BPM: {new_bpm}")
        
        # Copy to clipboard
        root.clipboard_clear()
        root.clipboard_append(str(new_bpm))
        messagebox.showinfo("Success", f"New BPM ({new_bpm}) copied to clipboard!")
    else:
        new_bpm_label.config(text="New BPM: Error")

# --- GUI Setup ---
root = tk.Tk()
root.title("osu! BPM Calculator")
root.geometry("450x300") # Adjust size as needed

# Set theme to dark mode permanently
style = ttk.Style()
style.theme_use("clam") # A modern light theme base to customize
style.configure("TLabel", background="#333", foreground="#EEE")
style.configure("TFrame", background="#333")
style.configure("TLabelframe", background="#333", foreground="#EEE")
style.configure("TLabelframe.Label", background="#333", foreground="#EEE")
style.configure("TButton", background="#555", foreground="#EEE")
style.map('TButton', background=[('active', '#777')])
style.configure("TEntry", fieldbackground="#555", foreground="#EEE", insertcolor="#EEE")
root.config(bg="#333") # Root window background

# Main Title
tk.Label(root, text="osu! BPM Calculator", font=("Arial", 16, "bold")).pack(pady=15)

# --- Original BPM Section ---
bpm_frame = ttk.LabelFrame(root, text="Original BPM")
bpm_frame.pack(pady=5, padx=15, fill="x")

ttk.Label(bpm_frame, text="Enter BPM or Load from .osu:").pack(side=tk.LEFT, padx=5, pady=5)
original_bpm_entry = ttk.Entry(bpm_frame, width=20)
original_bpm_entry.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill="x")
ttk.Button(bpm_frame, text="Load from .osu", command=load_bpm_from_osu).pack(side=tk.RIGHT, padx=5, pady=5)

# --- Desired Snap Section ---
snap_frame = ttk.LabelFrame(root, text="Desired Snap")
snap_frame.pack(pady=5, padx=15, fill="x")

ttk.Label(snap_frame, text="Desired Snap (e.g., 5.5):").pack(side=tk.LEFT, padx=5, pady=5)
desired_snap_entry = ttk.Entry(snap_frame, width=20)
desired_snap_entry.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill="x")

# --- Calculate Button ---
ttk.Button(root, text="Calculate & Copy New BPM", command=calculate_and_copy, style='TButton').pack(pady=15)

# --- New BPM Output ---
new_bpm_label = ttk.Label(root, text="New BPM: ", font=("Arial", 12, "bold"))
new_bpm_label.pack(pady=10)

root.mainloop()