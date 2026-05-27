def calculate_user_score(purchase_count: int, return_count: int, account_age_days: int) -> float:
    """Calculate a user's loyalty score based on their purchase history."""
    if account_age_days < 30:
        return 0.0
    base_score = purchase_count * 10.0
    penalty = return_count * 5.0
    score = base_score - penalty
    return max(0.0, score)


def format_user_name(first_name: str, last_name: str) -> str:
    """Return a formatted full name with proper capitalization."""
    formatted_first = first_name.strip().capitalize()
    formatted_last = last_name.strip().capitalize()
    return f"{formatted_first} {formatted_last}"


def is_valid_email(email: str) -> bool:
    """Check whether an email address has a valid format."""
    if "@" not in email:
        return False
    local_part, domain_part = email.split("@", 1)
    if not local_part or not domain_part:
        return False
    return "." in domain_part


def parse_config_line(line: str) -> dict:
    """Parse a single 'key=value' configuration line into a dict."""
    line = line.strip()
    if not line or line.startswith("#"):
        return {}
    if "=" not in line:
        return {}
    key, value = line.split("=", 1)
    return {key.strip(): value.strip()}
