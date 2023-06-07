from PyQt6.QtCore import QCoreApplication


def getLanguageNames() -> dict[str, str]:
    return {
        "en": QCoreApplication.translate("Language", "English"),
        "de": QCoreApplication.translate("Language", "German"),
    }