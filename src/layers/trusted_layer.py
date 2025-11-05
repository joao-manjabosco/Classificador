"""
TRUSTED LAYER - Camada de Transformação de Dados
Responsável por transformar JSON em DataFrame e aplicar limpezas/transformações
"""

import json
import pandas as pd
from typing import Dict, Any
from pathlib import Path


class TrustedLayer:
    """Transforma dados JSON em DataFrame limpo e estruturado"""
    
    def __init__(self):
        self.df = None
    
    def load_json(self, json_path: str) -> pd.DataFrame:
        """
        Carrega dados de um arquivo JSON
        
        Args:
            json_path: Caminho do arquivo JSON
            
        Returns:
            DataFrame com os dados carregados
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return pd.DataFrame(data)
    
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica transformações nos dados
        
        Args:
            df: DataFrame bruto
            
        Returns:
            DataFrame transformado
        """
        df = df.copy()
        
        # Adiciona coluna de origem baseada no tipo de transação
        df["origem"] = df['tipo_transacao'].map({
            'credit': 'CAR',  # Crédito = Entrada (CAR)
            'debit': 'CAP',   # Débito = Saída (CAP)
            'dep': 'CAR'      # Depósito = Entrada (CAR)
        })
        
        # Preenche valores nulos em origem (caso existam tipos não mapeados)
        df["origem"] = df["origem"].fillna("DESCONHECIDO")
        
        # Converte data para datetime (se necessário para análises futuras)
        if "data" in df.columns:
            try:
                df["data_dt"] = pd.to_datetime(df["data"], format='%d/%m/%Y', errors='coerce')
            except Exception:
                pass
        
        # Remove espaços extras nas strings
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]
        
        # Remove transações com "Saldo" na descrição (saldos iniciais)
        if "descricao" in df.columns:
            mask_saldo = df["descricao"].str.contains("SALDO", case=False, na=False)
            qtd_removidos = mask_saldo.sum()
            if qtd_removidos > 0:
                print(f"   🗑️  Removendo {qtd_removidos} transações de saldo inicial")
            df = df[~mask_saldo].copy()
        
        # Garante que valores monetários são numéricos
        if "valor" in df.columns:
            df["valor"] = pd.to_numeric(df["valor"], errors='coerce').fillna(0.0)
        
        if "saldo" in df.columns:
            df["saldo"] = pd.to_numeric(df["saldo"], errors='coerce').fillna(0.0)
        
        return df
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valida a qualidade dos dados
        
        Args:
            df: DataFrame a ser validado
            
        Returns:
            Dicionário com informações de validação
        """
        validation = {
            "total_records": len(df),
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict()
        }
        
        return validation
    
    def execute(self, json_path: str) -> pd.DataFrame:
        """
        Executa o processo completo da camada TRUSTED
        
        Args:
            json_path: Caminho do arquivo JSON de entrada
            
        Returns:
            DataFrame transformado e limpo
        """
        print("🔄 [TRUSTED LAYER] Iniciando transformação de dados...")
        
        # Carrega JSON
        df = self.load_json(json_path)
        print(f"   📊 Registros carregados: {len(df)}")
        
        # Transforma dados
        df = self.transform_data(df)
        print(f"   ✨ Transformações aplicadas")
        
        # Valida dados
        validation = self.validate_data(df)
        print(f"   ✅ Validação concluída")
        print(f"   📈 Total de registros: {validation['total_records']}")
        
        self.df = df
        
        print(f"✅ [TRUSTED LAYER] Transformação concluída!")
        
        return df
    
    def save_to_csv(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Salva o DataFrame em CSV (opcional)
        
        Args:
            df: DataFrame a ser salvo
            output_path: Caminho do arquivo CSV de saída
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"   💾 CSV salvo em: {output_path}")


# Função de conveniência para uso direto
def transform_json_to_dataframe(json_path: str) -> pd.DataFrame:
    """
    Função de conveniência para transformar JSON em DataFrame
    
    Args:
        json_path: Caminho do arquivo JSON
        
    Returns:
        DataFrame transformado
    """
    trusted_layer = TrustedLayer()
    return trusted_layer.execute(json_path)
