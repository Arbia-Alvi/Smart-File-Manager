from pathlib import Path
import shutil
import hashlib
import sqlite3
import json
import logging
import argparse


# =========================
# Logging
# =========================

logging.basicConfig(
    filename="file_manager.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("File Manager Started")


# =========================
# Settings
# =========================

dry_run = False

move_history = []


# =========================
# Database
# =========================

connection = sqlite3.connect("file_history.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS move_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_path TEXT,
        new_path TEXT,
        move_time TEXT
    )
""")

connection.commit()


# =========================
# Load Categories
# =========================

with open("config/categories.json", "r", encoding="utf-8") as file:
    categories = json.load(file)


# =========================
# Unique File Name
# =========================

def get_unique_path(destination_folder, file):

    destination = destination_folder / file.name

    if not destination.exists():
        return destination

    counter = 1

    while True:

        new_name = f"{file.stem}_{counter}{file.suffix}"
        new_path = destination_folder / new_name

        if not new_path.exists():
            return new_path

        counter += 1


# =========================
# File Hash
# =========================

def get_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while chunk := file.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


# =========================
# Scan / Organize Files
# =========================

def scan_files():

    global move_history

    folder = Path(".")

    if dry_run:
        print("\n--- DRY RUN MODE: No file will be moved ---")

    for item in folder.iterdir():

        if (
            item.is_file()
            and item.name != "file_history.db"
            and item.suffix != ".log"
        ):

            category = categories.get(item.suffix, "Other")

            print(item.name, "->", category)

            Path(category).mkdir(exist_ok=True)

            destination = get_unique_path(
                Path(category),
                item
            )

            print(
                "Would move:",
                item.name,
                "->",
                destination
            )

            if not dry_run:

                original_path = item

                try:

                    shutil.move(
                        str(item),
                        str(destination)
                    )

                    logging.info(
                        "Moved %s -> %s",
                        original_path,
                        destination
                    )

                    move_history.append({
                        "original": original_path,
                        "new": destination
                    })

                    cursor.execute("""
                        INSERT INTO move_history
                        (original_path, new_path, move_time)
                        VALUES (?, ?, datetime('now'))
                    """, (
                        str(original_path),
                        str(destination)
                    ))

                    connection.commit()

                except Exception as error:

                    logging.exception(
                        "Failed to move %s: %s",
                        original_path,
                        error
                    )


    # =========================
    # Current Run History
    # =========================

    if move_history:

        print("\n--- MOVE HISTORY ---")

        for move in move_history:

            print(
                "Original:",
                move["original"]
            )

            print(
                "New:",
                move["new"]
            )


    # =========================
    # Duplicate Detection
    # =========================

    documents_folder = Path("Documents")

    if documents_folder.exists():

        print("\n--- DUPLICATE CHECK ---")

        file_hashes = {}

        for file in documents_folder.iterdir():

            if file.is_file():

                file_size = file.stat().st_size

                print(
                    file.name,
                    "->",
                    file_size,
                    "bytes"
                )

                file_hash = get_file_hash(file)

                print(
                    file.name,
                    "->",
                    file_hash
                )

                file_key = (
                    file.suffix,
                    file_size,
                    file_hash
                )

                if file_key in file_hashes:

                    print(
                        "Duplicate:",
                        file.name
                    )

                    print(
                        "Same as:",
                        file_hashes[file_key]
                    )

                else:

                    file_hashes[file_key] = file.name


# =========================
# Show Database History
# =========================

def show_history():

    print("\n--- DATABASE HISTORY ---")

    cursor.execute("""
        SELECT id, original_path, new_path, move_time
        FROM move_history
        ORDER BY id DESC
    """)

    history = cursor.fetchall()

    if not history:

        print("No history found.")

    else:

        for row in history:
            print(row)


# =========================
# Undo Last Move
# =========================

def undo_last_move():

    cursor.execute("""
        SELECT id, original_path, new_path
        FROM move_history
        ORDER BY id DESC
        LIMIT 1
    """)

    last_move = cursor.fetchone()

    if not last_move:

        print("Nothing to undo.")

        return

    move_id, original_path, new_path = last_move

    original = Path(original_path)
    new = Path(new_path)

    try:

        if not new.exists():

            print(
                "File to undo was not found:",
                new
            )

            return

        if original.exists():

            print(
                "Original location already has a file:",
                original
            )

            return

        shutil.move(
            str(new),
            str(original)
        )

        cursor.execute("""
            DELETE FROM move_history
            WHERE id = ?
        """, (move_id,))

        connection.commit()

        print(
            "Undo complete:",
            new,
            "->",
            original
        )

        logging.info(
            "Undo: %s -> %s",
            new,
            original
        )

    except Exception as error:

        print(
            "Undo failed:",
            error
        )

        logging.exception(
            "Undo failed: %s",
            error
        )


# =========================
# Main CLI
# =========================

def main():

    parser = argparse.ArgumentParser(
        description="Smart File Manager"
    )

    parser.add_argument(
        "command",
        choices=["scan", "history", "undo"],
        help="Choose what the File Manager should do"
    )

    args = parser.parse_args()


    # =========================
    # CLI Commands
    # =========================

    if args.command == "scan":

        print("\n--- SCAN STARTED ---")

        print(
            "Categories loaded:",
            categories
        )

        scan_files()


    elif args.command == "history":

        show_history()


    elif args.command == "undo":

        undo_last_move()


# =========================
# Program Entry Point
# =========================

if __name__ == "__main__":

    try:

        main()

    finally:

        cursor.close()
        connection.close()