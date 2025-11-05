"""
Aplicação Flask - Backend do Classificador de Transações Bancárias
"""

import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
import shutil

# Importa as camadas de processamento
from src.layers.raw_layer import RawLayer
from src.layers.trusted_layer import TrustedLayer
from src.layers.business_layer import BusinessLayer
from src.layers.financial_analysis import FinancialAnalyzer
from src.utils.pdf_generator import FinancialPDFGenerator
from src.utils.executive_pdf_generator import ExecutivePDFGenerator


# Configurações da aplicação
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['OUTPUT_FOLDER'] = './output'
app.config['ALLOWED_EXTENSIONS'] = {'ofx'}

# Variável global para armazenar o DataFrame atual
current_df = None
current_categories = []
# Cache do último relatório gerado para a página (/api/relatorio)
# Usado para gerar o PDF sem reexecutar a IA
cached_report = None

# Garante que as pastas existem
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def cleanup_folders():
    """Limpa as pastas de upload e output"""
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
        if Path(folder).exists():
            shutil.rmtree(folder)
        Path(folder).mkdir(parents=True, exist_ok=True)


@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_files():
    """Processa os arquivos OFX enviados"""
    global current_df, current_categories
    
    try:
        # Verifica se há arquivos na requisição
        if 'files' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Limpa pastas antes de processar
        cleanup_folders()
        
        # Salva os arquivos enviados
        file_paths = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                file_paths.append(filepath)
            else:
                return jsonify({
                    'error': f'Arquivo não permitido: {file.filename}. Apenas arquivos .ofx são aceitos.'
                }), 400
        
        if not file_paths:
            return jsonify({'error': 'Nenhum arquivo OFX válido foi enviado'}), 400
        
        print(f"\n{'='*60}")
        print(f"🚀 INICIANDO PROCESSAMENTO")
        print(f"{'='*60}")
        print(f"📁 Arquivos recebidos: {len(file_paths)}")
        for fp in file_paths:
            print(f"   - {os.path.basename(fp)}")
        
        # ==== CAMADA RAW: Processa arquivos OFX e gera JSON ====
        raw_layer = RawLayer()
        json_path = os.path.join(app.config['OUTPUT_FOLDER'], 'raw_transactions.json')
        raw_result = raw_layer.execute(file_paths, json_path)
        
        # ==== CAMADA TRUSTED: Transforma JSON em DataFrame ====
        trusted_layer = TrustedLayer()
        df = trusted_layer.execute(json_path)
        
        # ==== CAMADA BUSINESS: Classifica transações com IA ====
        business_layer = BusinessLayer(regra_path='./src/prompts/regra.json')
        df_classificado = business_layer.execute(df)
        
        # Adiciona índice único para cada transação
        df_classificado['index'] = range(len(df_classificado))
        
        # Carrega categorias estruturadas do arquivo catetegorias.json
        with open('./src/prompts/catetegorias.json', 'r', encoding='utf-8') as f:
            categorias_data = json.load(f)
        
        # Extrai todas as subcontas para usar no dropdown
        categories_list = []
        for grupo in categorias_data['grupos']:
            for subconta in grupo['subcontas']:
                # Formato: "codigo - descricao"
                categories_list.append(f"{subconta['codigo']} - {subconta['descricao']}")
        
        # Armazena DataFrame e categorias globalmente
        current_df = df_classificado
        current_categories = sorted(categories_list)  # Ordena alfabeticamente
        
        # Salva resultado final em Excel
        output_excel = os.path.join(app.config['OUTPUT_FOLDER'], 'classified_transactions.xlsx')
        business_layer.save_to_excel(df_classificado, output_excel)
        
        print(f"\n{'='*60}")
        print(f"✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'message': f'✅ Processamento concluído! {len(df_classificado)} transações classificadas.',
            'total_files': len(file_paths),
            'total_transactions': len(df_classificado),
            'redirect': '/results'
        }), 200
        
    except Exception as e:
        print(f"\n❌ ERRO NO PROCESSAMENTO: {str(e)}\n")
        return jsonify({'error': f'Erro ao processar arquivos: {str(e)}'}), 500


@app.route('/download')
def download_file():
    """Faz download do arquivo Excel gerado"""
    try:
        output_excel = os.path.join(app.config['OUTPUT_FOLDER'], 'classified_transactions.xlsx')
        
        if not Path(output_excel).exists():
            return jsonify({'error': 'Arquivo não encontrado. Execute o processamento primeiro.'}), 404
        
        return send_file(
            output_excel,
            as_attachment=True,
            download_name='transacoes_classificadas.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao baixar arquivo: {str(e)}'}), 500


@app.route('/results')
def results():
    """Página de resultados"""
    return render_template('results.html')


