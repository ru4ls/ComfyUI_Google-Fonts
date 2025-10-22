# file: ComfyUI_Google-Fonts/nodes.py

import os, torch, numpy as np
from PIL import Image, ImageOps
import folder_paths, time
from playwright.async_api import async_playwright

from .font_utils import (
    load_api_key, get_google_fonts_data, 
    create_playwright_google_font_html
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
                # Font selection and styling
                "font_family": (FONT_FAMILIES,),
                "font_size": ("INT", {"default": 48, "min": 1, "max": 1024, "step": 1}),
                "font_weight": (["100", "200", "300", "400", "500", "600", "700", "800", "900"], {"default": "400"}),
                "font_style": (["normal", "italic"],),
                # Text content and formatting
                "output_mode": (["Custom Text", "Standard Character Set"],),
                "text": ("STRING", {"multiline": True, "default": "Sample Text"}),
                "text_align": (["center", "left", "right"],),
                "line_height": ("FLOAT", {"default": 1.2, "min": 0.1, "max": 5.0, "step": 0.1}),
                "text_transform": (["none", "uppercase", "lowercase", "capitalize"],),
                "text_color": ("STRING", {"default": "#000000"}),
                # Dimension mode and settings
                "dimension_mode": (["Auto", "Define Manually"], {"default": "Auto"}),
                "width": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8}),
                "height": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8}),
                "padding_top": ("INT", {"default": 20, "min": 0, "max": 200, "step": 1}),
                "padding_right": ("INT", {"default": 20, "min": 0, "max": 200, "step": 1}),
                "padding_bottom": ("INT", {"default": 20, "min": 0, "max": 200, "step": 1}),
                "padding_left": ("INT", {"default": 20, "min": 0, "max": 200, "step": 1}),
                # Background and transparency
                "background_color": ("STRING", {"default": "#FFFFFF"}),
                "transparent_background": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK",)
    FUNCTION = "render_text"
    CATEGORY = "Ru4ls/Google Fonts"
    
    async def render_text(self, font_family, output_mode, text, dimension_mode, width, height, font_size, font_weight, font_style, 
                    text_align, line_height, text_transform, text_color, background_color, transparent_background,
                    padding_top, padding_right, padding_bottom, padding_left):
        
        # Prepare text based on output mode
        render_text = text if output_mode == "Custom Text" else STANDARD_CHAR_SET
        
        style_params = {
            'font_size': font_size,
            'font_weight': font_weight,
            'font_style': font_style,
            'text_align': text_align,
            'line_height': line_height,
            'text_transform': text_transform,
            'text_color': text_color,
            'background_color': background_color if not transparent_background else 'transparent',
            'padding_top': max(1, padding_top),
            'padding_right': max(1, padding_right),
            'padding_bottom': max(1, padding_bottom),
            'padding_left': max(1, padding_left)
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
        
        # Render image using Playwright
        output_dir = folder_paths.get_temp_directory()
        
        # Determine dimensions based on mode
        if dimension_mode == "Auto":
            render_width = None
            render_height = None
        else:
            render_width = width
            render_height = height
        
        # Create HTML content optimized for Playwright with width/height for text wrapping
        html_str = create_playwright_google_font_html(font_family, render_text, style_params, render_width, render_height)
        
        output_filename = f"google_font_{int(time.time())}.png"
        image_path = os.path.join(output_dir, output_filename)
        
        # Use Playwright to render HTML to image
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # For auto-sizing mode, use a large initial viewport to prevent text wrapping before measurement
            if dimension_mode == "Auto":
                await page.set_viewport_size({"width": 8192, "height": 8192})  # Large viewport to prevent wrapping
            
            # Set the HTML content
            await page.set_content(html_str)
            
            # Wait for fonts to load
            await page.wait_for_timeout(1000)  # Wait for font loading
            
            # Get the bounding box of the text container to calculate actual dimensions
            bbox = await page.locator('.text-container').bounding_box()
            
            # Determine dimensions based on the selected mode
            if dimension_mode == "Auto":
                # Auto-size based on content
                if bbox:
                    # Add individual padding values for auto-sizing (use internally adjusted values)
                    actual_padding_left = max(1, padding_left)
                    actual_padding_right = max(1, padding_right) 
                    actual_padding_top = max(1, padding_top)
                    actual_padding_bottom = max(1, padding_bottom)
                    
                    calculated_width = int(bbox['width']) + actual_padding_left + actual_padding_right
                    calculated_height = int(bbox['height']) + actual_padding_top + actual_padding_bottom
                    final_width = min(max(calculated_width, 64), 8192)  # Keep within bounds
                    final_height = min(max(calculated_height, 64), 8192)  # Keep within bounds
                else:
                    # Fallback if bbox not available
                    final_width = 512
                    final_height = 512
            else:
                # Use user-defined dimensions
                final_width = width
                final_height = height
            
            # Set viewport size to calculated dimensions
            await page.set_viewport_size({"width": final_width, "height": final_height})
            
            # Take screenshot - ensure transparent background when needed
            await page.screenshot(path=image_path, type='png', omit_background=transparent_background)
            
            await browser.close()
        
        # Process the output image
        i = Image.open(image_path)
        i = ImageOps.exif_transpose(i)
        
        # Ensure it's RGBA for transparency
        if i.mode != 'RGBA':
            i = i.convert('RGBA')

        # Split into RGB image and alpha mask
        image_rgb = Image.merge("RGB", i.split()[0:3])
        alpha_channel = i.split()[3]  # Get the alpha channel (mask)
        
        # Convert to ComfyUI tensors
        image_tensor = np.array(image_rgb).astype(np.float32) / 255.0
        mask_np = np.array(alpha_channel).astype(np.float32) / 255.0
        
        # Ensure mask is 2D (H, W) as expected by ComfyUI - some operations may add extra dims
        if mask_np.ndim > 2:
            # If it's 3D, squeeze the channel dimension to make it 2D
            if mask_np.shape[-1] == 1:
                mask_np = mask_np.squeeze(-1)  # Remove singleton channel dimension
            elif mask_np.shape[0] == 1:
                mask_np = mask_np.squeeze(0)   # Remove singleton batch dimension
            else:
                # If multiple channels somehow, take just the first one
                mask_np = mask_np[..., 0] if mask_np.ndim == 3 else mask_np
        
        # The mask should be (H, W) shape now, then unsqueeze to (1, H, W)
        mask_tensor = torch.from_numpy(mask_np).unsqueeze(0)
        
        return (torch.from_numpy(image_tensor)[None,], mask_tensor)

# ====================================================================================================
# NODE MAPPINGS
# ====================================================================================================
NODE_CLASS_MAPPINGS = {
    "GoogleFontTextNode": GoogleFontTextNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "GoogleFontTextNode": "Google Font Text Image",
}