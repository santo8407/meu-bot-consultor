import os
import logging
import yfinance as yf
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

async def analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Informe o ticker. Ex: /analisar BBAS3")
        return
        
    ticker = context.args[0].upper() + ".SA"
    msg = await update.message.reply_text(f"📊 Analisando {ticker}...")
    
    try:
        ativo = yf.Ticker(ticker)
        cotacao = ativo.info.get('currentPrice', 'N/A')
        prompt = f"Analise o ativo {ticker}. Cotação: {cotacao}. Seja breve."
        api_key = os.environ.get('GEMINI_API_KEY')
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        # Lógica de Retry com Atraso
        wait_time = 2
        for i in range(3):  # Tenta até 3 vezes
            resposta = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]})
            if resposta.status_code == 200:
                analise = resposta.json()['candidates'][0]['content']['parts'][0]['text']
                return await msg.edit_text(f"📈 {ticker}\n\n{analise}")
            elif resposta.status_code == 429:
                await msg.edit_text(f"⏳ Sobrecarga (429), tentando novamente em {wait_time}s...")
                await asyncio.sleep(wait_time)
                wait_time *= 2
            else:
                break
        
        await msg.edit_text(f"❌ Erro na API após várias tentativas.")
            
    except Exception as e:
        await msg.edit_text(f"Erro: {str(e)}")

if __name__ == '__main__':
    TOKEN = os.environ.get('TOKEN')
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("analisar", analisar))
    print("Bot rodando!")
    app.run_polling()