@app.route('/api/results')
def api_results():
    """Retorna os dados processados em JSON"""
    global current_df, current_categories
    
    if current_df is None:
        return jsonify({'error': 'Nenhum dado processado. Execute o processamento primeiro.'}), 404
    
    try:
        # Converte DataFrame para lista de dicionários
        transactions = current_df.to_dict('records')
        
        # Converte valores numpy para tipos Python nativos
        for t in transactions:
            for key, value in t.items():
                if pd.isna(value):
                    t[key] = None
                elif hasattr(value, 'item'):  # numpy types
                    t[key] = value.item()
        
        return jsonify({
            'transactions': transactions,
            'categories': current_categories,
            'total': len(transactions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar resultados: {str(e)}'}), 500


@app.route('/api/save', methods=['POST'])
def api_save():
    """Salva as edições feitas pelo usuário"""
    global current_df
    
    if current_df is None:
        return jsonify({'error': 'Nenhum dado processado.'}), 404
    
    try:
        data = request.get_json()
        edits = data.get('edits', {})
        
        if not edits:
            return jsonify({'error': 'Nenhuma edição foi enviada.'}), 400
        
        # Aplica as edições no DataFrame
        for index_str, new_classification in edits.items():
            index = int(index_str)
            if index in current_df['index'].values:
                current_df.loc[current_df['index'] == index, 'classificacao_sugerida'] = new_classification
        
        # Salva o DataFrame atualizado em Excel
        output_excel = os.path.join(app.config['OUTPUT_FOLDER'], 'classified_transactions.xlsx')
        current_df.to_excel(output_excel, index=False, engine='openpyxl')
        
        print(f"✅ {len(edits)} edições salvas com sucesso!")
        
        return jsonify({
            'success': True,
            'message': f'✅ {len(edits)} alterações salvas com sucesso!',
            'edited_count': len(edits)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao salvar: {str(e)}'}), 500


@app.route('/health')
def health():
    """Endpoint de health check"""
    return jsonify({'status': 'ok', 'message': 'Servidor funcionando'}), 200


@app.route('/relatorio')
def relatorio():
    """Página do relatório financeiro executivo com DADOS REAIS dos arquivos OFX"""
    global current_df
    
    if current_df is None:
        return render_template('index.html')
    
    # Usar template novo que exibe APENAS dados reais dos arquivos OFX
    # O template antigo (relatorio_executivo.html) tinha valores hardcoded fictícios
    return render_template('relatorio_executivo_real.html')


@app.route('/relatorio-executivo-mockup')
def relatorio_executivo_mockup():
    """Template antigo com dados de exemplo (apenas para referência visual)"""
    global current_df
    
    if current_df is None:
        return render_template('index.html')
    
    # Template antigo com dados hardcoded - mantido apenas para referência
    # ATENÇÃO: Este template contém valores fictícios de exemplo
    return render_template('relatorio_executivo.html')


@app.route('/api/relatorio')
def api_relatorio():
    """API que retorna dados do relatório financeiro"""
    global current_df, cached_report
    
    if current_df is None:
        return jsonify({'error': 'Nenhum dado processado'}), 404
    
    try:
        # Gera análise financeira (dados reais)
        analyzer = FinancialAnalyzer()
        report = analyzer.generate_full_report(current_df)

        # Gera análise estratégica com IA para a TELA também
        try:
            from src.layers.strategic_analyzer import StrategicAnalyzer
            strategic_analyzer = StrategicAnalyzer()
            strategic_report = strategic_analyzer.generate_full_strategic_report(
                financial_summary=report['sumario'],
                monthly_analysis=report['tendencia_mensal'],
                category_analysis=report['analise_categorias']
            )
            report['strategic_report'] = strategic_report
        except Exception as ia_err:
            # Não derruba a API se a IA falhar; apenas registra a mensagem
            print(f"\n❌ ERRO AO GERAR ANÁLISE ESTRATÉGICA: {str(ia_err)}")
            import traceback
            traceback.print_exc()
            report['strategic_report'] = {
                'error': f'Falha ao gerar análise estratégica: {str(ia_err)}'
            }
        
        # Armazena em cache para reaproveitar no PDF sem reexecutar IA
        cached_report = report
        
        # Adiciona headers para desabilitar cache no navegador
        response = jsonify(report)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response, 200
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar relatório: {str(e)}'}), 500


@app.route('/relatorio/download')
def download_relatorio():
    """Download do relatório executivo em PDF com análises REAIS"""
    global current_df, cached_report
    
    if current_df is None:
        return jsonify({'error': 'Nenhum dado processado'}), 404
    
    try:
        # Usa o relatório em cache (gerado pela página /api/relatorio) para NÃO reexecutar a IA
        # Caso o cache não exista, gera apenas a parte financeira (sem IA)
        if cached_report is not None:
            print("\n� Usando relatório em cache para gerar PDF (sem reexecutar IA)...")
            financial_report = dict(cached_report)
            strategic_report = cached_report.get('strategic_report', {
                'key_events': [],
                'swot': {
                    'forcas': [], 'fraquezas': [], 'oportunidades': [], 'ameacas': []
                },
                'action_plans': [],
                'revenue_analysis': {'analise_completa': ''},
                'generated_at': None
            })
            # Remove a chave estratégica do bloco financeiro, se existir
            financial_report.pop('strategic_report', None)
        else:
            print("\n⚠️ Cache vazio. Gerando SOMENTE a análise financeira para o PDF (sem IA)...")
            analyzer = FinancialAnalyzer()
            financial_report = analyzer.generate_full_report(current_df)
            strategic_report = {
                'key_events': [],
                'swot': {
                    'forcas': [], 'fraquezas': [], 'oportunidades': [], 'ameacas': []
                },
                'action_plans': [],
                'revenue_analysis': {'analise_completa': ''},
                'generated_at': None
            }
        
        # Gera PDF executivo V2 (com dados reais)
        print("📄 Gerando PDF executivo...")
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], 'relatorio_executivo.pdf')
        from src.utils.executive_pdf_generator_v2 import ExecutivePDFGeneratorV2
        executive_pdf = ExecutivePDFGeneratorV2()
        executive_pdf.generate_executive_report(financial_report, strategic_report, pdf_path)
        
        # Retorna PDF
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'relatorio_executivo_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar PDF: {str(e)}'}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏦 CLASSIFICADOR DE TRANSAÇÕES BANCÁRIAS")
    print("="*60)
    print("🌐 Servidor iniciado em: http://localhost:5000")
    print("📝 Acesse o navegador para fazer upload dos arquivos OFX")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
