import tkinter as tk
from tkinter import ttk


# ============================================================
# PROPOSITIONAL LOGIC DISEASE DETECTION
# ============================================================

DISEASE_RULES = {
    "FLU": {
        "conditions": [
            ("Fever", True),
            ("Cough", True),
            ("Body Ache", True),
            ("Fatigue", True),
        ],
        "display_rule": "Fever AND Cough AND Body Ache AND Fatigue"
    },

    "COMMON COLD": {
        "conditions": [
            ("Cough", True),
            ("Runny Nose", True),
            ("Sore Throat", True),
            ("Fever", False),
        ],
        "display_rule": "Cough AND Runny Nose AND Sore Throat AND NOT Fever"
    },

    "DENGUE": {
        "conditions": [
            ("Fever", True),
            ("Headache", True),
            ("Body Ache", True),
            ("Nausea", True),
        ],
        "display_rule": "Fever AND Headache AND Body Ache AND Nausea"
    },

    "FOOD POISONING": {
        "conditions": [
            ("Nausea", True),
            ("Diarrhea", True),
            ("Cough", False),
        ],
        "display_rule": "Nausea AND Diarrhea AND NOT Cough"
    }
}


SYMPTOMS = [
    "Fever",
    "Cough",
    "Body Ache",
    "Headache",
    "Sore Throat",
    "Runny Nose",
    "Nausea",
    "Diarrhea",
    "Fatigue"
]


# ============================================================
# DISEASE DETECTION LOGIC
# ============================================================

def detect_disease(selected_symptoms):

    detected = []

    for disease, rule in DISEASE_RULES.items():

        rule_satisfied = True

        for symptom, required_value in rule["conditions"]:

            actual_value = symptom in selected_symptoms

            if actual_value != required_value:
                rule_satisfied = False
                break

        if rule_satisfied:
            detected.append(
                (disease, rule["display_rule"])
            )

    return detected


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title("Disease Detection System")
root.geometry("1250x720")
root.minsize(1100, 650)
root.configure(bg="#EAF2F8")


# ============================================================
# STYLE
# ============================================================

style = ttk.Style()

try:
    style.theme_use("clam")
except tk.TclError:
    pass


style.configure(
    "Title.TLabel",
    font=("Arial", 24, "bold"),
    background="#EAF2F8",
    foreground="#1B4F72"
)

style.configure(
    "Subtitle.TLabel",
    font=("Arial", 12),
    background="#EAF2F8",
    foreground="#566573"
)

style.configure(
    "PanelTitle.TLabel",
    font=("Arial", 15, "bold"),
    background="white",
    foreground="#154360"
)

style.configure(
    "Symptom.TCheckbutton",
    font=("Arial", 11),
    background="white"
)


# ============================================================
# HEADER
# ============================================================

header = tk.Frame(
    root,
    bg="#EAF2F8"
)

header.pack(
    fill="x",
    padx=20,
    pady=(15, 5)
)


ttk.Label(
    header,
    text="DISEASE DETECTION SYSTEM",
    style="Title.TLabel"
).pack()


ttk.Label(
    header,
    text="Rule-Based Expert System using Propositional Logic",
    style="Subtitle.TLabel"
).pack(
    pady=(3, 0)
)


# ============================================================
# MAIN CONTAINER
# ============================================================

main = tk.Frame(
    root,
    bg="#EAF2F8"
)

main.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=15
)

main.grid_columnconfigure(0, weight=0)
main.grid_columnconfigure(1, weight=1)
main.grid_columnconfigure(2, weight=1)

main.grid_rowconfigure(0, weight=1)


# ============================================================
# LEFT PANEL - SYMPTOMS
# ============================================================

symptom_panel = tk.Frame(
    main,
    bg="white",
    bd=2,
    relief="ridge",
    width=260
)

symptom_panel.grid(
    row=0,
    column=0,
    sticky="ns",
    padx=(0, 8)
)

symptom_panel.grid_propagate(False)


ttk.Label(
    symptom_panel,
    text="Select Symptoms",
    style="PanelTitle.TLabel"
).pack(
    pady=(18, 12)
)


# Information label

info_label = tk.Label(
    symptom_panel,
    text="Select all symptoms\nthat are present.",
    font=("Arial", 10),
    bg="white",
    fg="#7F8C8D",
    justify="center"
)

info_label.pack(
    pady=(0, 12)
)


# ============================================================
# CHECKBOXES
# ============================================================

symptom_vars = {}

checkbox_container = tk.Frame(
    symptom_panel,
    bg="white"
)

checkbox_container.pack(
    fill="both",
    expand=True,
    padx=20
)


for symptom in SYMPTOMS:

    var = tk.BooleanVar(value=False)

    symptom_vars[symptom] = var

    check = ttk.Checkbutton(
        checkbox_container,
        text=symptom,
        variable=var,
        style="Symptom.TCheckbutton"
    )

    check.pack(
        anchor="w",
        pady=5
    )


