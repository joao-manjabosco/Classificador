"""
RAW LAYER - Camada de Ingestão de Dados
Responsável por ler arquivos OFX e gerar dados em formato JSON
"""

import json
import ofxparse
from typing import List, Dict, Any
from pathlib import Path


class RawLayer:
    """Processa arquivos OFX e retorna dados brutos em formato JSON"""
    
    def __init__(self):
        self.transactions = []
    
    def process_ofx_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Processa um único arquivo OFX
        
        Args:
            file_path: Caminho do arquivo OFX
            
        Returns:
            Lista de transações extraídas do arquivo
        """
        transactions = []
        
        # Tenta diferentes encodings comuns em arquivos OFX
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        ofx = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    ofx = ofxparse.OfxParser.parse(f)
                    break
            except Exception:
                continue
        
        if ofx is None:
            raise Exception(f"Não foi possível ler o arquivo {file_path} com os encodings disponíveis")
        
        # Extrai informações da conta
        account = ofx.account
        statement = account.statement
        
        # Nome do banco
        banco_nome = "Desconhecido"
        if account.institution and account.institution.organization:
            banco_nome = account.institution.organization
        
        # Processa cada transação
        for transaction in statement.transactions:
            registro = {
                "cod_banco": account.routing_number,
                "banco": banco_nome,
                "agencia": account.branch_id,
                "num_conta": account.account_id,
                "tipo_conta": account.account_type,
                "data_inicio": statement.start_date.strftime('%d/%m/%Y') if statement.start_date else None,
                "data_fim": statement.end_date.strftime('%d/%m/%Y') if statement.end_date else None,
                "saldo": float(statement.balance) if statement.balance else 0.0,
                "favorecido": transaction.payee,
                "tipo_transacao": transaction.type,
                "data": transaction.date.strftime('%d/%m/%Y') if transaction.date else None,
                "valor": float(transaction.amount) if transaction.amount else 0.0,
                "descricao": transaction.memo,
            }
            transactions.append(registro)
        
        return transactions
    
    def process_multiple_ofx_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Processa múltiplos arquivos OFX
        
        Args:
            file_paths: Lista de caminhos dos arquivos OFX
            
        Returns:
            Lista consolidada de todas as transações
        """
        all_transactions = []
        
        for file_path in file_paths:
            try:
                transactions = self.process_ofx_file(file_path)
                all_transactions.extend(transactions)
            except Exception as e:
                print(f"❌ Erro ao processar arquivo {file_path}: {str(e)}")
                continue
        
        return all_transactions
    
    def save_to_json(self, transactions: List[Dict[str, Any]], output_path: str) -> None:
        """
        Salva as transações em um arquivo JSON
        
        Args:
            transactions: Lista de transações
            output_path: Caminho do arquivo JSON de saída
        """
        # Garante que o diretório existe
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, ensure_ascii=False, indent=4)
    
    def execute(self, file_paths: List[str], output_json_path: str) -> Dict[str, Any]:
        """
        Executa o processo completo da camada RAW
        
        Args:
            file_paths: Lista de caminhos dos arquivos OFX
            output_json_path: Caminho do arquivo JSON de saída
            
        Returns:
            Dicionário com informações do processamento
        """
        print("🔄 [RAW LAYER] Iniciando processamento de arquivos OFX...")
        
        # Processa todos os arquivos
        transactions = self.process_multiple_ofx_files(file_paths)
        
        if not transactions:
            raise Exception("Nenhuma transação foi extraída dos arquivos OFX")
        
        # Salva em JSON
        self.save_to_json(transactions, output_json_path)
        
        result = {
            "status": "success",
            "total_files": len(file_paths),
            "total_transactions": len(transactions),
            "output_file": output_json_path
        }
        
        print(f"✅ [RAW LAYER] Processamento concluído!")
        print(f"   📁 Arquivos processados: {len(file_paths)}")
        print(f"   📊 Transações extraídas: {len(transactions)}")
        print(f"   💾 JSON salvo em: {output_json_path}")
        
        return result


# Função de conveniência para uso direto
def process_ofx_to_json(file_paths: List[str], output_json_path: str) -> Dict[str, Any]:
    """
    Função de conveniência para processar arquivos OFX e gerar JSON
    
    Args:
        file_paths: Lista de caminhos dos arquivos OFX
        output_json_path: Caminho do arquivo JSON de saída
        
    Returns:
        Dicionário com informações do processamento
    """
    raw_layer = RawLayer()
    return raw_layer.execute(file_paths, output_json_path)
