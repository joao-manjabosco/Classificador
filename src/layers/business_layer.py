"""
BUSINESS LAYER - Camada de Negócio
Responsável pela classificação inteligente de transações usando IA
"""

import json
import asyncio
import pandas as pd
from typing import Optional, Literal, Dict, Any, List
from pydantic import BaseModel, Field
from tqdm import tqdm
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
from src.utils.ai_decision_logger import get_logger

# Configurar nest_asyncio para permitir loops aninhados
import nest_asyncio
nest_asyncio.apply()

load_dotenv()


class BusinessLayer:
    """Classifica transações bancárias usando IA e regras de negócio"""
    
    def __init__(self, 
                 model: str = "gpt-4o-mini",
                 temperature: float = 0,
                 max_concurrency: int = 6,
                 regra_path: str = "./src/prompts/regra.json"):
        """
        Inicializa a camada de negócio
        
        Args:
            model: Modelo de IA a ser usado
            temperature: Temperatura para geração
            max_concurrency: Máximo de requisições simultâneas
            regra_path: Caminho do arquivo de regras
        """
        self.model = model
        self.temperature = temperature
        self.max_concurrency = max_concurrency
        
        # Carrega regras de classificação
        with open(regra_path, 'r', encoding='utf-8') as f:
            self.regra = json.load(f)
            self.classes_permitidas = self.regra["contexto"]["classes_permitidas"]
        
        # Modelo de dados para classificação
        class ClassificacaoTransacao(BaseModel):
            classificacao_sugerida: Literal[tuple(self.classes_permitidas)] = Field(
                ..., description="Classificação da transação."
            )
            explicacao: str = Field(..., description="Explicação da classificação.")
        
        self.ClassificacaoTransacao = ClassificacaoTransacao
        
        # Configura o prompt
        system_prompt = f"""
Você é um analista financeiro especializado em classificar transações bancárias.

REGRAS DE CLASSIFICAÇÃO:
{json.dumps(self.regra["contexto"]["instrucoes_gerais"], indent=2, ensure_ascii=False)}

CLASSES PERMITIDAS:
{json.dumps(self.classes_permitidas, indent=2, ensure_ascii=False)}
"""
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", """Classifique a transação a seguir:
    
Descrição: {descricao}
Origem: {origem} (CAR=Crédito, CAP=Débito)
Valor: R$ {valor}

