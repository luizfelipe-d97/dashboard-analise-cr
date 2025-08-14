from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import traceback
import os
import logging
from werkzeug.utils import secure_filename

# Configuração do app
app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_temp_file(file):
    """Salva arquivo temporariamente com nome seguro"""
    filename = secure_filename(file.filename)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(temp_path)
    return temp_path

def perform_analysis(file_rp_path, file_fat_path):
    try:
        # COLUNAS ESPECÍFICAS (garanta que os nomes estão EXATAMENTE iguais aos seus arquivos)
        COLS_RP = [
            'Nº DOCUMENTO Ajustado', 
            'Ano de emissão (backup)', 
            'VALOR TOTAL', 
            'CPF /CNPJ', 
            'DATA DE EMISSÃO DO TÍTULO', 
            'VENCIMENTO'
        ]
        
        COLS_FAT = [
            'Título', 
            'Data de emissão', 
            'Valor bruto', 
            'CPF ou CNPJ', 
            'Data de vencimento'
        ]

        # LEITURA DOS ARQUIVOS (apenas colunas necessárias)
        logger.info("Processando Relatório de Performance...")
        df_rp = pd.read_excel(
            file_rp_path,
            sheet_name='Consolidado',  # Força ler apenas esta aba
            header=13,                 # Linha do cabeçalho real
            usecols=COLS_RP,           # Apenas estas colunas
            engine='openpyxl'
        )
        
        logger.info("Processando Faturamento...")
        df_fat = pd.read_excel(
            file_fat_path,
            header=0,
            usecols=COLS_FAT,
            engine='openpyxl'
        )

        # --- LÓGICA COMPLETA DE ANÁLISE ---
        
        # 1. Análise de Títulos
        titulos_rp = set(df_rp['Nº DOCUMENTO Ajustado'].dropna().astype(str))
        titulos_fat = set(df_fat['Título'].dropna().astype(str))
        
        # 2. Análise Anual (se necessário)
        df_rp['Ano de emissão (backup)'] = pd.to_numeric(df_rp['Ano de emissão (backup)'], errors='coerce')
        df_fat['Ano'] = pd.to_datetime(df_fat['Data de emissão']).dt.year
        
        # 3. Cálculos (exemplo - adapte conforme sua necessidade)
        analise_anual = df_rp.groupby('Ano de emissão (backup)')['VALOR TOTAL'].sum().to_dict()
        
        # 4. Resultados
        return {
            "success": True,
            "cards": {
                "reconciliados": len(titulos_rp & titulos_fat),
                "so_performance": len(titulos_rp - titulos_fat),
                "so_faturamento": len(titulos_fat - titulos_rp),
                "total_faturamento": len(titulos_fat)
            },
            "anual": analise_anual,
            "detalhada_rp": df_rp[['CPF /CNPJ', 'VALOR TOTAL']].to_dict('records'),
            "detalhada_fat": df_fat[['CPF ou CNPJ', 'Valor bruto']].to_dict('records')
        }

    except Exception as e:
        logger.error(f"Erro na análise: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file_rp' not in request.files or 'file_fat' not in request.files:
            return jsonify({"success": False, "error": "Envie ambos os arquivos"}), 400

        # Processamento seguro
        rp_path = save_temp_file(request.files['file_rp'])
        fat_path = save_temp_file(request.files['file_fat'])

        try:
            result = perform_analysis(rp_path, fat_path)
            return jsonify(result)
        finally:
            # Limpeza
            if os.path.exists(rp_path):
                os.remove(rp_path)
            if os.path.exists(fat_path):
                os.remove(fat_path)

    except Exception as e:
        logger.error(f"Erro no endpoint: {traceback.format_exc()}")
        return jsonify({"success": False, "error": "Erro interno"}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)