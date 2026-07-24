from pathlib import Path
import json
import shutil
import os

ROOT = Path(".").resolve()

PLAN_FILE = ROOT / "SERVICE_RELOCATION_PLAN.json"
BACKUP_DIR = ROOT / "architecture_backup"


# -----------------------------
# SAFETY INIT
# -----------------------------

def ensure_backup():
    BACKUP_DIR.mkdir(exist_ok=True)
    print(f"📦 Backup directory ready: {BACKUP_DIR}")


def backup_file(src: Path):
    if src.exists():
        target = BACKUP_DIR / src.name
        shutil.copy2(src, target)


# -----------------------------
# IMPORT FIXER (basic safe rewrite)
# -----------------------------

def fix_imports(file_path: Path, old_module: str, new_module: str):
    if not file_path.exists():
        return

    text = file_path.read_text()

    updated = text.replace(old_module, new_module)

    file_path.write_text(updated)


# -----------------------------
# MOVE ENGINE
# -----------------------------

def move_file(src: str, dest_stack: str):

    src_path = ROOT / src.replace("/home/tkanhai/Neurovest/", "").replace("File: ", "").strip()

    if not src_path.exists():
        print(f"⚠ Missing: {src_path}")
        return

    dest_dir = ROOT / "backend/app" / dest_stack
    dest_dir.mkdir(parents=True, exist_ok=True)

    backup_file(src_path)

    dest_path = dest_dir / src_path.name

    print(f"📦 Moving:")
    print(f"   {src_path}")
    print(f"   → {dest_path}")

    shutil.move(str(src_path), str(dest_path))


# -----------------------------
# MAIN
# -----------------------------

def main():

    if not PLAN_FILE.exists():
        print("❌ SERVICE_RELOCATION_PLAN.json not found")
        return

    ensure_backup()

    plan = json.loads(PLAN_FILE.read_text())

    print("\n🧠 APPLYING SERVICE → STACK MIGRATION\n")

    for entry in plan:

        src, dest_stack = entry

        if dest_stack == "STACK_REVIEW_REQUIRED":
            print(f"⚠ Skipping unresolved: {src}")
            continue

        move_file(src, dest_stack)

    print("\n✔ Migration complete")
    print(f"📦 Backup stored in {BACKUP_DIR}")


if __name__ == "__main__":
    main()
