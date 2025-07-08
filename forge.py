import customtkinter as ctk
from tkinter import messagebox, filedialog
import string, random, math, pyperclip, os, qrcode
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import time, pygame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

pygame.mixer.init()
sound_path = os.path.join(os.path.dirname(__file__), "click.wav")

class UltraSecureForge(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Y7X Password Forge PRO")
        self.geometry("780x660")
        self.resizable(False, False)
        self.configure(bg="#000000")

        self.colors = {
            'bg': "#000000",
            'card': "#1a1a1a",
            'accent': "#ff003c",
            'secondary': "#ff5252",
            'danger': "#ff0000",
            'gold': "#ff3e3e",
            'font': ("Segoe UI", 16),
            'title': ("Orbitron", 28, "bold"),
            'mono': ("Consolas", 20, "bold")
        }
        self.history = []
        self.init_ui()

    def init_ui(self):
        ctk.CTkLabel(self, text="🔐 Y7X ULTRA SECURE FORGE", font=self.colors['title'], text_color=self.colors['accent']).pack(pady=20)

        main_frame = ctk.CTkFrame(self, fg_color=self.colors['card'], corner_radius=25)
        main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.length_var = ctk.IntVar(value=16)
        self.lower = ctk.BooleanVar(value=True)
        self.upper = ctk.BooleanVar(value=True)
        self.numbers = ctk.BooleanVar(value=True)
        self.symbols = ctk.BooleanVar(value=True)

        controls = ctk.CTkFrame(main_frame, fg_color=self.colors['card'], corner_radius=20)
        controls.pack(pady=10)

        ctk.CTkLabel(controls, text="Password Length:", font=self.colors['font'], text_color=self.colors['secondary']).pack()

        slider_frame = ctk.CTkFrame(controls, fg_color=self.colors['card'])
        slider_frame.pack()

        self.length_slider = ctk.CTkSlider(slider_frame, from_=8, to=64, variable=self.length_var, command=self.update_entropy, width=300, progress_color=self.colors['accent'])
        self.length_slider.pack(side="left", padx=10, pady=10)

        self.len_label = ctk.CTkLabel(slider_frame, text="16 chars", font=self.colors['font'])
        self.len_label.pack(side="left", padx=10)

        opts = ctk.CTkFrame(main_frame, fg_color=self.colors['card'], corner_radius=20)
        opts.pack(pady=10)

        ctk.CTkCheckBox(opts, text="Lowercase", variable=self.lower, font=self.colors['font'], border_color=self.colors['accent'], hover_color=self.colors['accent']).grid(row=0, column=0, padx=20, pady=10)
        ctk.CTkCheckBox(opts, text="Uppercase", variable=self.upper, font=self.colors['font'], border_color=self.colors['accent'], hover_color=self.colors['accent']).grid(row=0, column=1, padx=20, pady=10)
        ctk.CTkCheckBox(opts, text="Numbers", variable=self.numbers, font=self.colors['font'], border_color=self.colors['accent'], hover_color=self.colors['accent']).grid(row=0, column=2, padx=20, pady=10)
        ctk.CTkCheckBox(opts, text="Symbols", variable=self.symbols, font=self.colors['font'], border_color=self.colors['accent'], hover_color=self.colors['accent']).grid(row=0, column=3, padx=20, pady=10)

        for i in range(4):
            opts.grid_columnconfigure(i, weight=1)

        self.password_entry = ctk.CTkEntry(main_frame, font=self.colors['mono'], width=600, height=45, corner_radius=30, text_color=self.colors['gold'], fg_color=self.colors['bg'], border_color=self.colors['accent'], border_width=2)
        self.password_entry.pack(pady=20)

        self.feedback = ctk.CTkLabel(main_frame, text="🧠 Strength: Unknown", font=self.colors['font'], text_color=self.colors['secondary'])
        self.feedback.pack()
        self.entropy = ctk.CTkLabel(main_frame, text="🔢 Entropy: 0 bits", font=self.colors['font'], text_color=self.colors['accent'])
        self.entropy.pack(pady=(0, 15))

        btn_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['card'], corner_radius=20)
        btn_frame.pack(pady=10)

        button_style = dict(width=200, height=45, font=self.colors['font'], fg_color=self.colors['accent'], corner_radius=20, border_color=self.colors['danger'], border_width=2, hover_color=self.colors['secondary'])

        ctk.CTkButton(btn_frame, text="⚡ Generate", command=self.generate_password, **button_style).grid(row=0, column=0, padx=15, pady=10)
        ctk.CTkButton(btn_frame, text="📋 Copy", command=self.copy_to_clipboard, **button_style).grid(row=0, column=1, padx=15, pady=10)
        ctk.CTkButton(btn_frame, text="📜 Save History", command=self.export_history, **button_style).grid(row=1, column=0, padx=15, pady=10)
        ctk.CTkButton(btn_frame, text="📱 QR", command=self.qr_show, **button_style).grid(row=1, column=1, padx=15, pady=10)

    def play_sound(self):
        if os.path.exists(sound_path):
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()

    def update_entropy(self, _=None):
        length = self.length_var.get()
        charset = len(self.get_charset())
        entropy = length * math.log2(charset) if charset else 0
        self.entropy.configure(text=f"🔢 Entropy: {entropy:.2f} bits")
        self.len_label.configure(text=f"{length} chars")

    def get_charset(self):
        charset = ""
        if self.lower.get(): charset += string.ascii_lowercase
        if self.upper.get(): charset += string.ascii_uppercase
        if self.numbers.get(): charset += string.digits
        if self.symbols.get(): charset += string.punctuation
        return charset

    def generate_password(self):
        self.play_sound()
        charset = self.get_charset()
        if not charset:
            messagebox.showwarning("Empty Set", "No character types selected!")
            return
        length = self.length_var.get()
        password = ''.join(random.choice(charset) for _ in range(length))
        self.password_entry.delete(0, 'end')
        self.password_entry.insert(0, password)
        self.update_entropy()
        self.analyze_strength(password)
        self.history.append(password)

    def analyze_strength(self, pwd):
        tips = []
        score = 0
        if len(pwd) < 12: tips.append("Make it longer (12+ chars)")
        if not any(c.isupper() for c in pwd): tips.append("Add uppercase letters")
        if not any(c.isdigit() for c in pwd): tips.append("Add digits")
        if not any(c in string.punctuation for c in pwd): tips.append("Add special characters")

        if not tips:
            self.feedback.configure(text="✅ Ultra Secure", text_color=self.colors['accent'])
        else:
            self.feedback.configure(text="⚠️ Weak: " + "; ".join(tips), text_color=self.colors['danger'])

    def copy_to_clipboard(self):
        pyperclip.copy(self.password_entry.get())
        messagebox.showinfo("Copied", "Password copied!")

    def export_history(self):
        if not self.history:
            messagebox.showwarning("No History", "No passwords to export yet!")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".txt")
        if filepath:
            with open(filepath, "w") as f:
                for pwd in self.history:
                    f.write(pwd + "\n")
            messagebox.showinfo("Exported", "History saved successfully!")

    def qr_show(self):
        pwd = self.password_entry.get()
        if not pwd:
            messagebox.showerror("Error", "Nothing to export")
            return
        qr = qrcode.make(pwd)
        path = "qr.png"
        qr.save(path)
        img = Image.open(path)
        img.show()
        os.remove(path)

if __name__ == '__main__':
    app = UltraSecureForge()
    app.mainloop()