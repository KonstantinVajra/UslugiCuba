# compile_translations.py
import os
import polib

BASE_DIR = "locales"

for lang in os.listdir(BASE_DIR):
    po_path = os.path.join(BASE_DIR, lang, "LC_MESSAGES", "bot.po")
    mo_path = os.path.join(BASE_DIR, lang, "LC_MESSAGES", "bot.mo")

    if os.path.exists(po_path):
        po = polib.pofile(po_path)
        po.save_as_mofile(mo_path)
        print(f"Compiled: {mo_path}")
