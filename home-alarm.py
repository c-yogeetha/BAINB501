import tkinter as tk
from tkinter import ttk


# ============================================================
# HOME ALARM DETECTION SYSTEM
# USING PROPOSITIONAL LOGIC
# ============================================================

CONDITIONS = [
    "Alarm Armed",
    "Door Opened",
    "Window Opened",
    "Motion Detected",
    "Glass Break Detected",
    "Night Time",
    "Smoke Detected"
]


# ============================================================
# PROPOSITIONAL LOGIC RULES
# ============================================================

ALARM_RULES = {

    "INTRUSION ALARM": {
        "conditions": [
            ("Alarm Armed", True),
            ("Door Opened", True),
            ("Night Time", True)
        ],
        "display_rule":
            "Alarm Armed AND Door Opened AND Night Time"
    },

    "WINDOW INTRUSION": {
        "conditions": [
            ("Alarm Armed", True),
            ("Window Opened", True),
            ("Night Time", True)
        ],
        "display_rule":
            "Alarm Armed AND Window Opened AND Night Time"
    },

    "MOTION ALARM": {
        "conditions": [
            ("Alarm Armed", True),
            ("Motion Detected", True),
            ("Night Time", True)
        ],
        "display_rule":
            "Alarm Armed AND Motion Detected AND Night Time"
    },

    "BURGLARY ALERT": {
        "conditions": [
            ("Alarm Armed", True),
            ("Glass Break Detected", True)
        ],
        "display_rule":
            "Alarm Armed AND Glass Break Detected"
    },

    "FIRE ALARM": {
        "conditions": [
            ("Smoke Detected", True)
        ],
        "display_rule":
            "Smoke Detected"
    }
}


# ============================================================
# LOGIC ENGINE
# ============================================================

def detect_alarm(selected_conditions):

    detected = []

    for alarm, rule in ALARM_RULES.items():

        satisfied = True

        for condition, required_value in rule["conditions"]:

            actual_value = condition in selected_conditions

            if actual_value != required_value:
                satisfied = False
                break

        if satisfied:
            detected.append(
                (alarm, rule["display_rule"])
            )

    return detected


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title("Home Alarm Detection System")
root.geometry("1250x720")

# Important:
# Reserve enough space so the bottom controls are always visible.
root.minsize(1100, 680)

root.configure(bg="#EAF2F8")


# ============================================================
# ROOT GRID
# ============================================================
#
# Row 0 = Header
# Row 1 = Main content (expands)
# Row 2 = Buttons (FIXED)
# Row 3 = Disclaimer (FIXED)
#

root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=0)
root.grid_rowconfigure(3, weight=0)

root.grid_columnconfigure(0, weight=1)


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
    "Condition.TCheckbutton",
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

header.grid(
    row=0,
    column=0,
    sticky="ew",
    padx=20,
    pady=(12, 5)
)


ttk.Label(
    header,
    text="HOME ALARM DETECTION SYSTEM",
    style="Title.TLabel"
).pack()


ttk.Label(
    header,
    text="Rule-Based Security System using Propositional Logic",
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

main.grid(
    row=1,
    column=0,
    sticky="nsew",
    padx=20,
    pady=10
)


# 3 columns:
# Left   = conditions
# Center = logic diagram
# Right  = result

main.grid_columnconfigure(0, weight=0)
main.grid_columnconfigure(1, weight=1)
main.grid_columnconfigure(2, weight=1)

main.grid_rowconfigure(0, weight=1)


# ============================================================
# LEFT PANEL
# ============================================================

condition_panel = tk.Frame(
    main,
    bg="white",
    bd=2,
    relief="ridge",
    width=270
)

condition_panel.grid(
    row=0,
    column=0,
    sticky="nsew",
    padx=(0, 8)
)

# Prevent the panel from changing width
condition_panel.grid_propagate(False)

condition_title = ttk.Label(
    condition_panel,
    text="House Conditions",
    style="PanelTitle.TLabel"
)

condition_title.pack(
    pady=(15, 10)
)


info_label = tk.Label(
    condition_panel,
    text="Select the conditions detected\n"
         "by the house sensors.",
    font=("Arial", 10),
    bg="white",
    fg="#7F8C8D",
    justify="center"
)

info_label.pack(
    pady=(0, 15)
)


# ============================================================
# CONDITION CHECKBOXES
# ============================================================

condition_vars = {}

checkbox_container = tk.Frame(
    condition_panel,
    bg="white"
)

checkbox_container.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=(0, 10)
)


