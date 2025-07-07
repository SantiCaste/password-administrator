import os
import re
import math
import string
from threading import Thread, Event
from os.path import abspath

MIN_PASS_LEN = 16
LEAKED_PASS_DIR = "password-administrator/administrator/leaked_passwords/"

def check_brute_force(password, problems, event):
    if(len(password) < MIN_PASS_LEN):
        problems.append("Tiene pocos caracteres")

    # Verificar si la contraseña contiene solo letras o solo números
    if password.isalpha():
        problems.append("Contiene solo letras")

    if(password.isdigit()):
        problems.append("Contiene solo números")

    # Verificar si la contraseña es una secuencia de números
    if password.isdigit() and password in "1234567890":
        problems.append("Contiene secuencia de números")

    # Verificar si la contraseña es una secuencia de letras
    if password.isalpha() and password.lower() in "abcdefghijklmnopqrstuvwxyz":
        problems.append("Tiene secuencia de letras")

    # Verificar si la contraseña contiene caracteres especiales
    if not re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password):
        problems.append("No tiene carácteres especiales")
    
def validate_patterns(password, problems, event):
    patterns = [
        [r'\d{6}', "Digitos secuenciales"],                           # Sequential digits
        [r'(.)\1+', "Caracteres repetidos"],                          # Repeated characters
        [r'qwerty|asdf|zxcv|123', "Patrones de teclado"],             # Keyboard patterns
        [r'(?:password|contraseña|admin|123456)', "Palabras comunes de diccionario"], # Common dictionary words
        [r'\b(\w+)\s*\1\b', "Palabras repetidas"],                    # Repeated words
    ]

    for pattern in patterns:
        if re.search(pattern[0], password, re.IGNORECASE):
            problems.append(pattern[1])

    
def search_leaked_pass_in_file(password, problems, filepath, event, parent_event):
    file1 = open(filepath, 'r',encoding="ISO-8859-1")
    leaked = False

    while True:
        line = file1.readline()
        
        if not line or event.is_set() or parent_event.is_set():
            break
        
        if line.rstrip() == password:
            leaked = True
            break

    if leaked:
        event.set()
        problems.append("Contraseña vulnerada")

    file1.close()

def is_leaked_pass(password, problems, event):
    childEvent = Event()
    threads = list()
    files = [f for f in os.listdir(LEAKED_PASS_DIR)]
    for filename in files:
        if not filename.endswith("txt"):
            continue
        threads.append(Thread(target = search_leaked_pass_in_file, args = (password, problems, LEAKED_PASS_DIR + filename, childEvent,event)))

    for x in threads:
        x.start()

    for x in threads:
        x.join()

def calculate_entropy(password, problems, event):
    charset_size = 0

    # Verificar qué tipos de caracteres están presentes en la contraseña para estimar el alfabeto
    if any(c in string.ascii_lowercase for c in password):
        charset_size += len(string.ascii_lowercase)
    if any(c in string.ascii_uppercase for c in password):
        charset_size += len(string.ascii_uppercase)
    if any(c in string.digits for c in password):
        charset_size += len(string.digits)
    if any(c in string.punctuation for c in password):
        charset_size += len(string.punctuation)

    # Si la contraseña no contiene ningún tipo de los caracteres comunes,
    # establecemos un tamaño mínimo de alfabeto para evitar errores (log2(0) o log2(1) = 0)
    # Esto es una simplificación, ya que una contraseña podría usar caracteres Unicode raros.
    if charset_size == 0:
        charset_size = 1 # Evitar logaritmo de cero, aunque esto implicaría una contraseña de 0 entropía

    password_length = len(password)

    # Entropía = Longitud de la Contraseña * log2(Tamaño del Alfabeto Posible)
    if charset_size > 1: 
        entropy = password_length * math.log2(charset_size)
    else:
        entropy = 0
    
    if entropy < 60:
        problems.append("La contraseña tiene baja entropía")