from PyQt6.QtWebEngineWidgets import QWebEngineView
from ...utils.NewsGenerator import GenerateNewsPage
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, QCoreApplication
from ...Constants import NewsTypeSetting
from typing import cast, TYPE_CHECKING
import webbrowser
import traceback
import sys


if TYPE_CHECKING:
    from ...Environment import Environment


class _NewsPage(QWebEnginePage):
    def __init__(self, env: "Environment") -> None:
        super().__init__()

        self._env = env

    def _renderNewsPage(self) -> None:
        try:
            self.setHtml(GenerateNewsPage(self._env), QUrl("localhost"))
        except ModuleNotFoundError as ex:
            errorText = QCoreApplication.translate("NewsTab", "{{name}} not installed").replace("{{name}}", cast(str, ex.name)) + "<br>"
            errorText += QCoreApplication.translate("NewsTab", "You need the {{name}} Python package installed to use this feature").replace("{{name}}", cast(str, ex.name))
            self.setHtml(errorText, QUrl("localhost"))
        except Exception:
            errorText = "<h1>" + QCoreApplication.translate("NewsTab", "Error") + "</h1>"
            match self._env.settings.get("newsType"):
                case NewsTypeSetting.MINECRAFT:
                    errorText += "<p>" + QCoreApplication.translate("NewsTab", "Unable to render Minecraft News") + "<p>"
                case NewsTypeSetting.RSS:
                    url = self._env.settings.get("newsFeedURL")
                    link = f'<a href="{url}">{url}</a>'
                    errorText += "<p>" + QCoreApplication.translate("NewsTab", "Unable to render RSS feed {{url}}").replace("{{url}}", link) + "<p>"
            self.setHtml(errorText, QUrl("localhost"))
            print(traceback.format_exc(), file=sys.stderr)

    def updateNews(self) -> None:
        match self._env.settings.get("newsType"):
            case NewsTypeSetting.MINECRAFT | NewsTypeSetting.RSS:
                self._renderNewsPage()
            case NewsTypeSetting.WEBSITE:
                self.setUrl(QUrl(self._env.settings.get("newsURL")))

    def acceptNavigationRequest(self, url: QUrl, navigationType: QWebEnginePage.NavigationType, isMainFrame: bool) -> bool:
        if navigationType == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            if self._env.settings.get("newsFeedDefaultBrowser"):
                webbrowser.open(url.toString())
                return False
            else:
                return True
        else:
            return True


class NewsTab(QWebEngineView):
    def __init__(self, env: "Environment") -> None:
        super().__init__()

        self._env = env

        self._page = _NewsPage(env)
        self.setPage(self._page)

    def updateNews(self) -> None:
        self._page.updateNews()
