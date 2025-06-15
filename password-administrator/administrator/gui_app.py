import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, filedialog
import admin
import password_handler as handler
import constants
import crypto_handler
import os

class PasswordAdminApp:
    def __init__(self, root):
        print("PasswordAdminApp: __init__ started") # Debug print
        self.root = root
        self.root.title("Password Administrator")
        self.root.geometry("600x450")
        self.password_visibility = {}  # Track which users passwords are visible
        self.current_file = crypto_handler.DATA_FILE
        # self.root.withdraw() # Hide the main window initially (REMOVE THIS LINE)
        print("PasswordAdminApp: Calling master_password_setup()") # Debug print
        self.master_password_setup()
        print("PasswordAdminApp: __init__ finished") # Debug print

    def master_password_setup(self):
        print("master_password_setup: started") # Debug print
        self.setup_window = Toplevel(self.root)
        self.setup_window.title("Setup Password File")
        self.setup_window.geometry("350x180")
        self.setup_window.transient(self.root)
        self.setup_window.grab_set()

        tk.Label(self.setup_window, text="Welcome!").pack(pady=10)
        tk.Button(self.setup_window, text="Open Existing File", command=self.open_existing_file).pack(pady=5)
        tk.Button(self.setup_window, text="Create New File", command=self.create_new_file).pack(pady=5)
        tk.Button(self.setup_window, text="Select File...", command=self.select_file_dialog).pack(pady=5)

        self.setup_window.protocol("WM_DELETE_WINDOW", self.on_setup_window_close)
        print("master_password_setup: finished, setup_window should be visible") # Debug print

    def on_setup_window_close(self):
        print("on_setup_window_close: called") # Debug print
        if crypto_handler.master_pwd_session is None:
            messagebox.showinfo("Exit", "No file selected or created. Exiting application.")
            self.root.destroy()
        else:
            self.setup_window.destroy()

    def select_file_dialog(self):
        file_path = filedialog.askopenfilename(
            title="Select Encrypted Data File",
            filetypes=[("Encrypted JSON", "*.enc"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            crypto_handler.DATA_FILE = file_path
            messagebox.showinfo("File Selected", f"Selected file:\n{file_path}")

    def open_existing_file(self):
        print("open_existing_file: called") # Debug print
        # --- Add file dialog here ---
        file_path = filedialog.askopenfilename(
            title="Select Encrypted Data File",
            filetypes=[("Encrypted JSON", "*.enc"), ("All Files", "*.*")]
        )
        if not file_path:
            print("open_existing_file: No file selected, returning to setup.") # Debug print
            return  # User cancelled

        self.current_file = file_path
        crypto_handler.DATA_FILE = file_path
        self.setup_window.destroy()
        # --- rest of your code unchanged ---
        max_attempts = 3
        attempts = 0
        while attempts < max_attempts:
            master_pwd = simpledialog.askstring("Master Password", "Enter your master password for the existing file:", show='*')
            if master_pwd is None:
                print("open_existing_file: User cancelled master password entry, destroying root.") # Debug print
                self.root.destroy()
                return

            crypto_handler.master_pwd_session = master_pwd
            registers, status = crypto_handler.load_registers(master_pwd)

            if status == "SUCCESS":
                admin.registers = registers
                self.initialize_main_app()
                print("open_existing_file: Successfully opened, main app initialized.") # Debug print
                return
            elif status == "FILE_NOT_FOUND":
                messagebox.showerror("Error", f"Encrypted data file '{crypto_handler.DATA_FILE}' not found. Please create a new one.")
                self.master_password_setup() # Go back to setup options
                print("open_existing_file: File not found, returning to setup.") # Debug print
                return
            elif status == "INVALID_PASSWORD":
                attempts += 1
                messagebox.showerror("Decryption Failed", f"Incorrect master password. {max_attempts - attempts} attempt(s) remaining.")
                print(f"open_existing_file: Invalid password, attempt {attempts}.") # Debug print
            else:
                messagebox.showerror("Decryption Failed", f"An error occurred during decryption: {status}. Please check the file or try again.")
                self.master_password_setup()
                print(f"open_existing_file: Decryption error: {status}, returning to setup.") # Debug print
                return

        messagebox.showerror("Attempts Exceeded", "Too many incorrect master password attempts. Exiting.")
        print("open_existing_file: Attempts exceeded, destroying root.") # Debug print
        self.root.destroy()

    def create_new_file(self):
        print("create_new_file: called") # Debug print
        self.setup_window.destroy()

        while True:
            new_master_pwd = self.request_password_gui("Define your new master password:")
            if new_master_pwd is None:
                print("create_new_file: User cancelled new master password entry, destroying root.") # Debug print
                self.root.destroy()
                return

            confirm_pwd = simpledialog.askstring("Confirm Master Password", "Confirm your new master password:", show='*')
            if confirm_pwd is None:
                print("create_new_file: User cancelled confirm password entry, destroying root.") # Debug print
                self.root.destroy()
                return

            if new_master_pwd == confirm_pwd:
                crypto_handler.master_pwd_session = new_master_pwd
                try:
                    crypto_handler.create_empty_registers(new_master_pwd)
                    admin.registers = {}
                    messagebox.showinfo("Success", f"New password file '{crypto_handler.DATA_FILE}' created successfully.")
                    self.initialize_main_app()
                    print("create_new_file: Successfully created, main app initialized.") # Debug print
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create new file: {e}")
                    print(f"create_new_file: Error creating file: {e}, destroying root.") # Debug print
                    self.root.destroy()
                    return
            else:
                messagebox.showerror("Mismatch", "Passwords do not match. Please try again.")
                print("create_new_file: Passwords mismatch.") # Debug print

    def initialize_main_app(self):
        print("initialize_main_app: called") # Debug print
        self.root.deiconify()
        self.create_widgets()
        self.update_register_display()
        messagebox.showinfo("Ready", "Registers loaded successfully. You can now manage your passwords.")
        print("initialize_main_app: Main window deiconified and widgets created.") # Debug print

    def create_widgets(self):
        # Frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Buttons
        tk.Button(button_frame, text="Add User", command=self.add_user).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Change Password", command=self.change_password).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Change User Name", command=self.change_user_name).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete User", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Show Users", command=self.show_users).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Select File...", command=self.select_file_and_reload).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=5)

        self.message_label = tk.Label(self.root, text="", fg="blue")
        self.message_label.pack(pady=5)

        # Use a frame for user list with scroll
        self.users_frame = tk.Frame(self.root)
        self.users_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.users_canvas = tk.Canvas(self.users_frame)
        self.scrollbar = tk.Scrollbar(self.users_frame, orient="vertical", command=self.users_canvas.yview)
        self.users_list_frame = tk.Frame(self.users_canvas)

        self.users_list_frame.bind(
            "<Configure>",
            lambda e: self.users_canvas.configure(
                scrollregion=self.users_canvas.bbox("all")
            )
        )

        self.users_canvas.create_window((0, 0), window=self.users_list_frame, anchor="nw")
        self.users_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.users_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Add a label to show the current file
        self.current_file_label = tk.Label(self.root, text=f"Current file: {os.path.basename(self.current_file)}", fg="gray")
        self.current_file_label.pack(pady=2)

    def update_message(self, message, is_error=False):
        self.message_label.config(text=message, fg="red" if is_error else "blue")

    def update_register_display(self):
        # Clear previous widgets
        for widget in self.users_list_frame.winfo_children():
            widget.destroy()

        if not admin.registers:
            tk.Label(self.users_list_frame, text="No users registered.").pack(anchor="w")
        else:
            for idx, (name, pwd) in enumerate(admin.registers.items()):
                row = tk.Frame(self.users_list_frame)
                row.pack(fill="x", pady=2, padx=5)

                tk.Label(row, text=name, width=20, anchor="w").pack(side="left")

                # Password display
                show = self.password_visibility.get(name, False)
                pwd_display = pwd if show else "********"
                pwd_var = tk.StringVar(value=pwd_display)
                pwd_entry = tk.Entry(row, textvariable=pwd_var, show="" if show else "*", width=20, state="readonly")
                pwd_entry.pack(side="left", padx=5)

                def make_toggle(name=name, pwd=pwd, var=pwd_var, entry=pwd_entry):
                    def toggle():
                        current = self.password_visibility.get(name, False)
                        self.password_visibility[name] = not current
                        if self.password_visibility[name]:
                            var.set(pwd)
                            entry.config(show="")
                        else:
                            var.set("********")
                            entry.config(show="*")
                    return toggle

                btn_text = "Hide" if show else "Show"
                tk.Button(row, text=btn_text, width=6, command=make_toggle()).pack(side="left", padx=2)

    def select_file_and_reload(self):
        file_path = filedialog.askopenfilename(
            title="Select Encrypted Data File",
            filetypes=[("Encrypted JSON", "*.enc"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            crypto_handler.DATA_FILE = file_path
            # Prompt for master password again
            master_pwd = simpledialog.askstring("Master Password", f"Enter master password for:\n{file_path}", show='*')
            if master_pwd is None:
                return
            crypto_handler.master_pwd_session = master_pwd
            registers, status = crypto_handler.load_registers(master_pwd)
            if status == "SUCCESS":
                admin.registers = registers
                self.password_visibility = {}
                self.update_register_display()
                self.update_message(f"Loaded file: {os.path.basename(file_path)}")
                self.update_current_file_label()
            else:
                messagebox.showerror("Error", f"Could not load file: {status}")

    def request_password_gui(self, prompt_message="Insert the password:"):
        """Requests a password via GUI and validates its strength."""
        messagebox.showinfo("Password Criteria",
                            f"1. Minimum length: {constants.MIN_LENGTH} characters\n"
                            f"2. At least {constants.MIN_UPPERCASE} uppercase letter(s)\n"
                            f"3. At least {constants.MIN_LOWERCASE} lowercase letter(s)\n"
                            f"4. At least {constants.MIN_DIGITS} digit(s)\n"
                            f"5. At least {constants.MIN_SPECIAL} special character(s)\n")

        while True:
            pwd = simpledialog.askstring("Password Entry", prompt_message, show='*')
            if pwd is None: # User cancelled
                return None

            result = handler.measure_strength(pwd)
            if result == constants.PWD_STRONG:
                return pwd
            else:
                messagebox.showerror("Password Strength", constants.PWD_VALIDATION_MESSAGES[result] + "\nPlease try again.")

    def add_user(self):
        name = simpledialog.askstring("Add User", "Insert the name:")
        if not name:
            return

        if name in admin.registers:
            self.update_message("Name already taken.", is_error=True)
            return

        opt = messagebox.askyesno("Generate Password", "Do you want to generate a random password?")
        if opt:
            pwd = handler.generate_random_password()
            messagebox.showinfo("Generated Password", f"Generated password: {pwd}")
        else:
            pwd = self.request_password_gui()
            if pwd is None: # User cancelled password entry
                return

        admin.registers[name] = pwd
        admin.save_registers(admin.registers, crypto_handler.get_master_password())
        self.update_message("User registered successfully.")
        self.update_register_display()

    def change_password(self):
        name = simpledialog.askstring("Change Password", "Insert the name:")
        if not name:
            return

        if name not in admin.registers:
            self.update_message("User not found.", is_error=True)
            return

        old_pwd = simpledialog.askstring("Change Password", f"Insert the previous password for '{name}':", show='*')
        if not old_pwd:
            return

        if admin.registers[name] != old_pwd:
            self.update_message(f"Incorrect password for user {name}.", is_error=True)
            return

        new_pwd = self.request_password_gui("Please insert the new password below.")
        if new_pwd is None:
            return

        admin.registers[name] = new_pwd
        admin.save_registers(admin.registers, crypto_handler.get_master_password())
        self.update_message("Password changed successfully.")
        self.update_register_display()

    def change_user_name(self):
        cur_name = simpledialog.askstring("Change User Name", "Insert the current name:")
        if not cur_name:
            return

        if cur_name not in admin.registers:
            self.update_message("User not found.", is_error=True)
            return

        pwd = simpledialog.askstring("Change User Name", f"Insert the password for '{cur_name}':", show='*')
        if not pwd:
            return

        if admin.registers[cur_name] != pwd:
            self.update_message(f"Incorrect password for user {cur_name}.", is_error=True)
            return

        new_name = simpledialog.askstring("Change User Name", "Insert the new name:")
        if not new_name:
            return

        if new_name in admin.registers:
            self.update_message("New name already taken.", is_error=True)
            return

        admin.registers[new_name] = admin.registers.pop(cur_name)
        admin.save_registers(admin.registers, crypto_handler.get_master_password())
        self.update_message(f"User name changed successfully from '{cur_name}' to '{new_name}'.")
        self.update_register_display()

    def delete_user(self):
        name = simpledialog.askstring("Delete User", "Insert the name to delete:")
        if not name:
            return

        if name not in admin.registers:
            self.update_message("User not found.", is_error=True)
            return

        pwd = simpledialog.askstring("Delete User", f"Insert the password for '{name}':", show='*')
        if not pwd:
            return

        if admin.registers[name] != pwd:
            self.update_message(f"Incorrect password for user {name}.", is_error=True)
            return

        del admin.registers[name]
        admin.save_registers(admin.registers, crypto_handler.get_master_password())
        self.update_message(f"User '{name}' deleted successfully.")
        self.update_register_display()

    def show_users(self):
        self.update_register_display()
        self.update_message("Displaying registered users.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordAdminApp(root)
    root.mainloop()