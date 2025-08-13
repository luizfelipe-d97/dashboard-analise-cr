from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import traceback
import os
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_temp_file(file):
    """Salva arquivo temporariamente e retorna o caminho"""
    filename = secure_filename(file.filename)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(temp_path)
    return temp_path

def perform_analysis(file_rp_path, file_fat_path):
    try:
        # Configurações otimizadas para grandes arquivos
        read_opts = {
            'engine': 'openpyxl',
            'dtype': {
                'Nº DOCUMENTO Ajustado': 'string',
                'CPF /CNPJ': 'string',
                'CPF ou CNPJ': 'string'
            }
        }

        # Processa RP
        logger.info("Lendo arquivo RP...")
        df_rp = pd.read_excel(
            file_rp_path,
            sheet_name='Consolidado',
            header=13,
            usecols=['Nº DOCUMENTO Ajustado', 'Ano de emissão (backup)', 'VALOR TOTAL', 
                    'CPF /CNPJ', 'DATA DE EMISSÃO DO TÍTULO', 'VENCIMENTO'],
            **read_opts
        )

        # Processa FAT
        logger.info("Lendo arquivo FAT...")
        df_fat = pd.read_excel(
            file_fat_path,
            header=0,
            usecols=['Título', 'Data de emissão', 'Valor bruto', 'CPF ou CNPJ', 'Data de vencimento'],
            **read_opts
        )

        # Sua lógica de análise (exemplo simplificado)
        titulos_rp = set(df_rp['Nº DOCUMENTO Ajustado'].dropna().astype(str))
        titulos_fat = set(df_fat['Título'].dropna().astype(str))

        return {
            "success": True,
            "cards": {
                "reconciliados": len(titulos_rp & titulos_fat),
                "so_performance": len(titulos_rp - titulos_fat),
                "so_faturamento": len(titulos_fat - titulos_rp),
                "total_faturamento": len(titulos_fat)
            }
        }

    except Exception as e:
        logger.error(f"Erro na análise: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file_rp' not in request.files or 'file_fat' not in request.files:
            return jsonify({"success": False, "error": "Envie ambos os arquivos"}), 400

        # Salva arquivos temporariamente
        rp_path = save_temp_file(request.files['file_rp'])
        fat_path = save_temp_file(request.files['file_fat'])

        try:
            result = perform_analysis(rp_path, fat_path)
            return jsonify(result)
        finally:
            # Limpeza dos arquivos temporários
            os.remove(rp_path)
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