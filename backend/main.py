import os
import json
import sqlite3
import logging
import asyncio
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import google.generativeai as genai

from backend.parser import parse_html_content, parse_xml_content

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables")

# Configure Google AI
genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI(title="Flashcard Study App")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = "flashcards.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class Flashcard(BaseModel):
    id: Optional[int] = None
    question: str
    answer: str
    source_file: Optional[str] = None

class GenerationConfig(BaseModel):
    count: int = 50
    model: str = "gemini-1.5-flash"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename
    
    try:
        if filename.endswith('.html') or filename.endswith('.htm'):
            parsed_content = parse_html_content(content.decode('utf-8'))
        elif filename.endswith('.xml'):
            parsed_content = parse_xml_content(content.decode('utf-8'))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload XML or HTML.")
        
        return {"filename": filename, "sections": parsed_content}
    except Exception as e:
        logger.error(f"Error parsing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")

@app.post("/generate")
async def generate_flashcards(
    sections: List[dict], 
    count: int = Form(50), 
    model_name: str = Form("gemini-1.5-flash"),
    source_file: str = Form("unknown")
):
    try:
        model = genai.GenerativeModel(model_name)
        
        # Prepare context from sections
        context = ""
        for section in sections:
            context += f"\n\nHeading: {section.get('heading', 'No Heading')}\nContent: {section.get('content', '')}"
        
        prompt = f"""
        Generate {count} high-quality flashcards based on the following textbook content.
        
        Requirements:
        1. Be clear and concise.
        2. Cover key concepts, definitions, and relationships.
        3. Avoid trivial or redundant questions.
        4. Return the result strictly as a JSON array of objects with "question" and "answer" keys.
        
        Content:
        {context[:15000]} # Truncate if too large for simple model
        """
        
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        try:
            # Handle potential markdown formatting in response
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            flashcards_data = json.loads(text)
        except Exception as json_err:
            logger.error(f"Failed to parse AI response as JSON: {json_err}")
            logger.error(f"Raw response: {response.text}")
            raise HTTPException(status_code=500, detail="AI response format was invalid.")

        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        saved_cards = []
        
        for card in flashcards_data:
            cursor.execute(
                "INSERT INTO flashcards (question, answer, source_file) VALUES (?, ?, ?)",
                (card['question'], card['answer'], source_file)
            )
            card_id = cursor.lastrowid
            saved_cards.append({
                "id": card_id,
                "question": card['question'],
                "answer": card['answer'],
                "source_file": source_file
            })
            
        conn.commit()
        conn.close()
        
        return saved_cards
    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/flashcards", response_model=List[Flashcard])
async def get_flashcards(source_file: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if source_file:
        cursor.execute("SELECT * FROM flashcards WHERE source_file = ?", (source_file,))
    else:
        cursor.execute("SELECT * FROM flashcards ORDER BY created_at DESC")
        
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.delete("/flashcards/{card_id}")
async def delete_flashcard(card_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))
    conn.commit()
    conn.close()
    return {"message": "Flashcard deleted"}

@app.get("/export/json")
async def export_json():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM flashcards")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.get("/export/csv")
async def export_csv():
    # Simple CSV export implementation
    import io
    import csv
    from fastapi.responses import StreamingResponse
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM flashcards")
    rows = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Question", "Answer"])
    for row in rows:
        writer.writerow(row)
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=flashcards.csv"}
    )

# Serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
