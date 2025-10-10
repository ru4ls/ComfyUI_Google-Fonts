# file: ComfyUI_Google-Font/font_utils.py

import os
import requests
from dotenv import load_dotenv

FONT_DATA_CACHE = None

def load_api_key():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
    return os.getenv("GOOGLE_FONTS_API_KEY")

def get_google_fonts_data(api_key, sort_by="alpha"):
    global FONT_DATA_CACHE
    if FONT_DATA_CACHE is not None:
        return FONT_DATA_CACHE
    print("GoogleFontNode: Fetching full font data from Google Fonts API...")
    api_url = f"https://www.googleapis.com/webfonts/v1/webfonts?sort={sort_by}&key={api_key or ''}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        FONT_DATA_CACHE = response.json().get('items', [])
        print(f"GoogleFontNode: Successfully loaded data for {len(FONT_DATA_CACHE)} fonts.")
        return FONT_DATA_CACHE
    except requests.exceptions.RequestException as e:
        print(f"GoogleFontNode: ERROR! Failed to fetch Google Fonts list: {e}")
        return []

# --- HTML GENERATION FUNCTION ---
def create_advanced_font_html(font_family, font_weight, font_style, text, width, height, font_size, text_color, bg_color, text_align, line_height, text_transform):
    """
    Generates a complete HTML string with advanced typographic controls.
    """
    google_font_url_name = font_family.replace(' ', '+')
    escaped_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')

    justify_content_map = {"left": "flex-start", "center": "center", "right": "flex-end"}
    css_justify_content = justify_content_map.get(text_align, "center")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family={google_font_url_name}:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
        <style>
            body {{
                margin: 0; padding: 20px;
                font-family: '{font_family}', sans-serif;
                font-size: {font_size}px;
                font-weight: {font_weight};
                font-style: {font_style};
                color: {text_color};
                background-color: {bg_color};
                box-sizing: border-box;
                display: flex;
                justify-content: {css_justify_content};
                align-items: center;
                width: {width}px;
                height: {height}px;
            }}
            .text-wrapper {{
                text-align: {text_align};
                word-wrap: break-word;
                word-break: break-word;
                max-width: 100%;
                /* --- NEW PROPERTIES --- */
                line-height: {line_height};
                text-transform: {text_transform};
            }}
        </style>
    </head>
    <body><div class="text-wrapper">{escaped_text}</div></body>
    </html>
    """
    return html_content