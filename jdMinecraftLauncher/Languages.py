from PyQt6.QtCore import QCoreApplication


def getLanguageNames() -> dict[str, str]:
    return {
        "en": QCoreApplication.translate("Language", "English"),
        "de": QCoreApplication.translate("Language", "German"),
        "nl": QCoreApplication.translate("Language", "Dutch"),
        "es": QCoreApplication.translate("Language", "Spanish"),
        "ru": QCoreApplication.translate("Language", "Russian"),
    }