# ============================================================
# CENTER PANEL - PICTORIAL LOGIC
# ============================================================

logic_panel = tk.Frame(
    main,
    bg="white",
    bd=2,
    relief="ridge"
)

logic_panel.grid(
    row=0,
    column=1,
    sticky="nsew",
    padx=8
)


ttk.Label(
    logic_panel,
    text="Propositional Logic Flow",
    style="PanelTitle.TLabel"
).pack(
    pady=(15, 5)
)


# Canvas

logic_canvas = tk.Canvas(
    logic_panel,
    bg="#FBFCFC",
    highlightthickness=0
)

logic_canvas.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


# ============================================================
# DRAWING FUNCTIONS
# ============================================================

def draw_box(x1, y1, x2, y2, text, fill):

    logic_canvas.create_rectangle(
        x1,
        y1,
        x2,
        y2,
        fill=fill,
        outline="#2E86C1",
        width=2
    )

    logic_canvas.create_text(
        (x1 + x2) / 2,
        (y1 + y2) / 2,
        text=text,
        font=("Arial", 11, "bold"),
        justify="center"
    )


def draw_arrow(x1, y1, x2, y2):

    logic_canvas.create_line(
        x1,
        y1,
        x2,
        y2,
        arrow=tk.LAST,
        width=2,
        fill="#566573"
    )


def draw_logic_flow():

    logic_canvas.delete("all")

    # Get current canvas size

    width = logic_canvas.winfo_width()
    height = logic_canvas.winfo_height()

    if width < 300:
        width = 500

    if height < 400:
        height = 550

    center_x = width / 2

    box_width = min(300, width - 50)

    x1 = center_x - box_width / 2
    x2 = center_x + box_width / 2

    # --------------------------------------------------------
    # Box 1
    # --------------------------------------------------------

    draw_box(
        x1,
        35,
        x2,
        100,
        "PATIENT\nSYMPTOMS",
        "#D6EAF8"
    )

    draw_arrow(
        center_x,
        100,
        center_x,
        145
    )

    # --------------------------------------------------------
    # Box 2
    # --------------------------------------------------------

    draw_box(
        x1,
        145,
        x2,
        215,
        "PROPOSITIONAL\nLOGIC",
        "#D5F5E3"
    )

    draw_arrow(
        center_x,
        215,
        center_x,
        260
    )

    # --------------------------------------------------------
    # Box 3
    # --------------------------------------------------------

    draw_box(
        x1,
        260,
        x2,
        330,
        "CHECK\nDISEASE RULES",
        "#FCF3CF"
    )

    draw_arrow(
        center_x,
        330,
        center_x,
        375
    )

    # --------------------------------------------------------
    # Box 4
    # --------------------------------------------------------

    draw_box(
        x1,
        375,
        x2,
        445,
        "DISEASE\nDETECTION",
        "#FADBD8"
    )

    logic_canvas.create_text(
        center_x,
        490,
        text="AND  =  ∧\nNOT  =  ¬\nIF CONDITIONS → DISEASE",
        font=("Arial", 10),
        fill="#566573",
        justify="center"
    )


# Draw after window has loaded

root.after(
    100,
    draw_logic_flow
)


# Redraw when window size changes

logic_canvas.bind(
    "<Configure>",
    lambda event: draw_logic_flow()
)


# ============================================================
# RIGHT PANEL - RESULT
# ============================================================

result_panel = tk.Frame(
    main,
    bg="white",
    bd=2,
    relief="ridge"
)

result_panel.grid(
    row=0,
    column=2,
    sticky="nsew",
    padx=(8, 0)
)


ttk.Label(
    result_panel,
    text="Detection Result",
    style="PanelTitle.TLabel"
).pack(
    pady=(15, 10)
)


# ------------------------------------------------------------
# Selected symptoms area
# ------------------------------------------------------------

selected_frame = tk.LabelFrame(
    result_panel,
    text="Selected Symptoms",
    font=("Arial", 11, "bold"),
    bg="white",
    fg="#34495E"
)

selected_frame.pack(
    fill="x",
    padx=15,
    pady=8
)


selected_label = tk.Label(
    selected_frame,
    text="None selected",
    font=("Arial", 10),
    bg="white",
    fg="#7F8C8D",
    wraplength=330,
    justify="left"
)

selected_label.pack(
    padx=10,
    pady=10
)


# ------------------------------------------------------------
# Disease result
# ------------------------------------------------------------

disease_frame = tk.LabelFrame(
    result_panel,
    text="Result",
    font=("Arial", 11, "bold"),
    bg="white",
    fg="#34495E"
)

disease_frame.pack(
    fill="x",
    padx=15,
    pady=8
)


disease_label = tk.Label(
    disease_frame,
    text="Waiting for input...",
    font=("Arial", 15, "bold"),
    bg="white",
    fg="#7F8C8D",
    wraplength=330,
    justify="center"
)

