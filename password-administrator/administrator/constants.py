RANDOM_PWD_LENGTH = 12

# Password strength criteria
MIN_LENGTH = 16
MIN_UPPERCASE = 1
MIN_LOWERCASE = 1
MIN_DIGITS = 1
MIN_SPECIAL = 1

# Password validation codes
PWD_STRONG = 0
PWD_MUST_MIN_LENGTH = 1
PWD_MUST_UPPERCASE = 2
PWD_MUST_LOWERCASE = 3
PWD_MUST_DIGITS = 4
PWD_MUST_SPECIAL = 5


PWD_VALIDATION_MESSAGES = {
    PWD_STRONG: "La contraseña cumple con todos los criterios.",
    PWD_MUST_MIN_LENGTH: f"La contraseña debe tener al menos {MIN_LENGTH} caracteres.",
    PWD_MUST_UPPERCASE: f"La contraseña debe contener al menos {MIN_UPPERCASE} letra(s) mayúscula(s).",
    PWD_MUST_LOWERCASE: f"La contraseña debe contener al menos {MIN_LOWERCASE} letra(s) minúscula(s).",
    PWD_MUST_DIGITS: f"La contraseña debe contener al menos {MIN_DIGITS} dígito(s).",
    PWD_MUST_SPECIAL: f"La contraseña debe contener al menos {MIN_SPECIAL} carácter(es) especial(es)."
}