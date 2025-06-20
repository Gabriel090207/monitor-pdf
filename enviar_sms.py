from twilio.rest import Client

def enviar_sms():
    account_sid = 'AC1258482b6fffbcf6b349b6b0c15aa18e'  # seu Account SID da Twilio
    auth_token = '78d750af88f290d862918c652d1c2b86'  # seu Auth Token da Twilio

    client = Client(account_sid, auth_token)

    numero_destino = input("Digite o número do destinatário com código do país (ex: +5516999999999): ")
    mensagem = input("Digite a mensagem para enviar: ")

    try:
        message = client.messages.create(
            body=mensagem,
            from_='+5516993072704',  # seu número Twilio com código do país
            to=numero_destino  # número de destino informado pelo usuário
        )
        print(f"Mensagem enviada com sucesso! SID: {message.sid}")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

if __name__ == "__main__":
    enviar_sms()
