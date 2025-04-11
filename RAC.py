import os
import re
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

non_images = [".gif", ".mp4", ".avi", ".mkv", ".mov", ".flv", ".webm"]
excluded_extensions = [".py", ".exe"]

def is_correctly_named(filename):
    return bool(re.match(r'^(\d+)\.[a-zA-Z0-9]+$', filename))

def get_conversion_format():
    while True:
        choice = input("Choose a format for conversion (png/jpg): ").strip().lower()
        if choice in ["png", "jpg"]:
            return choice
        print("Invalid input. Enter 'png' or 'jpg'.")

conversion_format = get_conversion_format()
folder_path = os.getcwd()
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f != os.path.basename(__file__)]

excluded = excluded_extensions
all_for_rename = [f for f in files if os.path.splitext(f)[1].lower() not in excluded]

correct_files = [f for f in all_for_rename if is_correctly_named(f)]
incorrect_files = [f for f in all_for_rename if not is_correctly_named(f)]

correct_files.sort(key=lambda f: int(re.match(r'^(\d+)', f).group(1)) if re.match(r'^(\d+)', f) else float('inf'))
incorrect_files.sort()

rename_map = {}
next_number = 1
for file in correct_files + incorrect_files:
    _, extension = os.path.splitext(file)
    new_name = f"{next_number}{extension}"
    rename_map[file] = new_name
    next_number += 1

total_files = len(rename_map)
processed = 0

for old_name, new_name in rename_map.items():
    os.rename(os.path.join(folder_path, old_name), os.path.join(folder_path, new_name))
    processed += 1
    print(f"\rProcessed: {processed}/{total_files} files", end="", flush=True)

files_after_rename = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
convert_files = [f for f in files_after_rename if os.path.splitext(f)[1].lower() not in non_images + excluded_extensions]

total_files += len(convert_files)
processed = 0
lock = __import__('threading').Lock()

def convert_file(file):
    global processed
    file_path = os.path.join(folder_path, file)
    filename, _ = os.path.splitext(file)
    new_file_path = os.path.join(folder_path, f"{filename}.{conversion_format}")
    try:
        if not os.path.exists(new_file_path):
            img = Image.open(file_path)
            if conversion_format == "jpg":
                img = img.convert("RGB")
                img.save(new_file_path, "JPEG", quality=95)
            else:
                img.save(new_file_path, "PNG")
            os.remove(file_path)
        with lock:
            processed += 1
            print(f"\rProcessed: {processed}/{total_files} files", end="", flush=True)
    except Exception as e:
        print(f"\rError converting {file}: {e}", flush=True)

with ThreadPoolExecutor() as executor:
    executor.map(convert_file, convert_files)

input("\nPress Enter to finish.")
print("Done!")