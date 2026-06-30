import os
import logging
import yfinance as yf
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuração básica de log para vermos erros no console do Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot iniciado! Use /analisar TICKER (ex: /analisar BBAS3)")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Bot ativo. Você enviou: {update.message.text}")

async def analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Por favor, informe o ticker. Exemplo: /analisar BBAS3")
        return
        
    ticker = context.args[0].upper() + ".SA"
    await update.message.reply_text(f"📊 Analisando {ticker}...")
    
    try:
        # Busca dados financeiros
        ativo = yf.Ticker(ticker)
        cotacao = ativo.info.get('currentPrice', 'Não disponível')
        
        # Monta prompt
        prompt = f"Analise o ativo {ticker}. Cotação atual: {cotacao}. Dê uma visão técnica e fundamentalista curta."
        
        # Requisição Gemini
        api_key = os.environ.get('GEMINI_API_KEY')
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        resposta_ia = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]})
        
        if resposta_ia.status_code == 200:
            analise = resposta_ia.json()['candidates'][0]['content']['parts'][0]['text']
            await update.message.reply_text(f"📈 Análise {ticker}\n\n{analise}")
        else:
            await update.message.reply_text(f"Erro na IA: {resposta_ia.text}")
            
    except Exception as e:
        logging.error(f"Erro crítico: {e}")
        await update.message.reply_text(f"Erro ao processar: {str(e)}")

if __name__ == "__main__":
    TOKEN = os.environ.get('TOKEN')
    if not TOKEN:
        print("ERRO: Variável TOKEN não encontrada no Render!")
    else:
        print("Token carregado. Iniciando Bot...")
        app_bot = Application.builder().token(TOKEN).build()
        
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CommandHandler("analisar", analisar))
        # Filtro corrigido com parênteses
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
        
        print("Bot rodando com sucesso!")
        app_bot.run_polling()
