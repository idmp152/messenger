import re


def validate_email(email: str) -> bool:
    valid_email_regex = r"^[a-z0-9]+[\._]?[ a-z0-9]+[@]\w+[. ]\w{2,3}$"
    return re.search(valid_email_regex, email) is not None


def validate_username(username: str) -> bool:
    return username != ""


def validate_password_sha256_hash(hex_value: str) -> bool:
    empty_string_sha256_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    return hex_value != empty_string_sha256_hash


def validate_password(password: str) -> bool:
    valid_password_regex = r"^[a-zA-Z0-9]{8,32}$"
    return re.search(valid_password_regex, password) is not None
