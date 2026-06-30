import os
import logging
from flask import Flask
from threading import Thread
import yfinance as yf
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuração de Logs
logging.basicConfig(level=logging.INFO)

# Camada Flask para o Render manter o serviço online
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot esta online e operante"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Inicia o servidor web em uma thread separada
Thread(target=run_web).start()

# Configuração de Segurança (Chaves lidas do Render)
TOKEN = os.environ.get('TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

async def analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Por favor, informe o ticker. Exemplo: /analisar BBAS3")
        return
        
    ticker = context.args[0].upper() + ".SA"
    await update.message.reply_text(f"📊 Analisando {ticker}...")
    
    try:
        # Busca dados financeiros básicos
        ativo = yf.Ticker(ticker)
        cotacao = ativo.info.get('currentPrice', 'Não disponível')
        
        # Monta prompt para a IA
        prompt = f"Analise o ativo {ticker}. Cotação atual: {cotacao}. Dê uma visão técnica e fundamentalista curta."
        
        # Requisição para a API do Gemini
        resposta_ia = requests.post(API_URL, json={"contents": [{"parts": [{"text": prompt}]}]})
        analise = resposta_ia.json()['candidates'][0]['content']['parts'][0]['text']
        
        await update.message.reply_message(f"📈 Análise {ticker}\n\n{analise}")
    except Exception as e:
        await update.message.reply_text(f"Erro ao analisar: {str(e)}")

if __name__ == "__main__":
    # Inicia o bot do Telegram
    app_bot = Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("analisar", analisar))
    
    logging.info("Bot iniciado com sucesso na nuvem.")
    app_bot.run_polling()
