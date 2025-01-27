from typing import TypedDict, TYPE_CHECKING
from ...Constants import NewsTypeSetting
import minecraft_launcher_lib
import requests
import base64
import html
import os


if TYPE_CHECKING:
    from ...Environment import Environment


class _NewsEntry(TypedDict):
    title: str
    summary: str
    link: str


def _newsListToHtml(newsList: list[_NewsEntry]) -> str:
    if len(newsList) == 0:
        return "<div>No News found</div>"

    html_code = ""

    for currentNews in newsList:
        html_code += '<div style="margin-top:16px">\n'
        html_code += f'<h3><a href="{currentNews["link"]}"">{currentNews["title"]}</a></h3>\n'
        html_code += f'<p class="content">{currentNews["summary"]}</p>\n'
        html_code += "</p></div>"

    return html_code


def _getMinecraftNews() -> list[_NewsEntry]:
    minecraftNews = minecraft_launcher_lib.news.get_minecraft_news()
    newsList = []

    for currentNews in minecraftNews["entries"]:
        newsList.append(_NewsEntry({
            "title": currentNews["title"],
            "summary": currentNews["text"],
            "link": currentNews["readMoreLink"],
        }))

    return newsList


def _parseRssFeed(env: "Environment") -> list[_NewsEntry]:
    import feedparser  # type:ignore[import-untyped]

    header = {"user-agent": f"jdMinecraftLauncher/{env.launcherVersion}"}
    r = requests.get(env.settings.get("newsFeedURL"), headers=header)
    feed = feedparser.parse(r.text)

    newsList = []

    for entry in feed["entries"]:
        if entry["title_detail"]["type"] == "text/html":
            title = entry["title"]
        else:
            title = html.escape(entry["title"])

        if entry["summary_detail"]["type"] == "text/html":
            summary = entry["summary"]
        else:
            summary = html.escape(entry["summary"])

        newsList.append(_NewsEntry({
            "title": title,
            "summary": summary,
            "link": entry["link"],
        }))

    return newsList


def GenerateNewsPage(env: "Environment") -> str:
    with open(os.path.join(env.currentDir, "utils", "NewsGenerator", "files", "News.html"), "r", encoding="utf-8") as f:
        template = f.read()

    with open(os.path.join(env.currentDir, "utils", "NewsGenerator", "files", "Background.png"), "rb") as f:
        template = template.replace("{{BackgroundImage}}", base64.b64encode(f.read()).decode("utf-8"))

    with open(os.path.join(env.currentDir, "utils", "NewsGenerator", "files", "Style.css"), "r", encoding="utf-8") as f:
        template = template.replace("{{Style}}", f.read())

    match env.settings.get("newsType"):
        case NewsTypeSetting.MINECRAFT:
            template = template.replace("{{ItemList}}", _newsListToHtml(_getMinecraftNews()))
        case NewsTypeSetting.RSS:
            template = template.replace("{{ItemList}}", _newsListToHtml(_parseRssFeed(env)))

    return template
