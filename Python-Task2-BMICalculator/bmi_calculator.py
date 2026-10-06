import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os


# =========================================================
# DATABASE
# =========================================================

# Database will be created automatically
# in the same folder as this Python file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "bmi_records.db")

# Store current BMI result
current_bmi = None
current_category = None


def create_database():

    try:

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Check whether table already exists
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name='bmi_records'
        """)

        table_exists = cursor.fetchone()

        # If table exists, check its columns
        if table_exists:

            cursor.execute("PRAGMA table_info(bmi_records)")

            columns = cursor.fetchall()

            column_names = [
                column[1]
                for column in columns
            ]

            required_columns = [
                "id",
                "name",
                "weight",
                "height",
                "bmi",
                "category",
                "date_time"
            ]

            # If old database has wrong structure
            if not all(
                column in column_names
                for column in required_columns
            ):

                # Rename old table
                cursor.execute("""
                    ALTER TABLE bmi_records
                    RENAME TO old_bmi_records
                """)

                # Create correct table
                cursor.execute("""
                    CREATE TABLE bmi_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        weight REAL NOT NULL,
                        height REAL NOT NULL,
                        bmi REAL NOT NULL,
                        category TEXT NOT NULL,
                        date_time TEXT NOT NULL
                    )
                """)

                # Copy old records if possible
                if all(
                    column in column_names
                    for column in [
                        "weight",
                        "height",
                        "bmi",
                        "category",
                        "date_time"
                    ]
                ):

                    cursor.execute("""
                        INSERT INTO bmi_records
                        (name, weight, height, bmi, category, date_time)
                        SELECT
                            'Unknown',
                            weight,
                            height,
                            bmi,
                            category,
                            date_time
                        FROM old_bmi_records
                    """)

                # Delete old table
                cursor.execute("""
                    DROP TABLE old_bmi_records
                """)

        else:

            # Create new table
            cursor.execute("""
                CREATE TABLE bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    date_time TEXT NOT NULL
                )
            """)

        conn.commit()
        conn.close()

    except sqlite3.Error as e:

        messagebox.showerror(
            "Database Error",
            f"Could not create or update database.\n\n{e}"
        )


# =========================================================
# BMI CALCULATION
# =========================================================

def calculate_bmi():

    global current_bmi, current_category

    try:

        # Get values from entry boxes
        name = name_entry.get().strip()
        weight_text = weight_entry.get().strip()
        height_text = height_entry.get().strip()

        # Check name
        if not name:

            messagebox.showwarning(
                "Missing Name",
                "Please enter your name."
            )

            return False

        # Check weight and height
        if not weight_text or not height_text:

            messagebox.showwarning(
                "Missing Details",
                "Please enter weight and height."
            )

            return False

        # Convert values to numbers
        weight = float(weight_text)
        height_cm = float(height_text)

        # Validate weight
        if weight <= 0:

            messagebox.showwarning(
                "Invalid Weight",
                "Weight must be greater than 0."
            )

            return False

        # Validate height
        if height_cm <= 0:

            messagebox.showwarning(
                "Invalid Height",
                "Height must be greater than 0."
            )

            return False

        # Convert height from cm to metres
        height_m = height_cm / 100

        # BMI formula
        bmi = weight / (height_m ** 2)

        # Determine BMI category
        if bmi < 18.5:

            category = "Underweight"

        elif bmi < 25:

            category = "Normal"

        elif bmi < 30:

            category = "Overweight"

        else:

            category = "Obese"

        # Store result
        current_bmi = bmi
        current_category = category

        # Display BMI
        bmi_value_label.config(
            text=f"{bmi:.2f}"
        )

        # Display category
        category_label.config(
            text=category
        )

        # Display status
        status_label.config(
            text="BMI calculated successfully."
        )

        return True

    except ValueError:

        current_bmi = None
        current_category = None

        messagebox.showerror(
            "Invalid Input",
            "Please enter numbers only for weight and height."
        )

        return False

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"Something went wrong.\n\n{e}"
        )

        return False


# =========================================================
# SAVE RECORD
# =========================================================

def save_record():

    global current_bmi, current_category

    try:

        name = name_entry.get().strip()
        weight_text = weight_entry.get().strip()
        height_text = height_entry.get().strip()

        # Check name
        if not name:

            messagebox.showwarning(
                "Missing Name",
                "Please enter your name."
            )

            return

        # Check weight and height
        if not weight_text or not height_text:

            messagebox.showwarning(
                "Missing Details",
                "Please enter weight and height first."
            )

            return

        # Calculate BMI before saving
        if not calculate_bmi():

            return

        weight = float(weight_text)
        height_cm = float(height_text)

        # Current date and time
        date_time = datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        )

        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Insert record
        cursor.execute("""
            INSERT INTO bmi_records
            (name, weight, height, bmi, category, date_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            weight,
            height_cm,
            current_bmi,
            current_category,
            date_time
        ))

        conn.commit()
        conn.close()

        # Update status
        status_label.config(
            text="Record saved successfully."
        )

        # Success message
        messagebox.showinfo(
            "Saved",
            "BMI record saved successfully!"
        )

    except ValueError:

        messagebox.showerror(
            "Invalid Input",
            "Please enter valid numeric values."
        )

    except sqlite3.Error as e:

        messagebox.showerror(
            "Database Error",
            f"Could not save the record.\n\n{e}"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"Something went wrong.\n\n{e}"
        )


