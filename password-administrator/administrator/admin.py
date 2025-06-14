import random, string
from constants import RANDOM_PWD_LENGTH

registers = {}

def handle_registration():
    global registers
    print("\n=== User Registration ===")
    name = input("Insert the name: ")
    if name in registers:
        print("Name already taken.\n")
        return
    
    opt = input("Do you want to generate a random password? (y/n): ")
    if opt.lower() == 'y':
        pwd = generate_random_pwd()
        print(f"Generated password: {pwd}")
        registers[name] = pwd
    else:
        pwd = input("Insert the password: ")
        registers[name] = pwd

    print("User registered successfully.\n")

def change_pwd(name: str):
    global registers
    print(f"\n=== Change Password for '{name}' ===")
    if name not in registers:
        print("User not found.\n")
        return
    
    old_pwd = input("Insert the previous password: ")

    if registers[name] != old_pwd:
        print("Incorrect password.\n")
        return

    new_pwd = input("Insert the new password: ")
    registers[name] = new_pwd

    print("Password changed successfully.\n")

def show_reg():
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

def generate_random_pwd():
    return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=RANDOM_PWD_LENGTH))

# measure password strength considering length and complexity
def measure_password_strength(password: str) -> str:
    if len(password) < 8:
        return "Weak: Password must be at least 8 characters long.", 
    if not any(c.isdigit() for c in password):
        return "Weak: Password must contain at least one digit.", 
    if not any(c.isupper() for c in password):
        return "Weak: Password must contain at least one uppercase letter.", 
    if not any(c.islower() for c in password):
        return "Weak: Password must contain at least one lowercase letter.", 
    if not any(c in string.punctuation for c in password):
        return "Weak: Password must contain at least one special character."

    return "Strong: Password meets all criteria."