# api/validators.py
import re
from django.core.exceptions import ValidationError

class StrongPasswordValidator:
    def validate(self, password, user=None):
        errors = []
        if len(password) < 8:
            errors.append("Parola trebuie să aibă minim 8 caractere.")
        if not re.search(r'[A-Z]', password):
            errors.append("Parola trebuie să conțină cel puțin o literă mare.")
        if not re.search(r'[a-z]', password):
            errors.append("Parola trebuie să conțină cel puțin o literă mică.")
        if not re.search(r'\d', password):
            errors.append("Parola trebuie să conțină cel puțin o cifră.")
        if not re.search(r'[^A-Za-z0-9]', password):
            errors.append("Parola trebuie să conțină cel puțin un caracter special.")
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return "Parola trebuie să conțină majuscule, minuscule, cifre și un caracter special (minim 8 caractere)."