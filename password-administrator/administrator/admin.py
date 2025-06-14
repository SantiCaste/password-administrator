import random, string
from constants import RANDOM_PWD_LENGTH

registers = {}

def handle_registration():
    global registers
    name = input("Insert the name: ")
    if name in registers:
        print("name already taken")
        return
    
    opt = input("do you want to generate a random password? (y/n): ")
    if opt.lower() == 'y':
        pwd = generate_random_pwd()
        print(f"Generated password: {pwd}")
        registers[name] = pwd
    else:
        pwd = input("Insert the password: ")
        registers[name] = pwd

    print("User registered successfully")

def change_pwd(name: str):
    global registers
    if name not in registers:
        print("User not found")
        return
    
    # TODO: validar input (vacío por ej)
    old_pwd = input("insert the previous password: ")

    if registers[name] != old_pwd:
        print("incorrect password")
        return

    # TODO: validar input (vacío por ej)
    new_pwd = input("insert the new password: ")
    registers[name] = new_pwd

    print("password changed successfully")

def show_reg():
    global registers
    print("Registered users:")
    for name, pwd in registers.items():
        if pwd != "":
            print(f"{name}: {pwd}")
        else:
            print(f"{name}: not registered")
    print()

def generate_random_pwd():
    return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=RANDOM_PWD_LENGTH))