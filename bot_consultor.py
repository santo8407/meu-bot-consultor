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

# Configuração Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot esta online"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Inicia o Flask em uma Thread
Thread(target=run_web).start()

# Função do Bot
async def analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Informe o ticker. Ex: /analisar BBAS3")
        return
    ticker = context.args[0].upper() + ".SA"
    await update.message.reply_text(f"📊 Analisando {ticker}...")
    try:
        ativo = yf.Ticker(ticker)
        cotacao = ativo.info.get('currentPrice', 'N/A')
        prompt = f"Analise o ativo {ticker}. Cotação: {cotacao}."
        API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={os.environ.get('GEMINI_API_KEY')}"
        resposta_ia = requests.post(API_URL, json={"contents": [{"parts": [{"text": prompt}]}]})
        analise = resposta_ia.json()['candidates'][0]['content']['parts'][0]['text']
        await update.message.reply_text(f"📈 {ticker}\n\n{analise}")
    except Exception as e:
        await update.message.reply_text(f"Erro: {str(e)}")

# Execução Principal
if __name__ == "__main__":
    TOKEN = os.environ.get('TOKEN')
    app_bot = Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("analisar", analisar))
    print("Iniciando o bot do Telegram...")
    app_bot.run_polling()
