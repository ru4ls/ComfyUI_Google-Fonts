# file: ComfyUI_Google-Fonts/__init__.py

import os
import shutil
import folder_paths

# Now, we can safely import our nodes
from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# --- Setup Logic (runs once to help the user with the .env file) ---
p = os.path.dirname(os.path.realpath(__file__))
env_example_file = os.path.join(p, ".env.example")
env_file = os.path.join(p, ".env")

if not os.path.exists(env_file) and os.path.exists(env_example_file):
    print("GoogleFontNode: No .env file found. Copying .env.example to .env")
    shutil.copyfile(env_example_file, env_file)

print("------------------------------------------")
print("Ru4ls Google Font Node: Loaded.")
print("------------------------------------------")