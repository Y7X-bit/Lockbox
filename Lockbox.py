import customtkinter as ctk
from tkinter import messagebox, filedialog
import string, random, math, pyperclip, os, qrcode
from PIL import Image
import pygame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

pygame.mixer.init()
sound_path = os.path.join(os.path.dirname(__file__), "click.wav")

class Y7XLockBox(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔒 Y7X LockBox")
        self.geometry("740x600")
        self.resizable(False, False)
        self.configure(bg="#000000")  # Pure AMOLED black

        self.colors = {
            'bg': "#000000",
            'card': "#000000",         # Full AMOLED
            'accent': "#ff0000",       # Red outline
            'hover': "#1a0000",        # Slight red hover
            'font': ("Segoe UI", 16),
            'title': ("Orbitron", 24, "bold"),
            'mono': ("Consolas", 18, "bold"),
            'muted': "#cccccc"
        }

        self.history = []
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="🧠 Y7X LOCKBOX", font=self.colors['title'],
                     text_color=self.colors['accent']).pack(pady=20)

        container = ctk.CTkFrame(self, fg_color=self.colors['card'], corner_radius=20)
        container.pack(fill="both", expand=True, padx=20, pady=10)

        self.length_var = ctk.IntVar(value=16)
        self.lower = ctk.BooleanVar(value=True)
        self.upper = ctk.BooleanVar(value=True)
        self.numbers = ctk.BooleanVar(value=True)
        self.symbols = ctk.BooleanVar(value=True)

        # Length Control
        ctk.CTkLabel(container, text="Password Length", font=self.colors['font'],
                     text_color=self.colors['muted']).pack(pady=(10, 0))
        length_frame = ctk.CTkFrame(container, fg_color=self.colors['card'])
        length_frame.pack(pady=5)
        self.length_slider = ctk.CTkSlider(length_frame, from_=8, to=64, variable=self.length_var,
                                           width=300, command=self.update_entropy,
                                           progress_color=self.colors['accent'])
        self.length_slider.pack(side='left', padx=10)
        self.len_label = ctk.CTkLabel(length_frame, text="16 chars", font=self.colors['font'])
        self.len_label.pack(side='left', padx=10)

        # Options
        opts = ctk.CTkFrame(container, fg_color=self.colors['card'])
        opts.pack(pady=10)
        for i, (label, var) in enumerate([
            ("Lowercase", self.lower),
            ("Uppercase", self.upper),
            ("Numbers", self.numbers),
            ("Symbols", self.symbols)
        ]):
            ctk.CTkCheckBox(opts, text=label, variable=var,
                            font=self.colors['font'],
                            border_color=self.colors['accent'],
                            hover_color=self.colors['accent'],
                            fg_color=self.colors['bg'],
                            text_color=self.colors['muted']).grid(row=0, column=i, padx=10, pady=5)

        # Password Box
        self.password_entry = ctk.CTkEntry(container, width=620, height=45,
                                           font=self.colors['mono'],
                                           text_color=self.colors['accent'],
                                           fg_color=self.colors['bg'],
                                           border_color=self.colors['accent'],
                                           corner_radius=30, border_width=2)
        self.password_entry.pack(pady=15)

        # Feedback
        self.feedback = ctk.CTkLabel(container, text="🧠 Strength: Unknown",
                                     font=self.colors['font'], text_color=self.colors['muted'])
        self.feedback.pack()
        self.entropy = ctk.CTkLabel(container, text="🔢 Entropy: 0 bits",
                                    font=self.colors['font'], text_color=self.colors['accent'])
        self.entropy.pack(pady=10)

        # Buttons
        btns = ctk.CTkFrame(container, fg_color=self.colors['card'])
        btns.pack(pady=10)

        btn_style = dict(width=190, height=45, font=self.colors['font'],
                         fg_color=self.colors['bg'],
                         text_color=self.colors['accent'],
                         hover_color=self.colors['hover'],
                         corner_radius=20, border_color=self.colors['accent'], border_width=2)

        ctk.CTkButton(btns, text="⚡ Generate", command=self.generate_password, **btn_style).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(btns, text="📋 Copy", command=self.copy_to_clipboard, **btn_style).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(btns, text="💾 Save", command=self.export_history, **btn_style).grid(row=1, column=0, padx=10, pady=10)
        ctk.CTkButton(btns, text="📱 QR", command=self.qr_show, **btn_style).grid(row=1, column=1, padx=10, pady=10)

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
            messagebox.showwarning("⚠️ Error", "Please select at least one character type.")
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
        if len(pwd) < 12: tips.append("Short")
        if not any(c.isupper() for c in pwd): tips.append("No uppercase")
        if not any(c.isdigit() for c in pwd): tips.append("No digits")
        if not any(c in string.punctuation for c in pwd): tips.append("No symbols")

        if not tips:
            self.feedback.configure(text="✅ Ultra Secure", text_color=self.colors['accent'])
        else:
            msg = "⚠️ Weak: " + ", ".join(tips)
            self.feedback.configure(text=msg, text_color="#ff4444")

    def play_sound(self):
        if os.path.exists(sound_path):
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()

    def copy_to_clipboard(self):
        pyperclip.copy(self.password_entry.get())
        messagebox.showinfo("Copied", "Password copied to clipboard!")

    def export_history(self):
        if not self.history:
            messagebox.showwarning("⚠️ Warning", "No password history to save!")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".txt")
        if filepath:
            with open(filepath, "w") as f:
                f.writelines(p + "\n" for p in self.history)
            messagebox.showinfo("✅ Saved", "Password history saved successfully!")

    def qr_show(self):
        pwd = self.password_entry.get()
        if not pwd:
            messagebox.showwarning("⚠️ Empty", "No password to encode.")
            return
        img = qrcode.make(pwd)
        path = "qr_temp.png"
        img.save(path)
        Image.open(path).show()
        os.remove(path)

if __name__ == '__main__':
    app = Y7XLockBox()
    app.mainloop()