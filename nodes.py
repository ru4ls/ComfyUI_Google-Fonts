# file: ComfyUI_Google-Fonts/nodes.py

import os, torch, numpy as np
from PIL import Image, ImageOps
from html2image import Html2Image
import folder_paths, time

from .font_utils import (
    load_api_key, get_google_fonts_data, 
    create_simple_google_font_html
)

# --- Load Data on Startup ---
API_KEY = load_api_key()
FONT_DATA = get_google_fonts_data(API_KEY)
FONT_FAMILIES = sorted([font['family'] for font in FONT_DATA]) if FONT_DATA else ["Arial"]
STANDARD_CHAR_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz\n0123456789\n!@#$%^&*()_+-=[]{}|;"

# ====================================================================================================
# NODE 1: Google Font Text Image Node
# ====================================================================================================
class GoogleFontTextNode:
    """
    Renders text using Google Fonts and outputs both an IMAGE and a MASK.
    """
    @classmethod
    def INPUT_TYPES(s):
        return { 
            "required": {
                "font_family": (FONT_FAMILIES,),
                "output_mode": (["Custom Text", "Standard Character Set"],),
                "text": ("STRING", {"multiline": True, "default": "Sample Text"}),
                "width": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8}),
                "height": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8}),
                "font_size": ("INT", {"default": 48, "min": 1, "max": 1024, "step": 1}),
                "font_weight": (["100", "200", "300", "400", "500", "600", "700", "800", "900"], {"default": "400"}),
                "font_style": (["normal", "italic"],),
                "text_align": (["center", "left", "right"],),
                "line_height": ("FLOAT", {"default": 1.2, "min": 0.1, "max": 5.0, "step": 0.1}),
                "text_transform": (["none", "uppercase", "lowercase", "capitalize"],),
                "text_color": ("STRING", {"default": "#000000"}),
                "background_color": ("STRING", {"default": "#FFFFFF"}),
                "transparent_background": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK",)
    FUNCTION = "render_text"
    CATEGORY = "Ru4ls/Google Fonts"
    
    def render_text(self, font_family, output_mode, text, width, height, font_size, font_weight, font_style, 
                    text_align, line_height, text_transform, text_color, background_color, transparent_background):
        
        # Prepare text based on output mode
        render_text = text if output_mode == "Custom Text" else STANDARD_CHAR_SET
        
        # Prepare style parameters
        style_params = {
            'font_size': font_size,
            'font_weight': font_weight,
            'font_style': font_style,
            'text_align': text_align,
            'line_height': line_height,
            'text_transform': text_transform,
            'text_color': text_color,
            'background_color': 'transparent' if transparent_background else background_color
        }
        
        # Validate font variant
        selected_font_info = next((font for font in FONT_DATA if font['family'] == font_family), None)
        if selected_font_info:
            weight = font_weight
            style = font_style
            available_variants = selected_font_info.get('variants', ['400'])
            target_variant = f"{weight}italic" if style == 'italic' else weight
            
            # Normalize variant names for comparison
            if "regular" in available_variants: available_variants = [v.replace("regular", "400") for v in available_variants]
            if "italic" in available_variants: available_variants = [v.replace("italic", "400italic") for v in available_variants]
            
            if target_variant not in available_variants:
                 print(f"GoogleFontNode: Warning! Variant '{target_variant}' not available for '{font_family}'. Falling back.")
                 fallback = available_variants[0]
                 font_style = 'italic' if 'italic' in fallback else 'normal'
                 font_weight = fallback.replace('italic', '') or '400'
                 style_params['font_style'] = font_style
                 style_params['font_weight'] = font_weight
        
        # Render image using the backend engine
        output_dir = folder_paths.get_temp_directory()
        hti = Html2Image(output_path=output_dir)
        
        html_str = create_simple_google_font_html(font_family, render_text, width, height, style_params)
        
        output_filename = f"google_font_{int(time.time())}.png"
        hti.screenshot(html_str=html_str, save_as=output_filename, size=(width, height))
        image_path = os.path.join(output_dir, output_filename)
        
        # Process the output image
        i = Image.open(image_path)
        i = ImageOps.exif_transpose(i)
        
        # Ensure it's RGBA for transparency
        if i.mode != 'RGBA':
            i = i.convert('RGBA')

        # Split into RGB image and alpha mask
        image_rgb = Image.merge("RGB", i.split()[0:3])
        mask = i.split()[3]
        
        # Convert to ComfyUI tensors
        image_tensor = np.array(image_rgb).astype(np.float32) / 255.0
        mask_tensor = np.array(mask).astype(np.float32) / 255.0
        
        return (torch.from_numpy(image_tensor)[None,], torch.from_numpy(mask_tensor).unsqueeze(0))

# ====================================================================================================
# NODE MAPPINGS
# ====================================================================================================
NODE_CLASS_MAPPINGS = {
    "GoogleFontTextNode": GoogleFontTextNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "GoogleFontTextNode": "Google Font Text Image",
}