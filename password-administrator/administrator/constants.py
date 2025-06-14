RANDOM_PWD_LENGTH = 12

# Password strength criteria
MIN_LENGTH = 8
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
    PWD_STRONG: "Password meets all criteria.",
    PWD_MUST_MIN_LENGTH: f"Password must be at least {MIN_LENGTH} characters long.",
    PWD_MUST_UPPERCASE: f"Password must contain at least {MIN_UPPERCASE} uppercase letter(s).",
    PWD_MUST_LOWERCASE: f"Password must contain at least {MIN_LOWERCASE} lowercase letter(s).",
    PWD_MUST_DIGITS: f"Password must contain at least {MIN_DIGITS} digit(s).",
    PWD_MUST_SPECIAL: f"Password must contain at least {MIN_SPECIAL} special character(s)."
}