# =========================================================
# VIEW HISTORY
# =========================================================

def view_history():

    try:

        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Get saved records
        cursor.execute("""
            SELECT
                name,
                weight,
                height,
                bmi,
                category,
                date_time
            FROM bmi_records
            ORDER BY id DESC
        """)

        records = cursor.fetchall()

        conn.close()

        # Create history window
        history_window = tk.Toplevel(root)

        history_window.title(
            "BMI History"
        )

        history_window.geometry(
            "900x500"
        )

        history_window.configure(
            bg="#f4f6f9"
        )

        # History title
        tk.Label(
            history_window,
            text="BMI History",
            font=("Arial", 22, "bold"),
            bg="#f4f6f9",
            fg="#1f3c88"
        ).pack(
            pady=15
        )

        # If no records
        if not records:

            tk.Label(
                history_window,
                text="No BMI records saved yet.",
                font=("Arial", 14),
                bg="#f4f6f9",
                fg="#555555"
            ).pack(
                pady=30
            )

            return

        # Table frame
        frame = tk.Frame(
            history_window,
            bg="#f4f6f9"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # Table columns
        columns = (
            "Name",
            "Weight",
            "Height",
            "BMI",
            "Category",
            "Date"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        # Column headings
        for column in columns:

            tree.heading(
                column,
                text=column
            )

        # Column widths
        tree.column(
            "Name",
            width=150,
            anchor="center"
        )

        tree.column(
            "Weight",
            width=100,
            anchor="center"
        )

        tree.column(
            "Height",
            width=100,
            anchor="center"
        )

        tree.column(
            "BMI",
            width=100,
            anchor="center"
        )

        tree.column(
            "Category",
            width=130,
            anchor="center"
        )

        tree.column(
            "Date",
            width=180,
            anchor="center"
        )

        # Insert records into table
        for record in records:

            tree.insert(
                "",
                "end",
                values=record
            )

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )

        tree.configure(
            yscrollcommand=scrollbar.set
        )

        tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    except sqlite3.Error as e:

        messagebox.showerror(
            "Database Error",
            f"Could not load history.\n\n{e}"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"Something went wrong.\n\n{e}"
        )


# =========================================================
# CLEAR FIELDS
# =========================================================

def clear_fields():

    global current_bmi, current_category

    # Clear name
    name_entry.delete(
        0,
        tk.END
    )

    # Clear weight
    weight_entry.delete(
        0,
        tk.END
    )

    # Clear height
    height_entry.delete(
        0,
        tk.END
    )

    # Reset BMI
    bmi_value_label.config(
        text="--"
    )

    # Reset category
    category_label.config(
        text="--"
    )

    # Reset status
    status_label.config(
        text="Enter your details to calculate BMI."
    )

    # Reset variables
    current_bmi = None
    current_category = None


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title(
    "BMI Calculator | OIBSIP Task 2"
)

root.geometry(
    "1250x750"
)

root.minsize(
    1000,
    650
)

root.configure(
    bg="#f4f6f9"
)


# =========================================================
# CREATE DATABASE
# =========================================================

create_database()


# =========================================================
# HEADER
# =========================================================

header = tk.Frame(
    root,
    bg="#2453d4",
    height=130
)

header.pack(
    fill="x"
)

header.pack_propagate(False)

tk.Label(
    header,
    text="⚖  BMI Calculator",
    font=("Arial", 32, "bold"),
    bg="#2453d4",
    fg="white"
).pack(
    pady=(25, 5)
)

tk.Label(
    header,
    text="OIBSIP • Python Programming • Task 2",
    font=("Arial", 14),
    bg="#2453d4",
    fg="#dce5ff"
).pack()


# =========================================================
# MAIN CONTENT
# =========================================================

main_frame = tk.Frame(
    root,
    bg="#f4f6f9"
)

main_frame.pack(
    fill="both",
    expand=True,
    padx=35,
    pady=25
)


# =========================================================
# LEFT PANEL
# =========================================================

left_panel = tk.Frame(
    main_frame,
    bg="white",
    bd=1,
    relief="solid"
)

left_panel.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 10)
)

