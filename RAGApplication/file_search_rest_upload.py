import requests
import os

api_key = "AIzaSyDozUi50Nlq2YHmruVo9nmp0pybzfKPNpI"
store_name = "fileSearchStores/myfilesearchstore-8sfn1in8688v"  # Use the correct name
file_path = "C:/Users/Personal/Documents/japancapital.txt"                           # Path to your file
mime_type = "text/plain"                              # Use "application/pdf" for PDFs

file_size = os.path.getsize(file_path)

# Step 1: Start upload session
start_url = f"https://generativelanguage.googleapis.com/upload/v1beta/{store_name}:uploadToFileSearchStore?key={api_key}"
headers = {
    "X-Goog-Upload-Protocol": "resumable",
    "X-Goog-Upload-Command": "start",
    "X-Goog-Upload-Header-Content-Length": str(file_size),
    "X-Goog-Upload-Header-Content-Type": mime_type,
    "Content-Type": "application/json"
}
data = {
    "display_name": os.path.basename(file_path)
}
start_response = requests.post(start_url, headers=headers, json=data)
upload_url = start_response.headers.get("X-Goog-Upload-URL")
print("Stage 1 - Start:", start_response.status_code, start_response.text)
print("Upload URL:", upload_url)

# Step 2: Upload file bytes to the session URL
with open(file_path, "rb") as file_data:
    upload_headers = {
        "Content-Length": str(file_size),
        "X-Goog-Upload-Offset": "0",
        "X-Goog-Upload-Command": "upload, finalize"
        # DO NOT need Content-Type here
    }
    upload_response = requests.post(upload_url, headers=upload_headers, data=file_data)
    print("Stage 2 - Upload:", upload_response.status_code, upload_response.text)

# Check upload_response.status_code == 200 AND look for "operation" completion in response text

