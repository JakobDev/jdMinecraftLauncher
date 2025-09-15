from ...utils.NewsGenerator import GenerateNewsPage, GeneratePlaceholderNewsPage
from PyQt6.QtCore import QThread, QUrl, QCoreApplication, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from ...Constants import NewsTypeSetting
from ...Settings import Settings
from typing import cast
import webbrowser
import traceback
import sys


class _NewsThread(QThread):
    setHtml = pyqtSignal(str)

    def run(self) -> None:
        settings = Settings.getInstance()

        self.setHtml.emit(GeneratePlaceholderNewsPage("Loading..."))

        try:
            self.setHtml.emit(GenerateNewsPage())
        except ModuleNotFoundError as ex:
            errorText = QCoreApplication.translate("NewsTab", "{{name}} not installed").replace("{{name}}", cast(str, ex.name)) + "<br>"
            errorText += QCoreApplication.translate("NewsTab", "You need the {{name}} Python package installed to use this feature").replace("{{name}}", cast(str, ex.name))
            self.setHtml.emit(GeneratePlaceholderNewsPage(errorText))
        except Exception:
            errorText = "<h1>" + QCoreApplication.translate("NewsTab", "Error") + "</h1>"
            match settings.get("newsType"):
                case NewsTypeSetting.MINECRAFT:
                    errorText += "<p>" + QCoreApplication.translate("NewsTab", "Unable to render Minecraft News") + "<p>"
                case NewsTypeSetting.RSS:
                    url = settings.get("newsFeedURL")
                    link = f'<a href="{url}">{url}</a>'
                    errorText += "<p>" + QCoreApplication.translate("NewsTab", "Unable to render RSS feed {{url}}").replace("{{url}}", link) + "<p>"
            self.setHtml.emit(GeneratePlaceholderNewsPage(errorText))
            print(traceback.format_exc(), file=sys.stderr)


class _NewsPage(QWebEnginePage):
    def __init__(self) -> None:
        super().__init__()

        self._thread = _NewsThread()

        self._thread.setHtml.connect(lambda text: self.setHtml(text, QUrl("localhost")))

    def _renderNewsPage(self) -> None:
        settings = Settings.getInstance()

        try:
            self.setHtml(GenerateNewsPage(), QUrl("localhost"))
        except ModuleNotFoundError as ex:
            errorText = QCoreApplication.translate("NewsTab", "{{name}} not installed").replace("{{name}}", cast(str, ex.name)) + "<br>"
            errorText += QCoreApplication.translate("NewsTab", "You need the {{name}} Python package installed to use this feature").replace("{{name}}", cast(str, ex.name))
            self.setHtml(errorText, QUrl("localhost"))
        except Exception:
            errorText = "<h1>" + QCoreApplication.translate("NewsTab", "Error") + "</h1>"
            match settings.get("newsType"):
                case NewsTypeSetting.MINECRAFT:
                    errorText += "<p>" + QCoreApplication.translate("NewsTab", "Unable to render Minecraft News") + "<p>"
                case NewsTypeSetting.RSS:
                    url = settings.get("newsFeedURL")
                    link = f'<a href="{url}">{url}</a>'
                    errorText += "<p>" + QCoreApplication.translate("NewsTab", "Unable to render RSS feed {{url}}").replace("{{url}}", link) + "<p>"
            self.setHtml(errorText, QUrl("localhost"))
            print(traceback.format_exc(), file=sys.stderr)

    def updateNews(self) -> None:
        settings = Settings.getInstance()

        match settings.get("newsType"):
            case NewsTypeSetting.MINECRAFT | NewsTypeSetting.RSS:
                self._thread.quit()
                self._thread.start()
            case NewsTypeSetting.WEBSITE:
                self.setUrl(QUrl(settings.get("newsURL")))

    def acceptNavigationRequest(self, url: QUrl, navigationType: QWebEnginePage.NavigationType, isMainFrame: bool) -> bool:
        if navigationType == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            if Settings.getInstance().get("newsFeedDefaultBrowser"):
                webbrowser.open(url.toString())
                return False
            else:
                return True
        else:
            return True


class NewsTab(QWebEngineView):
    def __init__(self) -> None:
        super().__init__()

        self._page = _NewsPage()
        self.setPage(self._page)

    def updateNews(self) -> None:
        self._page.updateNews()
