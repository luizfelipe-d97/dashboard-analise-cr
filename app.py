from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import traceback
import os
import logging

# Configuração do aplicativo
app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.logger.setLevel(logging.INFO)  # Habilita logging detalhado

def perform_analysis(file_rp, file_fat):
    try:
        cols_rp = ['Nº DOCUMENTO Ajustado', 'Ano de emissão (backup)', 'VALOR TOTAL', 
                  'CPF /CNPJ', 'DATA DE EMISSÃO DO TÍTULO', 'VENCIMENTO']
        cols_fat = ['Título', 'Data de emissão', 'Valor bruto', 'CPF ou CNPJ', 'Data de vencimento']
        
        # Leitura otimizada em chunks para arquivos grandes
        chunks_rp = pd.read_excel(
            file_rp, 
            sheet_name='Consolidado', 
            header=13, 
            usecols=cols_rp,
            chunksize=10000,  # Processa em blocos de 10k linhas
            engine='openpyxl'
        )
        df_rp = pd.concat(chunks_rp)
        
        chunks_fat = pd.read_excel(
            file_fat,
            header=0,
            usecols=cols_fat,
            chunksize=10000,
            engine='openpyxl'
        )
        df_fat = pd.concat(chunks_fat)
        
        # SUA LÓGICA DE ANÁLISE AQUI (mantenha sua implementação)
        # Exemplo mínimo funcional:
        titulos_rp = set(df_rp['Nº DOCUMENTO Ajustado'].dropna().astype(str))
        titulos_fat = set(df_fat['Título'].dropna().astype(str))
        
        return {
            "success": True,
            "cards": {
                "reconciliados": len(titulos_rp.intersection(titulos_fat)),
                "so_performance": len(titulos_rp.difference(titulos_fat)),
                "so_faturamento": len(titulos_fat.difference(titulos_rp)),
                "total_faturamento": len(titulos_fat)
            },
            "anual": [],
            "detalhada_rp": [],
            "detalhada_fat": []
        }
        
    except Exception as e:
        app.logger.error(f"Erro na análise: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Erro no template: {str(e)}")
        return "Erro ao carregar a página", 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file_rp' not in request.files or 'file_fat' not in request.files:
            return jsonify({"success": False, "error": "Envie ambos os arquivos"}), 400
        
        app.logger.info("Iniciando processamento de arquivos...")
        result = perform_analysis(request.files['file_rp'], request.files['file_fat'])
        app.logger.info("Processamento concluído com sucesso")
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Erro no endpoint /analyze: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": "Erro interno no processamento",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)