tk.Label(
    left_panel,
    text="Enter Your Details",
    font=("Arial", 22, "bold"),
    bg="white",
    fg="#172b4d"
).pack(
    anchor="w",
    padx=35,
    pady=(35, 5)
)

tk.Label(
    left_panel,
    text="Enter your information to calculate BMI.",
    font=("Arial", 11),
    bg="white",
    fg="#777777"
).pack(
    anchor="w",
    padx=35,
    pady=(0, 25)
)


# =========================================================
# NAME
# =========================================================

tk.Label(
    left_panel,
    text="Full Name",
    font=("Arial", 12, "bold"),
    bg="white",
    fg="#333333"
).pack(
    anchor="w",
    padx=35
)

name_entry = tk.Entry(
    left_panel,
    font=("Arial", 14),
    bd=1,
    relief="solid"
)

name_entry.pack(
    fill="x",
    padx=35,
    pady=(7, 20),
    ipady=8
)


# =========================================================
# WEIGHT
# =========================================================

tk.Label(
    left_panel,
    text="Weight (kg)",
    font=("Arial", 12, "bold"),
    bg="white",
    fg="#333333"
).pack(
    anchor="w",
    padx=35
)

weight_entry = tk.Entry(
    left_panel,
    font=("Arial", 14),
    bd=1,
    relief="solid"
)

weight_entry.pack(
    fill="x",
    padx=35,
    pady=(7, 20),
    ipady=8
)


# =========================================================
# HEIGHT
# =========================================================

tk.Label(
    left_panel,
    text="Height (cm)",
    font=("Arial", 12, "bold"),
    bg="white",
    fg="#333333"
).pack(
    anchor="w",
    padx=35
)

height_entry = tk.Entry(
    left_panel,
    font=("Arial", 14),
    bd=1,
    relief="solid"
)

height_entry.pack(
    fill="x",
    padx=35,
    pady=(7, 25),
    ipady=8
)


# =========================================================
# CALCULATE BUTTON
# =========================================================

calculate_button = tk.Button(
    left_panel,
    text="Calculate BMI",
    command=calculate_bmi,
    font=("Arial", 13, "bold"),
    bg="#2864e6",
    fg="white",
    activebackground="#174bb8",
    activeforeground="white",
    bd=0,
    cursor="hand2"
)

calculate_button.pack(
    fill="x",
    padx=35,
    ipady=12
)


# =========================================================
# RIGHT PANEL
# =========================================================

right_panel = tk.Frame(
    main_frame,
    bg="white",
    bd=1,
    relief="solid"
)

right_panel.pack(
    side="right",
    fill="both",
    expand=True,
    padx=(10, 0)
)

tk.Label(
    right_panel,
    text="Your BMI Result",
    font=("Arial", 22, "bold"),
    bg="white",
    fg="#172b4d"
).pack(
    pady=(35, 5)
)

