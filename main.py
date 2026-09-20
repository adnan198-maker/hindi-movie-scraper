from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

@app.get("/extract-stream")
def extract_stream(page_url: str):
    try:
        response = requests.get(page_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Page fetch nahi ho saka")

        html_text = response.text
        extracted_links = []

        # Check karein ke page par Hindi audio mention hai ya nahi
        is_hindi = bool(re.search(r'(hindi|dual audio|org 2\.0|hindi dubbed)', html_text, re.IGNORECASE))

        # 1. Direct slash423kix links dhoondna
        slash_matches = re.findall(r'https?://slash423kix\.com/play/[a-zA-Z0-9]+', html_text)
        for link in slash_matches:
            if link not in extracted_links:
                extracted_links.append(link)

        # 2. Match IMDB ID if direct link not found
        if not extracted_links:
            imdb_matches = re.findall(r'tt\d{7,8}', html_text)
            for imdb_id in set(imdb_matches):
                constructed_url = f"https://slash423kix.com/play/{imdb_id}"
                if constructed_url not in extracted_links:
                    extracted_links.append(constructed_url)

        if extracted_links:
            return {
                "status": "success",
                "is_hindi_available": is_hindi,
                "audio_language": "Hindi / Dual Audio" if is_hindi else "Default/English",
                "count": len(extracted_links),
                "stream_urls": extracted_links,
                "primary_url": extracted_links[0]
            }

        return {"status": "error", "message": "Hindi stream ya player link nahi mila"}

    except Exception as e:
        return {"status": "error", "message": str(e)}