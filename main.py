# main.py
import os
import shutil
from fastapi import FastAPI, Depends, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db
import models
import schemas
import services

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Plataforma de Avaliação - BPA Ventures")

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/api/opportunities/submit")
async def submit_opportunity(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    file: UploadFile = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Save file locally
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. Register in DB
    new_opportunity = models.Opportunity(
        name=name,
        email=email,
        phone=phone,
        file_path=file_path,
        status="UNDER_ANALYSIS"
    )
    db.add(new_opportunity)
    db.commit()
    db.refresh(new_opportunity)

    # 3. Trigger background AI processing
    background_tasks.add_task(process_opportunity, new_opportunity.id, file_path, db)

    # Return message in PT-BR
    return {
        "message": "Ideia submetida com sucesso! A nossa inteligência artificial está analisando o material.", 
        "id": new_opportunity.id
    }


def process_opportunity(op_id: int, file_path: str, db: Session):
    """Background task to extract text, run AI and notify Evaluator."""
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == op_id).first()
    if not opportunity:
        return

    extracted_text = services.extract_text_from_file(file_path)
    if extracted_text:
        ai_result = services.analyze_with_ai(extracted_text)
        
        # Save parsed AI results to DB
        opportunity.score = ai_result.get("score")
        opportunity.verdict = ai_result.get("verdict")
        opportunity.red_flags = ai_result.get("red_flags")
        opportunity.opportunity_cost = ai_result.get("opportunity_cost")
        db.commit()

        # Email content in PT-BR for the Evaluator
        evaluation_link = f"http://localhost:3000/evaluator/{opportunity.id}"
        email_body = f"""
        <h2>Nova Oportunidade Analisada</h2>
        <p><strong>Proponente:</strong> {opportunity.name}</p>
        <p><strong>Veredito da IA:</strong> {opportunity.verdict}</p>
        <p><strong>Score:</strong> {opportunity.score}</p>
        <hr>
        <p>Para ver os detalhes completos e decidir, clique no link abaixo:</p>
        <a href="{evaluation_link}">Acessar Plataforma de Avaliação</a>
        """
        services.send_email(
            recipient=services.EMAIL_SENDER,
            subject=f"[BPA Deal Flow] {opportunity.verdict} - {opportunity.name}",
            body=email_body
        )

@app.get("/api/opportunities/{op_id}", response_model=schemas.OpportunityResponse)
def get_opportunity(op_id: int, db: Session = Depends(get_db)):
    """Fetch opportunity data for the front-end screen."""
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == op_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada no sistema.")
    return opportunity

@app.post("/api/opportunities/{op_id}/evaluate")
def evaluate_opportunity(op_id: int, payload: schemas.EvaluatorDecision, db: Session = Depends(get_db)):
    """Receives the final decision from the Evaluator."""
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == op_id).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada no sistema.")
    
    if payload.decision not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Decisão inválida. Use APPROVED ou REJECTED.")

    opportunity.status = payload.decision
    db.commit()

    # Define the email content in PT-BR
    if payload.decision == "APPROVED":
        subject = "BPA Ventures - Atualização sobre a sua ideia!"
        body = f"Olá {opportunity.name},<br><br>Temos boas notícias! A sua oportunidade foi <b>APROVADA</b> pela nossa equipe de Deal Flow. Em breve entraremos em contato para os próximos passos."
        decision_pt = "APROVADA"
    else:
        subject = "BPA Ventures - Retorno sobre a sua submissão"
        body = f"Olá {opportunity.name},<br><br>Agradecemos o envio da sua ideia. Após análise criteriosa da nossa equipe, decidimos que a sua proposta não possui fit com o nosso modelo neste momento. Desejamos sucesso na sua jornada!"
        decision_pt = "REPROVADA"

    services.send_email(
        recipient=opportunity.email, 
        subject=subject, 
        body=body
    )

    return {"message": f"Oportunidade {decision_pt} com sucesso. Proponente notificado por e-mail."}