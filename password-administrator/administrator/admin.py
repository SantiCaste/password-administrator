import password_handler as handler
import constants

registers = {}

def handle_registration():
    global registers
    print("\n=== User Registration ===")
    name = input("Insert the name: ")
    if name in registers:
        print("Name already taken.\n")
        return
    
    opt = input("Do you want to generate a random password? (y/N): ")
    if opt.lower() == 'y':
        pwd = handler.generate_random_password()
        print(f"Generated password: {pwd}")
    else:
        pwd = request_password()

    registers[name] = pwd
    print("User registered successfully.\n")

def change_password(name: str):
    global registers
    print(f"\n=== Change Password for '{name}' ===")
    if name not in registers:
        print("User not found.\n")
        return
    
    old_pwd = input("Insert the previous password: ")

    if registers[name] != old_pwd:
        print(f"Incorrect password for user {name}.\n")
        return

    print("Please insert the new password below.")
    new_pwd = request_password()
    registers[name] = new_pwd

    print("Password changed successfully.\n")

def change_user_name(cur_name: str):
    global registers
    print(f"\n=== Change User Name from '{cur_name}' ===")
    if cur_name not in registers:
        print("User not found.\n")
        return
    
    # request the old password to confirm identity
    pwd = input("Insert the password: ")
    if registers[cur_name] != pwd:
        print(f"Incorrect password for user {cur_name}.\n")
        return
    
    new_name = input("Insert the new name: ")
    if new_name in registers:
        print("New name already taken.\n")
        return
    
    registers[new_name] = registers.pop(cur_name)
    print(f"User name changed successfully from '{cur_name}' to '{new_name}'.\n")

def delete_user(name: str):
    global registers
    print(f"\n=== Delete User '{name}' ===")
    if name not in registers:
        print("User not found.\n")
        return
    
    # request the password to confirm identity
    pwd = input("Insert the password: ")
    if registers[name] != pwd:
        print(f"Incorrect password for user {name}.\n")
        return
    
    del registers[name]
    print(f"User '{name}' deleted successfully.\n")

def request_password() -> str:
    handler.print_password_criteria()
    while True:
        # ask for the password and check its strength
        pwd = input("Insert the password: ")
        result = handler.measure_strength(pwd)
        if result == constants.PWD_STRONG:
            break
        print(f"\n{constants.PWD_VALIDATION_MESSAGES[result]}")
        print("Please try again.\n")

    return pwd

def show_registers():
    global registers
    print("\n=== Registered Users ===")
    if not registers:
        print("No users registered.\n")
        return
    for name, pwd in registers.items():
        if pwd != "":
            print(f"  - {name}: {pwd}")
        else:
            print(f"  - {name}: not registered")
    print()
