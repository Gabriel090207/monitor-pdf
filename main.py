from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import pdfplumber
from urllib.parse import urljoin
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import firebase_admin
from firebase_admin import credentials, firestore
import re

app = FastAPI()

# Inicializar Firestore uma vez
cred = credentials.Certificate("chave-firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def enviar_email(destinatario, assunto, corpo, remetente, senha):
    msg = MIMEMultipart("alternative")
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <div style="background-color:#007BFF;color:white;padding:10px;">
          <h2>Radar Edital</h2>
        </div>
        <div style="padding:10px;">
          <p>{corpo}</p>
          <a href="{corpo.split('Link: ')[-1]}" style="background-color:#28a745;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Clique aqui para conferir</a>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email enviado para {destinatario}")
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")

def baixar_pdf_mais_recente(url_base):
    headers = {"User-Agent": "Mozilla/5.0"}
    resposta = requests.get(url_base, headers=headers)
    resposta.raise_for_status()
    soup = BeautifulSoup(resposta.text, "html.parser")
    links_pdf = [urljoin(url_base, a['href']) for a in soup.find_all('a', href=True) if a['href'].endswith('.pdf')]
    return links_pdf[0] if links_pdf else None

def baixar_pdf(pdf_url):
    resposta_pdf = requests.get(pdf_url)
    resposta_pdf.raise_for_status()
    with open("ultimo.pdf", "wb") as f:
        f.write(resposta_pdf.content)
    return "ultimo.pdf"

def normalizar(texto):
    return re.sub(r'\W+', '', texto).lower()

def procurar_palavra_no_pdf(arquivo_pdf, palavra_chave):
    palavra_chave_norm = normalizar(palavra_chave)
    with pdfplumber.open(arquivo_pdf) as pdf:
        texto_completo = "".join(page.extract_text() or "" for page in pdf.pages)
    return palavra_chave_norm in normalizar(texto_completo)

@app.get("/monitorar")
def monitorar():
    remetente = "testeconcursopdf@gmail.com"
    senha = "jfjriwzzbzqgputl"

    usuarios = db.collection("usuarios").stream()
    for doc in usuarios:
        dados = doc.to_dict()
        usuario_id = doc.id
        link = dados.get("link")
        palavra_chave = dados.get("palavra_chave")
        email_destino = dados.get("email")
        ultimo_pdf_url = dados.get("ultimo_pdf")

        if not link or not palavra_chave or not email_destino:
            print(f"⚠ Dados incompletos para {usuario_id}, ignorando...")
            continue

        try:
            pdf_url = baixar_pdf_mais_recente(link)
            if pdf_url and pdf_url != ultimo_pdf_url:
                print(f"🔔 Novo PDF detectado para {usuario_id}: {pdf_url}")
                arquivo = baixar_pdf(pdf_url)

                if procurar_palavra_no_pdf(arquivo, palavra_chave):
                    print(f"✅ Palavra '{palavra_chave}' encontrada.")
                    corpo = f"Encontramos um novo PDF no site {link} com a palavra-chave '{palavra_chave}'. Link: {pdf_url}"
                    enviar_email(email_destino, f"Novo PDF com '{palavra_chave}'", corpo, remetente, senha)
                else:
                    print(f"⚠ Palavra '{palavra_chave}' não encontrada no novo PDF.")

                db.collection("usuarios").document(usuario_id).update({"ultimo_pdf": pdf_url})
            else:
                print(f"Nenhum PDF novo para {usuario_id}.")

        except Exception as e:
            print(f"❌ Erro no monitoramento para {usuario_id}: {e}")

    return {"status": "OK", "msg": "Monitoramento concluído"}

