import os
import logging
import yfinance as yf
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Configuração de logs para monitoramento no Render
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot operacional! Use /analisar TICKER (ex: /analisar BBAS3)")

async def analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verifica se o usuário enviou o ticker
    if not context.args:
        await update.message.reply_text("Por favor, informe o ticker. Exemplo: /analisar BBAS3")
        return
        
    ticker = context.args[0].upper() + ".SA"
    msg = await update.message.reply_text(f"📊 Analisando {ticker}...")
    
    try:
        # Busca cotação atual
        ativo = yf.Ticker(ticker)
        cotacao = ativo.info.get('currentPrice', 'N/A')
        
        prompt = f"Analise o ativo {ticker}. Cotação atual: {cotacao}. Seja técnico e direto."
        api_key = os.environ.get('GEMINI_API_KEY')
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        # Lógica de Retry (Tenta 3 vezes antes de desistir)
        wait_time = 3
        for tentativa in range(3):
            resposta = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]})
            
            if resposta.status_code == 200:
                analise = resposta.json()['candidates'][0]['content']['parts'][0]['text']
                await msg.edit_text(f"📈 Análise {ticker}\n\n{analise}")
                return
            elif resposta.status_code == 429:
                await msg.edit_text(f"⏳ Sobrecarga (429), tentando novamente em {wait_time}s...")
                await asyncio.sleep(wait_time)
                wait_time *= 2 # Espera exponencial
            else:
                await msg.edit_text(f"Erro na IA (código {resposta.status_code})")
                return
        
        await msg.edit_text("❌ Erro: API indisponível após 3 tentativas.")
            
    except Exception as e:
        logging.error(f"Erro crítico: {e}")
        await msg.edit_text(f"Erro inesperado: Tente novamente mais tarde.")

if __name__ == '__main__':
    TOKEN = os.environ.get('TOKEN')
    
    if not TOKEN:
        print("ERRO: Token não definido!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("analisar", analisar))
        
        print("Bot rodando com sucesso!")
        app.run_polling()
