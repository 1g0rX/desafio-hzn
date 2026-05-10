from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Plataforma de Avaliação - BPA Ventures")

# CORS, para permitir a conversa entre o front-end com a API
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")

def health_check():
    return {"status": "Servidor rodandno"}
