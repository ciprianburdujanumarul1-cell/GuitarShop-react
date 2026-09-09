from decimal import Decimal

VAT_RATES = {
    "md": Decimal("20"),
    "at": Decimal("20"), "be": Decimal("21"), "bg": Decimal("20"), "hr": Decimal("25"),
    "cy": Decimal("19"), "cz": Decimal("21"), "dk": Decimal("25"), "ee": Decimal("24"),
    "fi": Decimal("25.5"), "fr": Decimal("20"), "de": Decimal("19"), "gr": Decimal("24"),
    "hu": Decimal("27"), "ie": Decimal("23"), "it": Decimal("22"), "lv": Decimal("21"),
    "lt": Decimal("21"), "lu": Decimal("17"), "mt": Decimal("18"), "nl": Decimal("21"),
    "pl": Decimal("23"), "pt": Decimal("23"), "ro": Decimal("21"), "sk": Decimal("23"),
    "si": Decimal("22"), "es": Decimal("21"), "se": Decimal("25"),
}
DEFAULT_VAT_RATE = VAT_RATES["md"]


def get_vat_rate(country_code):
    return VAT_RATES.get((country_code or "").lower(), DEFAULT_VAT_RATE)