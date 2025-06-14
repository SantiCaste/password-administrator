import random, string
import constants


def generate_random_password():
    pwd = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=constants.RANDOM_PWD_LENGTH))
    while measure_strength(pwd) != constants.PWD_STRONG:
        pwd = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=constants.RANDOM_PWD_LENGTH))
    
    return pwd

# measure password strength considering length and complexity
def measure_strength(password: str) -> int:
    if len(password) < constants.MIN_LENGTH:
        return constants.PWD_MUST_MIN_LENGTH
    
    if sum(c.isdigit() for c in password) < constants.MIN_DIGITS:
        return constants.PWD_MUST_DIGITS

    if sum(c.isupper() for c in password) < constants.MIN_UPPERCASE:
        return constants.PWD_MUST_UPPERCASE

    if sum(c.islower() for c in password) < constants.MIN_LOWERCASE:
        return constants.PWD_MUST_LOWERCASE

    if sum(c in string.punctuation for c in password) < constants.MIN_SPECIAL:
        return constants.PWD_MUST_SPECIAL
    
    # If all criteria are met
    return constants.PWD_STRONG