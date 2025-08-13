from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import traceback
import os

# Configuração explícita da pasta de templates
app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

def perform_analysis(file_rp, file_fat):
    try:
        cols_rp = ['Nº DOCUMENTO Ajustado', 'Ano de emissão (backup)', 'VALOR TOTAL', 
                  'CPF /CNPJ', 'DATA DE EMISSÃO DO TÍTULO', 'VENCIMENTO']
        cols_fat = ['Título', 'Data de emissão', 'Valor bruto', 'CPF ou CNPJ', 'Data de vencimento']
        
        # Leitura otimizada
        df_rp = pd.read_excel(file_rp, sheet_name='Consolidado', header=13, usecols=cols_rp)
        df_fat = pd.read_excel(file_fat, header=0, usecols=cols_fat)
        
        # Sua lógica de análise aqui...
        # (Mantenha sua implementação atual)

        return {
            "success": True,
            "cards": {
                "reconciliados": 0,  # Substitua por seus valores reais
                "so_performance": 0,
                "so_faturamento": 0,
                "total_faturamento": 0
            },
            "anual": [],
            "detalhada_rp": [],
            "detalhada_fat": []
        }
    except Exception as e:
        print(f"Erro na análise: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

@app.route('/')
def home():
    try:
        # Debug: Verifique se o template existe
        template_path = os.path.join(app.template_folder, 'index.html')
        if not os.path.exists(template_path):
            return f"Template não encontrado em: {template_path}", 404
        return render_template('index.html')
    except Exception as e:
        return f"Erro ao renderizar template: {str(e)}", 500

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file_rp' not in request.files or 'file_fat' not in request.files:
        return jsonify({"success": False, "error": "Envie ambos os arquivos"})
    return jsonify(perform_analysis(request.files['file_rp'], request.files['file_fat']))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)