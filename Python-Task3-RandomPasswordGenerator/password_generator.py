
import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string
import pyperclip

# Only 4 character types
CHARACTER_TYPES = {
    "Uppercase (A-Z)": string.ascii_uppercase,
    "Lowercase (a-z)": string.ascii_lowercase,
    "Numbers (0-9)": string.digits,
    "Symbols (!@#...)": "!@#$%^&*()-_=+[]{};:,.?/"
}

BG = "#eef5f4"
TEAL = "#087f8c"
DARK = "#183b40"
WHITE = "#ffffff"


class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("SecureKey - Password Generator")
        self.root.geometry("900x760")
        self.root.minsize(760, 680)
        self.root.configure(bg=BG)

        self.length = tk.IntVar(value=16)
        self.password = tk.StringVar()
        self.history = []

        self.options = {
            name: tk.BooleanVar(value=True)
            for name in CHARACTER_TYPES
        }

        self.build_gui()

    def build_gui(self):
        header = tk.Frame(self.root, bg=TEAL, height=65)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="SecureKey",
            font=("Segoe UI", 22, "bold"),
            bg=TEAL, fg=WHITE
        ).pack(side="left", padx=24)

        tk.Label(
            header, text="SECURE PASSWORD GENERATOR",
            font=("Segoe UI", 10, "bold"),
            bg=TEAL, fg=WHITE
        ).pack(side="right", padx=24)

        main = tk.Frame(self.root, bg=BG, padx=22, pady=14)
        main.pack(fill="both", expand=True)

        # Password length
        length_card = self.make_card(main)

        tk.Label(
            length_card, text="1. Choose Password Length",
            font=("Segoe UI", 12, "bold"),
            bg=WHITE, fg=DARK
        ).pack(anchor="w")

        row = tk.Frame(length_card, bg=WHITE)
        row.pack(fill="x", pady=8)

        tk.Scale(
            row, from_=8, to=64,
            orient="horizontal",
            variable=self.length,
            showvalue=False,
            command=self.update_length,
            bg=WHITE, fg=TEAL,
            troughcolor="#d9eeeb",
            highlightthickness=0,
            bd=0, sliderlength=20
        ).pack(side="left", fill="x", expand=True)

        self.length_label = tk.Label(
            row, text="16 characters",
            font=("Segoe UI", 10, "bold"),
            bg=WHITE, fg=TEAL, width=16
        )
        self.length_label.pack(side="right", padx=10)

        # Exactly four character types
        type_card = self.make_card(main)

        tk.Label(
            type_card,
            text="2. Select Character Types (choose at least two)",
            font=("Segoe UI", 12, "bold"),
            bg=WHITE, fg=DARK
        ).pack(anchor="w")

        grid = tk.Frame(type_card, bg=WHITE)
        grid.pack(fill="x", pady=8)

        for i, (name, variable) in enumerate(self.options.items()):
            tk.Checkbutton(
                grid, text=name,
                variable=variable,
                font=("Segoe UI", 11),
                bg=WHITE, fg=DARK,
                activebackground=WHITE,
                selectcolor=WHITE,
                padx=5, pady=5
            ).grid(
                row=i // 2, column=i % 2,
                sticky="w", padx=10, pady=3
            )

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # Generate button
        tk.Button(
            main, text="GENERATE PASSWORD",
            command=self.generate_password,
            bg=TEAL, fg=WHITE,
            activebackground="#066973",
            activeforeground=WHITE,
            font=("Segoe UI", 11, "bold"),
            relief="flat", cursor="hand2",
            pady=10
        ).pack(fill="x", pady=5)

        # Password output
        output = self.make_card(main)

        tk.Label(
            output, text="3. Your Generated Password",
            font=("Segoe UI", 12, "bold"),
            bg=WHITE, fg=DARK
        ).pack(anchor="w")

        tk.Entry(
            output, textvariable=self.password,
            font=("Consolas", 15),
            justify="center",
            bg="#f1f7f6", fg=TEAL,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#c8e1dd"
        ).pack(fill="x", ipady=8, pady=8)

        buttons = tk.Frame(output, bg=WHITE)
        buttons.pack(fill="x")

        tk.Button(
            buttons, text="Copy to Clipboard",
            command=self.copy_password,
            bg="#16845b", fg=WHITE,
            font=("Segoe UI", 10, "bold"),
            relief="flat", cursor="hand2",
            pady=8
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(
            buttons, text="Clear",
            command=self.clear_password,
            bg="#e8f0ef", fg=DARK,
            font=("Segoe UI", 10),
            relief="flat", cursor="hand2",
            pady=8
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

        strength_row = tk.Frame(output, bg=WHITE)
        strength_row.pack(fill="x", pady=(10, 3))

        tk.Label(
            strength_row, text="Password Strength:",
            font=("Segoe UI", 10, "bold"),
            bg=WHITE, fg=DARK
        ).pack(side="left")

        self.strength_label = tk.Label(
            strength_row, text="Not generated",
            font=("Segoe UI", 10, "bold"),
            bg=WHITE, fg="#647875"
        )
        self.strength_label.pack(side="left", padx=8)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Strength.Horizontal.TProgressbar",
            troughcolor="#e2eeec",
            background=TEAL
        )

        self.strength_bar = ttk.Progressbar(
            output, maximum=3, value=0,
            style="Strength.Horizontal.TProgressbar"
        )
        self.strength_bar.pack(fill="x", pady=4)

        # Recent password history
        history_card = self.make_card(main, expand=True)

        tk.Label(
            history_card,
            text="Recent Passwords — Last 5 in This Session",
            font=("Segoe UI", 12, "bold"),
            bg=WHITE, fg=DARK
        ).pack(anchor="w")

        self.history_list = tk.Listbox(
            history_card, height=5,
            font=("Consolas", 10),
            bg="#f5faf9", fg=DARK,
            selectbackground=TEAL,
            selectforeground=WHITE,
            relief="solid", borderwidth=1
        )
        self.history_list.pack(fill="both", expand=True, pady=8)
        self.history_list.bind(
            "<<ListboxSelect>>", self.select_history
        )

        self.status = tk.Label(
            self.root, text="Ready",
            bg="#dcefeb", fg=DARK,
            font=("Segoe UI", 9), pady=5
        )
        self.status.pack(fill="x", side="bottom")

    def make_card(self, parent, expand=False):
        card = tk.Frame(
            parent, bg=WHITE, padx=16, pady=10,
            highlightbackground="#d3e4e2",
            highlightthickness=1
        )
        card.pack(
            fill="both" if expand else "x",
            expand=expand, pady=5
        )
        return card

    def update_length(self, value):
        self.length_label.config(
            text=f"{int(float(value))} characters"
        )

    def generate_password(self):
        selected_groups = [
            CHARACTER_TYPES[name]
            for name, variable in self.options.items()
            if variable.get()
        ]

        length = self.length.get()

        if len(selected_groups) < 2:
            messagebox.showwarning(
                "Select Character Types",
                "Please select at least two character types."
            )
            return

        # Guarantee one character from every selected type
        password_chars = [
            secrets.choice(group)
            for group in selected_groups
        ]

        all_chars = "".join(selected_groups)

        for _ in range(length - len(password_chars)):
            password_chars.append(secrets.choice(all_chars))

        secrets.SystemRandom().shuffle(password_chars)
        result = "".join(password_chars)

        self.password.set(result)

        # Estimate strength
        diversity = len(selected_groups)

        if length >= 16 and diversity >= 3:
            strength, score, color = "Strong", 3, "#16845b"
        elif length >= 12 and diversity >= 2:
            strength, score, color = "Medium", 2, "#b8790b"
        else:
            strength, score, color = "Weak", 1, "#d14343"

        self.strength_label.config(text=strength, fg=color)
        self.strength_bar.configure(value=score)

        # Automatically copy password
        try:
            pyperclip.copy(result)
            self.status.config(
                text="Password generated and copied to clipboard."
            )
        except Exception:
            self.status.config(
                text="Password generated. Use Copy to Clipboard if needed."
            )

        # Keep only the last five passwords
        self.history.insert(0, result)
        self.history = self.history[:5]
        self.refresh_history()

    def copy_password(self):
        result = self.password.get()

        if not result:
            messagebox.showwarning(
                "No Password",
                "Generate a password first."
            )
            return

        try:
            pyperclip.copy(result)
            self.status.config(text="Password copied to clipboard.")
        except Exception as error:
            messagebox.showerror(
                "Clipboard Error",
                f"Could not copy the password.\n{error}"
            )

    def clear_password(self):
        self.password.set("")
        self.strength_label.config(
            text="Not generated", fg="#647875"
        )
        self.strength_bar.configure(value=0)
        self.status.config(text="Password field cleared.")

    def refresh_history(self):
        self.history_list.delete(0, tk.END)
        for password in self.history:
            self.history_list.insert(tk.END, password)

    def select_history(self, event=None):
        selection = self.history_list.curselection()

        if selection:
            self.password.set(
                self.history_list.get(selection[0])
            )
            self.status.config(text="Recent password selected.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
