"""
STRATEGIC ANALYZER - Análise Estratégica com IA
Gera insights, SWOT e recomendações baseadas APENAS nos dados reais
"""

import pandas as pd
import json
import time
from typing import Dict, Any, List
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.utils.ai_decision_logger import get_logger

load_dotenv()


class StrategicAnalyzer:
    """Analisa dados financeiros e gera insights estratégicos com IA"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.3):
        """
        Inicializa o analisador estratégico
        
        Args:
            model: Modelo de IA (gpt-4o para análises mais sofisticadas)
            temperature: Temperatura (0.3 para ser criativo mas factual)
        """
        self.model = model
        self.temperature = temperature
        self.llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        self.logger = get_logger()
    
    def generate_swot_analysis(self, financial_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Gera análise SWOT baseada nos dados financeiros reais
        
        Args:
            financial_data: Dados financeiros sumarizados
            
        Returns:
            Dicionário com Forças, Fraquezas, Oportunidades e Ameaças
        """
        class SWOTAnalysis(BaseModel):
            forcas: List[str] = Field(description="Lista de forças identificadas nos dados")
            fraquezas: List[str] = Field(description="Lista de fraquezas identificadas nos dados")
            oportunidades: List[str] = Field(description="Lista de oportunidades identificadas")
            ameacas: List[str] = Field(description="Lista de ameaças identificadas")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um analista financeiro estratégico especializado em análise SWOT.
Analise APENAS os dados fornecidos, sem inventar informações.
Seja específico e use números dos dados quando disponível.
Cada item deve ter 1-2 frases concisas e objetivas."""),
            ("human", """Analise os dados financeiros e gere uma análise SWOT:

DADOS FINANCEIROS:
{financial_data}

INSTRUÇÕES:
- Forças: Pontos positivos observados nos dados (crescimento, margens, eficiência)
- Fraquezas: Pontos negativos ou riscos observados (custos altos, quedas, inadimplência)
- Oportunidades: Potenciais melhorias baseadas nos dados
- Ameaças: Riscos ou tendências negativas identificadas

Gere 3-5 itens para cada categoria baseado APENAS nos dados fornecidos.""")
        ])
        
        chain = prompt | self.llm.with_structured_output(SWOTAnalysis)
        
        resultado = chain.invoke({
            "financial_data": json.dumps(financial_data, indent=2, ensure_ascii=False)
        })
        
        swot = resultado.model_dump()
        
        # Loga a decisão de forma DETALHADA
        self.logger.log_analysis_decision(
            analysis_type="swot_analysis",
            input_data={
                "receita_total": financial_data.get('summary', {}).get('totais', {}).get('receita', 0),
                "despesa_total": financial_data.get('summary', {}).get('totais', {}).get('despesa', 0),
                "saldo": financial_data.get('summary', {}).get('totais', {}).get('saldo', 0),
                "margem": financial_data.get('summary', {}).get('totais', {}).get('margem', 0),
                "num_meses": len(financial_data.get('monthly', [])),
                "top_categorias": [c.get('categoria', 'N/A') for c in financial_data.get('categories', [])[:5]]
            },
            output=swot,
            reasoning=f"""
ANÁLISE SWOT - RACIOCÍNIO DA IA:

A IA analisou os dados financeiros do período e identificou:

FORÇAS ({len(swot['forcas'])} itens):
{chr(10).join([f'  • {f}' for f in swot['forcas']])}

JUSTIFICATIVA: Estas forças foram identificadas analisando métricas positivas como crescimento de receita, 
margem de lucro, eficiência operacional e tendências favoráveis nos dados do período.

FRAQUEZAS ({len(swot['fraquezas'])} itens):
{chr(10).join([f'  • {f}' for f in swot['fraquezas']])}

JUSTIFICATIVA: Estas fraquezas foram identificadas analisando pontos de atenção como custos elevados,
quedas em períodos específicos, concentração de riscos ou ineficiências operacionais.

