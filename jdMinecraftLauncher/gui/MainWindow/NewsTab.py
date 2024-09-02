from PyQt6.QtWebEngineWidgets import QWebEngineView
from ...utils.RssGenerator import GenerateNewsPage
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, QCoreApplication
from ...Constants import NewsTypeSetting
from typing import TYPE_CHECKING
import webbrowser
import traceback
import sys


if TYPE_CHECKING:
    from ...Environment import Environment


class _NewsPage(QWebEnginePage):
    def __init__(self, env: "Environment") -> None:
        super().__init__()

        self._env = env

    def _renderRssFeed(self) -> None:
        try:
            self.setHtml(GenerateNewsPage(self._env), QUrl("localhost"))
        except ModuleNotFoundError as ex:
            errorText = QCoreApplication.translate("NewsTab", "{{name}} not installed").replace("{{name}}", ex.name) + "<br>"
            errorText += QCoreApplication.translate("NewsTab", "You need the {{name}} Python package installed to use this feature").replace("{{name}}", ex.name)
            self.setHtml(errorText, QUrl("localhost"))
        except Exception:
            url = self._env.settings.get("newsFeedURL")
            link = f'<a href="{url}">{url}</a>'
            errorText = "<h1>" + QCoreApplication.translate("NewsTab", "Error") + "</h1>"
            errorText += "<p>" + QCoreApplication.translate("NewsTab", "Unable to render RSS feed {{url}}").replace("{{url}}", link) +  "<p>"
            self.setHtml(errorText, QUrl("localhost"))
            print(traceback.format_exc(), file=sys.stderr)

    def updateNews(self) -> None:
         match self._env.settings.get("newsType"):
            case NewsTypeSetting.RSS:
                self._renderRssFeed()
            case NewsTypeSetting.WEBSITE:
                self.setUrl(QUrl(self._env.settings.get("newsURL")))

    def acceptNavigationRequest(self, url: QUrl, navigationType: QWebEnginePage.NavigationType, isMainFrame: bool) -> None:
        if navigationType == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            if self._env.settings.get("newsType") == NewsTypeSetting.RSS and self._env.settings.get("newsFeedDefaultBrowser"):
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
