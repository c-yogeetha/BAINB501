import tkinter as tk
from tkinter import ttk
from collections import deque


# ============================================================
# ELEVATOR / LIFT SIMULATOR
# ============================================================
# 3 Lifts
# 5 Floors
# One common call button on every floor
#
# Objective:
# Select the lift with the smallest predicted pickup time.
#
# Cost:
#     Idle lift:
#         |current_floor - request_floor|
#
#     Busy lift:
#         remaining distance for its current/queued requests
#         + distance from its last target to the new request
#
# Tie breaker:
#     1. Smaller ETA
#     2. Smaller number of queued requests
#     3. Lower lift ID
# ============================================================


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

NUM_FLOORS = 5
NUM_LIFTS = 3

FLOORS = list(range(1, NUM_FLOORS + 1))

LIFT_NAMES = ["Lift 1", "Lift 2", "Lift 3"]

# Initial lift positions
INITIAL_LIFT_POSITIONS = {
    "Lift 1": 1,
    "Lift 2": 3,
    "Lift 3": 5
}

# How long one floor movement takes
MOVE_TIME = 700


# ------------------------------------------------------------
# LIFT CLASS
# ------------------------------------------------------------

class Lift:

    def __init__(self, name, start_floor):
        self.name = name
        self.current_floor = start_floor

        # Floor the lift is currently moving toward
        self.target_floor = None

        # Pending requests assigned to this lift
        self.queue = deque()

        # Whether the lift is currently moving
        self.moving = False

        # Total requests served
        self.served = 0

        # Animation ID
        self.after_id = None

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    def is_idle(self):
        return not self.moving and len(self.queue) == 0

    # --------------------------------------------------------
    # CALCULATE ETA
    # --------------------------------------------------------

    def estimated_pickup_time(self, request_floor):

        # Completely idle lift
        if self.is_idle():
            return abs(self.current_floor - request_floor)

        # Start from current position
        position = self.current_floor

        total_distance = 0

        # Current target + existing queue
        targets = []

        if self.target_floor is not None:
            targets.append(self.target_floor)

        targets.extend(list(self.queue))

        # Travel through existing targets
        for target in targets:
            total_distance += abs(position - target)
            position = target

        # Finally travel to the new request
        total_distance += abs(position - request_floor)

        return total_distance

    # --------------------------------------------------------
    # NUMBER OF PENDING REQUESTS
    # --------------------------------------------------------

    def pending_requests(self):

        count = len(self.queue)

        if self.target_floor is not None:
            count += 1

        return count


# ------------------------------------------------------------
# MAIN SIMULATOR
# ------------------------------------------------------------

