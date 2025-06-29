from admin import initialize_registers, handle_registration, change_password, change_user_name, delete_user, show_registers, check_strength

def print_banner():
    print("\n" + "="*35)
    print(" Password Administrator Menu")
    print("="*35)
    print("1. Add user")
    print("2. Change password")
    print("3. Change user name")
    print("4. Delete user")
    print("5. Show registered users")
    print("6. Messure stregth")
    print("7. Exit")
    print("="*35)

def main():
    print("Welcome to the Password Administrator!\n")
    print("Please enter your master password to access the registers.\n")
    print("Initializing registers...\n")
    initialize_registers()

    while True:
        print_banner()
        try:
            choice = int(input("Choose an option (1-7): "))
        except ValueError:
            print("\nInvalid input. Please enter a number between 1 and 6.")
            continue
        print()
        if choice == 1:
            handle_registration()
        elif choice == 2:
            name = input("Insert the name: ")
            change_password(name)
        elif choice == 3:
            cur_name = input("Insert the current name: ")
            change_user_name(cur_name)
        elif choice == 4:
            name = input("Insert the name to delete: ")
            delete_user(name)
        elif choice == 5:
            show_registers()
        elif choice == 6:
            name = input("Insert name: ")
            check_strength(name)
        elif choice == 7:
            print("Exiting Password Administrator. Goodbye!\n")
            break
        else:
            print("Invalid option, please choose a number between 1 and 6.")

if __name__ == "__main__":
    main()