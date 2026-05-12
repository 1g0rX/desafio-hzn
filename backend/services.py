# services.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pdfplumber
import docx
import re
import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# load env vars
load_dotenv()

# confidential data
AI_API_KEY = os.getenv("AI_API_KEY") 
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# read prompt from file or env
try:
    with open("prompt.txt", "r", encoding="utf-8") as f:
        BPA_PROMPT = f.read()
except FileNotFoundError:
        BPA_PROMPT = os.getenv("BPA_PROMPT", "")

def extract_text_from_file(file_path: str) -> str:
    """extract text from pdf or docx."""
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
    """send text to ai and parse."""
    if not AI_API_KEY:
        raise ValueError("Chave da API da IA não configurada no ambiente.")

    # init ai client
    client = genai.Client(api_key=AI_API_KEY)

    try:
        # call model
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=f"Aqui está o input para análise:\n\n{idea_text}",
            config=types.GenerateContentConfig(
                system_instruction=BPA_PROMPT,
            )
        )
        ai_content = response.text

        # save raw ai output to log
        try:
            timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            with open("historico_ia.txt", "a", encoding="utf-8") as log_file:
                log_file.write("\n" + "="*50 + "\n")
                log_file.write(f"ANÁLISE DA IA - {timestamp}\n")
                log_file.write("="*50 + "\n")
                log_file.write(ai_content + "\n")
        except Exception as log_err:
            print(f"Aviso: Não foi possível salvar o log da IA: {log_err}")

        # extract data with regex
        score_match = re.search(r'SCORE:\s*(\d+/\d+)', ai_content, re.IGNORECASE)
        verdict_match = re.search(r'VEREDITO:\s*(PASSAR|APROFUNDAR|AVANÇAR)', ai_content, re.IGNORECASE)
        
        # extract red flags
        red_flags_match = re.search(r'RED FLAGS[^\w]*\s*(.*?)(?=CUSTO DE OPORTUNIDADE|$)', ai_content, re.IGNORECASE | re.DOTALL)
        
        # extract opportunity cost
        cost_match = re.search(r'CUSTO DE OPORTUNIDADE[^\w]*\s*(.*?)(?=🎬|$)', ai_content, re.IGNORECASE | re.DOTALL)

        return {
            "full_text": ai_content,
            "score": score_match.group(1) if score_match else "N/A",
            "verdict": verdict_match.group(1).upper() if verdict_match else "Indefinido",
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
    """send email via smtp."""
    
    # mock email if no credentials
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("Erro: EMAIL_SENDER ou EMAIL_PASSWORD não configurados no .env")
        return

    # setup email message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        # send via gmail smtp
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # enable tls
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"E-mail enviado com sucesso para: {recipient}")
    except Exception as e:
        print(f"Falha ao enviar e-mail para {recipient}: {e}")