class LiftSimulator:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "3-Lift / 5-Floor Optimal Lift Simulator"
        )

        self.root.geometry("1100x750")

        # ----------------------------------------------------
        # DATA
        # ----------------------------------------------------

        self.lifts = {
            name: Lift(
                name,
                INITIAL_LIFT_POSITIONS[name]
            )
            for name in LIFT_NAMES
        }

        # People waiting at each floor
        self.waiting_people = {
            floor: []
            for floor in FLOORS
        }

        # Request counter
        self.person_counter = 0

        # ----------------------------------------------------
        # CANVAS
        # ----------------------------------------------------

        self.canvas = tk.Canvas(
            root,
            width=780,
            height=650,
            bg="white"
        )

        self.canvas.pack(
            side=tk.LEFT,
            padx=15,
            pady=15
        )

        # ----------------------------------------------------
        # RIGHT PANEL
        # ----------------------------------------------------

        self.panel = tk.Frame(root)

        self.panel.pack(
            side=tk.RIGHT,
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=15
        )

        title = tk.Label(
            self.panel,
            text="LIFT CONTROLLER",
            font=("Arial", 18, "bold")
        )

        title.pack(pady=10)

        # ----------------------------------------------------
        # CALL BUTTONS
        # ----------------------------------------------------

        button_title = tk.Label(
            self.panel,
            text="Call Lift from Floor",
            font=("Arial", 12, "bold")
        )

        button_title.pack(pady=5)

        self.call_buttons = {}

        for floor in reversed(FLOORS):

            button = tk.Button(
                self.panel,
                text=f"CALL LIFT  —  Floor {floor}",
                width=25,
                command=lambda f=floor: self.call_lift(f)
            )

            button.pack(pady=3)

            self.call_buttons[floor] = button

        # ----------------------------------------------------
        # RANDOM PERSON
        # ----------------------------------------------------

        random_button = tk.Button(
            self.panel,
            text="RANDOM PERSON",
            width=25,
            command=self.random_request
        )

        random_button.pack(pady=12)

        # ----------------------------------------------------
        # RESET
        # ----------------------------------------------------

        reset_button = tk.Button(
            self.panel,
            text="RESET SIMULATOR",
            width=25,
            command=self.reset
        )

        reset_button.pack(pady=5)

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        tk.Label(
            self.panel,
            text="Controller Status",
            font=("Arial", 12, "bold")
        ).pack(
            pady=(20, 5)
        )

        self.status = tk.Text(
            self.panel,
            width=40,
            height=18,
            font=("Courier New", 9)
        )

        self.status.pack()

        # ----------------------------------------------------
        # DRAW INITIAL SIMULATION
        # ----------------------------------------------------

        self.draw()

    # ========================================================
    # DRAW BUILDING
    # ========================================================

    def draw(self):

        self.canvas.delete("all")

        floor_height = 110
        building_left = 80
        building_right = 720
        top = 50

        lift_width = 100

        # ----------------------------------------------------
        # FLOOR LINES
        # ----------------------------------------------------

        for floor in reversed(FLOORS):

            y = top + (NUM_FLOORS - floor) * floor_height

            self.canvas.create_line(
                building_left,
                y,
                building_right,
                y,
                width=2
            )

            self.canvas.create_text(
                35,
                y + 45,
                text=f"Floor {floor}",
                font=("Arial", 12, "bold")
            )

        # ----------------------------------------------------
        # LIFT SHAFTS
        # ----------------------------------------------------

        shaft_x = [
            130,
            340,
            550
        ]

        for i, x in enumerate(shaft_x):

            self.canvas.create_rectangle(
                x,
                top,
                x + lift_width,
                top + floor_height * NUM_FLOORS,
                outline="black",
                width=2
            )

            self.canvas.create_text(
                x + lift_width / 2,
                25,
                text=LIFT_NAMES[i],
                font=("Arial", 12, "bold")
            )

        # ----------------------------------------------------
        # DRAW LIFTS
        # ----------------------------------------------------

        for i, name in enumerate(LIFT_NAMES):

            lift = self.lifts[name]

            x = shaft_x[i] + 10

            y = (
                top
                + (NUM_FLOORS - lift.current_floor)
                * floor_height
                + 10
            )

            self.canvas.create_rectangle(
                x,
                y,
                x + lift_width - 20,
                y + floor_height - 20,
                fill="lightblue",
                outline="black",
                width=2
            )

            self.canvas.create_text(
                x + (lift_width - 20) / 2,
                y + 35,
                text=name,
                font=("Arial", 11, "bold")
            )

            self.canvas.create_text(
                x + (lift_width - 20) / 2,
                y + 65,
                text=f"Floor {lift.current_floor}",
                font=("Arial", 10)
            )

        # ----------------------------------------------------
        # DRAW PEOPLE
        # ----------------------------------------------------

        for floor in FLOORS:

            y = (
                top
                + (NUM_FLOORS - floor)
                * floor_height
                + 80
            )

            people = self.waiting_people[floor]

            for index, person in enumerate(people):

                x = (
                    20
                    + index * 18
                )

                self.canvas.create_oval(
                    x,
                    y,
                    x + 12,
                    y + 12,
                    fill="black"
                )

        # ----------------------------------------------------
        # FLOOR BUTTON INDICATORS
        # ----------------------------------------------------

        for floor in FLOORS:

            waiting = len(
                self.waiting_people[floor]
            )

            if waiting > 0:

                y = (
                    top
                    + (NUM_FLOORS - floor)
                    * floor_height
                    + 35
                )

                self.canvas.create_text(
                    750,
                    y,
                    text=f"Waiting: {waiting}",
                    font=("Arial", 10, "bold")
                )

        self.update_status()

    # ========================================================
    # CALL LIFT
    # ========================================================

    def call_lift(self, floor):

        self.person_counter += 1

        person = f"P{self.person_counter}"

        self.waiting_people[floor].append(person)

        # Find optimal lift
        selected_lift, eta_table = self.find_best_lift(
            floor
        )

        # Add request to selected lift
        selected_lift.queue.append(floor)

        # Log decision
        self.log_decision(
            person,
            floor,
            selected_lift,
            eta_table
        )

        # Start lift if idle
        self.start_lift(selected_lift)

        self.draw()

    # ========================================================
    # FIND BEST LIFT
    # ========================================================

    def find_best_lift(self, request_floor):

        candidates = []

        for name in LIFT_NAMES:

            lift = self.lifts[name]

            eta = lift.estimated_pickup_time(
                request_floor
            )

            candidates.append(
                (
                    eta,
                    lift.pending_requests(),
                    name,
                    lift
                )
            )

        # ----------------------------------------------------
        # SORT BY:
        # 1. ETA
        # 2. Number of pending requests
        # 3. Lift name
        # ----------------------------------------------------

        candidates.sort(
            key=lambda item: (
                item[0],
                item[1],
                item[2]
            )
        )

        best = candidates[0][3]

        eta_table = [
            (item[2], item[0])
            for item in candidates
        ]

        return best, eta_table

    # ========================================================
    # START LIFT
    # ========================================================

    def start_lift(self, lift):

        # Already moving
        if lift.moving:
            return

        # No pending requests
        if len(lift.queue) == 0:
            return

        # Get next target
        lift.target_floor = lift.queue.popleft()

        lift.moving = True

        self.move_lift(lift)

    # ========================================================
    # MOVE LIFT
    # ========================================================

    def move_lift(self, lift):

        target = lift.target_floor

        # Already at destination
        if lift.current_floor == target:

            self.pickup_people(
                lift,
                target
            )

            return

        # Move one floor
        if target > lift.current_floor:

            lift.current_floor += 1

        else:

            lift.current_floor -= 1

        self.draw()

        # Continue animation
        lift.after_id = self.root.after(
            MOVE_TIME,
            lambda: self.move_lift(lift)
        )

    # ========================================================
    # PICK UP PEOPLE
    # ========================================================

    def pickup_people(self, lift, floor):

        people = self.waiting_people[floor]

        if people:

            count = len(people)

            self.waiting_people[floor] = []

            lift.served += count

            self.status.insert(
                "end",
                f"\n{lift.name} picked up "
                f"{count} person(s) at Floor {floor}."
            )

            self.status.see("end")

        # ----------------------------------------------------
        # Move to next request
        # ----------------------------------------------------

        if len(lift.queue) > 0:

            lift.target_floor = lift.queue.popleft()

            self.move_lift(lift)

        else:

            lift.target_floor = None
            lift.moving = False

            self.draw()

    # ========================================================
    # RANDOM REQUEST
    # ========================================================

    def random_request(self):

        import random

        floor = random.choice(FLOORS)

        self.call_lift(floor)

    # ========================================================
    # LOG DECISION
    # ========================================================

    def log_decision(
        self,
        person,
        floor,
        selected_lift,
        eta_table
    ):

        self.status.insert(
            "end",
            "\n"
            + "-" * 38
            + "\n"
        )

        self.status.insert(
            "end",
            f"{person} requested lift at Floor {floor}\n"
        )

        self.status.insert(
            "end",
            "Predicted pickup distances:\n"
        )

        for name, eta in eta_table:

            self.status.insert(
                "end",
                f"  {name}: {eta} floor(s)\n"
            )

        self.status.insert(
            "end",
            f"\nSELECTED -> {selected_lift.name}\n"
        )

        self.status.insert(
            "end",
            "Reason: minimum predicted pickup time\n"
        )

        self.status.see("end")

    # ========================================================
    # STATUS PANEL
    # ========================================================

    def update_status(self):

        # Preserve controller messages
        old_messages = self.status.get(
            "1.0",
            "end"
        )

        self.status.delete(
            "1.0",
            "end"
        )

        self.status.insert(
            "end",
            "CURRENT LIFT STATUS\n"
        )

        self.status.insert(
            "end",
            "=" * 38
            + "\n"
        )

        for name in LIFT_NAMES:

            lift = self.lifts[name]

            if lift.moving:
                state = (
                    f"Moving -> Floor {lift.target_floor}"
                )
            else:
                state = "IDLE"

            self.status.insert(
                "end",
                f"{name:<8} "
                f"Floor {lift.current_floor}  "
                f"{state}\n"
            )

            self.status.insert(
                "end",
                f"         Queue: "
                f"{list(lift.queue)}\n"
            )

            self.status.insert(
                "end",
                f"         Served: "
                f"{lift.served}\n"
            )

        self.status.insert(
            "end",
            "\n"
            + "=" * 38
            + "\n"
        )

        self.status.insert(
            "end",
            "WAITING PEOPLE\n"
        )

        for floor in FLOORS:

            count = len(
                self.waiting_people[floor]
            )

            if count > 0:

                self.status.insert(
                    "end",
                    f"Floor {floor}: "
                    f"{count} person(s)\n"
                )

        # Restore old controller messages
        self.status.insert(
            "end",
            "\n"
            + old_messages
        )

        self.status.see("end")

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        # Cancel animations
        for lift in self.lifts.values():

            if lift.after_id is not None:

                self.root.after_cancel(
                    lift.after_id
                )

            lift.current_floor = (
                INITIAL_LIFT_POSITIONS[
                    lift.name
                ]
            )

            lift.target_floor = None
            lift.queue.clear()
            lift.moving = False
            lift.served = 0
            lift.after_id = None

        # Remove waiting people
        self.waiting_people = {
            floor: []
            for floor in FLOORS
        }

        self.person_counter = 0

        self.status.delete(
            "1.0",
            "end"
        )

        self.draw()


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    simulator = LiftSimulator(root)

    root.mainloop()