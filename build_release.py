import os
import sys
import shutil
import zipfile
import hashlib
import subprocess

# Windows cp1252 console utf-8 fix
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.version import APP_VERSION

VERSION = APP_VERSION
DIST_DIR = os.path.abspath("dist")
BUILD_DIR = os.path.abspath("build")
BUNDLE_NAME = f"KM-Layout-Tables-v{VERSION}-win64"

def calculate_sha256(filepath: str) -> str:
    """Dosyanın SHA-256 özetini hesaplar."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def create_zip_archive(source_dir: str, zip_path: str):
    """Klasörü ZIP arşivi haline getirir."""
    print(f"📦 ZIP arşivi oluşturuluyor: {zip_path}...")
    base_folder_name = os.path.basename(source_dir)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_full = os.path.join(root, file)
                rel_path = os.path.relpath(file_full, os.path.dirname(source_dir))
                zipf.write(file_full, rel_path)
    print(f"✅ ZIP başarıyla oluşturuldu: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")

def build_portable():
    """Spec dosyasını kullanarak klasör tabanlı taşınabilir sürümü derler."""
    print("\n=======================================================")
    print(f"🚀 KM Layout Tables Studio v{VERSION} - Portable Build Başlıyor")
    print("=======================================================\n")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "km_tables.spec",
        "--clean",
        "--noconfirm"
    ]
    print(f"Komut: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("❌ PyInstaller derlemesi başarısız oldu!")
        sys.exit(result.returncode)

    portable_folder = os.path.join(DIST_DIR, BUNDLE_NAME)
    if not os.path.exists(portable_folder):
        print(f"❌ Beklenen çıktı klasörü bulunamadı: {portable_folder}")
        sys.exit(1)

    zip_file = os.path.join(DIST_DIR, f"{BUNDLE_NAME}.zip")
    create_zip_archive(portable_folder, zip_file)

    # Checksum hesapla
    checksum_file = os.path.join(DIST_DIR, "checksums.txt")
    checksum_lines = []

    zip_file = os.path.join(DIST_DIR, f"{BUNDLE_NAME}.zip")
    if os.path.exists(zip_file):
        sha_zip = calculate_sha256(zip_file)
        checksum_lines.append(f"{sha_zip}  {os.path.basename(zip_file)}\n")
        print(f"\n🔑 ZIP SHA-256: {sha_zip}")
        print(f"🎉 Taşınabilir Paket: {zip_file}")

    standalone_exe = os.path.join(DIST_DIR, f"KM-Layout-Tables-v{VERSION}-Standalone.exe")
    if os.path.exists(standalone_exe):
        sha_exe = calculate_sha256(standalone_exe)
        checksum_lines.append(f"{sha_exe}  {os.path.basename(standalone_exe)}\n")
        print(f"🔑 EXE SHA-256: {sha_exe}")
        print(f"🎉 Tek Parça EXE: {standalone_exe} ({os.path.getsize(standalone_exe) / (1024*1024):.2f} MB)")

    with open(checksum_file, "w", encoding="utf-8") as f:
        f.writelines(checksum_lines)

if __name__ == "__main__":
    build_portable()
