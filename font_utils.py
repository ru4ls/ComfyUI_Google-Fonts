# file: ComfyUI_Google-Fonts/font_utils.py

import os, requests
from dotenv import load_dotenv

FONT_DATA_CACHE = None

def load_api_key():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
    return os.getenv("GOOGLE_FONTS_API_KEY")

def get_google_fonts_data(api_key):
    global FONT_DATA_CACHE
    if FONT_DATA_CACHE is not None: return FONT_DATA_CACHE
    print("GoogleFontNode: Fetching full font data from Google Fonts API...")
    api_url = f"https://www.googleapis.com/webfonts/v1/webfonts?sort=alpha&key={api_key or ''}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        FONT_DATA_CACHE = response.json().get('items', [])
        print(f"GoogleFontNode: Successfully loaded data for {len(FONT_DATA_CACHE)} fonts.")
        return FONT_DATA_CACHE
    except requests.exceptions.RequestException as e:
        print(f"GoogleFontNode: ERROR! Failed to fetch Google Fonts list: {e}")
        return []

# --- SIMPLE GOOGLE FONT HTML RENDERER ---
def create_simple_google_font_html(font_family, text, width, height, style_params):
    google_font_url_name = font_family.replace(' ', '+') 
    escaped_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
    
    font_size = style_params.get('font_size', 48)
    font_weight = style_params.get('font_weight', '400')
    font_style = style_params.get('font_style', 'normal')
    text_align = style_params.get('text_align', 'center')
    line_height = style_params.get('line_height', 1.2)
    text_transform = style_params.get('text_transform', 'none')
    text_color = style_params.get('text_color', '#000000')
    background_color = style_params.get('background_color', '#FFFFFF')
    
    # Construct the font URL with the specific weights and styles needed
    font_request_url = f"https://fonts.googleapis.com/css2?family={google_font_url_name}:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap"

    html_content = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <link href="{font_request_url}" rel="stylesheet">
    <style>
        html, body {{ height: 100%; width: 100%; margin: 0; padding: 0; box-sizing: border-box; background-color: {background_color}; }}
        body {{ 
            display: flex; 
            justify-content: {'center' if text_align == 'center' else 'flex-start' if text_align == 'left' else 'flex-end'};
            align-items: center; 
        }}
        .text-container {{
            font-family: '{font_family}', sans-serif;
            font-size: {font_size}px;
            font-weight: {font_weight};
            font-style: {font_style};
            color: {text_color};
            text-align: {text_align};
            line-height: {line_height};
            text-transform: {text_transform};
            width: 100%;
            padding: 20px;
            box-sizing: border-box;
        }}
    </style></head><body><div class="text-container">{escaped_text}</div></body></html>
    """
    return html_content