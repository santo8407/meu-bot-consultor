async def analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Informe o ticker. Ex: /analisar BBAS3")
        return
        
    ticker = context.args[0].upper() + ".SA"
    
    # Envia mensagem inicial
    msg = await update.message.reply_text(f"📊 Analisando {ticker}...")
    
    try:
        ativo = yf.Ticker(ticker)
        cotacao = ativo.info.get('currentPrice', 'N/A')
        
        prompt = f"Analise o ativo {ticker}. Cotação atual: {cotacao}. Seja breve."
        api_key = os.environ.get('GEMINI_API_KEY')
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        resposta_ia = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]})
        
        if resposta_ia.status_code == 200:
            dados = resposta_ia.json()
            analise = dados['candidates'][0]['content']['parts'][0]['text']
            await msg.edit_text(f"📈 Análise {ticker}\n\n{analise}")
        elif resposta_ia.status_code == 429:
            await msg.edit_text("⚠️ API sobrecarregada. Aguarde 1 minuto e tente novamente.")
        else:
            await msg.edit_text(f"Erro na IA: {resposta_ia.status_code}")
            
    except Exception as e:
        await msg.edit_text(f"Erro ao processar: Tente novamente mais tarde.")
