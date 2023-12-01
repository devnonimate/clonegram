from telethon import TelegramClient, events
import asyncio
from telethon.tl.functions.channels import ReadHistoryRequest
from telethon.sessions import MemorySession
import re
import datetime

# Constantes
ORIGINAL_CHANNEL_USERNAME = 'sbroletabrasileira'  # Substitua pelo nome do canal original
NOVO_CANAL_USERNAME = 'gbrole'  # Substitua pelo nome do novo canal
SESSION_FILE = MemorySession()

# Inicializa o cliente do Telegram
def iniciar_cliente():
    client = TelegramClient(SESSION_FILE, 25356283, 'efcf5005566af49047f19ccc708ed371')
    return client

# Função para modificar o link da mensagem
def modify_message_link(message):
    if message.text:
        modified_text = re.sub(r'Playtech - Roleta Brasileira', 'GreenBets - Roleta Brasileira', message.text)
        modified_text = re.sub(r'https://www.segurobet.com/\?btag=1176229&accounts=%2A&register=%2A', 'https://afiliados.greenbets.io/visit/?bta=62357&brand=greenbetsio', modified_text)
        return modified_text
    else:
        return ""

# Função principal assíncrona
async def main():
    # Inicializa o cliente
    client = iniciar_cliente()
    await client.start()

    # Obtém os objetos do canal original e do novo canal
    original_channel = await client.get_entity(ORIGINAL_CHANNEL_USERNAME)
    novo_canal = await client.get_entity(NOVO_CANAL_USERNAME)

    # Variáveis de controle
    mensagens_clonadas = 0
    green_count = 0
    red_count = 0
    is_clone_paused = False
    mensagem_anterior = None
    report_data = []

    # Manipulador para novas mensagens no canal original
    @client.on(events.NewMessage(chats=original_channel))
    async def handler(event):
        nonlocal mensagens_clonadas, green_count, red_count, is_clone_paused, mensagem_anterior, report_data

        # Verifica se o clone está pausado
        if is_clone_paused:
            return

        # Verifica se a mensagem é duplicada
        if mensagem_anterior and event.text == mensagem_anterior.text:
            # Apaga a mensagem duplicada no novo canal
            await client.delete_messages(novo_canal, [event.message.id])
        else:
            mensagem_anterior = event.message

        # Verifica se a mensagem contém "ANALISANDO"
        if "ANALISANDO" in event.text:
            modified_text = modify_message_link(event.message)
            await client.send_message(novo_canal, modified_text)

        # Verifica se a mensagem contém "ENTRADA CONFIRMADA"
        if "ENTRADA CONFIRMADA" in event.text:
            modified_text = modify_message_link(event.message)
            await client.send_message(novo_canal, modified_text)

        # Verifica se a mensagem contém "APOSTA ENCERRADA"
        if "APOSTA ENCERRADA" in event.text:
            modified_text = modify_message_link(event.message)
            await client.send_message(novo_canal, modified_text)
            mensagens_clonadas += 1
            timestamp = datetime.datetime.now().strftime("%H:%M")
            if "GREEN" in event.text:
                green_count += 1
                report_data.append(f"{timestamp} > Win✅")
            elif "RED" in event.text:
                red_count += 1
                report_data.append(f"{timestamp} > RED❌")

            # Remover mensagens com "ANALISANDO" do histórico do canal
            async for message in client.iter_messages(novo_canal):
                if "ANALISANDO" in message.text:
                    await client.delete_messages(novo_canal, message)

        # Verifica se o número de mensagens clonadas é igual a 3
        if mensagens_clonadas == 10:
            report = "\n".join(report_data)
            await client.send_message(novo_canal, f'RELATÓRIO:\n{report}')
            mensagens_clonadas = 0
            green_count = 0
            red_count = 0
            is_clone_paused = True

    # Apaga as mensagens de "ANALISANDO" restantes no novo canal
    async for message in client.iter_messages(novo_canal, search='ANALISANDO'):
        await message.delete()

    # Função para retomar o processo de clonagem
    async def resume_cloning():
        nonlocal is_clone_paused
        while True:
            now = datetime.datetime.now().time()
            if now.hour == 11 and now.minute == 0:
                is_clone_paused = False
            elif now.hour == 16 and now.minute == 0:
                is_clone_paused = False
            elif now.hour == 20 and now.minute == 0:
                is_clone_paused = False
            await asyncio.sleep(1)  # Verifica a cada minuto

    # Executa a função para retomar o processo de clonagem em segundo plano
    asyncio.ensure_future(resume_cloning())

    # Executa o cliente até que a conexão seja encerrada
    await client.run_until_disconnected()

# Executa a função principal assíncrona
asyncio.run(main())