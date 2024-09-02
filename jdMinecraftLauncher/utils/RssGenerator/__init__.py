from typing import Any, TYPE_CHECKING
import requests
import base64
import html
import os


if TYPE_CHECKING:
    from ...Environment import Environment


def _getFeedHtml(entry: dict[str, Any]) -> str:
    if entry["title_detail"]["type"] == "text/html":
        title = entry["title"]
    else:
        title = html.escape(entry["title"])

    if entry["summary_detail"]["type"] == "text/html":
        summary = entry["summary"]
    else:
        summary = html.escape(entry["summary"])

    html_code = '<div style="margin-top:16px">\n'
    html_code += f'<h3><a href="{entry["link"]}"">{title}</a></h3>\n'
    html_code += f'<p class="content">{summary}</p>\n'
    html_code += "</p></div>"

    return html_code


def _parseRssFeed(env: "Environment") -> str:
    import feedparser

    header = {"user-agent": f"jdMinecraftLauncher/{env.launcherVersion}"}
    r = requests.get(env.settings.get("newsFeedURL"), headers=header)
    feed = feedparser.parse(r.text)
    html_code = ""

    for entry in feed["entries"]:
        html_code += _getFeedHtml(entry)

    return html_code


def GenerateNewsPage(env: "Environment") -> str:
    with open(os.path.join(env.currentDir, "utils", "RssGenerator", "files", "News.html"), "r", encoding="utf-8") as f:
        template = f.read()

    with open(os.path.join(env.currentDir, "utils", "RssGenerator", "files", "Background.png"), "rb") as f:
        template = template.replace("{{BackgroundImage}}", base64.b64encode(f.read()).decode("utf-8"))

    with open(os.path.join(env.currentDir, "utils", "RssGenerator", "files", "Style.css"), "r", encoding="utf-8") as f:
        template = template.replace("{{Style}}", f.read())

    template = template.replace("{{ItemList}}", _parseRssFeed(env))

    return template