for condition in CONDITIONS:

    var = tk.BooleanVar(value=False)

    condition_vars[condition] = var

    checkbox = ttk.Checkbutton(
        checkbox_container,
        text=condition,
        variable=var,
        style="Condition.TCheckbutton"
    )

    checkbox.pack(
        anchor="w",
        pady=6
    )


# ============================================================
# CENTER PANEL
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

logic_panel.grid_rowconfigure(1, weight=1)
logic_panel.grid_columnconfigure(0, weight=1)


logic_title = ttk.Label(
    logic_panel,
    text="Propositional Logic Flow",
    style="PanelTitle.TLabel"
)

logic_title.grid(
    row=0,
    column=0,
    pady=(12, 5)
)


logic_canvas = tk.Canvas(
    logic_panel,
    bg="#FBFCFC",
    highlightthickness=0
)

logic_canvas.grid(
    row=1,
    column=0,
    sticky="nsew",
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

    width = max(logic_canvas.winfo_width(), 400)
    height = max(logic_canvas.winfo_height(), 450)

    center_x = width / 2

    box_width = min(310, width - 40)

    x1 = center_x - box_width / 2
    x2 = center_x + box_width / 2


    # --------------------------------------------------------
    # Calculate vertical positions based on current canvas
    # --------------------------------------------------------

    box_height = 58
    arrow_gap = 25

    total_height = (
        box_height * 4
        + arrow_gap * 4
        + 70
    )

    start_y = max(
        20,
        (height - total_height) / 2
    )


    # --------------------------------------------------------
    # BOX 1
    # --------------------------------------------------------

    y1 = start_y
    y2 = y1 + box_height

    draw_box(
        x1, y1, x2, y2,
        "HOUSE SENSOR\nINPUT",
        "#D6EAF8"
    )


    # --------------------------------------------------------
    # BOX 2
    # --------------------------------------------------------

    arrow_start = y2
    arrow_end = arrow_start + arrow_gap

    draw_arrow(
        center_x,
        arrow_start,
        center_x,
        arrow_end
    )

    y1 = arrow_end
    y2 = y1 + box_height

    draw_box(
        x1, y1, x2, y2,
        "PROPOSITIONAL\nLOGIC",
        "#D5F5E3"
    )


    # --------------------------------------------------------
    # BOX 3
    # --------------------------------------------------------

    arrow_start = y2
    arrow_end = arrow_start + arrow_gap

    draw_arrow(
        center_x,
        arrow_start,
        center_x,
        arrow_end
    )

    y1 = arrow_end
    y2 = y1 + box_height

    draw_box(
        x1, y1, x2, y2,
        "CHECK SECURITY\nRULES",
        "#FCF3CF"
    )


    # --------------------------------------------------------
    # BOX 4
    # --------------------------------------------------------

    arrow_start = y2
    arrow_end = arrow_start + arrow_gap

    draw_arrow(
        center_x,
        arrow_start,
        center_x,
        arrow_end
    )

    y1 = arrow_end
    y2 = y1 + box_height

    draw_box(
        x1, y1, x2, y2,
        "ALARM\nDECISION",
        "#FADBD8"
    )


    # --------------------------------------------------------
    # LOGIC LEGEND
    # --------------------------------------------------------

    legend_y = min(
        y2 + 45,
        height - 45
    )

    logic_canvas.create_text(
        center_x,
        legend_y,
        text="AND = ∧     OR = ∨     NOT = ¬\n"
             "CONDITIONS → ALARM",
        font=("Arial", 10),
        fill="#566573",
        justify="center"
    )


logic_canvas.bind(
    "<Configure>",
    lambda event: draw_logic_flow()
)


# ============================================================
# RIGHT PANEL
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

result_panel.grid_rowconfigure(3, weight=1)
result_panel.grid_columnconfigure(0, weight=1)


result_title = ttk.Label(
    result_panel,
    text="Alarm Result",
    style="PanelTitle.TLabel"
)

result_title.grid(
    row=0,
    column=0,
    pady=(12, 8)
)


# ============================================================
# SELECTED CONDITIONS
# ============================================================

selected_frame = tk.LabelFrame(
    result_panel,
    text="Detected Conditions",
    font=("Arial", 11, "bold"),
    bg="white",
    fg="#34495E"
)

selected_frame.grid(
    row=1,
    column=0,
    sticky="ew",
    padx=15,
    pady=7
)


selected_label = tk.Label(
    selected_frame,
    text="No conditions selected",
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


# ============================================================
# ALARM STATUS
# ============================================================

alarm_frame = tk.LabelFrame(
    result_panel,
    text="System Status",
    font=("Arial", 11, "bold"),
    bg="white",
    fg="#34495E"
)

alarm_frame.grid(
    row=2,
    column=0,
    sticky="ew",
    padx=15,
    pady=7
)


alarm_label = tk.Label(
    alarm_frame,
    text="SYSTEM READY",
    font=("Arial", 15, "bold"),
    bg="white",
    fg="#229954",
    wraplength=330,
    justify="center"
)

alarm_label.pack(
    padx=10,
    pady=15
)


# ============================================================
# RULE REASONING
# ============================================================

reason_frame = tk.LabelFrame(
    result_panel,
    text="Satisfied Security Rules",
    font=("Arial", 11, "bold"),
    bg="white",
    fg="#34495E"
)

reason_frame.grid(
    row=3,
    column=0,
    sticky="nsew",
    padx=15,
    pady=7
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
    "No security rules evaluated yet."
)

reason_text.config(
    state="disabled"
)


# ============================================================
# CHECK ALARM
# ============================================================

def check_alarm():

    selected_conditions = {
        condition
        for condition, var in condition_vars.items()
        if var.get()
    }


    # --------------------------------------------------------
    # Display selected conditions
    # --------------------------------------------------------

    if selected_conditions:

        selected_text = "\n".join(
            "✓ " + condition
            for condition in sorted(selected_conditions)
        )

        selected_label.config(
            text=selected_text,
            fg="#1B4F72"
        )

    else:

        selected_label.config(
            text="No conditions selected",
            fg="#7F8C8D"
        )


    # --------------------------------------------------------
    # Evaluate propositional rules
    # --------------------------------------------------------

    detected = detect_alarm(
        selected_conditions
    )


    # --------------------------------------------------------
    # Display alarm status
    # --------------------------------------------------------

    if detected:

        alarm_names = [
            alarm
            for alarm, rule in detected
        ]

        alarm_label.config(
            text="ALARM TRIGGERED\n\n"
                 + "\n".join(alarm_names),
            fg="#C0392B"
        )

    else:

        alarm_label.config(
            text="SYSTEM SECURE",
            fg="#229954"
        )


    # --------------------------------------------------------
    # Display reasoning
    # --------------------------------------------------------

    reason_text.config(
        state="normal"
    )

    reason_text.delete(
        "1.0",
        tk.END
    )


    if detected:

        for alarm, rule in detected:

            reason_text.insert(
                tk.END,
                f"ALARM: {alarm}\n"
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
            "No predefined alarm rule was satisfied.\n\n"
        )

        reason_text.insert(
            tk.END,
            "The system evaluates the selected "
            "sensor conditions using propositional logic."
        )


    reason_text.config(
        state="disabled"
    )


# ============================================================
# RESET
# ============================================================

def reset_system():

    for var in condition_vars.values():
        var.set(False)


    selected_label.config(
        text="No conditions selected",
        fg="#7F8C8D"
    )


    alarm_label.config(
        text="SYSTEM READY",
        fg="#229954"
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
        "No security rules evaluated yet."
    )

    reason_text.config(
        state="disabled"
    )


# ============================================================
# BOTTOM BUTTON BAR
# ============================================================
#
# IMPORTANT:
# This row has weight=0, so the expanding main area
# can NEVER push these buttons out of the window.
#

button_frame = tk.Frame(
    root,
    bg="#EAF2F8",
    height=65
)

button_frame.grid(
    row=2,
    column=0,
    sticky="ew",
    padx=20,
    pady=(0, 5)
)

button_frame.grid_propagate(False)


# Make the buttons centered
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)
button_frame.grid_columnconfigure(2, weight=1)


# Internal button holder

button_holder = tk.Frame(
    button_frame,
    bg="#EAF2F8"
)

button_holder.grid(
    row=0,
    column=1,
    sticky="nsew"
)


detect_button = tk.Button(
    button_holder,
    text="CHECK ALARM",
    command=check_alarm,
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
    button_holder,
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
    text="Educational propositional-logic demonstration only.",
    font=("Arial", 9, "italic"),
    bg="#EAF2F8",
    fg="#7B241C"
)

disclaimer.grid(
    row=3,
    column=0,
    sticky="ew",
    pady=(0, 7)
)


# ============================================================
# INITIAL DRAW
# ============================================================

root.after(
    100,
    draw_logic_flow
)


# ============================================================
# START
# ============================================================

root.mainloop()