#!/usr/bin/env python3
"""
Script para generar el PDF del TFI usando Playwright.
Convierte el borrador Markdown a HTML con formato académico y lo renderiza a PDF.
"""

import asyncio
import re
from pathlib import Path

import markdown
from playwright.async_api import async_playwright

# Rutas
RUTA_PROYECTO = Path(__file__).parent
RUTA_BORRADOR = RUTA_PROYECTO / "BORRADOR_PDF.md"
RUTA_SALIDA = RUTA_PROYECTO / "TFI_BDI_C2_G03-G12_Fernandez-DiLorenzo-Gallardo.pdf"

CSS = """
        @page {
            size: A4;
            margin: 2.54cm;
        }

        body {
            font-family: 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #000;
            margin: 0;
            padding: 0;
        }

        .portada {
            text-align: center;
            page-break-after: always;
            padding-top: 3cm;
        }

        .portada h1 {
            font-size: 20pt;
            font-weight: bold;
            margin-bottom: 0.5cm;
            text-transform: uppercase;
        }

        .portada h2 {
            font-size: 14pt;
            font-weight: normal;
            margin-bottom: 3cm;
        }

        .portada .datos {
            font-size: 12pt;
            line-height: 2.5;
            margin-top: 2cm;
        }

        .portada .datos p {
            margin: 0;
        }

        h1 {
            font-size: 12pt;
            font-weight: bold;
            text-transform: uppercase;
            margin-top: 1.5cm;
            margin-bottom: 0.5cm;
            page-break-after: avoid;
        }

        h2 {
            font-size: 12pt;
            font-weight: bold;
            margin-top: 1cm;
            margin-bottom: 0.5cm;
            page-break-after: avoid;
        }

        h3 {
            font-size: 11pt;
            font-weight: bold;
            margin-top: 0.8cm;
            margin-bottom: 0.4cm;
            page-break-after: avoid;
        }

        h4 {
            font-size: 11pt;
            font-weight: bold;
            margin-top: 0.6cm;
            margin-bottom: 0.3cm;
            page-break-after: avoid;
        }

        p {
            margin-bottom: 0.5cm;
            text-align: justify;
        }

        ul, ol {
            margin-bottom: 0.5cm;
            padding-left: 1cm;
        }

        li {
            margin-bottom: 0.2cm;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 0.5cm 0;
            font-size: 10pt;
            page-break-inside: avoid;
        }

        th, td {
            border: 1px solid #000;
            padding: 0.3cm;
            text-align: left;
            vertical-align: top;
        }

        th {
            background-color: #f0f0f0;
            font-weight: bold;
        }

        code {
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            background-color: #f5f5f5;
            padding: 0.1cm 0.3cm;
        }

        pre {
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            background-color: #f5f5f5;
            padding: 0.5cm;
            border: 1px solid #ddd;
            overflow-x: auto;
            page-break-inside: avoid;
        }

        pre code {
            background-color: transparent;
            padding: 0;
        }

        .imagen {
            text-align: center;
            margin: 0.5cm 0;
            page-break-inside: avoid;
        }

        .imagen img {
            max-width: 100%;
            max-height: 20cm;
            width: auto;
            height: auto;
            border: 1px solid #ddd;
        }

        .imagen-caption {
            font-size: 9pt;
            font-style: italic;
            margin-top: 0.2cm;
        }

        hr {
            border: none;
            border-top: 1px solid #000;
            margin: 1cm 0;
        }

        strong {
            font-weight: bold;
        }

        em {
            font-style: italic;
        }
"""


def _portada(lineas):
    """Genera el HTML de la portada a partir de las primeras líneas del Markdown."""
    html = '<div class="portada">\n'
    for linea in lineas:
        linea = linea.rstrip()
        if linea.startswith('# '):
            html += f'<h1>{linea[2:].strip()}</h1>\n'
        elif linea.startswith('## '):
            html += f'<h2>{linea[3:].strip()}</h2>\n'
        elif linea.startswith('**') and ':' in linea:
            clave, valor = linea.split(':', 1)
            html += f'<p><strong>{clave.strip("* ")}:</strong> {valor.strip()}</p>\n'
        elif linea.startswith('- '):
            html += f'<p>{linea[2:].strip()}</p>\n'
    html += '</div>\n'
    return html


def _normalizar_encabezados(html):
    """Baja un nivel los encabezados para respetar la jerarquía del CSS."""
    html = re.sub(r'<h([1-6])', lambda m: f'<h{max(1, int(m.group(1)) - 1)}', html)
    html = re.sub(r'</h([1-6])>', lambda m: f'</h{max(1, int(m.group(1)) - 1)}>', html)
    return html


def _envolver_imagenes(html):
    """Convierte <p><img ...></p> en figuras con epígrafe y ruta absoluta."""

    def reemplazo(m):
        alt, src = m.group(1), m.group(2)
        ruta = Path(src)
        if not ruta.is_absolute():
            ruta = (RUTA_PROYECTO / ruta)
        if not ruta.exists():
            return f'<p>[Imagen no encontrada: {src}]</p>'
        return (
            '<div class="imagen">'
            f'<img src="{ruta.resolve().as_uri()}" alt="{alt}">'
            f'<div class="imagen-caption">{alt}</div>'
            '</div>'
        )

    patron = r'<p>\s*<img\s+alt="([^"]*)"\s+src="([^"]+)"\s*/?>\s*</p>'
    return re.sub(patron, reemplazo, html)


def procesar_markdown():
    """Procesa el Markdown y genera HTML con formato académico."""
    texto = RUTA_BORRADOR.read_text(encoding='utf-8')
    lineas = texto.splitlines()

    # Separar la portada (todo lo anterior al primer separador horizontal)
    try:
        corte = lineas.index('---')
    except ValueError:
        corte = 0

    portada = _portada(lineas[:corte])
    cuerpo_md = '\n'.join(lineas[corte + 1:])

    cuerpo = markdown.markdown(
        cuerpo_md,
        extensions=['tables', 'fenced_code', 'sane_lists'],
    )
    cuerpo = _normalizar_encabezados(cuerpo)
    cuerpo = _envolver_imagenes(cuerpo)

    return (
        '<!DOCTYPE html>\n<html lang="es">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<title>TFI - Bases de Datos I</title>\n'
        f'<style>{CSS}</style>\n'
        '</head>\n<body>\n'
        f'{portada}\n{cuerpo}\n'
        '</body>\n</html>'
    )


async def generar_pdf():
    """Genera el PDF usando Playwright."""
    html = procesar_markdown()

    # Guardar HTML temporal
    ruta_html = RUTA_PROYECTO / "temporal.html"
    ruta_html.write_text(html, encoding='utf-8')

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto(ruta_html.resolve().as_uri())

        # Esperar a que todas las imágenes estén decodificadas antes de imprimir
        await page.wait_for_load_state("networkidle")
        await page.evaluate(
            "() => Promise.all(Array.from(document.images).map(img => "
            "img.complete ? Promise.resolve() : new Promise(res => {"
            "img.onload = res; img.onerror = res; })))"
        )

        # Generar PDF con alta calidad
        await page.pdf(
            path=str(RUTA_SALIDA),
            format='A4',
            print_background=True,
            margin={
                'top': '2.54cm',
                'right': '2.54cm',
                'bottom': '2.54cm',
                'left': '2.54cm',
            },
        )

        await browser.close()

    # Eliminar HTML temporal
    ruta_html.unlink()

    print(f"PDF generado: {RUTA_SALIDA}")


if __name__ == "__main__":
    asyncio.run(generar_pdf())
