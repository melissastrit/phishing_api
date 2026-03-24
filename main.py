import os
import json
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
        prompt = f"""
        Şu metni siber güvenlik açısından analiz et. SADECE JSON formatında dön. Başka hiçbir kelime yazma.
        Format: {{"risk_seviyesi": "Düşük/Orta/Yüksek", "sebep": "Açıklama..."}}
        Metin: "{request.text}"
        """
        
        chat_completion = client.chat.completions.create(
            messages=[{ "role": "user", "content": prompt }],
            model="llama3-8b-8192",
            temperature=0.2,
        )
        
        response_text = chat_completion.choices[0].message.content
        raw_text = response_text.replace('```json', '').replace('```', '').strip()
        return {"analiz_sonucu": json.loads(raw_text)}

    except Exception as e:
        return {"hata": f"Groq (Llama 3) Hatası: {str(e)}"}