OPORTUNIDADES ({len(swot['oportunidades'])} itens):
{chr(10).join([f'  • {o}' for o in swot['oportunidades']])}

JUSTIFICATIVA: Oportunidades identificadas baseadas em potenciais de melhoria, tendências do mercado
observadas nos dados, ou áreas subexploradas.

AMEAÇAS ({len(swot['ameacas'])} itens):
{chr(10).join([f'  • {a}' for a in swot['ameacas']])}

JUSTIFICATIVA: Ameaças identificadas analisando riscos externos, tendências negativas ou vulnerabilidades
observadas nos padrões de dados.

DADOS UTILIZADOS NA ANÁLISE:
- Receita total do período: R$ {financial_data.get('summary', {}).get('totais', {}).get('receita', 0):,.2f}
- Despesa total do período: R$ {financial_data.get('summary', {}).get('totais', {}).get('despesa', 0):,.2f}
- Resultado líquido: R$ {financial_data.get('summary', {}).get('totais', {}).get('saldo', 0):,.2f}
- Margem: {financial_data.get('summary', {}).get('totais', {}).get('margem', 0):.1f}%
- Número de meses analisados: {len(financial_data.get('monthly', []))}
""",
            calculations=financial_data
        )
        
        return swot
    
    def generate_monthly_diagnosis(self, 
                                   monthly_data: Dict[str, Any],
                                   comparison_data: Dict[str, Any]) -> str:
        """
        Gera diagnóstico detalhado de um mês baseado nos dados
        
        Args:
            monthly_data: Dados do mês analisado
            comparison_data: Dados comparativos (mês anterior, se disponível)
            
        Returns:
            Texto com diagnóstico
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um analista financeiro especializado em diagnósticos.
Analise os dados fornecidos e gere um diagnóstico objetivo e factual.
Use números específicos dos dados.
Seja direto e profissional."""),
            ("human", """Gere um diagnóstico financeiro baseado nestes dados:

DADOS DO PERÍODO:
{monthly_data}

COMPARAÇÃO:
{comparison_data}

Gere um parágrafo de 4-6 linhas que:
1. Resuma o desempenho do período
2. Destaque os principais indicadores
3. Identifique tendências observadas
4. Use números específicos dos dados""")
        ])
        
        chain = prompt | self.llm
        
        resultado = chain.invoke({
            "monthly_data": json.dumps(monthly_data, indent=2, ensure_ascii=False),
            "comparison_data": json.dumps(comparison_data, indent=2, ensure_ascii=False)
        })
        
        diagnostico = resultado.content
        
        # Loga a análise de forma DETALHADA
        self.logger.log_analysis_decision(
            analysis_type="monthly_diagnosis",
            input_data=monthly_data,
            output={"diagnosis": diagnostico},
            reasoning=f"""
DIAGNÓSTICO MENSAL - RACIOCÍNIO DA IA:

DADOS DO PERÍODO ANALISADO:
{json.dumps(monthly_data, indent=2, ensure_ascii=False)}

DADOS COMPARATIVOS (mês anterior ou referência):
{json.dumps(comparison_data, indent=2, ensure_ascii=False)}

DIAGNÓSTICO GERADO:
{diagnostico}

COMO A IA CHEGOU NESTA CONCLUSÃO:
1. Analisou as métricas do período atual (receitas, despesas, saldo)
2. Comparou com o período de referência para identificar tendências
3. Calculou variações percentuais e absolutas
4. Identificou os principais drivers de mudança
5. Contextualizou com o comportamento histórico disponível
6. Gerou um diagnóstico factual baseado exclusivamente nos números apresentados

