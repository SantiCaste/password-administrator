import random, string
import constants


def generate_random_password():
    pwd = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=constants.RANDOM_PWD_LENGTH))
    while measure_strength(pwd)[0] != constants.PWD_STRONG:
        pwd = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=constants.RANDOM_PWD_LENGTH))
    
    return pwd

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
