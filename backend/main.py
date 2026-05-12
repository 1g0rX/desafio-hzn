import os
import shutil
from fastapi import FastAPI, Depends, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db
import models
import schemas
import services

# --- CONFIGURATION ---

EVALUATOR_REAL_EMAIL = os.getenv("EVALUATOR_REAL_EMAIL")


# init database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Plataforma de Avaliação - BPA Ventures")

# cors config
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
    # save file locally
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # register in db
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

    # trigger background ai processing
    background_tasks.add_task(process_opportunity, new_opportunity.id, file_path, db)

    return {
        "message": "Ideia submetida com sucesso! A nossa inteligência artificial está analisando o material.", 
        "id": new_opportunity.id
    }

def process_opportunity(op_id: int, file_path: str, db: Session):
    """background task to run ai and notify evaluator."""
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == op_id).first()
    if not opportunity:
        return

    extracted_text = services.extract_text_from_file(file_path)
    if extracted_text:
        ai_result = services.analyze_with_ai(extracted_text)
        
        # save parsed ai results to db
        opportunity.score = ai_result.get("score")
        opportunity.verdict = ai_result.get("verdict")
        opportunity.red_flags = ai_result.get("red_flags")
        opportunity.opportunity_cost = ai_result.get("opportunity_cost")
        db.commit()

        # email for evaluator
        evaluation_link = f"http://127.0.0.1:5500/frontend/dashboard.html?id={opportunity.id}"
        email_body = f"""
        <h2>Nova Oportunidade Analisada</h2>
        <p><strong>Proponente:</strong> {opportunity.name}</p>
        <p><strong>Veredito da IA:</strong> {opportunity.verdict}</p>
        <p><strong>Score:</strong> {opportunity.score}</p>
        <hr>
        <p>Para ver os detalhes completos e decidir, acesse o seu painel de avaliador.</p>
        <p><a href="{evaluation_link}">Abrir Painel de Avaliação</a></p>
        """
        
        # notify evaluator using email from env
        if EVALUATOR_REAL_EMAIL:
            services.send_email(
                recipient=EVALUATOR_REAL_EMAIL,
                subject=f"[BPA Deal Flow] {opportunity.verdict} - {opportunity.name}",
                body=email_body
            )

@app.get("/api/opportunities/{op_id}", response_model=schemas.OpportunityResponse)
def get_opportunity(op_id: int, db: Session = Depends(get_db)):
    """fetch opportunity data for frontend."""
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == op_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada no sistema.")
    return opportunity

@app.post("/api/opportunities/{op_id}/evaluate")
def evaluate_opportunity(op_id: int, payload: schemas.EvaluatorDecision, db: Session = Depends(get_db)):
    """receive final decision and notify proponent."""
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == op_id).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidade não encontrada.")
    
    if payload.decision not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Decisão inválida.")

    opportunity.status = payload.decision
    db.commit()

    # prepare response for proponent
    if payload.decision == "APPROVED":
        subject = "BPA Ventures - Atualização sobre a sua ideia!"
        body = f"Olá {opportunity.name},<br><br>Temos boas notícias! A sua oportunidade foi <b>APROVADA</b> pela nossa equipe. Em breve entraremos em contato."
        decision_pt = "APROVADA"
    else:
        subject = "BPA Ventures - Retorno sobre a sua submissão"
        body = f"Olá {opportunity.name},<br><br>Agradecemos o envio. No momento, sua proposta não possui fit com nosso modelo. Desejamos sucesso!"
        decision_pt = "REPROVADA"

    # notify proponent
    services.send_email(
        recipient=opportunity.email, 
        subject=subject, 
        body=body
    )

    return {"message": f"Oportunidade {decision_pt} com sucesso. Proponente notificado."}