disease_label.pack(
    padx=10,
    pady=18
)


# ------------------------------------------------------------
# Logic reasoning
# ------------------------------------------------------------

reason_frame = tk.LabelFrame(
    result_panel,
    text="Satisfied Rules",
    font=("Arial", 11, "bold"),
    bg="white",
    fg="#34495E"
)

reason_frame.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=8
)


reason_text = tk.Text(
    reason_frame,
    font=("Consolas", 10),
    bg="#FBFCFC",
    fg="#2C3E50",
    relief="flat",
    wrap="word"
)

reason_text.pack(
    fill="both",
    expand=True,
    padx=8,
    pady=8
)

reason_text.insert(
    "1.0",
    "No rules evaluated yet."
)

reason_text.config(
    state="disabled"
)


# ============================================================
# DETECTION FUNCTION
# ============================================================

def check_disease():

    # --------------------------------------------------------
    # Get selected symptoms
    # --------------------------------------------------------

    selected_symptoms = {
        symptom
        for symptom, var in symptom_vars.items()
        if var.get()
    }

    # --------------------------------------------------------
    # Update selected symptom display
    # --------------------------------------------------------

    if selected_symptoms:

        selected_text = "\n".join(
            "✓ " + symptom
            for symptom in sorted(selected_symptoms)
        )

        selected_label.config(
            text=selected_text,
            fg="#1B4F72"
        )

    else:

        selected_label.config(
            text="None selected",
            fg="#7F8C8D"
        )

    # --------------------------------------------------------
    # Detect disease
    # --------------------------------------------------------

    detected = detect_disease(
        selected_symptoms
    )

    # --------------------------------------------------------
    # Update result
    # --------------------------------------------------------

    if detected:

        disease_names = [
            disease
            for disease, rule in detected
        ]

        disease_label.config(
            text="\n".join(disease_names),
            fg="#C0392B"
        )

    else:

        disease_label.config(
            text="NO MATCHING DISEASE",
            fg="#D68910"
        )

    # --------------------------------------------------------
    # Update reasoning
    # --------------------------------------------------------

    reason_text.config(
        state="normal"
    )

    reason_text.delete(
        "1.0",
        tk.END
    )

    if detected:

        for disease, rule in detected:

            reason_text.insert(
                tk.END,
                f"DISEASE: {disease}\n"
            )

            reason_text.insert(
                tk.END,
                f"RULE:\n{rule}\n"
            )

            reason_text.insert(
                tk.END,
                "STATUS: SATISFIED\n"
            )

            reason_text.insert(
                tk.END,
                "-" * 35 + "\n\n"
            )

    else:

        reason_text.insert(
            tk.END,
            "No predefined propositional rule "
            "was completely satisfied.\n\n"
        )

        reason_text.insert(
            tk.END,
            "The system checks each disease rule "
            "using AND / NOT conditions."
        )

    reason_text.config(
        state="disabled"
    )


# ============================================================
# RESET FUNCTION
# ============================================================

def reset_system():

    for var in symptom_vars.values():
        var.set(False)

    selected_label.config(
        text="None selected",
        fg="#7F8C8D"
    )

    disease_label.config(
        text="Waiting for input...",
        fg="#7F8C8D"
    )

    reason_text.config(
        state="normal"
    )

    reason_text.delete(
        "1.0",
        tk.END
    )

    reason_text.insert(
        "1.0",
        "No rules evaluated yet."
    )

    reason_text.config(
        state="disabled"
    )


# ============================================================
# BOTTOM BUTTONS
# ============================================================

button_frame = tk.Frame(
    root,
    bg="#EAF2F8"
)

button_frame.pack(
    pady=(0, 15)
)


detect_button = tk.Button(
    button_frame,
    text="DETECT DISEASE",
    command=check_disease,
    font=("Arial", 11, "bold"),
    bg="#2E86C1",
    fg="white",
    activebackground="#21618C",
    activeforeground="white",
    width=18,
    height=2,
    relief="flat",
    cursor="hand2"
)

detect_button.pack(
    side="left",
    padx=8
)


reset_button = tk.Button(
    button_frame,
    text="RESET",
    command=reset_system,
    font=("Arial", 11, "bold"),
    bg="#7F8C8D",
    fg="white",
    activebackground="#616A6B",
    activeforeground="white",
    width=12,
    height=2,
    relief="flat",
    cursor="hand2"
)

reset_button.pack(
    side="left",
    padx=8
)


# ============================================================
# DISCLAIMER
# ============================================================

disclaimer = tk.Label(
    root,
    text="Educational demonstration only — not a medical diagnostic system.",
    font=("Arial", 9, "italic"),
    bg="#EAF2F8",
    fg="#7B241C"
)

disclaimer.pack(
    pady=(0, 8)
)


# ============================================================
# START
# ============================================================

root.mainloop()