import password_handler as handler
import constants
from crypto_handler import load_registers, save_registers, get_master_password # Ensure these are imported

registers = {}

def initialize_registers():
    global registers
    # This function is now called by gui_app.py after a master password is established
    # and load_registers is successful.
    # The actual loading logic with error handling is now in gui_app.py
    pass # No direct action here, as gui_app handles the loading result

# The rest of admin.py remains unchanged as its core logic is sound for managing 'registers'.
# The GUI handles all input/output for these functions.

def handle_registration():
    global registers
    # The GUI calls this logic internally after getting inputs
    # Not directly called from the main loop anymore.
    pass # Replaced by gui_app methods


def change_password(name: str):
    global registers
    # The GUI calls this logic internally after getting inputs
    pass # Replaced by gui_app methods

def change_user_name(cur_name: str):
    global registers
    # The GUI calls this logic internally after getting inputs
    pass # Replaced by gui_app methods

def delete_user(name: str):
    global registers
    # The GUI calls this logic internally after getting inputs
    pass # Replaced by gui_app methods

# The request_password function in admin.py is effectively replaced
# by request_password_gui in gui_app.py for GUI interactions.
# If admin.py is only used as a backend for gui_app, this function can be removed from admin.py
# to avoid confusion, or kept if there's a console-only fallback.
# For this integrated GUI solution, it's safer to rely on gui_app's version.
def request_password() -> str:
    handler.print_password_criteria() # This would still print to console
    while True:
        pwd = input("Insert the password: ")
        result = handler.measure_strength(pwd)
        if result == constants.PWD_STRONG:
            break
        print(f"\n{constants.PWD_VALIDATION_MESSAGES[result]}")
        print("Please try again.\n")
    return pwd

def show_registers():
    global registers
    # This logic is now handled by gui_app.update_register_display
    # to update the Tkinter Text widget, not print to console.
    pass # Replaced by gui_app methods