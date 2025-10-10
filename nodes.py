# file: ComfyUI_Google-Font/nodes.py

import os
import torch
import numpy as np
from PIL import Image, ImageOps
from html2image import Html2Image
import folder_paths
import time

from .font_utils import load_api_key, get_google_fonts_data, create_advanced_font_html

API_KEY = load_api_key()
FONT_DATA = get_google_fonts_data(API_KEY)
FONT_FAMILIES = sorted([font['family'] for font in FONT_DATA]) if FONT_DATA else ["Arial"]
STANDARD_CHAR_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz\n0123456789\n!@#$%^&*()_+-=[]{}|;"

class GoogleFontNodeAdvanced:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "font_family": (FONT_FAMILIES,),
                "output_mode": (["Custom Text", "Standard Character Set"],),
                "text": ("STRING", {"multiline": True, "default": "Your Text Here, its support multiple lines!"}),
                "width": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "height": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8}),
                "font_size": ("INT", {"default": 120, "min": 8, "max": 1024, "step": 1}),
                "font_weight": (["100", "200", "300", "regular", "400", "500", "600", "700", "800", "900"], {"default": "regular"}),
                "font_style": (["normal", "italic"],),
                "text_align": (["center", "left", "right"],),
                "line_height": ("FLOAT", {"default": 1.2, "min": 0.1, "max": 5.0, "step": 0.1}),
                "text_transform": (["none", "uppercase", "lowercase", "capitalize"],),
                "text_color": ("STRING", {"default": "#000000"}),
                "background_color": ("STRING", {"default": "#FFFFFF"}),
                "transparent_background": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "generate_image_advanced"
    CATEGORY = "Ru4ls/Google Fonts"

    def generate_image_advanced(self, font_family, output_mode, text, width, height, font_size, font_weight, font_style, text_align, line_height, text_transform, text_color, background_color, transparent_background):
        
        render_text = text if output_mode == "Custom Text" else STANDARD_CHAR_SET
        final_bg_color = "transparent" if transparent_background else background_color
            
        selected_font_info = next((font for font in FONT_DATA if font['family'] == font_family), None)
        if not selected_font_info: raise Exception(f"Font '{font_family}' not found.")
        if font_weight == "regular": font_weight = "400"
        available_variants = selected_font_info.get('variants', ['400']); target_variant = f"{font_weight}italic" if font_style == 'italic' else font_weight
        if "regular" in available_variants: available_variants = [v.replace("regular", "400") for v in available_variants]
        if "italic" in available_variants: available_variants = [v.replace("italic", "400italic") for v in available_variants]
        if target_variant not in available_variants:
             print(f"GoogleFontNode: Warning! Variant '{target_variant}' not available. Falling back."); fallback = available_variants[0]
             font_style = 'italic' if 'italic' in fallback else 'normal'; font_weight = fallback.replace('italic', '') or '400'

        output_dir = folder_paths.get_temp_directory()
        hti = Html2Image(output_path=output_dir)
        
        html_str = create_advanced_font_html(font_family, font_weight, font_style, render_text, width, height, font_size, text_color, final_bg_color, text_align, line_height, text_transform)
        
        safe_filename = "".join(c for c in font_family if c.isalnum()).rstrip()
        output_filename = f"GoogleFontAdv_{safe_filename}_{int(time.time())}.png"

        hti.screenshot(html_str=html_str, save_as=output_filename, size=(width, height))
        image_path = os.path.join(output_dir, output_filename)
        
        i = Image.open(image_path)
        i = ImageOps.exif_transpose(i)
        
        if i.mode != 'RGBA': i = i.convert('RGBA')

        image_rgb = Image.merge("RGB", i.split()[0:3])
        mask = i.split()[3]
        
        image_tensor = np.array(image_rgb).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_tensor)[None,]
        
        mask_tensor = np.array(mask).astype(np.float32) / 255.0
        mask_tensor = torch.from_numpy(mask_tensor)
        
        return (image_tensor, mask_tensor.unsqueeze(0))