"""
AI DECISION LOGGER - Sistema de Logging de Decisões da IA
Registra como a IA chegou em cada conclusão/classificação
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class AIDecisionLogger:
    """Logger para registrar decisões e raciocínio da IA"""
    
    def __init__(self, log_dir: str = "./src/log"):
        """
        Inicializa o logger
        
        Args:
            log_dir: Diretório onde os logs serão salvos
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivo de log da sessão atual
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.log_dir / f"ai_decisions_{timestamp}.json"
        
        # Buffer de decisões
        self.decisions = []
        
        # Metadata da sessão
        self.session_metadata = {
            "session_id": timestamp,
            "start_time": datetime.now().isoformat(),
            "total_decisions": 0,
            "decision_types": {}
        }
    
    def log_classification_decision(self,
                                   transaction_id: int,
                                   input_data: Dict[str, Any],
                                   decision: Dict[str, Any],
                                   method: str,
                                   reasoning: str,
                                   confidence: Optional[float] = None) -> None:
        """
        Registra uma decisão de classificação de transação
        
        Args:
            transaction_id: ID da transação
            input_data: Dados de entrada (descrição, valor, origem, etc)
            decision: Decisão tomada (classificação, explicação)
            method: Método usado ('rule' ou 'ai')
            reasoning: Raciocínio/justificativa
            confidence: Nível de confiança (0-1) se aplicável
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "classification",
            "transaction_id": transaction_id,
            "input": input_data,
            "decision": decision,
            "method": method,
            "reasoning": reasoning,
            "confidence": confidence
        }
        
        self.decisions.append(log_entry)
        self.session_metadata["total_decisions"] += 1
        
        # Conta tipos de decisão
        if method not in self.session_metadata["decision_types"]:
            self.session_metadata["decision_types"][method] = 0
        self.session_metadata["decision_types"][method] += 1
    
    def log_analysis_decision(self,
                            analysis_type: str,
                            input_data: Dict[str, Any],
                            output: Dict[str, Any],
                            reasoning: str,
                            calculations: Optional[Dict[str, Any]] = None) -> None:
        """
        Registra uma decisão de análise financeira/estratégica
        
        Args:
            analysis_type: Tipo de análise (swot, diagnostico, tendencia, etc)
            input_data: Dados de entrada usados
            output: Resultado da análise
            reasoning: Como chegou na conclusão
            calculations: Cálculos realizados
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "analysis",
            "analysis_type": analysis_type,
            "input": input_data,
            "output": output,
            "reasoning": reasoning,
            "calculations": calculations
        }
        
        self.decisions.append(log_entry)
        self.session_metadata["total_decisions"] += 1
    
    def log_comparison_decision(self,
                               comparison_type: str,
                               period_a: str,
                               period_b: str,
                               metrics: Dict[str, Any],
                               interpretation: str,
                               calculations: Dict[str, Any]) -> None:
        """
        Registra uma decisão de comparação entre períodos
        
        Args:
            comparison_type: Tipo de comparação (mensal, anual, etc)
            period_a: Período A (ex: "Julho 2025")
            period_b: Período B (ex: "Agosto 2025")
            metrics: Métricas comparadas
            interpretation: Interpretação dos resultados
            calculations: Cálculos detalhados
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "comparison",
            "comparison_type": comparison_type,
            "period_a": period_a,
            "period_b": period_b,
            "metrics": metrics,
            "interpretation": interpretation,
            "calculations": calculations
        }
        
        self.decisions.append(log_entry)
        self.session_metadata["total_decisions"] += 1
    
    def log_strategic_insight(self,
                            insight_type: str,
                            data_analyzed: Dict[str, Any],
                            insight: str,
                            evidence: List[str],
                            recommendation: Optional[str] = None) -> None:
        """
        Registra um insight estratégico gerado pela IA
        
        Args:
            insight_type: Tipo de insight (oportunidade, ameaça, força, fraqueza)
            data_analyzed: Dados que foram analisados
            insight: Insight identificado
            evidence: Evidências que suportam o insight
            recommendation: Recomendação associada
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "strategic_insight",
            "insight_type": insight_type,
            "data_analyzed": data_analyzed,
            "insight": insight,
            "evidence": evidence,
            "recommendation": recommendation
        }
        
        self.decisions.append(log_entry)
        self.session_metadata["total_decisions"] += 1
    
    def save_session(self) -> str:
        """
        Salva todos os logs da sessão em arquivo JSON
        
        Returns:
            Caminho do arquivo salvo
        """
        self.session_metadata["end_time"] = datetime.now().isoformat()
        
        full_log = {
            "metadata": self.session_metadata,
            "decisions": self.decisions
        }
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(full_log, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Log de decisões salvo: {self.session_file}")
        print(f"   📊 Total de decisões: {self.session_metadata['total_decisions']}")
        print(f"   🔍 Tipos: {self.session_metadata['decision_types']}")
        
        return str(self.session_file)
    
    def save_summary_report(self) -> str:
        """
        Gera relatório resumido em formato texto
        
        Returns:
            Caminho do arquivo de resumo
        """
        summary_file = self.session_file.with_suffix('.txt')
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RELATÓRIO DE DECISÕES DA IA\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Sessão: {self.session_metadata['session_id']}\n")
            f.write(f"Início: {self.session_metadata['start_time']}\n")
            f.write(f"Fim: {self.session_metadata.get('end_time', 'Em andamento')}\n")
            f.write(f"Total de decisões: {self.session_metadata['total_decisions']}\n\n")
            
            f.write("-"*80 + "\n")
            f.write("TIPOS DE DECISÕES\n")
            f.write("-"*80 + "\n")
            for dtype, count in self.session_metadata['decision_types'].items():
                f.write(f"  {dtype}: {count} decisões\n")
            f.write("\n")
            
            # Agrupa decisões por tipo
            classifications = [d for d in self.decisions if d['type'] == 'classification']
            analyses = [d for d in self.decisions if d['type'] == 'analysis']
            comparisons = [d for d in self.decisions if d['type'] == 'comparison']
            insights = [d for d in self.decisions if d['type'] == 'strategic_insight']
            
            # Resumo de classificações
            if classifications:
                f.write("-"*80 + "\n")
                f.write(f"CLASSIFICAÇÕES ({len(classifications)} transações)\n")
                f.write("-"*80 + "\n")
                
                # Contadores
                by_method = {}
                for c in classifications:
                    method = c['method']
                    by_method[method] = by_method.get(method, 0) + 1
                
                f.write(f"\nMétodos usados:\n")
                for method, count in by_method.items():
                    f.write(f"  - {method}: {count} transações\n")
                f.write("\n")
                
                # Primeiras 5 classificações como exemplo
                f.write("Exemplos de classificações:\n\n")
                for i, c in enumerate(classifications[:5], 1):
                    f.write(f"{i}. Transação ID {c['transaction_id']}\n")
                    f.write(f"   Entrada: {c['input'].get('descricao', 'N/A')[:60]}\n")
                    f.write(f"   Decisão: {c['decision'].get('classificacao_sugerida', 'N/A')}\n")
                    f.write(f"   Método: {c['method']}\n")
                    f.write(f"   Raciocínio: {c['reasoning'][:100]}...\n\n")
            
            # Resumo de análises
            if analyses:
                f.write("\n" + "="*80 + "\n")
                f.write("EXPLICAÇÕES DAS DECISÕES DO RELATÓRIO EXECUTIVO\n")
                f.write("="*80 + "\n")
                f.write("Esta seção mostra COMO A IA chegou em cada conclusão do relatório.\n")
                f.write("Cada análise abaixo foi usada para gerar o PDF executivo.\n")
                f.write("="*80 + "\n\n")
                
                f.write("-"*80 + "\n")
                f.write(f"ANÁLISES ESTRATÉGICAS ({len(analyses)} análises)\n")
                f.write("-"*80 + "\n\n")
                
                for i, a in enumerate(analyses, 1):
                    f.write(f"{i}. {a['analysis_type'].upper()}\n")
                    f.write(f"   Data/Hora: {a['timestamp']}\n")
                    
                    # Mostra o raciocínio completo (não truncado)
                    reasoning = a.get('reasoning', 'Sem raciocínio registrado')
                    f.write(f"\n   EXPLICAÇÃO DE COMO A IA CHEGOU NESTA CONCLUSÃO:\n")
                    # Indenta o raciocínio para melhor legibilidade
                    for linha in reasoning.split('\n'):
                        f.write(f"   {linha}\n")
                    f.write("\n" + "-"*80 + "\n\n")
            
            # Resumo de comparações
            if comparisons:
                f.write("-"*80 + "\n")
                f.write(f"COMPARAÇÕES ({len(comparisons)} comparações)\n")
                f.write("-"*80 + "\n\n")
                
                for i, c in enumerate(comparisons, 1):
                    f.write(f"{i}. {c['comparison_type']}: {c['period_a']} vs {c['period_b']}\n")
                    f.write(f"   Interpretação: {c['interpretation'][:150]}\n\n")
            
            # Resumo de insights estratégicos
            if insights:
                f.write("-"*80 + "\n")
                f.write(f"INSIGHTS ESTRATÉGICOS ({len(insights)} insights)\n")
                f.write("-"*80 + "\n\n")
                
                for i, ins in enumerate(insights, 1):
                    f.write(f"{i}. {ins['insight_type'].upper()}\n")
                    f.write(f"   Data/Hora: {ins['timestamp']}\n")
                    f.write(f"   Insight: {ins['insight']}\n")
                    
                    # Mostra evidências que suportam o insight
                    if ins.get('evidence'):
                        f.write(f"\n   EVIDÊNCIAS:\n")
                        for ev in ins['evidence']:
                            f.write(f"   • {ev}\n")
                    
                    if ins.get('recommendation'):
                        f.write(f"\n   RECOMENDAÇÃO:\n   {ins['recommendation']}\n")
                    f.write("\n" + "-"*80 + "\n\n")
            
            f.write("="*80 + "\n")
            f.write("FIM DO RELATÓRIO\n")
            f.write("="*80 + "\n")
        
        print(f"📄 Resumo salvo: {summary_file}")
        
        return str(summary_file)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da sessão
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            "total_decisions": len(self.decisions),
            "decision_types": self.session_metadata["decision_types"],
            "session_duration": (datetime.now() - datetime.fromisoformat(self.session_metadata["start_time"])).total_seconds(),
            "log_file": str(self.session_file)
        }


# Instância global do logger (singleton)
_global_logger: Optional[AIDecisionLogger] = None


def get_logger() -> AIDecisionLogger:
    """Retorna a instância global do logger"""
    global _global_logger
    if _global_logger is None:
        _global_logger = AIDecisionLogger()
    return _global_logger


def reset_logger() -> None:
    """Reseta o logger global (útil para testes)"""
    global _global_logger
    _global_logger = None
