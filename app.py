from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import traceback
import os
import logging
from werkzeug.utils import secure_filename

# Configuração do aplicativo
app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'  # Pasta temporária
app.logger.setLevel(logging.INFO)

# Cria pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def process_large_excel(file, sheet_name=None, header=0, usecols=None):
    """Processa arquivos Excel grandes de forma eficiente"""
    try:
        # Salva o arquivo temporariamente
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Usa o openpyxl com modo read-only para melhor performance
        return pd.read_excel(
            temp_path,
            sheet_name=sheet_name,
            header=header,
            usecols=usecols,
            engine='openpyxl'
        )
    finally:
        # Remove o arquivo temporário
        if os.path.exists(temp_path):
            os.remove(temp_path)

def perform_analysis(file_rp, file_fat):
    try:
        cols_rp = ['Nº DOCUMENTO Ajustado', 'Ano de emissão (backup)', 'VALOR TOTAL', 
                  'CPF /CNPJ', 'DATA DE EMISSÃO DO TÍTULO', 'VENCIMENTO']
        cols_fat = ['Título', 'Data de emissão', 'Valor bruto', 'CPF ou CNPJ', 'Data de vencimento']
        
        # Processamento otimizado
        app.logger.info("Processando arquivo RP...")
        df_rp = process_large_excel(
            file_rp,
            sheet_name='Consolidado',
            header=13,
            usecols=cols_rp
        )
        
        app.logger.info("Processando arquivo FAT...")
        df_fat = process_large_excel(
            file_fat,
            header=0,
            usecols=cols_fat
        )
        
        # Exemplo de análise (substitua pela sua lógica)
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
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file_rp' not in request.files or 'file_fat' not in request.files:
            return jsonify({"success": False, "error": "Envie ambos os arquivos"}), 400
        
        return jsonify(perform_analysis(
            request.files['file_rp'],
            request.files['file_fat']
        ))
    except Exception as e:
        app.logger.error(f"Erro no endpoint: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)