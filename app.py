from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import traceback
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Aceita até 50MB

def perform_analysis(file_rp, file_fat):
    try:
        # Leitura em chunks para arquivos grandes
        chunks_rp = pd.read_excel(
            file_rp, 
            sheet_name='Consolidado', 
            header=13, 
            usecols=['Nº DOCUMENTO Ajustado', 'Ano de emissão (backup)', 'VALOR TOTAL', 'CPF /CNPJ', 'DATA DE EMISSÃO DO TÍTULO', 'VENCIMENTO'],
            chunksize=10000,
            engine='openpyxl'
        )
        df_rp = pd.concat(chunks_rp)
        
        # ... (restante da sua lógica de análise) ...

        return {
            "success": True,
            "cards": { "reconciliados": reconciliados, "so_performance": so_rp, "so_faturamento": so_fat, "total_faturamento": len(titulos_fat) },
            "anual": df_anual.reset_index().to_dict(orient='records'),
            "detalhada_rp": analise_rp.reset_index().to_dict(orient='records'),
            "detalhada_fat": analise_fat.reset_index().to_dict(orient='records')
        }
    except Exception as e:
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file_rp' not in request.files or 'file_fat' not in request.files:
        return jsonify({"success": False, "error": "Envie ambos os arquivos"})
    
    return jsonify(perform_analysis(request.files['file_rp'], request.files['file_fat']))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)