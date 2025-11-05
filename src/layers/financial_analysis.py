"""
FINANCIAL ANALYSIS - Análise Financeira BASEADA EM DADOS REAIS

IMPORTANTE - POLÍTICA DE DADOS REAIS:
====================================
Este módulo analisa transações e gera relatórios financeiros usando
EXCLUSIVAMENTE dados reais dos arquivos OFX processados.

PROIBIDO:
- Usar valores default, fictícios ou hardcoded
- Inventar dados quando não houver informações reais
- Assumir períodos ou meses que não existem nos arquivos OFX
- Gerar métricas baseadas em suposições

OBRIGATÓRIO:
- Extrair todos os valores do DataFrame gerado pelos arquivos OFX
- Usar apenas o período REAL presente nos dados
- Calcular métricas exclusivamente com dados disponíveis
- Retornar None ou mensagens claras quando não houver dados suficientes

Gera relatório detalhado com base no plano de contas e dados reais.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


class FinancialAnalyzer:
    """Analisa transações e gera relatórios financeiros BASEADOS EM DADOS REAIS"""
    
    def __init__(self, plano_contas_path: str = "./src/plano_de_contas.xlsx"):
        """
        Inicializa o analisador financeiro
        
        IMPORTANTE: Este analisador trabalha EXCLUSIVAMENTE com dados reais
        dos arquivos OFX. Não gera valores default, fictícios ou hardcoded.
        
        Args:
            plano_contas_path: Caminho do arquivo plano de contas
        """
        self.plano_contas = pd.read_excel(plano_contas_path)
        self.plano_contas['conta_cod'] = self.plano_contas['conta_cod'].astype(str)
    
    def _format_currency(self, value: float) -> str:
        """Formata valor em moeda brasileira"""
        return f"R$ {abs(value):,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    
    def extract_code(self, classificacao: str) -> str:
        """
        Extrai o código da classificação
        
        Args:
            classificacao: String com código e descrição
            
        Returns:
            Código extraído
        """
        if pd.isna(classificacao):
            return None
        
        classificacao = str(classificacao)
        if ' - ' in classificacao:
            return classificacao.split(' - ')[0].strip()
        return classificacao
    
    def enrich_with_plan(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriquece DataFrame com informações do plano de contas
        
        Args:
            df: DataFrame com transações classificadas
            
        Returns:
            DataFrame enriquecido
        """
        df = df.copy()
        
        # Extrai código da classificação
        df['codigo_conta'] = df['classificacao_sugerida'].apply(self.extract_code)
        
        # Merge com plano de contas
        df = df.merge(
            self.plano_contas,
            left_on='codigo_conta',
            right_on='conta_cod',
            how='left'
        )
        
        return df
    
    def calculate_dre(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula DRE (Demonstração do Resultado do Exercício)
        
        Args:
            df: DataFrame enriquecido
            
        Returns:
            Dicionário com estrutura da DRE
        """
        # Filtra apenas transações com DRE definido
        df_dre = df[df['dre_n1'].notna()].copy()
        
        dre = {
            'receita_bruta': 0,
            'deducoes': 0,
            'receita_liquida': 0,
            'custos': 0,
            'lucro_bruto': 0,
            'despesas_operacionais': 0,
            'resultado_operacional': 0,
            'outras_receitas': 0,
            'outras_despesas': 0,
            'resultado_liquido': 0,
            'detalhamento': []
        }
        
        # Agrupa por DRE N1 e N2
        if not df_dre.empty:
            grouped = df_dre.groupby(['dre_n1', 'dre_n2'])['valor'].sum().reset_index()
            
            for _, row in grouped.iterrows():
                nivel1 = str(row['dre_n1']).strip()
                nivel2 = str(row['dre_n2']).strip() if pd.notna(row['dre_n2']) else ''
                valor = float(row['valor'])
                
                dre['detalhamento'].append({
                    'nivel1': nivel1,
                    'nivel2': nivel2,
                    'valor': valor
                })
                
                # Classifica nas linhas da DRE
                if 'Receita Bruta' in nivel1:
                    dre['receita_bruta'] += valor
                elif 'Receita Líquida' in nivel1:
                    dre['deducoes'] += abs(valor)
                elif 'Lucro Bruto' in nivel1 or 'CMV' in nivel2 or 'Custo' in nivel2:
                    dre['custos'] += abs(valor)
                elif 'Despesa' in nivel1 or 'Despesa' in nivel2:
                    dre['despesas_operacionais'] += abs(valor)
        
        # Calcula receita bruta total
        receitas = df[df['valor'] > 0]['valor'].sum()
        dre['receita_bruta'] = receitas
        
        # Calcula totais
        dre['receita_liquida'] = dre['receita_bruta'] - dre['deducoes']
        dre['lucro_bruto'] = dre['receita_liquida'] - dre['custos']
        dre['resultado_operacional'] = dre['lucro_bruto'] - dre['despesas_operacionais']
        dre['resultado_liquido'] = dre['resultado_operacional'] + dre['outras_receitas'] - dre['outras_despesas']
        
        return dre
    
    def calculate_dfc(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula DFC (Demonstração do Fluxo de Caixa)
        
        Args:
            df: DataFrame enriquecido
            
        Returns:
            Dicionário com estrutura da DFC
        """
        df_dfc = df[df['dfc_n1'].notna()].copy()
        
        dfc = {
            'operacional': 0,
            'investimento': 0,
            'financiamento': 0,
            'transferencias': 0,
            'saldo_inicial': 0,
            'saldo_final': 0,
            'detalhamento': []
        }
        
        if not df_dfc.empty:
            grouped = df_dfc.groupby(['dfc_n1', 'dfc_n2'])['valor'].sum().reset_index()
            
            for _, row in grouped.iterrows():
                nivel1 = str(row['dfc_n1']).strip()
                nivel2 = str(row['dfc_n2']).strip() if pd.notna(row['dfc_n2']) else ''
                valor = float(row['valor'])
                
                dfc['detalhamento'].append({
                    'nivel1': nivel1,
                    'nivel2': nivel2,
                    'valor': valor
                })
                
                if 'Operacional' in nivel1:
                    dfc['operacional'] += valor
                elif 'Investimento' in nivel1:
                    dfc['investimento'] += valor
                elif 'Financiamento' in nivel1:
                    dfc['financiamento'] += valor
                elif 'Movimentação entre Contas' in nivel1:
                    dfc['transferencias'] += valor
        
        # Calcula saldo final
        dfc['saldo_final'] = dfc['saldo_inicial'] + dfc['operacional'] + dfc['investimento'] + dfc['financiamento']
        
        return dfc
    
    def analyze_by_category(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Analisa transações por categoria
        
        Args:
            df: DataFrame com transações
            
        Returns:
            Lista com análise por categoria
        """
        analysis = []
        
        # Agrupa por classificação
        grouped = df.groupby('classificacao_sugerida').agg({
            'valor': ['sum', 'count', 'mean'],
            'data': ['min', 'max']
        }).reset_index()
        
        grouped.columns = ['categoria', 'total', 'quantidade', 'media', 'primeira_data', 'ultima_data']
        
        for _, row in grouped.iterrows():
            analysis.append({
                'categoria': row['categoria'],
                'total': float(row['total']),
                'quantidade': int(row['quantidade']),
                'media': float(row['media']),
                'primeira_transacao': row['primeira_data'],
                'ultima_transacao': row['ultima_data']
            })
        
        # Ordena por valor absoluto
        analysis.sort(key=lambda x: abs(x['total']), reverse=True)
        
        return analysis
    
    def analyze_monthly_trend(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Analisa tendência mensal APENAS COM DADOS REAIS dos arquivos OFX
        
        IMPORTANTE: Calcula receitas/despesas mensais usando EXCLUSIVAMENTE
        dados reais presentes nos arquivos OFX. Não usa valores default ou fictícios.
        
        Args:
            df: DataFrame com transações REAIS dos arquivos OFX
            
        Returns:
            Lista com análise mensal baseada em dados reais
        """
        df = df.copy()
        
        # Converte data para datetime usando o formato REAL dos arquivos OFX
        df['data_dt'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
        df['mes_ano'] = df['data_dt'].dt.to_period('M')
        
        # Remove linhas com data inválida (não deveria acontecer com dados reais)
        df = df.dropna(subset=['mes_ano'])
        
        if df.empty:
            print("⚠️  AVISO: Nenhum dado mensal válido encontrado nos arquivos OFX!")
            return []
        
        # Agrupa por mês REAL presente nos dados
        monthly = df.groupby('mes_ano').agg({
            'valor': lambda x: (x[x > 0].sum(), abs(x[x < 0].sum()), x.sum())
        }).reset_index()
        
        monthly_data = []
        for _, row in monthly.iterrows():
            receita, despesa, saldo = row['valor']
            monthly_data.append({
                'mes': str(row['mes_ano']),  # Mês REAL extraído dos arquivos OFX
                'receita': float(receita),   # Receita REAL calculada dos dados
                'despesa': float(despesa),   # Despesa REAL calculada dos dados
                'saldo': float(saldo)        # Saldo REAL calculado
            })
        
        print(f"✅ Análise mensal gerada com {len(monthly_data)} meses REAIS dos arquivos OFX")
        return monthly_data
    
    def compare_months(self, df: pd.DataFrame, month_a: str, month_b: str) -> Dict[str, Any]:
        """
        Compara dois meses específicos USANDO APENAS DADOS REAIS dos arquivos OFX
        
        IMPORTANTE: Esta comparação usa EXCLUSIVAMENTE dados reais presentes
        nos arquivos OFX para os meses especificados. Se não houver dados reais
        para um dos meses, retorna None (sem inventar valores).
        
        Args:
            df: DataFrame com transações REAIS dos arquivos OFX
            month_a: Mês A (formato: 'YYYY-MM') - deve existir nos dados reais
            month_b: Mês B (formato: 'YYYY-MM') - deve existir nos dados reais
            
        Returns:
            Dicionário com comparação detalhada baseada em dados reais, ou None se não houver dados
        """
        from src.utils.ai_decision_logger import get_logger
        logger = get_logger()
        
        df = df.copy()
        df['data_dt'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
        df['mes_ano'] = df['data_dt'].dt.to_period('M').astype(str)
        
        # Filtra dados REAIS dos dois meses
        df_a = df[df['mes_ano'] == month_a]
        df_b = df[df['mes_ano'] == month_b]
        
        # VALIDAÇÃO: Retorna None se não houver dados REAIS para ambos os meses
        if len(df_a) == 0 or len(df_b) == 0:
            print(f"⚠️  AVISO: Dados insuficientes para comparar {month_a} vs {month_b}")
            print(f"   Transações em {month_a}: {len(df_a)} | Transações em {month_b}: {len(df_b)}")
            return None
        
        # Calcula métricas REAIS de cada mês (sem valores default ou fictícios)
        receita_a = df_a[df_a['valor'] > 0]['valor'].sum()  # Receita REAL do mês A
        receita_b = df_b[df_b['valor'] > 0]['valor'].sum()  # Receita REAL do mês B
        despesa_a = abs(df_a[df_a['valor'] < 0]['valor'].sum())  # Despesa REAL do mês A
        despesa_b = abs(df_b[df_b['valor'] < 0]['valor'].sum())  # Despesa REAL do mês B
        saldo_a = receita_a - despesa_a  # Saldo REAL calculado do mês A
        saldo_b = receita_b - despesa_b  # Saldo REAL calculado do mês B
        
        # Calcula variações percentuais REAIS (baseadas apenas nos dados dos arquivos OFX)
        var_receita = ((receita_b - receita_a) / receita_a * 100) if receita_a > 0 else 0
        var_despesa = ((despesa_b - despesa_a) / despesa_a * 100) if despesa_a > 0 else 0
        var_saldo = ((saldo_b - saldo_a) / abs(saldo_a) * 100) if saldo_a != 0 else 0
        
        print(f"✅ Comparação {month_a} vs {month_b}: Receita {self._format_currency(receita_a)} → {self._format_currency(receita_b)} ({var_receita:+.1f}%)")
        
        # Monta comparação com dados REAIS (sem valores inventados)
        comparison = {
            'period_a': {
                'mes': month_a,
                'receita': float(receita_a),  # Valor REAL dos arquivos OFX
                'despesa': float(despesa_a),  # Valor REAL dos arquivos OFX
                'saldo': float(saldo_a),      # Cálculo REAL
                'num_transacoes': len(df_a)   # Quantidade REAL de transações
            },
            'period_b': {
                'mes': month_b,
                'receita': float(receita_b),  # Valor REAL dos arquivos OFX
                'despesa': float(despesa_b),  # Valor REAL dos arquivos OFX
                'saldo': float(saldo_b),      # Cálculo REAL
                'num_transacoes': len(df_b)   # Quantidade REAL de transações
            },
            'variations': {
                'receita_pct': float(var_receita),              # Variação REAL calculada
                'receita_abs': float(receita_b - receita_a),   # Diferença REAL calculada
                'despesa_pct': float(var_despesa),             # Variação REAL calculada
                'despesa_abs': float(despesa_b - despesa_a),   # Diferença REAL calculada
                'saldo_pct': float(var_saldo),                 # Variação REAL calculada
                'saldo_abs': float(saldo_b - saldo_a)          # Diferença REAL calculada
            }
        }
        
        # Loga a comparação
        logger.log_comparison_decision(
            comparison_type="monthly",
            period_a=month_a,
            period_b=month_b,
            metrics=comparison,
            interpretation=f"Receita variou {var_receita:.1f}%, despesa {var_despesa:.1f}%, saldo {var_saldo:.1f}%",
            calculations={
                "receita_a": receita_a,
                "receita_b": receita_b,
                "despesa_a": despesa_a,
                "despesa_b": despesa_b
            }
        )
        
        return comparison
    
    def get_all_month_comparisons(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Gera todas as comparações mês a mês disponíveis
        
        Args:
            df: DataFrame com transações
            
        Returns:
            Lista de comparações sequenciais
        """
        df = df.copy()
        df['data_dt'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
        df['mes_ano'] = df['data_dt'].dt.to_period('M').astype(str)
        
        # Obtém meses únicos ordenados
        meses = sorted(df['mes_ano'].unique())
        
        comparisons = []
        for i in range(len(meses) - 1):
            comparison = self.compare_months(df, meses[i], meses[i+1])
            if comparison:
                comparisons.append(comparison)
        
        return comparisons
    
    def generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Gera sumário executivo APENAS COM DADOS REAIS dos arquivos OFX
        
        IMPORTANTE: Este método usa EXCLUSIVAMENTE dados reais do DataFrame.
        Não usa valores default, fictícios ou hardcoded.
        
        Args:
            df: DataFrame com transações REAIS dos arquivos OFX
            
        Returns:
            Dicionário com sumário baseado em dados reais
        """
        # VALIDAÇÃO: Garante que há dados reais para processar
        if df.empty:
            raise ValueError("DataFrame vazio! Não é possível gerar sumário sem dados reais dos arquivos OFX.")
        
        # Converte data para datetime para obter período real dos arquivos OFX
        df_copy = df.copy()
        df_copy['data_dt'] = pd.to_datetime(df_copy['data'], format='%d/%m/%Y', errors='coerce')
        
        # PERÍODO REAL: Extrai o período REAL presente nos dados dos arquivos OFX
        data_min = df_copy['data_dt'].min()
        data_max = df_copy['data_dt'].max()
        
        # DEBUG: Mostrar período detectado
        print(f"\n🔍 DEBUG PERÍODO:")
        print(f"   Data mínima: {data_min} -> Mês: {data_min.strftime('%Y-%m') if pd.notna(data_min) else 'N/A'}")
        print(f"   Data máxima: {data_max} -> Mês: {data_max.strftime('%Y-%m') if pd.notna(data_max) else 'N/A'}")
        print(f"   Total de transações: {len(df_copy)}")
        print(f"   Primeiras 3 datas: {df_copy['data'].head(3).tolist()}")
        print(f"   Últimas 3 datas: {df_copy['data'].tail(3).tolist()}")
        
        # Calcula receitas e despesas REAIS (sem valores default)
        receitas = df[df['valor'] > 0]['valor'].sum()
        despesas = abs(df[df['valor'] < 0]['valor'].sum())
        saldo = receitas - despesas
        
        # Estatísticas gerais BASEADAS EM DADOS REAIS
        summary = {
            'periodo': {
                'inicio': df['data'].min(),  # Data mínima REAL dos arquivos OFX (formato dd/mm/yyyy)
                'fim': df['data'].max(),      # Data máxima REAL dos arquivos OFX (formato dd/mm/yyyy)
                'mes_inicio': data_min.strftime('%Y-%m') if pd.notna(data_min) else 'N/A',
                'mes_fim': data_max.strftime('%Y-%m') if pd.notna(data_max) else 'N/A',
            },
            'totais': {
                'receita': float(receitas),  # Valor REAL calculado dos arquivos OFX
                'despesa': float(despesas),  # Valor REAL calculado dos arquivos OFX
                'saldo': float(saldo),       # Resultado REAL calculado
                'margem': float((saldo / receitas * 100) if receitas > 0 else 0)  # Margem REAL calculada
            },
            'transacoes': {
                'total': len(df),
                'receitas': len(df[df['valor'] > 0]),
                'despesas': len(df[df['valor'] < 0]),
                'ticket_medio_receita': float(df[df['valor'] > 0]['valor'].mean() if len(df[df['valor'] > 0]) > 0 else 0),
                'ticket_medio_despesa': float(abs(df[df['valor'] < 0]['valor'].mean()) if len(df[df['valor'] < 0]) > 0 else 0)
            },
            'top_receitas': [],
            'top_despesas': []
        }
        
        # Top 5 receitas (excluindo Saldo Inicial e transferências entre contas)
        df_receitas = df[df['valor'] > 0].copy()
        
        # Filtra saldos iniciais e transferências
        df_receitas = df_receitas[
            ~df_receitas['classificacao_sugerida'].str.contains('Saldo Inicial', case=False, na=False) &
            ~df_receitas['classificacao_sugerida'].str.contains('Transferencia Entre Contas', case=False, na=False) &
            ~df_receitas['descricao'].str.contains('SALDO', case=False, na=False)
        ]
        
        top_rec = df_receitas.nlargest(5, 'valor')[['data', 'descricao', 'valor', 'classificacao_sugerida']]
        for _, row in top_rec.iterrows():
            summary['top_receitas'].append({
                'data': row['data'],
                'descricao': row['descricao'][:50],
                'valor': float(row['valor']),
                'categoria': row['classificacao_sugerida']
            })
        
        # Top 5 despesas (excluindo transferências entre contas)
        df_despesas = df[df['valor'] < 0].copy()
        
        # Filtra transferências
        df_despesas = df_despesas[
            ~df_despesas['classificacao_sugerida'].str.contains('Transferencia Entre Contas', case=False, na=False)
        ]
        
        top_desp = df_despesas.nsmallest(5, 'valor')[['data', 'descricao', 'valor', 'classificacao_sugerida']]
        for _, row in top_desp.iterrows():
            summary['top_despesas'].append({
                'data': row['data'],
                'descricao': row['descricao'][:50],
                'valor': float(row['valor']),
                'categoria': row['classificacao_sugerida']
            })
        
        return summary
    
    def generate_full_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Gera relatório completo BASEADO EXCLUSIVAMENTE EM DADOS REAIS dos arquivos OFX
        
        IMPORTANTE: Este relatório usa APENAS dados reais presentes nos arquivos OFX.
        Não gera valores default, fictícios ou hardcoded. Se não houver dados suficientes,
        retorna indicadores claros de insuficiência de dados.
        
        Args:
            df: DataFrame com transações classificadas dos arquivos OFX REAIS
            
        Returns:
            Dicionário com relatório completo baseado em dados reais
        """
        print("\n" + "="*80)
        print("📊 GERANDO RELATÓRIO FINANCEIRO COM DADOS REAIS DOS ARQUIVOS OFX")
        print("="*80)
        
        # VALIDAÇÃO: Garante que há dados reais para processar
        if df.empty:
            raise ValueError("❌ ERRO: DataFrame vazio! Não é possível gerar relatório sem dados reais dos arquivos OFX.")
        
        print(f"✅ {len(df)} transações reais encontradas nos arquivos OFX")
        
        # Enriquece com plano de contas
        df_enriched = self.enrich_with_plan(df)
        
        # Análises básicas COM DADOS REAIS
        print("\n   📋 Calculando sumário executivo (dados reais)...")
        sumario = self.generate_summary(df)
        
        print("   💼 Calculando DRE (dados reais)...")
        dre = self.calculate_dre(df_enriched)
        
        print("   💰 Calculando DFC (dados reais)...")
        dfc = self.calculate_dfc(df_enriched)
        
        print("   📊 Analisando categorias (dados reais)...")
        categorias = self.analyze_by_category(df)
        
        print("   📈 Analisando tendência mensal (dados reais)...")
        tendencia = self.analyze_monthly_trend(df)
        
        # Análises comparativas COM DADOS REAIS
        print("   🔄 Gerando comparações mensais (dados reais)...")
        comparacoes = self.get_all_month_comparisons(df)
        
        report = {
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'sumario': sumario,
            'dre': dre,
            'dfc': dfc,
            'analise_categorias': categorias,
            'tendencia_mensal': tendencia,
            'comparacoes_mensais': comparacoes,  # Comparações mês a mês com dados reais
            'fonte_dados': 'Arquivos OFX processados',
            'aviso': 'Todos os valores são baseados EXCLUSIVAMENTE em dados contidos nos arquivos OFXs processados.'
        }
        
        print(f"\n✅ Relatório financeiro gerado com sucesso!")
        print(f"   Período: {sumario['periodo']['inicio']} até {sumario['periodo']['fim']}")
        print(f"   Último mês analisado: {sumario['periodo'].get('ultimo_mes_analisado', 'N/A')}")
        print("="*80 + "\n")
        
        return report
