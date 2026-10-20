"""Gera dark_mode.svg e light_mode.svg com a idade e as estatísticas do GitHub atualizadas."""

import datetime
import json
import os
import urllib.request
from html import escape
from pathlib import Path

USER = "BrunoMonfardini"
BIRTHDAY = datetime.date(2004, 8, 17)
BRASILIA = datetime.timezone(datetime.timedelta(hours=-3))  # sem horário de verão desde 2019
TODAY = datetime.datetime.now(BRASILIA).date()
ROOT = Path(__file__).parent

WIDTH = 60  # caracteres por linha do bloco de informações
INFO_X = 430
LINE_HEIGHT = 20

THEMES = {
    "dark_mode.svg": {"bg": "#161b22", "text": "#c9d1d9", "key": "#ffa657", "value": "#a5d6ff", "cc": "#616e7f"},
    "light_mode.svg": {"bg": "#f6f8fa", "text": "#24292f", "key": "#953800", "value": "#0a3069", "cc": "#c2cfde"},
}


def plural(n, singular, plural_form):
    return f"{n} {singular if n == 1 else plural_form}"


def age(birthday, today):
    years = today.year - birthday.year
    months = today.month - birthday.month
    days = today.day - birthday.day
    if days < 0:
        months -= 1
        last_month = today.replace(day=1) - datetime.timedelta(days=1)
        days += last_month.day
    if months < 0:
        years -= 1
        months += 12
    return ", ".join([plural(years, "ano", "anos"), plural(months, "mês", "meses"), plural(days, "dia", "dias")])


def request(url, body=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    with urllib.request.urlopen(urllib.request.Request(url, data, headers), timeout=30) as response:
        return json.load(response)


def github_stats():
    user = request(f"https://api.github.com/users/{USER}")
    repos = request(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
    stars = sum(repo["stargazers_count"] for repo in repos)

    commits = 0
    first_year = int(user["created_at"][:4])
    for year in range(first_year, TODAY.year + 1):
        query = """query($login: String!, $from: DateTime!, $to: DateTime!) {
          user(login: $login) { contributionsCollection(from: $from, to: $to) { totalCommitContributions } }
        }"""
        variables = {"login": USER, "from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"}
        result = request("https://api.github.com/graphql", {"query": query, "variables": variables})
        commits += result["data"]["user"]["contributionsCollection"]["totalCommitContributions"]

    return {
        "repos": user["public_repos"],
        "stars": stars,
        "followers": user["followers"],
        "commits": commits,
    }


def entry(key, value, width=WIDTH):
    """Linha `. Chave: ...... valor`, com pontos para alinhar o valor à direita."""
    keys = key.split(".")
    key_svg = '</tspan>.<tspan class="key">'.join(escape(k) for k in keys)
    dots = max(width - len(". ") - len(key) - len(": ") - len(" ") - len(value), 1)
    return (
        f'<tspan class="cc">. </tspan><tspan class="key">{key_svg}</tspan>:'
        f'<tspan class="cc"> {"." * dots} </tspan><tspan class="value">{escape(value)}</tspan>'
    )


def pair(key1, value1, key2, value2):
    left_width = WIDTH // 2
    right = entry(key2, value2, WIDTH - left_width - len(" | ") + len(". "))
    right = right.replace('<tspan class="cc">. </tspan>', "", 1)
    return f"{entry(key1, value1, left_width)} | {right}"


def header(title):
    return f"{escape(title)}</tspan> -{'—' * (WIDTH - len(title) - 5)}-—-"


def build_lines(stats):
    return [
        ("header", header("bruno@monfardini")),
        ("info", entry("OS", "Windows 11")),
        ("info", entry("Uptime", age(BIRTHDAY, TODAY))),
        ("info", entry("Host", "Itaú Unibanco")),
        ("info", entry("Kernel", "Analista Júnior · Desenvolvedor Front-end")),
        ("info", entry("IDE", "VS Code")),
        ("blank", None),
        ("info", entry("Languages.Programming", "TypeScript, JavaScript, Java")),
        ("info", entry("Languages.Computer", "HTML, CSS, SCSS, JSON, YAML")),
        ("info", entry("Frameworks", "Angular, Spring Boot")),
        ("blank", None),
        ("info", entry("Education.BCT", "Ciência e Tecnologia, UFABC (2026)")),
        ("info", entry("Education.BCC", "Ciência da Computação, UFABC (2027)")),
        ("empty", None),
        ("header", header("- Contact")),
        ("info", entry("Email.Principal", "vieira_bruno@outlook.com")),
        ("info", entry("Email.Secundário", "brunomlv2013@gmail.com")),
        ("info", entry("LinkedIn", "bruno-monfardini")),
        ("info", entry("Instagram", "@brunomlv_")),
        ("info", entry("Discord", "brunomlv")),
        ("empty", None),
        ("header", header("- GitHub Stats")),
        ("info", pair("Repos", str(stats["repos"]), "Stars", str(stats["stars"]))),
        ("info", pair("Commits", f"{stats['commits']:,}".replace(",", "."), "Followers", str(stats["followers"]))),
    ]


def render(theme, ascii_art, lines):
    rows = max(len(ascii_art), len(lines))
    height = 30 + (rows - 1) * LINE_HEIGHT + 20
    width = INFO_X + WIDTH * 10
    out = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" '
        f'width="{width}px" height="{height}px" font-size="16px">',
        "<style>",
        "@font-face {",
        "src: local('Consolas'), local('Consolas Bold');",
        "font-family: 'ConsolasFallback';",
        "font-display: swap;",
        "-webkit-size-adjust: 109%;",
        "size-adjust: 109%;",
        "}",
        f".key {{fill: {theme['key']};}}",
        f".value {{fill: {theme['value']};}}",
        f".cc {{fill: {theme['cc']};}}",
        "text, tspan {white-space: pre;}",
        "</style>",
        f'<rect width="{width}px" height="{height}px" fill="{theme["bg"]}" rx="15"/>',
        f'<text x="15" y="30" fill="{theme["text"]}" class="ascii">',
    ]
    for i, line in enumerate(ascii_art):
        out.append(f'<tspan x="15" y="{30 + i * LINE_HEIGHT}">{escape(line)}</tspan>')
    out.append("</text>")
    out.append(f'<text x="{INFO_X}" y="30" fill="{theme["text"]}">')
    for i, (kind, content) in enumerate(lines):
        y = 30 + i * LINE_HEIGHT
        if kind == "header":
            out.append(f'<tspan x="{INFO_X}" y="{y}">{content}')
        elif kind == "info":
            out.append(content.replace('<tspan class="cc">', f'<tspan x="{INFO_X}" y="{y}" class="cc">', 1))
        elif kind == "blank":
            out.append(f'<tspan x="{INFO_X}" y="{y}" class="cc">. </tspan>')
    out.append("</text>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    ascii_art = (ROOT / "ascii.txt").read_text(encoding="utf-8").rstrip("\n").split("\n")
    lines = build_lines(github_stats())
    for filename, theme in THEMES.items():
        (ROOT / filename).write_text(render(theme, ascii_art, lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
