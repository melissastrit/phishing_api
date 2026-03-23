import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Ayarları Yükle
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

app = FastAPI()

# 2. CORS (Frontend bağlantısı için)
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
    if not request.text:
        return {"hata": "Metin boş olamaz."}

    try:
        # DİKKAT: En garantili model isimlendirmesi budur
        # Bu yöntem sürüm karmaşasını kökten çözer
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
        Sen bir siber güvenlik uzmanısın. Aşağıdaki metni analiz et. 
        SADECE JSON dön. Başka metin ekleme.
        Format: {{"risk_seviyesi": "...", "sebep": "..."}}
        
        Metin: "{request.text}"
        """

        response = model.generate_content(prompt)
        
        # Markdown bloklarını temizleme (Hata önleyici)
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        result = json.loads(raw_text)

        return {
            "analiz_sonucu": result
        }

    except Exception as e:
        # Hata mesajını daha detaylı görelim
        return {"hata": f"Gemini Hatası: {str(e)}"}