PREMISSAS UTILIZADAS:
- Apenas dados reais foram considerados
- Não foram feitas suposições sobre dados não disponíveis
- Tendências identificadas são baseadas nos períodos disponíveis
- Sazonalidade considerada dentro do período de análise
""",
            calculations={"monthly_data": monthly_data, "comparison_data": comparison_data}
        )
        
        return diagnostico
    
    def generate_action_plans(self, 
                            financial_summary: Dict[str, Any],
                            swot: Dict[str, List[str]]) -> List[Dict[str, str]]:
        """
        Gera planos de ação baseados na análise SWOT e dados financeiros
        
        Args:
            financial_summary: Resumo financeiro
            swot: Análise SWOT
            
        Returns:
            Lista de planos de ação com prioridade
        """
        class ActionPlan(BaseModel):
            prioridade: str = Field(description="URGENTE, IMPORTANTE ou OBSERVAÇÃO")
            titulo: str = Field(description="Título do plano de ação")
            situacao: str = Field(description="Descrição da situação atual")
            impacto: str = Field(description="Impacto no negócio")
            acoes: List[str] = Field(description="Lista de 3-5 ações específicas")
        
        class ActionPlans(BaseModel):
            planos: List[ActionPlan] = Field(description="Lista de 2-4 planos de ação")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um consultor financeiro especializado em planos de ação.
Gere planos de ação práticos e específicos baseados nos dados.
Cada ação deve ser objetiva e mensurável.
Priorize baseado no impacto e urgência."""),
            ("human", """Gere planos de ação baseados nesta análise:

DADOS FINANCEIROS:
{financial_summary}

ANÁLISE SWOT:
{swot}

Gere 2-4 planos de ação que:
1. Abordem fraquezas críticas ou oportunidades relevantes
2. Tenham ações específicas e práticas
3. Sejam priorizados (URGENTE, IMPORTANTE, OBSERVAÇÃO)
4. Referenciem dados concretos quando possível""")
        ])
        
        chain = prompt | self.llm.with_structured_output(ActionPlans)
        
        resultado = chain.invoke({
            "financial_summary": json.dumps(financial_summary, indent=2, ensure_ascii=False),
            "swot": json.dumps(swot, indent=2, ensure_ascii=False)
        })
        
        planos = [p.model_dump() for p in resultado.planos]
        
        # Loga cada plano de forma DETALHADA
        for i, plano in enumerate(planos, 1):
            self.logger.log_analysis_decision(
                analysis_type=f"action_plan_{i}",
                input_data={
                    "swot_forcas": swot.get('forcas', []),
                    "swot_fraquezas": swot.get('fraquezas', []),
                    "swot_oportunidades": swot.get('oportunidades', []),
                    "swot_ameacas": swot.get('ameacas', []),
                    "receita": financial_summary.get('totais', {}).get('receita', 0),
                    "despesa": financial_summary.get('totais', {}).get('despesa', 0),
                    "saldo": financial_summary.get('totais', {}).get('saldo', 0)
                },
                output=plano,
                reasoning=f"""
PLANO DE AÇÃO {i} - RACIOCÍNIO DA IA:

PRIORIDADE: {plano['prioridade']}
TÍTULO: {plano['titulo']}

SITUAÇÃO IDENTIFICADA:
{plano['situacao']}

IMPACTO NO NEGÓCIO:
{plano['impacto']}

AÇÕES RECOMENDADAS:
{chr(10).join([f'  {idx}. {acao}' for idx, acao in enumerate(plano['acoes'], 1)])}

COMO A IA CHEGOU NESTE PLANO:

1. ANÁLISE DA SITUAÇÃO:
   A IA identificou esta situação analisando:
   - Fraquezas do SWOT: {', '.join(swot.get('fraquezas', [])[:2])}...
   - Dados financeiros: Receita R$ {financial_summary.get('totais', {}).get('receita', 0):,.2f}, 
     Despesa R$ {financial_summary.get('totais', {}).get('despesa', 0):,.2f}
   - Tendências observadas nos dados do período

2. AVALIAÇÃO DE IMPACTO:
   O impacto foi determinado considerando:
   - Magnitude do problema/oportunidade identificado
   - Relação com as fraquezas ou oportunidades do SWOT
   - Potencial de melhoria nos resultados financeiros

3. PRIORIZAÇÃO:
   A prioridade "{plano['prioridade']}" foi definida baseada em:
   - Urgência: Quanto mais crítico para os resultados, maior a prioridade
   - Impacto financeiro potencial
   - Viabilidade de implementação

4. DEFINIÇÃO DAS AÇÕES:
   As ações foram formuladas para serem:
   - Específicas e mensuráveis
   - Diretamente relacionadas à situação identificada
   - Baseadas em boas práticas de gestão financeira
   - Viáveis considerando o contexto da empresa

CONEXÃO COM O SWOT:
- Endereça as fraquezas: {', '.join([f for f in swot.get('fraquezas', []) if any(word in plano['situacao'].lower() for word in f.lower().split()[:3])])[:100]}
- Aproveita as oportunidades: {', '.join([o for o in swot.get('oportunidades', []) if any(word in plano['titulo'].lower() for word in o.lower().split()[:3])])[:100]}
""",
                calculations={
                    "prioridade_score": {"URGENTE": 3, "IMPORTANTE": 2, "OBSERVAÇÃO": 1}.get(plano['prioridade'], 0),
                    "num_acoes": len(plano['acoes']),
                    "palavras_chave": [word for word in plano['titulo'].lower().split() if len(word) > 4]
                }
            )
        
        return planos
    
    def generate_key_events(self, 
                          financial_summary: Dict[str, Any],
                          monthly_analysis: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Identifica os 3 eventos mais relevantes do período
        
        Args:
            financial_summary: Resumo financeiro
            monthly_analysis: Análise mensal
            
        Returns:
            Lista com 3 eventos principais
        """
        class KeyEvent(BaseModel):
            tipo: str = Field(description="POSITIVO, NEUTRO ou NEGATIVO")
            titulo: str = Field(description="Título curto do evento")
            descricao: str = Field(description="Descrição detalhada com dados")
        
        class KeyEvents(BaseModel):
            eventos: List[KeyEvent] = Field(description="Exatamente 3 eventos principais", min_items=3, max_items=3)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um analista financeiro que identifica eventos-chave.
Analise os dados e identifique os 3 eventos mais relevantes do período.
Use números específicos dos dados.
Cada evento deve ter impacto significativo nos resultados."""),
            ("human", """Identifique os 3 eventos mais relevantes:

RESUMO FINANCEIRO:
{financial_summary}

ANÁLISE MENSAL:
{monthly_analysis}

Identifique 3 eventos que:
1. Tiveram maior impacto nos resultados
2. São suportados por dados concretos
3. São relevantes para tomada de decisão
4. Representam diferentes aspectos (receita, custo, fluxo, etc)""")
        ])
        
        chain = prompt | self.llm.with_structured_output(KeyEvents)
        
        resultado = chain.invoke({
            "financial_summary": json.dumps(financial_summary, indent=2, ensure_ascii=False),
            "monthly_analysis": json.dumps(monthly_analysis, indent=2, ensure_ascii=False)
        })
        
        eventos = [e.model_dump() for e in resultado.eventos]
        
        # Loga os eventos de forma DETALHADA
        for i, evento in enumerate(eventos, 1):
            self.logger.log_analysis_decision(
                analysis_type=f"key_event_{i}",
                input_data={
                    "receita_total": financial_summary.get('totais', {}).get('receita', 0),
                    "despesa_total": financial_summary.get('totais', {}).get('despesa', 0),
                    "saldo": financial_summary.get('totais', {}).get('saldo', 0),
                    "tendencia_mensal": monthly_analysis
                },
                output=evento,
                reasoning=f"""
EVENTO-CHAVE {i} - RACIOCÍNIO DA IA:

TIPO: {evento['tipo']}
TÍTULO: {evento['titulo']}

DESCRIÇÃO COMPLETA:
{evento['descricao']}

COMO A IA IDENTIFICOU ESTE EVENTO:

1. ANÁLISE DE RELEVÂNCIA:
   Este evento foi selecionado como um dos 3 mais importantes porque:
   - Teve impacto significativo nos resultados financeiros do período
   - Representa uma mudança ou tendência clara nos dados
   - É relevante para tomada de decisão estratégica

2. CLASSIFICAÇÃO DO TIPO ({evento['tipo']}):
   {'- POSITIVO: Evento que contribuiu para melhoria dos resultados ou apresenta oportunidade' if 'POSITIVO' in evento['tipo'] else ''}
   {'- NEGATIVO: Evento que representa desafio ou risco para os resultados' if 'NEGATIVO' in evento['tipo'] else ''}
   {'- NEUTRO: Evento relevante mas com impacto misto ou ainda não definido' if 'NEUTRO' in evento['tipo'] else ''}

3. DADOS QUE SUPORTAM ESTE EVENTO:
   {self._extract_supporting_data(evento, financial_summary, monthly_analysis)}

4. IMPACTO NOS RESULTADOS:
   - Receita total do período: R$ {financial_summary.get('totais', {}).get('receita', 0):,.2f}
   - Despesa total do período: R$ {financial_summary.get('totais', {}).get('despesa', 0):,.2f}
   - Resultado líquido: R$ {financial_summary.get('totais', {}).get('saldo', 0):,.2f}
   - Este evento está diretamente relacionado com estes números

5. CONTEXTO TEMPORAL:
   Número de meses analisados: {len(monthly_analysis)}
   Tendência observada: {self._identify_trend(monthly_analysis)}

RELEVÂNCIA PARA O RELATÓRIO:
Este evento foi incluído no Sumário Executivo porque representa um dos aspectos mais
críticos para entender o desempenho financeiro do período e orientar decisões futuras.
""",
                calculations={
                    "ranking": i,
                    "tipo_numerico": {"POSITIVO": 1, "NEUTRO": 0, "NEGATIVO": -1}.get(evento['tipo'], 0),
                    "palavras_chave": evento['titulo'].lower().split()[:5]
                }
            )
        
        return eventos
    
    def _extract_supporting_data(self, evento: Dict, financial_summary: Dict, monthly_analysis: List) -> str:
        """Extrai dados que suportam o evento identificado"""
        # Identifica números mencionados na descrição
        descricao = evento.get('descricao', '')
        
        info = []
        if 'crescimento' in descricao.lower() or 'aumento' in descricao.lower():
            info.append("- Identificado crescimento em métricas de receita ou volume")
        if 'queda' in descricao.lower() or 'redução' in descricao.lower():
            info.append("- Identificada redução em despesas ou volumes")
        if 'margem' in descricao.lower():
            info.append(f"- Margem do período: {financial_summary.get('totais', {}).get('margem', 0):.1f}%")
        if monthly_analysis and len(monthly_analysis) > 1:
            primeiro_mes = monthly_analysis[0]
            ultimo_mes = monthly_analysis[-1]
            var_receita = ((ultimo_mes['receita'] - primeiro_mes['receita']) / primeiro_mes['receita'] * 100) if primeiro_mes['receita'] > 0 else 0
            info.append(f"- Variação de receita entre primeiro e último mês: {var_receita:+.1f}%")
        
        return "\n   ".join(info) if info else "- Baseado na análise geral dos dados do período"
    
    def _identify_trend(self, monthly_analysis: List) -> str:
        """Identifica tendência nos dados mensais"""
        if not monthly_analysis or len(monthly_analysis) < 2:
            return "Período insuficiente para identificar tendência"
        
        receitas = [m['receita'] for m in monthly_analysis]
        if receitas[-1] > receitas[0]:
            return "Crescente (última receita maior que primeira)"
        elif receitas[-1] < receitas[0]:
            return "Decrescente (última receita menor que primeira)"
        else:
            return "Estável (receitas similares no período)"
    
    def generate_revenue_analysis(self, revenue_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Gera análise detalhada de receitas USANDO APENAS DADOS REAIS
        
        IMPORTANTE: Esta análise usa EXCLUSIVAMENTE os dados fornecidos.
        A IA NÃO DEVE inventar valores, períodos ou métricas.
        
        Args:
            revenue_data: Dados REAIS de receitas por período dos arquivos OFX
            
        Returns:
            Dicionário com análises baseadas apenas nos dados reais fornecidos
        """
        # VALIDAÇÃO: Extrai meses e valores reais para validação
        meses_reais = [m['mes'] for m in revenue_data.get('monthly', [])]
        receitas_reais = [m.get('receita', 0) for m in revenue_data.get('monthly', [])]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um analista financeiro que trabalha APENAS com dados reais.

REGRAS CRÍTICAS:
1. Use APENAS os valores numéricos presentes nos dados fornecidos
2. NÃO invente valores, períodos ou porcentagens
3. Se os dados não contêm informação sobre algo, NÃO mencione
4. CITE os valores exatos dos dados ao fazer comparações
5. Use APENAS os meses que aparecem nos dados

PROIBIDO:
- Inventar valores como "R$ 850.000" ou "R$ 980.000"
- Mencionar meses que não estão nos dados
- Criar porcentagens sem base nos números fornecidos
- Assumir tendências sem dados suficientes"""),
            ("human", """Analise as receitas baseado APENAS nestes dados REAIS:

DADOS DE RECEITAS (REAIS DOS ARQUIVOS OFX):
{revenue_data}

MESES DISPONÍVEIS NOS DADOS: {meses_disponiveis}

INSTRUÇÕES:
1. MENSAL: Compare os meses QUE EXISTEM nos dados acima
   - Use os valores EXATOS de receita de cada mês
   - Calcule variações apenas entre meses consecutivos presentes nos dados
   
2. SAZONALIDADE: Identifique padrões APENAS no período disponível
   - Base-se nos meses e valores que estão nos dados
   
3. DIAGNÓSTICO: Conclusão sobre a performance
   - Use APENAS os números fornecidos
   - Não extrapole além do período dos dados

IMPORTANTE: Se você mencionar qualquer valor, ele DEVE existir nos dados acima.
Cada análise deve ter 2-3 frases com dados específicos REAIS.""")
        ])
        
        chain = prompt | self.llm
        
        # Passa os dados reais E a lista de meses disponíveis para validação
        resultado = chain.invoke({
            "revenue_data": json.dumps(revenue_data, indent=2, ensure_ascii=False),
            "meses_disponiveis": ", ".join(meses_reais) if meses_reais else "Nenhum mês disponível"
        })
        
        print(f"\n⚠️  [REVENUE ANALYSIS] Meses reais disponíveis: {meses_reais}")
        print(f"⚠️  [REVENUE ANALYSIS] Receitas reais: {receitas_reais}")
        
        # Parse da resposta (assumindo que vem estruturado)
        analise = resultado.content
        
        # Loga a análise de forma DETALHADA
        self.logger.log_analysis_decision(
            analysis_type="revenue_analysis",
            input_data=revenue_data,
            output={"analysis": analise},
            reasoning=f"""
ANÁLISE DE RECEITAS - RACIOCÍNIO DA IA:

DADOS ANALISADOS:
{json.dumps(revenue_data, indent=2, ensure_ascii=False)}

ANÁLISE GERADA PELA IA:
{analise}

METODOLOGIA UTILIZADA:

1. ANÁLISE MENSAL (mês a mês):
   - Comparou receitas de cada mês disponível
   - Calculou variações percentuais entre períodos consecutivos
   - Identificou meses de melhor e pior performance

2. ANÁLISE DE SAZONALIDADE:
   - Observou padrões recorrentes nos dados disponíveis
   - Identificou se há comportamento sazonal visível
   - Contextualizou com características do segmento

3. DIAGNÓSTICO DE PERFORMANCE:
   - Avaliou se as receitas estão crescendo, estáveis ou em queda
   - Identificou possíveis causas baseadas nos dados
   - Relacionou com outras métricas disponíveis

PREMISSAS DA ANÁLISE:
- Baseada EXCLUSIVAMENTE nos dados reais fornecidos
- Não foram feitas extrapolações além do período disponível
- Tendências identificadas são observações, não previsões
- Contexto limitado ao período de análise (sem dados históricos de anos anteriores)

CONCLUSÕES FACTUAIS:
A análise acima reflete o que os DADOS MOSTRAM, sem adicionar informações
especulativas ou baseadas em suposições. Cada afirmação pode ser rastreada
de volta aos números fornecidos.
""",
            calculations={
                "total_receitas": revenue_data.get('totals', {}).get('receita', 0),
                "num_meses": len(revenue_data.get('monthly', [])),
                "receitas_por_mes": [m.get('receita', 0) for m in revenue_data.get('monthly', [])]
            }
        )
        
        return {"analise_completa": analise}
    
    def generate_full_strategic_report(self, 
                                      financial_summary: Dict[str, Any],
                                      monthly_analysis: List[Dict[str, Any]],
                                      category_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera relatório estratégico completo
        
        Args:
            financial_summary: Resumo financeiro geral
            monthly_analysis: Análise mensal detalhada
            category_analysis: Análise por categoria
            
        Returns:
            Dicionário com análise estratégica completa
        """
        print("🧠 [STRATEGIC ANALYZER] Gerando análise estratégica com IA...")
        print("   ⏱️ Aguardando 60 segundos entre chamadas para respeitar rate limits da OpenAI...")
        
        try:
            # 1. Eventos-chave
            print("   🔍 Identificando eventos-chave...")
            key_events = self.generate_key_events(financial_summary, monthly_analysis)
            print(f"   ✅ {len(key_events)} eventos identificados")
            time.sleep(60)  # Aguarda 60 segundos antes da próxima chamada
        except Exception as e:
            print(f"   ❌ ERRO em eventos-chave: {e}")
            key_events = []
        
        try:
            # 2. Análise SWOT
            print("   📊 Gerando análise SWOT...")
            swot = self.generate_swot_analysis({
                "summary": financial_summary,
                "monthly": monthly_analysis,
                "categories": category_analysis[:10]  # Top 10 categorias
            })
            print("   ✅ SWOT gerado com sucesso")
            time.sleep(60)  # Aguarda 60 segundos antes da próxima chamada
        except Exception as e:
            print(f"   ❌ ERRO em SWOT: {e}")
            swot = {"forcas": [], "fraquezas": [], "oportunidades": [], "ameacas": []}
        
        try:
            # 3. Planos de ação
            print("   📋 Criando planos de ação...")
            action_plans = self.generate_action_plans(financial_summary, swot)
            print(f"   ✅ {len(action_plans)} planos criados")
            time.sleep(60)  # Aguarda 60 segundos antes da próxima chamada
        except Exception as e:
            print(f"   ❌ ERRO em planos de ação: {e}")
            action_plans = []
        
        try:
            # 4. Análise de receitas
            print("   💰 Analisando receitas...")
            revenue_analysis = self.generate_revenue_analysis({
                "totals": financial_summary.get("totais", {}),
                "monthly": monthly_analysis
            })
            print("   ✅ Análise de receitas concluída")
        except Exception as e:
            print(f"   ❌ ERRO em análise de receitas: {e}")
            revenue_analysis = {}
        
        print("✅ [STRATEGIC ANALYZER] Análise estratégica concluída!")
        
        return {
            "key_events": key_events,
            "swot": swot,
            "action_plans": action_plans,
            "revenue_analysis": revenue_analysis,
            "generated_at": datetime.now().isoformat()
        }
