"""Gera dark_mode.svg e light_mode.svg com a idade atualizada."""

import datetime
from html import escape
from pathlib import Path

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


def entry(key, value):
    """Linha `. Chave: ...... valor`, com pontos para alinhar o valor à direita."""
    key_svg = '</tspan>.<tspan class="key">'.join(escape(k) for k in key.split("."))
    dots = max(WIDTH - len(". ") - len(key) - len(": ") - len(" ") - len(value), 1)
    return (
        f'<tspan class="cc">. </tspan><tspan class="key">{key_svg}</tspan>:'
        f'<tspan class="cc"> {"." * dots} </tspan><tspan class="value">{escape(value)}</tspan>'
    )


def header(title):
    return f"{escape(title)}</tspan> -{'—' * (WIDTH - len(title) - 5)}-—-"


def build_lines():
    return [
        ("header", header("bruno@monfardini")),
        ("info", entry("OS", "Windows 11")),
        ("info", entry("Uptime", age(BIRTHDAY, TODAY))),
        ("info", entry("Host", "Itaú Unibanco")),
        ("info", entry("Kernel.Cargo", "Analista Júnior")),
        ("info", entry("Kernel.Área", "Desenvolvimento Front-end")),
        ("info", entry("Locale", "Santo André, SP")),
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
    ]


def render(theme, ascii_art, lines):
    rows = max(len(ascii_art), len(lines))
    offset = (rows - len(lines)) // 2  # centraliza as informações na altura do rosto
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
    for i, (kind, content) in enumerate(lines, start=offset):
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
    lines = build_lines()
    for filename, theme in THEMES.items():
        (ROOT / filename).write_text(render(theme, ascii_art, lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
