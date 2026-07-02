import os
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class ModTextUtility(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Modder's Text Utility (Standalone)")
        self.geometry("600x650")
        self.configure(padx=20, pady=20)
        
        # Title
        tk.Label(self, text="Modder's Text Utility", font=("Helvetica", 16, "bold")).pack(anchor="w", pady=(0, 10))
        tk.Label(self, text="Tools for bypassing game engine text limits.", font=("Helvetica", 10)).pack(anchor="w", pady=(0, 20))
        
        # File Selection
        frame_file = tk.LabelFrame(self, text="1. Select Input File (CSV)", padx=10, pady=10)
        frame_file.pack(fill="x", pady=10)
        
        self.txt_file = tk.Entry(frame_file, width=60)
        self.txt_file.pack(side="left", padx=(0, 10), expand=True, fill="x")
        
        btn_browse = tk.Button(frame_file, text="Browse...", command=self.browse_file)
        btn_browse.pack(side="right")
        
        # Feature 1: Byte Limit Validator
        frame_val = tk.LabelFrame(self, text="2. Byte Limit Validator (UTF-8)", padx=10, pady=10)
        frame_val.pack(fill="x", pady=10)
        
        tk.Label(frame_val, text="Max Bytes allowed (e.g. 63):").pack(side="left")
        
        self.spin_bytes = tk.Spinbox(frame_val, from_=1, to=9999, width=10)
        self.spin_bytes.delete(0, "end")
        self.spin_bytes.insert(0, "63")
        self.spin_bytes.pack(side="left", padx=10)
        
        btn_check = tk.Button(frame_val, text="Scan File", bg="#d0ebff", command=self.scan_file)
        btn_check.pack(side="right")
        
        # Feature 2: Thai to ANSI Converter
        frame_conv = tk.LabelFrame(self, text="3. Thai-to-ANSI Converter (Font Hack)", padx=10, pady=10)
        frame_conv.pack(fill="x", pady=10)
        
        tk.Label(frame_conv, text="Converts Thai chars to 1-Byte ANSI chars (Requires custom font).", fg="#555").pack(anchor="w", pady=(0, 10))
        
        btn_convert = tk.Button(frame_conv, text="Convert to ANSI CSV", bg="#d3f9d8", command=self.convert_to_ansi)
        btn_convert.pack(anchor="e")
        
        # Log Output
        tk.Label(self, text="Output Log:").pack(anchor="w", pady=(10, 0))
        self.txt_log = scrolledtext.ScrolledText(self, height=15)
        self.txt_log.pack(fill="both", expand=True)

    def log(self, msg):
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.txt_file.delete(0, tk.END)
            self.txt_file.insert(0, file_path)
            self.log(f"Selected: {file_path}")

    def scan_file(self):
        file_path = self.txt_file.get()
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid CSV file first.")
            return
            
        try:
            max_bytes = int(self.spin_bytes.get())
        except:
            messagebox.showerror("Error", "Invalid Max Bytes value.")
            return

        self.log(f"\n--- Scanning {os.path.basename(file_path)} for limits > {max_bytes} bytes ---")
        
        try:
            exceeded_count = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if not headers or "trans" not in headers:
                    self.log("ERROR: CSV must have a 'trans' column.")
                    return
                
                for i, row in enumerate(reader):
                    trans_text = row.get("trans", "")
                    byte_len = len(trans_text.encode('utf-8'))
                    if byte_len > max_bytes:
                        exceeded_count += 1
                        self.log(f"Row {i+2}: {byte_len} bytes -> {trans_text[:30]}...")
                        
            if exceeded_count == 0:
                self.log("✅ Perfect! No lines exceed the byte limit.")
            else:
                self.log(f"❌ Found {exceeded_count} lines exceeding {max_bytes} bytes.")
                messagebox.showwarning("Scan Complete", f"Found {exceeded_count} lines exceeding the limit.")
                
        except Exception as e:
            self.log(f"ERROR: {str(e)}")

    def convert_to_ansi(self):
        file_path = self.txt_file.get()
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid CSV file first.")
            return
            
        try:
            out_path = os.path.splitext(file_path)[0] + "_ANSI.csv"
            
            with open(file_path, 'r', encoding='utf-8') as fin, open(out_path, 'w', encoding='utf-8', newline='') as fout:
                reader = csv.DictReader(fin)
                headers = reader.fieldnames
                writer = csv.DictWriter(fout, fieldnames=headers)
                writer.writeheader()
                
                converted_count = 0
                for row in reader:
                    trans_text = row.get("trans", "")
                    new_text = ""
                    for char in trans_text:
                        code = ord(char)
                        if 0x0E01 <= code <= 0x0E5B:
                            ansi_char = chr(code - 0x0E00 + 0xA0)
                            new_text += ansi_char
                        else:
                            new_text += char
                            
                    row["trans"] = new_text
                    writer.writerow(row)
                    converted_count += 1
                    
            self.log(f"\n✅ Converted {converted_count} rows.")
            self.log(f"Saved to: {out_path}")
            self.log("NOTE: Open the ANSI.csv file in Notepad. It will look like gibberish (e.g., '¡¢£'), which is correct! The game will render this gibberish as Thai if you modded the font texture.")
            messagebox.showinfo("Success", f"File saved as:\n{os.path.basename(out_path)}")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")

if __name__ == "__main__":
    app = ModTextUtility()
    app.mainloop()
