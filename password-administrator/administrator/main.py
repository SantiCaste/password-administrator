from admin import change_password, show_registers, handle_registration


def print_banner():
    print("\n" + "="*35)
    print(" Password Administrator Menu")
    print("="*35)
    print("1. Add user")
    print("2. Change password")
    print("3. Show registered users")
    print("4. Exit")
    print("="*35)

if __name__ == "__main__":
    while True:
        print_banner()
        choice = input("Choose an option (1-4): ")
        print()
        if choice == "1":
            handle_registration()
        elif choice == "2":
            name = input("Insert the name: ")
            change_password(name)
        elif choice == "3":
            show_registers()
        elif choice == "4":
            print("Exiting Password Administrator. Goodbye!\n")
            break
        else:
            print("Invalid option, please choose a number between 1 and 4.")
