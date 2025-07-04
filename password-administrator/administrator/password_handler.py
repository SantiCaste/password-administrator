import random, string
import constants
import validators 
from threading import Event


def generate_random_password():
    """Genera una contraseña aleatoria que cumple todos los criterios de seguridad."""
    chars = string.ascii_letters + string.digits + string.punctuation
    length = random.randint(constants.MIN_LENGTH, constants.MAX_LENGTH)

    max_attempts = 1000

    for _ in range(max_attempts):
        # Garantiza al menos un carácter de cada tipo requerido
        pwd = [
            random.choice(string.ascii_uppercase) for _ in range(constants.MIN_UPPERCASE)
        ] + [
            random.choice(string.ascii_lowercase) for _ in range(constants.MIN_LOWERCASE)
        ] + [
            random.choice(string.digits) for _ in range(constants.MIN_DIGITS)
        ] + [
            random.choice(string.punctuation) for _ in range(constants.MIN_SPECIAL)
        ]
        # Completa el resto con caracteres aleatorios
        pwd += random.choices(chars, k=length - len(pwd))
        random.shuffle(pwd)
        pwd = ''.join(pwd)
        code, _ = measure_strength(pwd)
        if code == constants.PWD_STRONG:
            return pwd
    # Si no logra generar una contraseña válida, lanza excepción
    raise Exception("No se pudo generar una contraseña segura tras varios intentos.")

# measure password strength considering length and complexity
def measure_strength(password: str) -> tuple:
    score = 0
    if len(password) >= constants.MIN_LENGTH:
        score += 1
    if sum(c.isupper() for c in password) >= constants.MIN_UPPERCASE:
        score += 1
    if sum(c.islower() for c in password) >= constants.MIN_LOWERCASE:
        score += 1
    if sum(c.isdigit() for c in password) >= constants.MIN_DIGITS:
        score += 1
    if sum(c in string.punctuation for c in password) >= constants.MIN_SPECIAL:
        score += 1

    if len(password) < constants.MIN_LENGTH:
        return (constants.PWD_MUST_MIN_LENGTH, score)
    if sum(c.isupper() for c in password) < constants.MIN_UPPERCASE:
        return (constants.PWD_MUST_UPPERCASE, score)
    if sum(c.islower() for c in password) < constants.MIN_LOWERCASE:
        return (constants.PWD_MUST_LOWERCASE, score)
    if sum(c.isdigit() for c in password) < constants.MIN_DIGITS:
        return (constants.PWD_MUST_DIGITS, score)
    if sum(c in string.punctuation for c in password) < constants.MIN_SPECIAL:
        return (constants.PWD_MUST_SPECIAL, score)

    # If all criteria are met
    return (constants.PWD_STRONG, score)

# Returns an array with the passwords problems
def check_strength(password: str) -> str:
    problems = list()
    event = Event()
    # Seteamos validaciones a ejecutar
    validator_list = [validators.check_brute_force, validators.validate_patterns, validators.calculate_entropy, validators.is_leaked_pass]

    for val in validator_list:
        val(password, problems, event)

    return problems

def format_problems(problems: str) -> str: 
    output = ""
    if len(problems) == 0:
        output += "Contraseña segura"
    else:
        output = "Problemas:"
        for p in problems:
            output += "\n" + p  
        output += "\n"
    return output
