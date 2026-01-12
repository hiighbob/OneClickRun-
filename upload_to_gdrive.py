"""
Upload two notebooks and two HTML files to two Drive folders using PyDrive.

Requirements:
  pip install PyDrive google-auth-oauthlib

Before running:
  1) Create OAuth credentials (OAuth client ID) in Google Cloud Console for "Desktop".
     - Download the client_secrets.json and place in the same directory as this script.
  2) Create two target folders in Google Drive (or note existing folder IDs).

Usage:
  python upload_to_gdrive.py --folder1 FOLDERID1 --folder2 FOLDERID2

It will authenticate (opens a browser prompt), then upload:
  - CRD_attempt_with_fallback.ipynb  -> folder1
  - CRD_attempt_with_fallback.html  -> folder1
  - cloudflared_noVNC_with_codeserver.ipynb -> folder2
  - cloudflared_noVNC_with_codeserver.html -> folder2

After upload it prints the file IDs. Use those file IDs to update the HTML "Open in Colab" button links.
"""
import argparse
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

FILES_TO_UPLOAD_FOLDER1 = [
    "CRD_attempt_with_fallback.ipynb",
    "CRD_attempt_with_fallback.html"
]

FILES_TO_UPLOAD_FOLDER2 = [
    "cloudflared_noVNC_with_codeserver.ipynb",
    "cloudflared_noVNC_with_codeserver.html"
]

def ensure_exists(fpath):
    if not os.path.exists(fpath):
        raise SystemExit(f"Required file not found: {fpath}")

def upload_files(drive, folder_id, files):
    uploaded = []
    for f in files:
        ensure_exists(f)
        gfile = drive.CreateFile({'title': os.path.basename(f), 'parents':[{'id': folder_id}]})
        gfile.SetContentFile(f)
        gfile.Upload()
        uploaded.append((f, gfile['id']))
    return uploaded

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder1", required=True, help="Drive folder ID for notebook 1 + html")
    parser.add_argument("--folder2", required=True, help="Drive folder ID for notebook 2 + html")
    args = parser.parse_args()

    for f in FILES_TO_UPLOAD_FOLDER1 + FILES_TO_UPLOAD_FOLDER2:
        ensure_exists(f)

    # Authenticate
    gauth = GoogleAuth()
    # Try local webserver flow. If it fails, follow console auth.
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    print("Uploading to folder1:", args.folder1)
    out1 = upload_files(drive, args.folder1, FILES_TO_UPLOAD_FOLDER1)
    for f, fid in out1:
        print(f"Uploaded {f} -> fileId: {fid}")

    print("Uploading to folder2:", args.folder2)
    out2 = upload_files(drive, args.folder2, FILES_TO_UPLOAD_FOLDER2)
    for f, fid in out2:
        print(f"Uploaded {f} -> fileId: {fid}")

    print("\nDone. Use the printed file IDs to edit the HTML files (replace REPLACE_WITH_DRIVE_FILE_ID) or to open in Colab via:")
    print("https://colab.research.google.com/drive/<fileId>")

if __name__ == "__main__":
    main()