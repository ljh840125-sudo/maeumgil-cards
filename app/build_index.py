"""src.html(Claude 아티팩트와 같은 내용) → index.html(넷리파이용 완성 문서)."""
import os
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "src.html"), encoding="utf-8").read()
head = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<meta name="theme-color" content="#2f6f5e">'
        '<link rel="manifest" href="manifest.webmanifest">'
        '<link rel="icon" href="icon.svg" type="image/svg+xml">'
        '<link rel="apple-touch-icon" href="icon-192.png">'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
        'body{margin:0;font:14px system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>'
        '</head><body>')
open(os.path.join(here, "index.html"), "w", encoding="utf-8").write(head + src + "</body></html>")
print("index.html written")
