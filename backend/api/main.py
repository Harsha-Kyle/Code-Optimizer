import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
import sqlite3
import json

from compiler.pipeline import CompilerPipeline

app = FastAPI(title="Code Optimization Framework API", version="1.0.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize local SQLite DB for compilation runs storage
DB_PATH = "compilations.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compilations (
            id TEXT PRIMARY KEY,
            source TEXT,
            target TEXT,
            success INTEGER,
            response TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class CompileRequest(BaseModel):
    source: str
    target: Optional[str] = "arm_cortex_m4"
    passes: Optional[Dict[str, bool]] = None

# Built-in Hardware Profiles
HARDWARE_PROFILES = [
    {
        "id": "arm_cortex_m4",
        "name": "ARM Cortex-M4",
        "architecture": "ARM",
        "registers": 16,
        "word_size": "32-bit",
        "ram": "128 KB",
        "flash": "512 KB"
    },
    {
        "id": "arm_cortex_m0",
        "name": "ARM Cortex-M0+",
        "architecture": "ARM",
        "registers": 16,
        "word_size": "32-bit",
        "ram": "16 KB",
        "flash": "64 KB"
    },
    {
        "id": "avr_atmega328p",
        "name": "AVR ATmega328P",
        "architecture": "AVR",
        "registers": 32,
        "word_size": "8-bit",
        "ram": "2 KB",
        "flash": "32 KB"
    }
]

@app.get("/api/hardware")
def get_hardware_profiles():
    return HARDWARE_PROFILES

@app.post("/api/compile")
def compile_code(req: CompileRequest):
    pipeline = CompilerPipeline(req.source, target=req.target, passes=req.passes)
    result = pipeline.compile()
    
    # Store compilation in database
    comp_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO compilations (id, source, target, success, response) VALUES (?, ?, ?, ?, ?)",
        (comp_id, req.source, req.target, 1 if result["success"] else 0, json.dumps(result))
    )
    conn.commit()
    conn.close()
    
    result["id"] = comp_id
    return result

@app.get("/api/result/{comp_id}")
def get_compile_result(comp_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT response FROM compilations WHERE id = ?", (comp_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Compilation result not found")
        
    return json.loads(row[0])
