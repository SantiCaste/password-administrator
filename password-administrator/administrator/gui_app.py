import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, filedialog, ttk
import admin
import password_handler as handler
import constants
import crypto_handler
import os

class PasswordAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrador de Contraseñas")
        self.root.geometry("600x450")
        self.center_window(self.root, 600, 450)  # Centrar ventana principal
        self.password_visibility = {}  # Dict: user -> bool (True=visible)
        self.current_file = crypto_handler.DATA_FILE
        self.selected_user = None
        self.master_password_setup()

    def center_window(self, win, width=None, height=None):
        win.update_idletasks()
        if width is None or height is None:
            width = win.winfo_width()
            height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def master_password_setup(self):
        self.setup_window = Toplevel(self.root)
        self.setup_window.title("Configurar archivo de contraseñas")
        self.setup_window.geometry("350x200")
        self.setup_window.transient(self.root)
        self.setup_window.grab_set()
        self.center_window(self.setup_window, 350, 200)

        # Centrar contenido usando un frame
        content = tk.Frame(self.setup_window)
        content.pack(expand=True, fill="both")

        tk.Label(content, text="¡Bienvenido!").pack(pady=(20, 10), anchor="center")
        tk.Button(content, text="Abrir archivo existente", command=self.open_existing_file).pack(pady=5, anchor="center")
        tk.Button(content, text="Crear nuevo archivo", command=self.create_new_file).pack(pady=5, anchor="center")

        self.setup_window.protocol("WM_DELETE_WINDOW", self.on_setup_window_close)

    def on_setup_window_close(self):
        if crypto_handler.master_pwd_session is None:
            messagebox.showinfo("Salir", "No se seleccionó ni creó ningún archivo. Saliendo de la aplicación.")
            self.root.destroy()
        else:
            self.setup_window.destroy()

    def select_file_dialog(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de datos encriptado",
            filetypes=[("JSON Encriptado", "*.enc"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            crypto_handler.DATA_FILE = file_path
            messagebox.showinfo("Archivo seleccionado", f"Archivo seleccionado:\n{file_path}")

    def open_existing_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de datos encriptado",
            filetypes=[("JSON Encriptado", "*.enc"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return  # Usuario canceló

        self.current_file = file_path
        crypto_handler.DATA_FILE = file_path
        self.setup_window.destroy()
        max_attempts = 3
        attempts = 0
        while attempts < max_attempts:
            # --- USAR UN TOPLEVEL MODAL PARA EL PASSWORD ---
            pwd_dialog = tk.Toplevel(self.root)
            pwd_dialog.title("Contraseña maestra")
            pwd_dialog.geometry("320x120")
            pwd_dialog.transient(self.root)
            pwd_dialog.grab_set()
            self.center_window(pwd_dialog, 320, 120)

            tk.Label(pwd_dialog, text="Ingrese su contraseña maestra para el archivo seleccionado:").pack(pady=(15, 5))
            pwd_var = tk.StringVar()
            pwd_entry = tk.Entry(pwd_dialog, textvariable=pwd_var, show='*', width=25)
            pwd_entry.pack(pady=2)
            pwd_entry.focus_set()
            pwd_dialog.bind('<Return>', lambda event: on_ok())

            result = {"value": None}
            def on_ok():
                result["value"] = pwd_var.get()
                pwd_dialog.destroy()
            def on_cancel():
                result["value"] = None
                pwd_dialog.destroy()

            btn_frame = tk.Frame(pwd_dialog)
            btn_frame.pack(pady=8)
            tk.Button(btn_frame, text="Aceptar", command=on_ok).pack(side=tk.LEFT, padx=8)
            tk.Button(btn_frame, text="Cancelar", command=on_cancel).pack(side=tk.LEFT, padx=8)

            pwd_dialog.bind('<Return>', lambda event: on_ok())

            pwd_dialog.wait_window()
            master_pwd = result["value"]
            # --- FIN DEL TOPLEVEL MODAL ---

            if master_pwd is None:
                self.root.destroy()
                return

            crypto_handler.master_pwd_session = master_pwd
            registers, status = crypto_handler.load_registers(master_pwd)

            if status == "SUCCESS":
                admin.registers = registers
                self.initialize_main_app()
                return
            elif status == "FILE_NOT_FOUND":
                messagebox.showerror("Error", f"El archivo de datos encriptado '{crypto_handler.DATA_FILE}' no fue encontrado. Por favor, crea uno nuevo.")
                self.master_password_setup()
                return
            elif status == "INVALID_PASSWORD":
                attempts += 1
                messagebox.showerror("Desencriptado fallido", f"Contraseña maestra incorrecta. Quedan {max_attempts - attempts} intento(s).")
            else:
                messagebox.showerror("Desencriptado fallido", f"Ocurrió un error durante la desencriptación: {status}. Por favor, revisa el archivo o intenta nuevamente.")
                self.master_password_setup()
                return

        messagebox.showerror("Intentos excedidos", "Demasiados intentos incorrectos de contraseña maestra. Saliendo.")
        self.root.destroy()

    def create_new_file(self):
        self.setup_window.destroy()

        while True:
            new_master_pwd = self.request_password_gui("Defina su nueva contraseña maestra:")
            if new_master_pwd is None:
                self.root.destroy()
                return

            confirm_pwd = simpledialog.askstring("Confirmar contraseña maestra", "Confirme su nueva contraseña maestra:", show='*')
            if confirm_pwd is None:
                self.root.destroy()
                return

            if new_master_pwd == confirm_pwd:
                crypto_handler.master_pwd_session = new_master_pwd
                try:
                    crypto_handler.create_empty_registers(new_master_pwd)
                    admin.registers = {}
                    messagebox.showinfo("Éxito", f"Nuevo archivo de contraseñas '{crypto_handler.DATA_FILE}' creado correctamente.")
                    self.initialize_main_app()
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo crear el nuevo archivo: {e}")
                    self.root.destroy()
                    return
            else:
                messagebox.showerror("No coinciden", "Las contraseñas no coinciden. Intente nuevamente.")

    def initialize_main_app(self):
        self.root.deiconify()
        self.create_widgets()
        self.update_register_display()
        messagebox.showinfo("Listo", "Registros cargados correctamente. Ahora puede gestionar sus contraseñas.")

    def create_widgets(self):
        # Frame para botones
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Agregar usuario", command=self.add_user).pack(side=tk.LEFT, padx=5)
        self.modify_btn = tk.Button(button_frame, text="Modificar usuario", command=self.modify_selected_user, state=tk.DISABLED)
        self.modify_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn = tk.Button(button_frame, text="Eliminar usuario", command=self.delete_selected_user, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Seleccionar archivo...", command=self.select_file_and_reload).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Salir", command=self.root.quit).pack(side=tk.LEFT, padx=5)

        self.message_label = tk.Label(self.root, text="", fg="blue")
        self.message_label.pack(pady=5)

        # Etiqueta para mostrar el archivo actual
        self.current_file_label = tk.Label(self.root, text=f"Archivo actual: {os.path.basename(self.current_file)}", fg="gray")
        self.current_file_label.pack(pady=2)

        # Treeview para usuarios y contraseñas
        columns = ("Usuario", "Contraseña")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Contraseña", text="Contraseña")
        self.tree.column("Usuario", width=200)
        self.tree.column("Contraseña", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_user_select)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Menú contextual
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copiar usuario", command=self.copy_selected_user)
        self.context_menu.add_command(label="Copiar contraseña", command=self.copy_selected_password)

        # Botón para mostrar/ocultar contraseña
        self.show_password_btn = tk.Button(self.root, text="Mostrar contraseña", command=self.toggle_password, state=tk.DISABLED)
        self.show_password_btn.pack(pady=2)

    def update_message(self, message, is_error=False):
        self.message_label.config(text=message, fg="red" if is_error else "blue")

    def update_register_display(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for user, pwd in admin.registers.items():
            show = self.password_visibility.get(user, False)
            pwd_display = pwd if show else "********"
            self.tree.insert("", tk.END, iid=user, values=(user, pwd_display))
        self.modify_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        self.show_password_btn.config(state=tk.DISABLED)
        self.selected_user = None

    def on_user_select(self, event):
        selection = self.tree.selection()
        if selection:
            self.selected_user = selection[0]
            self.modify_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
            self.show_password_btn.config(state=tk.NORMAL)
            # Cambia el texto del botón según el estado
            show = self.password_visibility.get(self.selected_user, False)
            self.show_password_btn.config(text="Ocultar contraseña" if show else "Mostrar contraseña")
        else:
            self.selected_user = None
            self.modify_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            self.show_password_btn.config(state=tk.DISABLED)

    def toggle_password(self):
        if not self.selected_user:
            return
        current = self.password_visibility.get(self.selected_user, False)
        self.password_visibility[self.selected_user] = not current
        # Actualiza solo la fila seleccionada
        pwd = admin.registers[self.selected_user]
        pwd_display = pwd if not current else "********"
        self.tree.set(self.selected_user, "Contraseña", pwd_display)
        self.show_password_btn.config(text="Ocultar contraseña" if not current else "Mostrar contraseña")

    def show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.on_user_select(None)
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def copy_selected_user(self):
        if self.selected_user:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.selected_user)
            self.update_message("Usuario copiado al portapapeles.")

    def copy_selected_password(self):
        if self.selected_user:
            pwd = admin.registers.get(self.selected_user, "")
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            self.update_message("Contraseña copiada al portapapeles.")

    def modify_selected_user(self):
        if not self.selected_user:
            return

        old_name = self.selected_user
        old_pwd = admin.registers[old_name]

        # Ventana de edición
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Modificar usuario y contraseña")
        edit_win.geometry("420x300")
        edit_win.transient(self.root)
        edit_win.grab_set()

        tk.Label(edit_win, text="Usuario:").pack(pady=(10, 2))
        name_var = tk.StringVar(value=old_name)
        name_entry = tk.Entry(edit_win, textvariable=name_var, width=30)
        name_entry.pack(pady=2)

        tk.Label(edit_win, text="Contraseña:").pack(pady=(10, 2))
        pwd_var = tk.StringVar(value=old_pwd)
        pwd_entry = tk.Entry(edit_win, textvariable=pwd_var, show='*', width=30)
        pwd_entry.pack(pady=2)

        # Indicador de seguridad
        strength_label = tk.Label(edit_win, text="", font=("Arial", 10, "bold"))
        strength_label.pack(pady=4)

        # Barra de progreso de seguridad
        progress = ttk.Progressbar(edit_win, length=250, mode='determinate', maximum=5)
        progress.pack(pady=2)

        # Mensaje de criterios
        criteria = (
            f"1. Mínimo {constants.MIN_LENGTH} caracteres\n"
            f"2. {constants.MIN_UPPERCASE} mayúscula(s), {constants.MIN_LOWERCASE} minúscula(s)\n"
            f"3. {constants.MIN_DIGITS} dígito(s), {constants.MIN_SPECIAL} especial(es)"
        )
        tk.Label(edit_win, text=criteria, fg="gray").pack(pady=2)

        # Estilos de colores para la barra
        style = ttk.Style(edit_win)
        style.theme_use('default')
        style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        style.configure("red.Horizontal.TProgressbar", foreground='red', background='red')
        style.configure("orange.Horizontal.TProgressbar", foreground='orange', background='orange')

        def update_strength(*args):
            pwd = pwd_var.get()
            code = handler.measure_strength(pwd)
            score = 0
            if len(pwd) >= constants.MIN_LENGTH:
                score += 1
            if sum(c.isupper() for c in pwd) >= constants.MIN_UPPERCASE:
                score += 1
            if sum(c.islower() for c in pwd) >= constants.MIN_LOWERCASE:
                score += 1
            if sum(c.isdigit() for c in pwd) >= constants.MIN_DIGITS:
                score += 1
            if sum(c in handler.string.punctuation for c in pwd) >= constants.MIN_SPECIAL:
                score += 1
            progress['value'] = score

            if code == constants.PWD_STRONG:
                strength_label.config(text="Segura", fg="green")
                progress.configure(style="green.Horizontal.TProgressbar")
            elif code == constants.PWD_MUST_MIN_LENGTH:
                strength_label.config(text="Demasiado corta", fg="red")
                progress.configure(style="red.Horizontal.TProgressbar")
            elif code == constants.PWD_MUST_UPPERCASE:
                strength_label.config(text="Falta mayúscula", fg="orange")
                progress.configure(style="orange.Horizontal.TProgressbar")
            elif code == constants.PWD_MUST_LOWERCASE:
                strength_label.config(text="Falta minúscula", fg="orange")
                progress.configure(style="orange.Horizontal.TProgressbar")
            elif code == constants.PWD_MUST_DIGITS:
                strength_label.config(text="Falta dígito", fg="orange")
                progress.configure(style="orange.Horizontal.TProgressbar")
            elif code == constants.PWD_MUST_SPECIAL:
                strength_label.config(text="Falta especial", fg="orange")
                progress.configure(style="orange.Horizontal.TProgressbar")
            else:
                strength_label.config(text="", fg="black")
                progress.configure(style="red.Horizontal.TProgressbar")

        pwd_var.trace_add("write", update_strength)
        update_strength()

        def on_save():
            new_name = name_var.get().strip()
            new_pwd = pwd_var.get()
            code = handler.measure_strength(new_pwd)
            if not new_name:
                messagebox.showerror("Error", "El nombre de usuario no puede estar vacío.", parent=edit_win)
                return
            if new_name != old_name and new_name in admin.registers:
                messagebox.showerror("Error", "El nuevo nombre ya está en uso.", parent=edit_win)
                return
            if code != constants.PWD_STRONG:
                messagebox.showerror("Seguridad de contraseña", constants.PWD_VALIDATION_MESSAGES[code] + "\nPor favor, intente nuevamente.", parent=edit_win)
                return

            # Actualiza el registro
            if new_name != old_name:
                admin.registers[new_name] = new_pwd
                del admin.registers[old_name]
            else:
                admin.registers[old_name] = new_pwd
            admin.save_registers(admin.registers, crypto_handler.get_master_password())
            self.update_message("Usuario y/o contraseña modificados correctamente.")
            self.update_register_display()
            edit_win.destroy()

        def on_cancel():
            edit_win.destroy()

        btn_frame = tk.Frame(edit_win)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Guardar", command=on_save).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Cancelar", command=on_cancel).pack(side=tk.LEFT, padx=8)

    def delete_selected_user(self):
        if not self.selected_user:
            return
        confirm = messagebox.askyesno("Eliminar usuario", f"¿Seguro que deseas eliminar '{self.selected_user}'?")
        if not confirm:
            return
        del admin.registers[self.selected_user]
        admin.save_registers(admin.registers, crypto_handler.get_master_password())
        self.update_message(f"Usuario '{self.selected_user}' eliminado correctamente.")
        self.update_register_display()

    def change_password_selected(self):
        old_pwd = simpledialog.askstring("Cambiar contraseña", f"Ingrese la contraseña actual para '{self.selected_user}':", show='*')
        if not old_pwd:
            return
        if admin.registers[self.selected_user] != old_pwd:
            self.update_message(f"Contraseña incorrecta para {self.selected_user}.", is_error=True)
            return
        new_pwd = self.request_password_gui("Por favor, ingrese la nueva contraseña.")
        if new_pwd is None:
            return
        admin.registers[self.selected_user] = new_pwd
        admin.save_registers(admin.registers, crypto_handler.get_master_password())
        self.update_message("Contraseña cambiada correctamente.")
        self.update_register_display()

    def change_user_name_selected(self):
        pwd = simpledialog.askstring("Cambiar nombre de usuario", f"Ingrese la contraseña para '{self.selected_user}':", show='*')
        if not pwd:
            return
        if admin.registers[self.selected_user] != pwd:
            self.update_message(f"Contraseña incorrecta para {self.selected_user}.", is_error=True)
            return
        new_name = simpledialog.askstring("Cambiar nombre de usuario", "Ingrese el nuevo nombre:")
        if not new_name:
            return
        if new_name in admin.registers:
            self.update_message("El nuevo nombre ya está en uso.", is_error=True)
            return
        admin.registers[new_name] = admin.registers.pop(self.selected_user)
        admin.save_registers(admin.registers, crypto_handler.get_master_password())
        self.update_message(f"Nombre de usuario cambiado correctamente a '{new_name}'.")
        self.update_register_display()

    def select_file_and_reload(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de datos encriptado",
            filetypes=[("JSON Encriptado", "*.enc"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            crypto_handler.DATA_FILE = file_path
            master_pwd = simpledialog.askstring("Contraseña maestra", f"Ingrese la contraseña maestra para:\n{file_path}", show='*')
            if master_pwd is None:
                return
            crypto_handler.master_pwd_session = master_pwd
            registers, status = crypto_handler.load_registers(master_pwd)
            if status == "SUCCESS":
                admin.registers = registers
                self.password_visibility = {}
                self.update_register_display()
                self.update_message(f"Archivo cargado: {os.path.basename(file_path)}")
                self.update_current_file_label()
            else:
                messagebox.showerror("Error", f"No se pudo cargar el archivo: {status}")

    def update_current_file_label(self):
        if hasattr(self, 'current_file_label'):
            self.current_file_label.config(text=f"Archivo actual: {os.path.basename(self.current_file)}")

    def request_password_gui(self, prompt_message="Ingrese la contraseña:"):
        dialog = tk.Toplevel(self.root)
        dialog.title("Ingresar contraseña")
        dialog.geometry("400x240")
        dialog.transient(self.root)
        dialog.grab_set()
        self.center_window(dialog, 400, 240)

        tk.Label(dialog, text=prompt_message).pack(pady=(10, 2))
        pwd_var = tk.StringVar()
        pwd_entry = tk.Entry(dialog, textvariable=pwd_var, show='*', width=30)
        pwd_entry.pack(pady=2)
        pwd_entry.focus_set()
        dialog.bind('<Return>', lambda event: on_ok())

        # Indicador de seguridad
        strength_label = tk.Label(dialog, text="", font=("Arial", 10, "bold"))
        strength_label.pack(pady=4)

        # Barra de progreso de seguridad
        progress = ttk.Progressbar(dialog, length=250, mode='determinate', maximum=5)
        progress.pack(pady=2)

        # Mensaje de criterios
        criteria = (
            f"1. Mínimo {constants.MIN_LENGTH} caracteres\n"
            f"2. {constants.MIN_UPPERCASE} mayúscula(s), {constants.MIN_LOWERCASE} minúscula(s)\n"
            f"3. {constants.MIN_DIGITS} dígito(s), {constants.MIN_SPECIAL} especial(es)"
        )
        tk.Label(dialog, text=criteria, fg="gray").pack(pady=2)

        result = {"password": None}

        def update_strength(*args):
            pwd = pwd_var.get()
            code = handler.measure_strength(pwd)
            # Calcula el nivel de seguridad (0 a 5)
            score = 0
            if len(pwd) >= constants.MIN_LENGTH:
                score += 1
            if sum(c.isupper() for c in pwd) >= constants.MIN_UPPERCASE:
                score += 1
            if sum(c.islower() for c in pwd) >= constants.MIN_LOWERCASE:
                score += 1
            if sum(c.isdigit() for c in pwd) >= constants.MIN_DIGITS:
                score += 1
            if sum(c in handler.string.punctuation for c in pwd) >= constants.MIN_SPECIAL:
                score += 1
            progress['value'] = score

            # Cambia color y texto según el código
            if code == constants.PWD_STRONG:
                strength_label.config(text="Segura", fg="green")
                progress.configure(style="green.Horizontal.TProgressbar")
            elif code == constants.PWD_MUST_MIN_LENGTH:
                strength_label.config(text="Demasiado corta", fg="red")
                progress.configure(style="red.Horizontal.TProgressbar")
            elif code == constants.PWD_MUST_UPPERCASE:
                strength_label.config(text="Falta mayúscula", fg="orange")
                progress.configure(style="orange.Horizontal.TProgressbar")
            elif code == constants.PWD_MUST_LOWERCASE:
                strength_label.config(text="Falta minúscula", fg="orange")
                progress.configure(style="orange.Horizontal.TProgressbar")
            elif code == constants.PWD_MUST_DIGITS:
                strength_label.config(text="Falta dígito", fg="orange")
                progress.configure(style="orange.Horizontal.TProgressbar")
            elif code == constants.PWD_MUST_SPECIAL:
                strength_label.config(text="Falta especial", fg="orange")
                progress.configure(style="orange.Horizontal.TProgressbar")
            else:
                strength_label.config(text="", fg="black")
                progress.configure(style="red.Horizontal.TProgressbar")

        # Estilos de colores para la barra
        style = ttk.Style(dialog)
        style.theme_use('default')
        style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        style.configure("red.Horizontal.TProgressbar", foreground='red', background='red')
        style.configure("orange.Horizontal.TProgressbar", foreground='orange', background='orange')

        pwd_var.trace_add("write", update_strength)

        def on_ok():
            pwd = pwd_var.get()
            code = handler.measure_strength(pwd)
            if code == constants.PWD_STRONG:
                result["password"] = pwd
                dialog.destroy()
            else:
                messagebox.showerror("Seguridad de contraseña", constants.PWD_VALIDATION_MESSAGES[code] + "\nPor favor, intente nuevamente.", parent=dialog)

        def on_cancel():
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Aceptar", command=on_ok).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Cancelar", command=on_cancel).pack(side=tk.LEFT, padx=8)

        dialog.bind('<Return>', lambda event: on_ok())

        dialog.wait_window()
        return result["password"]

    def add_user(self):
        name = simpledialog.askstring("Agregar usuario", "Ingrese el nombre:")
        if not name:
            return

        if name in admin.registers:
            self.update_message("El nombre ya está en uso.", is_error=True)
            return

        opt = messagebox.askyesno("Generar contraseña", "¿Desea generar una contraseña aleatoria?")
        if opt:
            pwd = handler.generate_random_password()
            messagebox.showinfo("Contraseña generada", f"Contraseña generada: {pwd}")
        else:
            pwd = self.request_password_gui()
            if pwd is None:
                return

        admin.registers[name] = pwd
        admin.save_registers(admin.registers, crypto_handler.get_master_password())
        self.update_message("Usuario registrado correctamente.")
        self.update_register_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordAdminApp(root)
    root.mainloop()