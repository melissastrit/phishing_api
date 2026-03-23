import os
import json
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailRequest(BaseModel):
    text: str

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.post("/analyze")
async def analyze_email(request: EmailRequest):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Şu metni siber güvenlik açısından analiz et. SADECE JSON formatında dön. Başka hiçbir kelime yazma.
        Format: {{"risk_seviyesi": "Düşük/Orta/Yüksek", "sebep": "Açıklama..."}}
        Metin: "{request.text}"
        """
        response = model.generate_content(prompt)
        
        # Markdown işaretlerini temizle
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        return {"analiz_sonucu": json.loads(raw_text)}

    except Exception as e:
        return {"hata": f"Gemini Hatası: {str(e)}"}