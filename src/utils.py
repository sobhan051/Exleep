# src/utils.py

def ask_scale_1_5(question, label_low="Never / Not at all", label_high="Always / Very Much"):
    print(f"\n[?] {question}")
    print(f"    1: {label_low}")
    print("    2: Rarely / A little / Poor")
    print("    3: Sometimes / Somewhat / Average")
    print("    4: Often / Much / Good")
    print(f"    5: {label_high}")
    while True:
        try:
            val = int(input("    Enter 1-5: "))
            if 1 <= val <= 5: return val
        except ValueError: pass
        print("    Please enter a number between 1 and 5.")

def ask_choice(question, choices):
    print(f"\n[?] {question}")
    for i, c in enumerate(choices, 1):
        print(f"    {i}. {c}")
    while True:
        try:
            val = int(input("    Select option number: "))
            if 1 <= val <= len(choices):
                return choices[val-1]
        except ValueError: pass
        print("    Invalid selection.")

def ask_yes_no(question):
    print(f"\n[?] {question} (yes/no)")
    while True:
        val = input("    > ").lower().strip()
        if val in ['yes', 'y']: return True
        if val in ['no', 'n']: return False
        print("    Please type 'yes' or 'no'.")