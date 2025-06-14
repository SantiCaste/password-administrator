import random, string
import constants

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
    pwd = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=constants.RANDOM_PWD_LENGTH))
    while measure_password_strength(pwd) != "Strong: Password meets all criteria.":
        pwd = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=constants.RANDOM_PWD_LENGTH))
    
    return pwd

# measure password strength considering length and complexity
def measure_password_strength(password: str) -> str:
    if len(password) < constants.MIN_LENGTH:
        return constants.PWD_MUST_MIN_LENGTH
    
    if sum(c.isdigit() for c in password) < constants.MIN_DIGITS:
        return constants.PWD_MUST_DIGITS

    if sum(c.isupper() for c in password) < constants.MIN_UPPERCASE:
        return constants.PWD_MUST_UPPERCASE

    if sum(c.islower() for c in password) < constants.MIN_LOWERCASE:
        return constants.PWD_MUST_LOWERCASE

    if sum(c in string.punctuation for c in password) < constants.MIN_SPECIAL:
        return constants.PWD_MUST_SPECIAL
    
    # If all criteria are met
    return constants.PWD_STRONG