""")
        ])
        
        # Cria a chain de processamento
        llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        self.chain = (self.prompt | llm.with_structured_output(self.ClassificacaoTransacao))
    
    def regras_pre_classificacao(self, row: pd.Series, log_decision: bool = True) -> Optional[Dict[str, str]]:
        """
        Aplica regras de negócio antes de chamar a IA
        
        Args:
            row: Linha do DataFrame com a transação
            log_decision: Se deve logar a decisão
            
        Returns:
            Dicionário com classificação ou None se não houver regra aplicável
        """
        desc = str(row.get("descricao", "") or "").upper()  # Converte para maiúsculas
        logger = get_logger()
        
        # Regra ESPECIAL: Transferência entre contas próprias (BODY STATION e J E MADEIRA)
        if ("BODY STATION ACADEMIA" in desc or "J E MADEIRA A" in desc):
            if row["origem"] == "CAR":
                result = {
                    "classificacao_sugerida": "(+) Transferencia Entre Contas",
                    "explicacao": "Transferência entre contas próprias identificada (entrada)"
                }
                if log_decision:
                    logger.log_classification_decision(
                        transaction_id=row.get("index", -1),
                        input_data={
                            "descricao": row.get("descricao", ""),
                            "origem": row["origem"],
                            "valor": row["valor"]
                        },
                        decision=result,
                        method="rule",
                        reasoning="Regra: Transferência entre contas próprias (BODY STATION/J E MADEIRA) - Entrada (CAR)",
                        confidence=1.0
                    )
                return result
            else:
                result = {
                    "classificacao_sugerida": "(-) Transferencia Entre Contas",
                    "explicacao": "Transferência entre contas próprias identificada (saída)"
                }
                if log_decision:
                    logger.log_classification_decision(
                        transaction_id=row.get("index", -1),
                        input_data={
                            "descricao": row.get("descricao", ""),
                            "origem": row["origem"],
                            "valor": row["valor"]
                        },
                        decision=result,
                        method="rule",
                        reasoning="Regra: Transferência entre contas próprias (BODY STATION/J E MADEIRA) - Saída (CAP)",
                        confidence=1.0
                    )
                return result
        
        # Regra: Rende Fácil (aplicação/resgate) - VERIFICAR ANTES de outras regras genéricas
        if "RENDE FACIL" in desc or "RENDE FÁCIL" in desc:
            if row["origem"] == "CAR":
                result = {
                    "classificacao_sugerida": "Resgate Aplicação Financeira",
                    "explicacao": "Resgate de aplicação financeira identificado"
                }
                if log_decision:
                    logger.log_classification_decision(
                        transaction_id=row.get("index", -1),
                        input_data={"descricao": row.get("descricao", ""), "origem": row["origem"], "valor": row["valor"]},
                        decision=result,
                        method="rule",
                        reasoning="Regra: Rende Fácil detectado + origem CAR = Resgate",
                        confidence=1.0
                    )
                return result
            else:
                result = {
                    "classificacao_sugerida": "0.006 - Aplicação Financeira",
                    "explicacao": "Aplicação financeira identificada"
                }
                if log_decision:
                    logger.log_classification_decision(
                        transaction_id=row.get("index", -1),
                        input_data={"descricao": row.get("descricao", ""), "origem": row["origem"], "valor": row["valor"]},
                        decision=result,
                        method="rule",
                        reasoning="Regra: Rende Fácil detectado + origem CAP = Aplicação",
                        confidence=1.0
                    )
                return result
        
        # Regra: Transferências genéricas PIX/TED
        if "PIX" in desc or "TED" in desc:
            if row["origem"] == "CAP":
                return {
                    "classificacao_sugerida": "Saída de Transferência",
                    "explicacao": "Transferência genérica identificada (saída)"
                }
            else:
                return {
                    "classificacao_sugerida": "Entrada de Transferência",
                    "explicacao": "Transferência genérica identificada (entrada)"
                }
        
        # Regra: Recebimentos por cartão
        if "REDE" in desc or "CARTAO" in desc or "CARTÃO" in desc:
            return {
                "classificacao_sugerida": "Receita com Venda de Serviços",
                "explicacao": "Recebimento via cartão/maquininha"
            }
        
        # Regra: Gympass
        if "GYMPASS" in desc:
            return {
                "classificacao_sugerida": "Gympass",
                "explicacao": "Receita Gympass identificada"
            }
        
        # Regra: Seguros
        if "SEGURO" in desc:
            return {
                "classificacao_sugerida": "Seguros",
                "explicacao": "Seguro identificado na descrição"
            }
        
        # Regra: Consórcios
        if "CONSORCIO" in desc or "CONSÓRCIO" in desc:
            return {
                "classificacao_sugerida": "Consórcios",
                "explicacao": "Consórcio identificado na descrição"
            }
        
        # Regra: Investimentos genéricos
        if any(k in desc for k in ["OUROCAP", "INVEST"]):
            return {
                "classificacao_sugerida": "Investimento",
                "explicacao": "Investimento identificado na descrição"
            }
        
        return None
    
    async def classificar_transacao(self, row: pd.Series) -> Dict[str, str]:
        """
        Classifica uma única transação
        
        Args:
            row: Linha do DataFrame com a transação
            
        Returns:
            Dicionário com classificação e explicação
        """
        logger = get_logger()
        
        # Tenta regras pré-definidas primeiro
        pre_class = self.regras_pre_classificacao(row, log_decision=True)
        if pre_class:
            return pre_class
        
        # Se não conseguiu classificar com regras, usa a IA
        try:
            input_data = {
                "descricao": row["descricao"],
                "origem": row["origem"],
                "valor": row["valor"]
            }
            
            resultado = await self.chain.ainvoke(input_data)
            decision = resultado.model_dump()
            
            # Loga a decisão da IA
            logger.log_classification_decision(
                transaction_id=row.get("index", -1),
                input_data=input_data,
                decision=decision,
                method="ai",
                reasoning=f"IA (GPT-4o-mini) analisou a descrição '{row['descricao'][:50]}...' e classificou como '{decision.get('classificacao_sugerida', 'N/A')}'. Explicação: {decision.get('explicacao', 'N/A')}",
                confidence=None  # GPT não retorna confidence score
            )
            
            return decision
        except Exception as e:
            print(f"❌ Erro ao classificar transação: {e}")
            error_result = {
                "classificacao_sugerida": "Nao classificado",
                "explicacao": f"Erro na classificação: {str(e)}"
            }
            
            logger.log_classification_decision(
                transaction_id=row.get("index", -1),
                input_data={"descricao": row.get("descricao", ""), "origem": row.get("origem", ""), "valor": row.get("valor", 0)},
                decision=error_result,
                method="error",
                reasoning=f"Erro ao classificar: {str(e)}",
                confidence=0.0
            )
            
            return error_result
    
    async def _gather_limit(self, coros: List, limit: int):
        """
        Executa coroutines com limite de concorrência
        
        Args:
            coros: Lista de coroutines
            limit: Limite de concorrência
            
        Returns:
            Resultados das coroutines
        """
        sem = asyncio.Semaphore(limit)
        
        async def run(c):
            async with sem:
                return await c
        
        return await asyncio.gather(*(run(c) for c in coros))
    
    async def classificar_transacoes_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classifica todas as transações do DataFrame
        
        Args:
            df: DataFrame com transações
            
        Returns:
            DataFrame com classificações
        """
        df = df.copy()
        
        # Inicializa colunas se não existirem
        if "classificacao_sugerida" not in df.columns:
            df["classificacao_sugerida"] = None
        if "explicacao" not in df.columns:
            df["explicacao"] = None
        
        # Identifica transações não classificadas
        mask_sem_class = df["classificacao_sugerida"].isna()
        indices = df.index[mask_sem_class]
        
        if len(indices) > 0:
            print(f"   🤖 Classificando {len(indices)} transações com IA...")
            
            # Cria tasks para cada transação
            tasks = [self.classificar_transacao(df.loc[i]) for i in indices]
            
            # Processa em chunks para não sobrecarregar
            resultados = []
            for start in tqdm(range(0, len(tasks), 50), desc="   Progresso"):
                chunk = tasks[start:start + 50]
                out = await self._gather_limit(chunk, self.max_concurrency)
                resultados.extend(out)
            
            # Atualiza o DataFrame com os resultados
            for idx, res in zip(indices, resultados):
                df.loc[idx, ["classificacao_sugerida", "explicacao"]] = [
                    res["classificacao_sugerida"],
                    res["explicacao"]
                ]
        
        return df
    
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executa o processo completo da camada BUSINESS
        
        Args:
            df: DataFrame com transações
            
        Returns:
            DataFrame com classificações
        """
        print("🔄 [BUSINESS LAYER] Iniciando classificação de transações...")
        logger = get_logger()
        
        # Executa classificação assíncrona
        loop = asyncio.get_event_loop()
        df_classificado = loop.run_until_complete(self.classificar_transacoes_df(df))
        
        # Estatísticas
        total = len(df_classificado)
        classificados = df_classificado["classificacao_sugerida"].notna().sum()
        
        print(f"✅ [BUSINESS LAYER] Classificação concluída!")
        print(f"   📊 Total de transações: {total}")
        print(f"   ✨ Transações classificadas: {classificados}")
        
        # Salva logs da sessão
        logger.save_session()
        logger.save_summary_report()
        
        return df_classificado
    
    def save_to_excel(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Salva o DataFrame classificado em Excel
        
        Args:
            df: DataFrame a ser salvo
            output_path: Caminho do arquivo Excel de saída
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"   💾 Excel salvo em: {output_path}")


# Função de conveniência para uso direto
def classify_transactions(df: pd.DataFrame, 
                         regra_path: str = "./src/prompts/regra.json") -> pd.DataFrame:
    """
    Função de conveniência para classificar transações
    
    Args:
        df: DataFrame com transações
        regra_path: Caminho do arquivo de regras
        
    Returns:
        DataFrame com classificações
    """
    business_layer = BusinessLayer(regra_path=regra_path)
    return business_layer.execute(df)
