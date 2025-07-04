import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, filedialog, ttk
from PIL import Image, ImageTk
import password_handler as handler
import constants
import crypto_handler
import os

registers = {}

def save_registers(registers_dict, master_password, file_path):
    crypto_handler.save_registers(registers_dict, master_password, file_path)

def load_registers(master_password, file_path):
    return crypto_handler.load_registers(master_password, file_path)

# code_map is a dictionary that maps password strength codes to their display properties
code_map = {
    constants.PWD_STRONG:      ("Segura", "green", "green.Horizontal.TProgressbar"),
    constants.PWD_MUST_MIN_LENGTH: ("Demasiado corta", "red", "red.Horizontal.TProgressbar"),
    constants.PWD_MUST_UPPERCASE:  ("Falta mayúscula", "orange", "orange.Horizontal.TProgressbar"),
    constants.PWD_MUST_LOWERCASE:  ("Falta minúscula", "orange", "orange.Horizontal.TProgressbar"),
    constants.PWD_MUST_DIGITS:     ("Falta dígito", "orange", "orange.Horizontal.TProgressbar"),
    constants.PWD_MUST_SPECIAL:    ("Falta especial", "orange", "orange.Horizontal.TProgressbar"),
}

class PasswordAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrador de Contraseñas")
        self.root.geometry("600x450")
        self.center_window(self.root, 600, 450)
        self.root.lift()
        self.root.focus_force()
        self.password_visibility = {} 
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
        self.setup_window.lift()
        self.setup_window.focus_force()

        content = tk.Frame(self.setup_window)
        content.pack(expand=True, fill="both")

        tk.Label(content, text="¡Bienvenido!").pack(pady=(20, 10), anchor="center")
        tk.Button(content, text="Abrir archivo existente", command=self.open_existing_file).pack(pady=5, anchor="center")
        tk.Button(content, text="Crear nuevo archivo", command=self.create_new_file).pack(pady=5, anchor="center")

        self.setup_window.protocol("WM_DELETE_WINDOW", self.on_setup_window_close)

    def on_setup_window_close(self):
        if crypto_handler.master_pwd_session is None:
            messagebox.showinfo("Salir", "No se seleccionó ni creó ningún archivo. Saliendo de la aplicación.", parent=self.root)
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
            messagebox.showinfo("Archivo seleccionado", f"Archivo seleccionado:\n{os.path.basename(file_path)}", parent=self.root)

    def open_existing_file(self):
        global registers
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de datos encriptado",
            filetypes=[("JSON Encriptado", "*.enc"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        self.current_file = file_path
        crypto_handler.DATA_FILE = file_path
        self.setup_window.destroy()
        max_attempts = 3
        attempts = 0
        while attempts < max_attempts:
            pwd_dialog = tk.Toplevel(self.root)
            pwd_dialog.title("Contraseña maestra")
            pwd_dialog.geometry("320x120")
            pwd_dialog.transient(self.root)
            pwd_dialog.grab_set()
            self.center_window(pwd_dialog, 320, 120)
            pwd_dialog.lift()
            pwd_dialog.focus_force()

            tk.Label(pwd_dialog, text=f"Ingrese su contraseña maestra para {os.path.basename(self.current_file)}:").pack(pady=(15, 5))
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

            if master_pwd is None:
                self.root.destroy()
                return

            crypto_handler.master_pwd_session = master_pwd
            loaded, status = load_registers(master_pwd, self.current_file)

            if status == "SUCCESS":
                registers.clear()
                registers.update(loaded)
                self.initialize_main_app()
                return
            elif status == "FILE_NOT_FOUND":
                messagebox.showerror("Error", f"El archivo de datos encriptado '{crypto_handler.DATA_FILE}' no fue encontrado. Por favor, crea uno nuevo.", parent=self.root)
                self.master_password_setup()
                return
            elif status == "INVALID_PASSWORD":
                attempts += 1
                messagebox.showerror("Desencriptado fallido", f"Contraseña maestra incorrecta. Quedan {max_attempts - attempts} intento(s).", parent=self.root)
            else:
                messagebox.showerror("Desencriptado fallido", f"Ocurrió un error durante la desencriptación: {status}. Por favor, revisa el archivo o intenta nuevamente.", parent=self.root)
                self.master_password_setup()
                return

        messagebox.showerror("Intentos excedidos", "Demasiados intentos incorrectos de contraseña maestra. Saliendo.", parent=self.root)
        self.root.destroy()

    def create_new_file(self):
        global registers
        self.setup_window.destroy()

        while True:
            filename = simpledialog.askstring("Nombre del archivo", "Ingrese el nombre para el nuevo archivo de contraseñas (sin extensión):", parent=self.root)
            if filename is None:
                self.root.destroy()
                return

            if not filename.strip():
                messagebox.showerror("Error", "El nombre del archivo no puede estar vacío.", parent=self.root)
                continue

            if not filename.endswith('.json.enc'):
                filename = filename.strip() + '.json.enc'
            
            if os.path.exists(filename):
                messagebox.showerror("Error", f"El archivo '{filename}' ya existe. Por favor, elija otro nombre.", parent=self.root)
                continue
            
            new_master_pwd = self.request_password_gui("Defina su nueva contraseña maestra:")
            if new_master_pwd is None:
                self.root.destroy()
                return

            confirm_pwd = simpledialog.askstring("Confirmar contraseña maestra", "Confirme su nueva contraseña maestra:", show='*', parent=self.root)
            if confirm_pwd is None:
                self.root.destroy()
                return

            self.current_file = filename
            if new_master_pwd == confirm_pwd:
                crypto_handler.master_pwd_session = new_master_pwd
                try:
                    crypto_handler.create_empty_registers(new_master_pwd, self.current_file)
                    registers.clear()
                    messagebox.showinfo(
                        "Éxito",
                        f"Nuevo archivo de contraseñas '{os.path.basename(self.current_file)}' creado correctamente.",
                        parent=self.root
                    )
                    self.initialize_main_app()
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo crear el nuevo archivo: {e}", parent=self.root)
                    self.root.destroy()
                    return
            else:
                messagebox.showerror("No coinciden", "Las contraseñas no coinciden. Intente nuevamente.", parent=self.root)

    def initialize_main_app(self):
        self.root.deiconify()
        self.create_widgets()
        self.update_register_display()
        messagebox.showinfo("Listo", "Registros cargados correctamente. Ahora puede gestionar sus contraseñas.", parent=self.root)

    def create_widgets(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Agregar usuario", command=self.add_user).pack(side=tk.LEFT, padx=5)
        self.modify_btn = tk.Button(button_frame, text="Modificar usuario", command=self.modify_selected_user, state=tk.DISABLED)
        self.modify_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn = tk.Button(button_frame, text="Eliminar usuario", command=self.delete_selected_user, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Seleccionar archivo...", command=self.select_file_and_reload).pack(side=tk.LEFT, padx=5)
        self.str_btn = tk.Button(button_frame, text="Verificar fuerza", command=self.check_strength, state=tk.DISABLED)
        self.str_btn.pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Salir", command=self.root.quit).pack(side=tk.LEFT, padx=5)

        self.message_label = tk.Label(self.root, text="", fg="blue")
        self.message_label.pack(pady=5)

        self.current_file_label = tk.Label(self.root, text=f"Archivo actual: {os.path.basename(self.current_file)}", fg="gray")
        self.current_file_label.pack(pady=2)

        columns = ("Usuario", "Contraseña")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Contraseña", text="Contraseña")
        self.tree.column("Usuario", width=200)
        self.tree.column("Contraseña", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_user_select)
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copiar usuario", command=self.copy_selected_user)
        self.context_menu.add_command(label="Copiar contraseña", command=self.copy_selected_password)

        self.show_password_btn = tk.Button(self.root, text="Mostrar contraseña", command=self.toggle_password, state=tk.DISABLED)
        self.show_password_btn.pack(pady=2)

    def update_message(self, message, is_error=False):
        self.message_label.config(text=message, fg="red" if is_error else "blue")

    def update_register_display(self):
        self.tree.delete(*self.tree.get_children())
        for user, pwd in registers.items():
            show = self.password_visibility.get(user, False)
            pwd_display = pwd if show else "********"
            self.tree.insert("", tk.END, iid=user, values=(user, pwd_display))
        self.modify_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        self.str_btn.config(state=tk.DISABLED)
        self.show_password_btn.config(state=tk.DISABLED)
        self.selected_user = None

    def on_user_select(self, event):
        selection = self.tree.selection()
        if selection:
            self.selected_user = selection[0]
            self.modify_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
            self.str_btn.config(state=tk.NORMAL)
            self.show_password_btn.config(state=tk.NORMAL)
            show = self.password_visibility.get(self.selected_user, False)
            self.show_password_btn.config(text="Ocultar contraseña" if show else "Mostrar contraseña")
        else:
            self.selected_user = None
            self.modify_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            self.str_btn.config(state=tk.DISABLED)
            self.show_password_btn.config(state=tk.DISABLED)

    def toggle_password(self):
        if not self.selected_user:
            return
        current = self.password_visibility.get(self.selected_user, False)
        self.password_visibility[self.selected_user] = not current
        pwd = registers[self.selected_user]
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
            pwd = registers.get(self.selected_user, "")
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            self.update_message("Contraseña copiada al portapapeles.")

    def modify_selected_user(self):
        if not self.selected_user:
            return

        old_name = self.selected_user
        old_pwd = registers[old_name]

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
            code, score = handler.measure_strength(pwd)
            progress['value'] = score

            text, color, style = code_map.get(code, ("", "black", "red.Horizontal.TProgressbar"))
            strength_label.config(text=text, fg=color)
            progress.configure(style=style)


        pwd_var.trace_add("write", update_strength)
        update_strength()

        def on_save():
            new_name = name_var.get().strip()
            new_pwd = pwd_var.get()
            code, _ = handler.measure_strength(new_pwd)
            if not new_name:
                messagebox.showerror("Error", "El nombre de usuario no puede estar vacío.", parent=edit_win)
                return
            if new_name != old_name and new_name in registers:
                messagebox.showerror("Error", "El nuevo nombre ya está en uso.", parent=edit_win)
                return
            if code != constants.PWD_STRONG:
                messagebox.showerror("Seguridad de contraseña", constants.PWD_VALIDATION_MESSAGES[code] + "\nPor favor, intente nuevamente.", parent=edit_win)
                return

            # Actualiza el registro
            if new_name != old_name:
                registers[new_name] = new_pwd
                del registers[old_name]
            else:
                registers[old_name] = new_pwd
            save_registers(registers, crypto_handler.master_pwd_session, self.current_file)
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
        del registers[self.selected_user]
        save_registers(registers, crypto_handler.master_pwd_session, self.current_file)
        self.update_message(f"Usuario '{self.selected_user}' eliminado correctamente.")
        self.update_register_display()

    def change_password_selected(self):
        old_pwd = simpledialog.askstring("Cambiar contraseña", f"Ingrese la contraseña actual para '{self.selected_user}':", show='*')
        if not old_pwd:
            return
        if registers[self.selected_user] != old_pwd:
            self.update_message(f"Contraseña incorrecta para {self.selected_user}.", is_error=True)
            return
        new_pwd = self.request_password_gui("Por favor, ingrese la nueva contraseña.")
        if new_pwd is None:
            return
        registers[self.selected_user] = new_pwd
        save_registers(registers, crypto_handler.master_pwd_session, self.current_file)
        self.update_message("Contraseña cambiada correctamente.")
        self.update_register_display()

    def change_user_name_selected(self):
        pwd = simpledialog.askstring("Cambiar nombre de usuario", f"Ingrese la contraseña para '{self.selected_user}':", show='*')
        if not pwd:
            return
        if registers[self.selected_user] != pwd:
            self.update_message(f"Contraseña incorrecta para {self.selected_user}.", is_error=True)
            return
        new_name = simpledialog.askstring("Cambiar nombre de usuario", "Ingrese el nuevo nombre:")
        if not new_name:
            return
        if new_name in registers:
            self.update_message("El nuevo nombre ya está en uso.", is_error=True)
            return
        registers[new_name] = registers.pop(self.selected_user)
        save_registers(registers, crypto_handler.master_pwd_session, self.current_file)
        self.update_message(f"Nombre de usuario cambiado correctamente a '{new_name}'.")
        self.update_register_display()

    def select_file_and_reload(self):
        global registers
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de datos encriptado",
            filetypes=[("JSON Encriptado", "*.enc"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            crypto_handler.DATA_FILE = file_path
            
            master_pwd = simpledialog.askstring("Contraseña maestra", f"Ingrese la contraseña maestra para:\n{os.path.basename(file_path)}", show='*')
            if master_pwd is None:
                return
            crypto_handler.master_pwd_session = master_pwd
            loaded, status = load_registers(master_pwd, self.current_file)
            if status == "SUCCESS":
                registers.clear()
                registers.update(loaded)
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
        # Crear ventana oculta para evitar parpadeo
        dialog = tk.Toplevel(self.root)
        dialog.withdraw()
        dialog.title("Ingresar contraseña")
        dialog.transient(self.root)
        dialog.grab_set()

        # Frame principal para centrar todo
        main_frame = tk.Frame(dialog)
        main_frame.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(main_frame, text=prompt_message).pack(pady=(5, 2))
        pwd_var = tk.StringVar()
        pwd_entry = tk.Entry(main_frame, textvariable=pwd_var, show='*', width=30)
        pwd_entry.pack(pady=2)
        pwd_entry.focus_set()
        dialog.bind('<Return>', lambda event: on_ok())

        skip_check_var = tk.BooleanVar()
        skip_checkbox = tk.Checkbutton(main_frame, text="Si no lo veo, no es ilegal", variable=skip_check_var)
        skip_checkbox.pack(pady=5)

        # Frame para el gif animado (espacio reservado SIEMPRE)
        gif_frame = tk.Frame(main_frame, height=150, width=200)
        gif_frame.pack_propagate(False)
        gif_frame.pack(pady=2)
        gif_label = tk.Label(gif_frame)
        gif_label.pack(expand=True)

        # Cargar los frames del gif animado
        gif_frames = []
        gif_path = os.path.join(os.path.dirname(__file__), "homero.gif")
        try:
            im = Image.open(gif_path)
            while True:
                frame = im.copy().convert("RGBA")
                frame.thumbnail((150, 150))
                gif_frames.append(ImageTk.PhotoImage(frame))
                im.seek(im.tell() + 1)
        except EOFError:
            pass
        except Exception:
            gif_frames = []

        def show_gif():
            if not gif_frames:
                gif_label.config(image='', text='')
                return
            if len(gif_frames) == 1:
                gif_label.config(image=gif_frames[0])
                gif_label.image = gif_frames[0]
                return
            def animate(idx=0):
                if not skip_check_var.get():
                    gif_label.config(image='', text='')
                    return
                gif_label.config(image=gif_frames[idx])
                gif_label.image = gif_frames[idx]
                dialog.after(80, animate, (idx + 1) % len(gif_frames))
            animate()

        def hide_gif():
            gif_label.config(image='', text='')

        def on_skip_check(*args):
            if skip_check_var.get():
                show_gif()
            else:
                hide_gif()

        skip_check_var.trace_add("write", on_skip_check)
        hide_gif()  # Ocultar gif al inicio

        strength_label = tk.Label(main_frame, text="", font=("Arial", 10, "bold"))
        strength_label.pack(pady=4)

        progress = ttk.Progressbar(main_frame, length=250, mode='determinate', maximum=5)
        progress.pack(pady=2)

        # Mensaje de criterios
        criteria = (
            f"1. Mínimo {constants.MIN_LENGTH} caracteres\n"
            f"2. {constants.MIN_UPPERCASE} mayúscula(s), {constants.MIN_LOWERCASE} minúscula(s)\n"
            f"3. {constants.MIN_DIGITS} dígito(s), {constants.MIN_SPECIAL} especial(es)"
        )
        criteria_label = tk.Label(main_frame, text=criteria, fg="gray")
        criteria_label.pack(pady=2)

        result = {"password": None}

        def update_strength(*args):
            # Si la verificación está omitida, ocultar indicadores
            if skip_check_var.get():
                strength_label.config(text="Verificación omitida", fg="blue")
                progress['value'] = 0
                progress.configure(style="blue.Horizontal.TProgressbar")
                criteria_label.config(fg="lightgray")
                return
            
            # Mostrar criterios normalmente
            criteria_label.config(fg="gray")
            
            pwd = pwd_var.get()
            code, score = handler.measure_strength(pwd)
            progress['value'] = score

            text, color, style = code_map.get(code, ("", "black", "red.Horizontal.TProgressbar"))
            strength_label.config(text=text, fg=color)

            # Cambia color y texto según el código
            progress.configure(style=style)

        # Estilos de colores para la barra
        style = ttk.Style(dialog)
        style.theme_use('default')
        style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        style.configure("red.Horizontal.TProgressbar", foreground='red', background='red')
        style.configure("orange.Horizontal.TProgressbar", foreground='orange', background='orange')
        style.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue')

        pwd_var.trace_add("write", update_strength)
        skip_check_var.trace_add("write", update_strength)

        def on_ok():
            pwd = pwd_var.get()
            
            # Si la verificación está omitida, aceptar cualquier contraseña
            if skip_check_var.get():
                if not pwd:  # Solo verificar que no esté vacía
                    messagebox.showerror("Error", "La contraseña no puede estar vacía.", parent=dialog)
                    return
                result["password"] = pwd
                dialog.destroy()
                return
            
            # Verificación normal de seguridad
            code, _ = handler.measure_strength(pwd)
            if code == constants.PWD_STRONG:
                result["password"] = pwd
                dialog.destroy()
            else:
                messagebox.showerror("Seguridad de contraseña", constants.PWD_VALIDATION_MESSAGES[code] + "\nPor favor, intente nuevamente.", parent=dialog)

        def on_cancel():
            dialog.destroy()

        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Aceptar", command=on_ok).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Cancelar", command=on_cancel).pack(side=tk.LEFT, padx=8)

        # Centrar y mostrar la ventana ya armada
        dialog.update_idletasks()
        self.center_window(dialog, 400, dialog.winfo_height())
        dialog.deiconify()
        dialog.lift()
        dialog.focus_force()

        dialog.bind('<Return>', lambda event: on_ok())

        dialog.wait_window()
        return result["password"]

    def add_user(self):
        name = simpledialog.askstring("Agregar usuario", "Ingrese el nombre:", parent=self.root)
        if not name:
            return

        if name in registers:
            self.update_message("El nombre ya está en uso.", is_error=True)
            return

        opt = messagebox.askyesno("Generar contraseña", "¿Desea generar una contraseña aleatoria?", parent=self.root)
        if opt:
            pwd = handler.generate_random_password()
            messagebox.showinfo("Contraseña generada", f"Contraseña generada: {pwd}", parent=self.root)
        else:
            pwd = self.request_password_gui()
            if pwd is None:
                return

        registers[name] = pwd
        print(crypto_handler.master_pwd_session)
        save_registers(registers, crypto_handler.master_pwd_session, self.current_file)
        self.update_message("Usuario registrado correctamente.")
        self.update_register_display()

    def check_strength(self):
        if not self.selected_user:
            return
        problems = handler.format_problems(handler.check_strength(registers[self.selected_user]))

        win = tk.Toplevel()
        win.wm_title("Window")

        l = tk.Label(win, text=problems)
        l.grid(row=0, column=0)

        b = ttk.Button(win, text="Okay", command=win.destroy)
        b.grid(row=1, column=0)

        self.update_message(problems)
        self.update_register_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordAdminApp(root)
    root.mainloop()