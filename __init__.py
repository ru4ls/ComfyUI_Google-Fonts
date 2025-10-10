# file: ComfyUI_Google-Font/__init__.py

import os
import shutil
from .nodes import GoogleFontNodeAdvanced

# --- Mappings for ComfyUI ---
NODE_CLASS_MAPPINGS = {
    "GoogleFontNodeAdvanced": GoogleFontNodeAdvanced
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GoogleFontNodeAdvanced": "Google Font Text Image"
}

# --- Standard Boilerplate ---
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']


# --- Setup Logic (runs once to help the user with the .env file) ---
p = os.path.dirname(os.path.realpath(__file__))
env_example_file = os.path.join(p, ".env.example")
env_file = os.path.join(p, ".env")

if not os.path.exists(env_file) and os.path.exists(env_example_file):
    print("GoogleFontNode: No .env file found. Copying .env.example to .env")
    shutil.copyfile(env_example_file, env_file)

print("------------------------------------------")
print("ComfyUI Google Font Node: Loaded.")
print("------------------------------------------")