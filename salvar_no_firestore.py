import firebase_admin
from firebase_admin import credentials, firestore

def iniciar_firestore():
    cred = credentials.Certificate("chave-firebase.json")  # Substitua pelo nome da sua chave JSON
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

def salvar_dados(usuario_id, dados):
    db = iniciar_firestore()
    doc_ref = db.collection('usuarios').document(usuario_id)
    doc_ref.set(dados)
    print(f"✅ Dados salvos para o usuário {usuario_id}")

if __name__ == "__main__":
    usuario_id = input("Digite um identificador único do usuário (ex: email, CPF): ")
    site = input("Digite o site monitorado: ")
    palavra_chave = input("Digite a palavra-chave: ")

    dados = {
        'site': site,
        'palavra_chave': palavra_chave
    }

    salvar_dados(usuario_id, dados)