tk.Label(
    right_panel,
    text="Based on your entered details",
    font=("Arial", 11),
    bg="white",
    fg="#777777"
).pack(
    pady=(0, 25)
)


# BMI value
bmi_value_label = tk.Label(
    right_panel,
    text="--",
    font=("Arial", 42, "bold"),
    bg="white",
    fg="#2864e6"
)

bmi_value_label.pack()


tk.Label(
    right_panel,
    text="BMI",
    font=("Arial", 12),
    bg="white",
    fg="#888888"
).pack(
    pady=(0, 20)
)


# Category
category_label = tk.Label(
    right_panel,
    text="--",
    font=("Arial", 25, "bold"),
    bg="white",
    fg="#2864e6"
)

category_label.pack()


tk.Label(
    right_panel,
    text="Health Category",
    font=("Arial", 12),
    bg="white",
    fg="#888888"
).pack(
    pady=(5, 20)
)


# Status
status_label = tk.Label(
    right_panel,
    text="Enter your details to calculate BMI.",
    font=("Arial", 10),
    bg="white",
    fg="#2864e6"
)

status_label.pack(
    pady=5
)


# =========================================================
# BMI REFERENCE
# =========================================================

tk.Label(
    right_panel,
    text="BMI Reference",
    font=("Arial", 14, "bold"),
    bg="white",
    fg="#222222"
).pack(
    pady=(25, 15)
)

reference_frame = tk.Frame(
    right_panel,
    bg="white"
)

reference_frame.pack(
    fill="x",
    padx=35
)

reference_data = [
    ("Below 18.5", "Underweight"),
    ("18.5 – 24.9", "Normal"),
    ("25 – 29.9", "Overweight"),
    ("30 or above", "Obese")
]

for value, category in reference_data:

    row = tk.Frame(
        reference_frame,
        bg="white"
    )

    row.pack(
        fill="x",
        pady=5
    )

    tk.Label(
        row,
        text=value,
        font=("Arial", 10),
        bg="white",
        fg="#777777"
    ).pack(
        side="left"
    )

    tk.Label(
        row,
        text=category,
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#2864e6"
    ).pack(
        side="right"
    )


# =========================================================
# BOTTOM BUTTONS
# =========================================================

button_frame = tk.Frame(
    root,
    bg="#f4f6f9"
)

button_frame.pack(
    fill="x",
    padx=35,
    pady=(0, 15)
)


# =========================================================
# SAVE RECORD BUTTON
# =========================================================

save_button = tk.Button(
    button_frame,
    text="💾  Save Record",
    command=save_record,
    font=("Arial", 12, "bold"),
    bg="#16a34a",
    fg="white",
    activebackground="#12823b",
    activeforeground="white",
    bd=0,
    cursor="hand2"
)

save_button.pack(
    side="left",
    ipadx=20,
    ipady=12,
    padx=(0, 15)
)


# =========================================================
# VIEW HISTORY BUTTON
# =========================================================

history_button = tk.Button(
    button_frame,
    text="📋  View History",
    command=view_history,
    font=("Arial", 12, "bold"),
    bg="#7c3aed",
    fg="white",
    activebackground="#6425c5",
    activeforeground="white",
    bd=0,
    cursor="hand2"
)

history_button.pack(
    side="left",
    ipadx=20,
    ipady=12,
    padx=15
)


# =========================================================
# CLEAR BUTTON
# =========================================================

clear_button = tk.Button(
    button_frame,
    text="Clear",
    command=clear_fields,
    font=("Arial", 12, "bold"),
    bg="#6b7280",
    fg="white",
    activebackground="#4b5563",
    activeforeground="white",
    bd=0,
    cursor="hand2"
)

clear_button.pack(
    side="right",
    ipadx=25,
    ipady=12
)


# =========================================================
# FOOTER
# =========================================================

tk.Label(
    root,
    text="BMI = Weight (kg) ÷ Height² (m²)  •  Height is entered in centimetres",
    font=("Arial", 10),
    bg="#f4f6f9",
    fg="#777777"
).pack(
    pady=(0, 15)
)


# =========================================================
# START APPLICATION
# =========================================================

root.mainloop()