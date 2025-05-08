import os
import re

BASE_DIR = "app"
IGNORE_DIRS = ["__pycache__", ".venv", "tests"]
APP_MODULES = {"models", "dao", "database", "services", "routes", "config"}

def is_target_module(module):
    # Only match top-level modules that are part of your app
    top_level = module.split('.')[0]
    return top_level in APP_MODULES

def fix_imports(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Rewrite from X import ... → from app.X import ...
    content = re.sub(
        r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import",
        lambda m: f"from app.{m.group(1)} import" if is_target_module(m.group(1)) and not m.group(1).startswith("app.") else m.group(0),
        content
    )

    # Rewrite import X → import app.X
    content = re.sub(
        r"\bimport\s+([a-zA-Z_][a-zA-Z0-9_\.]*)",
        lambda m: f"import app.{m.group(1)}" if is_target_module(m.group(1)) and not m.group(1).startswith("app.") else m.group(0),
        content
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def traverse_and_fix(folder):
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                fix_imports(file_path)

if __name__ == "__main__":
    traverse_and_fix(BASE_DIR)
    print("✅ All safe app-relative imports rewritten to absolute form.")
