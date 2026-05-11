# services.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pdfplumber
import docx
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load the environment vars from the env file
load_dotenv()

# Confidential Data
AI_API_KEY = os.getenv("AI_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
BPA_PROMPT = os.getenv("BPA_PROMPT")

def extract_text_from_file(file_path: str) -> str:
    """Extracts text from PDF or DOCX files."""
    extracted_text = ""
    extension = file_path.lower().split('.')[-1]

    try:
        if extension == 'pdf':
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted_text += page.extract_text() + "\n"
        elif extension in ['doc', 'docx']:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                extracted_text += paragraph.text + "\n"
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
    except Exception as e:
        print(f"Erro ao extrair o texto do arquivo: {e}")
        return ""
    
    return extracted_text.strip()

def analyze_with_ai(idea_text: str) -> dict:
    """Send the text to the AI using the prompt."""
    if not AI_API_KEY:
        raise ValueError("Chave da API da IA não configurada no ambiente.")

    genai.configure(api_key=AI_API_KEY)
    
    model = genai.GenerativeModel(
        model_name="gemini-3.1-pro",
        system_instruction=BPA_PROMPT
    )

    try:
        response = model.generate_content(f"Aqui está o input para análise:\n\n{idea_text}")
        ai_content = response.text

        score_match = re.search(r'SCORE:\s*(\d+/\d+)', ai_content, re.IGNORECASE)
        verdict_match = re.search(r'VEREDITO:\s*(PASSAR|APROFUNDAR|AVANÇAR)', ai_content, re.IGNORECASE)
        red_flags_match = re.search(r'🚩\s*RED FLAGS(.*?)(?:💀|✅|⚖️|🎬|$)', ai_content, re.DOTALL)
        cost_match = re.search(r'⚖️\s*CUSTO DE OPORTUNIDADE(.*?)(?:🎬|$)', ai_content, re.DOTALL)

        return {
            "full_text": ai_content,
            "score": score_match.group(1) if score_match else "N/A",
            "verdict": verdict_match.group(1) if verdict_match else "Indefinido",
            "red_flags": red_flags_match.group(1).strip() if red_flags_match else "Não identificadas",
            "opportunity_cost": cost_match.group(1).strip() if cost_match else "Não definido"
        }
    except Exception as e:
        print(f"Erro na análise da IA: {e}")
        return {
            "full_text": f"Erro interno: {e}",
            "score": "N/A",
            "verdict": "Erro",
            "red_flags": "Erro",
            "opportunity_cost": "Erro"
        }

def send_email(recipient: str, subject: str, body: str):
    """Generic function to send emails via SMTP."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("Credenciais de e-mail não configuradas. O envio de e-mail foi ignorado.")
        return

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"E-mail enviado com sucesso para: {recipient}")
    except Exception as e:
        print(f"Falha ao enviar e-mail para {recipient}: {e}")