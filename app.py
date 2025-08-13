from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import traceback
import os

def perform_analysis(file_rp, file_fat):
    try:
        cols_rp = ['Nº DOCUMENTO Ajustado', 'Ano de emissão (backup)', 'VALOR TOTAL', 'CPF /CNPJ', 'DATA DE EMISSÃO DO TÍTULO', 'VENCIMENTO']
        cols_fat = ['Título', 'Data de emissão', 'Valor bruto', 'CPF ou CNPJ', 'Data de vencimento']
        
        # Leitura otimizada em chunks
        chunks_rp = pd.read_excel(file_rp, sheet_name='Consolidado', header=13, 
                                usecols=cols_rp, chunksize=10000, engine='openpyxl')
        df_rp = pd.concat(chunks_rp)
        
        chunks_fat = pd.read_excel(file_fat, header=0, usecols=cols_fat, 
                                 chunksize=10000, engine='openpyxl')
        df_fat = pd.concat(chunks_fat)
        
        # Restante da sua lógica de análise...
        # (Manter o mesmo código que você já tem para as análises)

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

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file_rp' not in request.files or 'file_fat' not in request.files:
        return jsonify({"success": False, "error": "Arquivos não encontrados."})
    
    file_rp = request.files['file_rp']
    file_fat = request.files['file_fat']
    
    results = perform_analysis(file_rp, file_fat)
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)