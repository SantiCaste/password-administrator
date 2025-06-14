from admin import change_pwd, show_reg, handle_registration


if __name__ == "__main__":
    while True:
        choice = input("1. Add user\n2. Change password\n3. Show registered users\n4. Exit\nChoose an option: ")
        if choice == "1":
            handle_registration()
        elif choice == "2":
            name = input("Insert the name: ")
            change_pwd(name)
        elif choice == "3":
            show_reg()
        elif choice == "4":
            break
        else:
            print("Invalid option, please try again.")