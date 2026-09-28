# ============================================================
# CSP-BASED ENGINEERING CLASS TIMETABLE
# Backtracking + MRV
# ============================================================

# ------------------------------------------------------------
# 1. SUBJECTS
# ------------------------------------------------------------

subjects = ["AI", "DBMS", "CN", "OS", "SE"]

# ------------------------------------------------------------
# 2. DAYS AND PERIODS
# ------------------------------------------------------------

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
periods = [1, 2, 3, 4]

# ------------------------------------------------------------
# 3. VARIABLES
# ------------------------------------------------------------
# X1  = Monday_P1
# X2  = Monday_P2
# ...
# X20 = Friday_P4
# ------------------------------------------------------------

variables = []

for day in days:
    for period in periods:
        variables.append(f"{day}_P{period}")

print("CSP VARIABLES")
print("=" * 40)

for i, variable in enumerate(variables, start=1):
    print(f"X{i} = {variable}")

# ------------------------------------------------------------
# 4. DOMAIN
# ------------------------------------------------------------
# Every slot initially has all 5 subjects as possible values.
# D = {AI, DBMS, CN, OS, SE}
# ------------------------------------------------------------

domains = {
    variable: subjects.copy()
    for variable in variables
}

# ------------------------------------------------------------
# 5. CONSTRAINTS
# ------------------------------------------------------------

# Each subject must occur exactly 4 times in the week.
REQUIRED_COUNT = 4

# A subject cannot be scheduled more than once on the same day.
# This prevents outputs such as:
# Monday -> AI, AI, AI, AI
# ------------------------------------------------------------

assignment = {}

# Number of times each subject has been used during the week
subject_count = {
    subject: 0
    for subject in subjects
}

# Number of times each subject has been used on each day
day_subject_count = {
    day: {
        subject: 0
        for subject in subjects
    }
    for day in days
}

# Search statistics
nodes_visited = 0
backtracks = 0


# ------------------------------------------------------------
# HELPER FUNCTION
# ------------------------------------------------------------

def get_day(variable):
    """
    Extract the day from a variable.

    Example:
        Monday_P1 -> Monday
    """
    return variable.split("_")[0]


# ------------------------------------------------------------
# 6. GET LEGAL VALUES
# ------------------------------------------------------------

def get_legal_values(variable):
    """
    Return all subjects that can legally be assigned
    to the given variable.
    """

    day = get_day(variable)

    legal_values = []

    for subject in domains[variable]:

        # Constraint 1:
        # Subject must not exceed 4 occurrences per week
        if subject_count[subject] >= REQUIRED_COUNT:
            continue

        # Constraint 2:
        # Subject can occur at most once on a particular day
        if day_subject_count[day][subject] >= 1:
            continue

        legal_values.append(subject)

    return legal_values


# ------------------------------------------------------------
# 7. MRV
# ------------------------------------------------------------

def select_unassigned_variable():
    """
    MRV = Minimum Remaining Values

    Select the unassigned variable having the smallest
    number of legal values.
    """

    unassigned = [
        variable
        for variable in variables
        if variable not in assignment
    ]

    # Calculate current domain size for every unassigned variable
    selected = min(
        unassigned,
        key=lambda variable: len(get_legal_values(variable))
    )

    return selected


# ------------------------------------------------------------
# 8. BACKTRACKING SEARCH
# ------------------------------------------------------------

def backtracking_search():

    global nodes_visited
    global backtracks

    # --------------------------------------------------------
    # BASE CASE
    # --------------------------------------------------------

    if len(assignment) == len(variables):

        # Verify exact weekly frequency
        for subject in subjects:
            if subject_count[subject] != REQUIRED_COUNT:
                return False

        return True

    # --------------------------------------------------------
    # MRV: choose next variable
    # --------------------------------------------------------

    variable = select_unassigned_variable()

    # Get current legal domain
    legal_values = get_legal_values(variable)

    # If no value is available, this branch fails
    if not legal_values:
        backtracks += 1
        return False

    # --------------------------------------------------------
    # TRY EACH VALUE
    # --------------------------------------------------------

    for subject in legal_values:

        nodes_visited += 1

        day = get_day(variable)

        # Assign
        assignment[variable] = subject

        subject_count[subject] += 1
        day_subject_count[day][subject] += 1

        # ----------------------------------------------------
        # RECURSIVE SEARCH
        # ----------------------------------------------------

        if backtracking_search():
            return True

        # ----------------------------------------------------
        # BACKTRACK
        # ----------------------------------------------------

        del assignment[variable]

        subject_count[subject] -= 1
        day_subject_count[day][subject] -= 1

        backtracks += 1

    return False


# ------------------------------------------------------------
# 9. DISPLAY TIMETABLE
# ------------------------------------------------------------

def display_timetable():

    print("\n")
    print("=" * 75)
    print("ENGINEERING CLASS TIMETABLE")
    print("=" * 75)

    print(
        f"{'Day':<12}"
        f"{'Period 1':<14}"
        f"{'Period 2':<14}"
        f"{'Period 3':<14}"
        f"{'Period 4':<14}"
    )

    print("-" * 75)

    for day in days:

        row = []

        for period in periods:

            variable = f"{day}_P{period}"
            row.append(assignment[variable])

        print(
            f"{day:<12}"
            f"{row[0]:<14}"
            f"{row[1]:<14}"
            f"{row[2]:<14}"
            f"{row[3]:<14}"
        )

    print("=" * 75)


# ------------------------------------------------------------
# 10. VERIFY CONSTRAINTS
# ------------------------------------------------------------

def verify_solution():

    print("\nCONSTRAINT VERIFICATION")
    print("=" * 55)

    valid = True

    # ----------------------------------------
    # Weekly frequency constraint
    # ----------------------------------------

    print("\nWeekly Subject Frequency:")

    for subject in subjects:

        count = subject_count[subject]

        print(
            f"{subject:<8} -> "
            f"{count} times "
            f"(required = {REQUIRED_COUNT})"
        )

        if count != REQUIRED_COUNT:
            valid = False

    # ----------------------------------------
    # Daily repetition constraint
    # ----------------------------------------

    print("\nDaily Repetition Check:")

    for day in days:

        for subject in subjects:

            count = day_subject_count[day][subject]

            if count > 1:
                print(
                    f"Violation: {subject} occurs "
                    f"{count} times on {day}"
                )
                valid = False

    if valid:
        print("\nAll constraints satisfied.")

    else:
        print("\nSome constraints are violated.")

    return valid


# ------------------------------------------------------------
# 11. MAIN
# ------------------------------------------------------------

print("\n")
print("Starting CSP timetable generation...")
print("Using Backtracking with MRV...")
print()

solution_found = backtracking_search()

if solution_found:

    display_timetable()

    verify_solution()

    print("\nSEARCH STATISTICS")
    print("=" * 40)
    print(f"Nodes visited : {nodes_visited}")
    print(f"Backtracks    : {backtracks}")

else:

    print("No valid timetable could be generated.")