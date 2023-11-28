from telethon import TelegramClient, events
import asyncio
from telethon.tl.functions.channels import ReadHistoryRequest
from telethon.sessions import MemorySession
import re
import datetime

ORIGINAL_CHANNEL_USERNAME = 'sbroletabrasileira'  # Substitua pelo nome do canal original
NOVO_CANAL_USERNAME = 'greenbetsrb'  # Substitua pelo nome do novo canal
SESSION_FILE = MemorySession()

def iniciar_cliente():
    client = TelegramClient(SESSION_FILE, 25356283, 'efcf5005566af49047f19ccc708ed371')
    return client

async def main():
    client = iniciar_cliente()
    await client.start()
    original_channel = await client.get_entity(ORIGINAL_CHANNEL_USERNAME)
    novo_canal = await client.get_entity(NOVO_CANAL_USERNAME)

    mensagens_clonadas = 0
    green_count = 0
    red_count = 0
    is_clone_paused = False
    mensagem_anterior = None
    report_data = []

    @client.on(events.NewMessage(chats=original_channel))
    async def handler(event):
        nonlocal mensagens_clonadas, green_count, red_count, is_clone_paused, mensagem_anterior

        if is_clone_paused:
            return

        if "ANALISANDO" in event.text or "ENTRADA CONFIRMADA" in event.text or "APOSTA ENCERRADA" in event.text:
            modified_text = modify_message_link(event.message)
            await client.send_message(novo_canal, modified_text)
            if "APOSTA ENCERRADA" in event.text:
                mensagens_clonadas += 1
                timestamp = datetime.datetime.now().strftime("%H:%M")
                if "GREEN" in event.text:
                    green_count += 1
                    report_data.append(f"{timestamp} > Win✅")
                elif "RED" in event.text:   
                    red_count += 1
                    report_data.append(f"{timestamp} > RED❌")
                async for message in client.iter_messages(novo_canal, from_user='me', search='ANALISANDO'):
                    await message.delete()

        if mensagens_clonadas == 3:
            report = "\n".join(report_data)
            await client.send_message(novo_canal, f'RELATÓRIO:\n{report}')
            mensagens_clonadas = 0
            green_count = 0
            red_count = 0
            is_clone_paused = True

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
            await asyncio.sleep(60)  # Verifica a cada minuto

    asyncio.ensure_future(resume_cloning())
    await client.run_until_disconnected()

def modify_message_link(message):
    if message.text:
        modified_text = re.sub(r'Playtech - Roleta Brasileira', 'GreenBets - Roleta Brasileira', message.text)
        modified_text = re.sub(r'https://www.segurobet.com/\?btag=1176229&accounts=%2A&register=%2A', 'https://afiliados.greenbets.io/visit/?bta=62357&brand=greenbetsio', modified_text)
        return modified_text
    else:
        return ""

asyncio.run(main())