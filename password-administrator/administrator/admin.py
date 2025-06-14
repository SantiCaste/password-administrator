import random, string
from constants import RANDOM_PWD_LENGTH

registers: dict

def handle_registration():
    name = input("Insert the name: ")
    if name in registers:
        print("name already taken")
        return
    
    opt = input("do you wnat to generate a random password? (y/n): ")
    if opt.lower() == 'y':
        pwd = generate_random_pwd()
        print(f"Generated password: {pwd}")
        add_reg(name, pwd)
    else:
        pwd = input("Insert the password: ")
        add_reg(name, pwd)

def add_reg(name: str, pwd: str):
    if registers[name] != "":
        print("name already taken")
        return

    registers[name] = pwd

def change_pwd(name: str):
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
    print("Registered users:")
    for name, pwd in registers.items():
        if pwd != "":
            print(f"{name}: {pwd}")
        else:
            print(f"{name}: not registered")
    print()

def generate_random_pwd():
    return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=RANDOM_PWD_LENGTH))