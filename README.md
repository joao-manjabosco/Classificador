# 🏦 Classificador de Transações Bancárias com IA

<div align="center">
  <img src="./static/TAG_BSS_OFICIAL.png" alt="TAG Business Solutions" height="100">
  
  **Sistema inteligente para análise e classificação automática de transações bancárias**
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
  [![OpenAI](https://img.shields.io/badge/AI-GPT--4-orange.svg)](https://openai.com/)
</div>

---

Sistema profissional desenvolvido pela **TAG Business Solutions** para processamento automatizado de extratos bancários (OFX), classificação inteligente via IA e geração de relatórios executivos com análise estratégica completa.

## ✨ Características Principais

### 🎯 Funcionalidades Core

- **📊 Processamento OFX Multi-Banco**
  - Suporte para Banco do Brasil e Itaú
  - Upload múltiplo de arquivos
  - Processamento em lote otimizado

- **🤖 Classificação Inteligente com IA**
  - Powered by OpenAI GPT-4
  - Categorização automática e contextual
  - Aprendizado baseado em padrões
  - Sistema de regras personalizável

- **📈 Análise Financeira Completa**
  - DRE (Demonstração do Resultado do Exercício)
  - DFC (Demonstração de Fluxo de Caixa)
  - Análise de tendências mensais e anuais
  - Identificação de padrões sazonais
  - Comparativos período a período

- **🎯 Inteligência Estratégica**
  - Análise SWOT automatizada
  - Identificação de eventos-chave
  - Planos de ação priorizados
  - Insights e recomendações executivas

- **📄 Relatórios Profissionais**
  - PDF executivo com design premium
  - Excel com dados editáveis
  - Interface web interativa
  - Gráficos e visualizações dinâmicas

- **🌐 Interface Moderna**
  - Design responsivo (Desktop, Tablet, Mobile)
  - Drag & drop para upload
  - Edição inline de transações
  - Temas corporativos TAG BSS

- **🔒 Segurança e Auditoria**
  - Logs detalhados de decisões da IA
  - Rastreabilidade completa
  - Dados processados localmente

## 🏗️ Arquitetura do Sistema

O projeto segue uma arquitetura em camadas:

```
├── Raw Layer (Camada Bruta)        # Processamento inicial dos arquivos OFX
├── Trusted Layer (Camada Confiável) # Limpeza e normalização dos dados
├── Business Layer (Camada Negócio)  # Classificação inteligente com IA
├── Financial Analysis              # Análise financeira e insights
└── Strategic Analyzer             # Análise estratégica e SWOT
```

### 📁 Estrutura do Projeto

```
Classificador/
├── app.py                     # Aplicação Flask principal
├── main.ipynb                # Jupyter Notebook para testes
├── requirements.txt          # Dependências Python
├── upgrade_pdf.py           # Script para upgrade do gerador PDF
│
├── src/
│   ├── layers/
│   │   ├── raw_layer.py           # Processamento inicial OFX
│   │   ├── trusted_layer.py       # Limpeza e normalização
│   │   ├── business_layer.py      # Classificação com IA
│   │   ├── financial_analysis.py  # Análise financeira
│   │   └── strategic_analyzer.py  # Análise estratégica
│   │
│   ├── models/
│   │   └── template_saida.json    # Template de saída padronizada
│   │
│   ├── prompts/
│   │   ├── categorias.json        # Categorias de transações
│   │   ├── modelo.json           # Modelo de resposta da IA
│   │   └── regra.json           # Regras de classificação
│   │
│   ├── utils/
│   │   ├── pdf_generator.py             # Gerador de PDF básico
│   │   ├── executive_pdf_generator_v2.py # Gerador PDF executivo avançado
│   │   └── ai_decision_logger.py        # Sistema de logs da IA
│   │
│   ├── log/                      # Logs das decisões da IA
│   └── reports/                  # Relatórios JSON gerados
│
├── static/
│   └── css/
│       └── theme.css            # Estilos da interface web
│
├── templates/
│   ├── index.html              # Página principal
│   ├── results.html           # Resultados da análise
│   ├── relatorio.html         # Visualização de relatórios
│   └── relatorio_executivo.html # Relatório executivo
│
├── uploads/                    # Arquivos OFX carregados
└── output/                    # Arquivos processados e PDFs gerados
```

## 📋 Pré-requisitos

- Python 3.8+
- Chave da API OpenAI
- Navegador web moderno

## 🛠️ Instalação

1. **Clone o repositório**:
   ```bash
   git clone [url-do-repositorio]
   cd Classificador
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # ou
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure a chave da API**:
   - Defina a variável de ambiente `OPENAI_API_KEY`
   - Ou configure diretamente no código (não recomendado para produção)
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="sua-chave-aqui"
   
   # Linux/Mac
   export OPENAI_API_KEY="sua-chave-aqui"
   ```

## 🚀 Como Usar

### 1️⃣ Iniciar a Aplicação

```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

### 2️⃣ Upload de Arquivos OFX

1. Acesse a interface web pelo navegador
2. Arraste seus arquivos OFX ou clique para selecionar
3. Aguarde o upload (múltiplos arquivos suportados)
4. Clique em **"Processar Arquivos"**

### 3️⃣ Análise e Classificação

O sistema irá automaticamente:
- ✅ Processar os arquivos OFX
- ✅ Extrair todas as transações
- ✅ Classificar via IA (GPT-4)
- ✅ Gerar análises financeiras
- ✅ Criar insights estratégicos

### 4️⃣ Visualizar e Editar Resultados

**Página de Resultados:**
- 📊 Visualize estatísticas gerais (Entrada, Saída, Saldo)
- 📈 Gráficos de evolução mensal
- 📋 Tabela completa de transações
- ✏️ Edite categorias e descrições inline
- 💾 Salve alterações em tempo real
- 📥 Baixe Excel com dados completos

### 5️⃣ Relatórios Executivos

**Relatório Completo:**
- 📄 DRE e DFC detalhados
- 📊 Análise por categoria
- 📈 Tendências e comparativos

**Relatório Executivo:**
- 🎯 Sumário executivo com eventos-chave
- 💰 Análise de receitas (mensal, anual, sazonalidade)
- 📦 Análise de custos e despesas
- 💵 Fluxo de caixa detalhado
- 🎯 Análise SWOT completa
- 📋 Planos de ação priorizados
- 📥 Download em PDF profissional

## 📊 Funcionalidades Detalhadas

### Classificação de Transações
- Categorização automática em: Alimentação, Transporte, Saúde, Educação, etc.
- Identificação de receitas e despesas
- Detecção de padrões e anomalias

### Análise Financeira
- Cálculo de totais por categoria
- Análise de tendências mensais
- Identificação de maiores gastos
- Comparativo de períodos

### Análise Estratégica
- **SWOT Analysis**: Forças, Fraquezas, Oportunidades e Ameaças
- **Planos de Ação**: Sugestões práticas baseadas nos dados
- **Insights Personalizados**: Recomendações específicas do perfil financeiro

### Relatórios
- **PDF Detalhado**: Relatório completo com gráficos e tabelas
- **PDF Executivo**: Resumo estratégico para tomada de decisões
- **Dados JSON**: Exportação estruturada para integração com outros sistemas

## 🔧 Configurações

### Categorias de Transações
As categorias são definidas em `src/prompts/categorias.json` e incluem:
- Alimentação
- Transporte
- Moradia
- Saúde e Bem-estar
- Educação
- Entretenimento
- Compras
- Serviços Financeiros
- Outros

### Sistema de Logs
Todas as decisões da IA são registradas em:
- `src/log/ai_decisions_[timestamp].json` (estruturado)
- `src/log/ai_decisions_[timestamp].txt` (legível)

## 🔐 Segurança e Privacidade

- Processamento local dos dados financeiros
- Não armazenamento permanente de informações sensíveis
- Logs detalhados para auditoria
- Limpeza automática de arquivos temporários
- Comunicação segura com API OpenAI via HTTPS

## �️ Stack Tecnológico

### Backend
- **Python 3.8+** - Linguagem principal
- **Flask 3.0+** - Framework web
- **Pandas** - Manipulação de dados
- **BeautifulSoup4** - Parsing de XML/OFX
- **ReportLab** - Geração de PDFs

### Inteligência Artificial
- **OpenAI GPT-4** - Modelo de linguagem para classificação e análise
- **Prompt Engineering** - Sistema de prompts otimizado para análise financeira

### Frontend
- **HTML5 / CSS3** - Interface responsiva
- **JavaScript** - Interatividade e validações
- **Design Responsivo** - Mobile, Tablet e Desktop

### Outros
- **JSON** - Armazenamento de configurações e dados
- **OFX** - Formato de arquivos bancários suportado

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou suporte:
- Abra uma issue no GitHub
- Consulte a documentação no código
- Verifique os logs em `src/log/` para debugging

## 🎨 Screenshots

### Página Inicial
Interface moderna com drag & drop para upload de arquivos OFX.

### Resultados
Dashboard com estatísticas, gráficos e tabela editável de transações.

### Relatório Executivo
Análise SWOT, planos de ação e insights estratégicos.

## 🔄 Roadmap e Melhorias Futuras

### Em Desenvolvimento
- [ ] Gráficos interativos avançados (Chart.js)
- [ ] Dashboard com atualizações em tempo real
- [ ] Sistema de alertas e notificações
- [ ] Exportação personalizada de relatórios

### Planejado
- [ ] Suporte a mais instituições bancárias
- [ ] API REST para integrações externas
- [ ] App mobile (iOS/Android)
- [ ] Comparativos com benchmarks de mercado
- [ ] Previsões financeiras com ML
- [ ] Análise de investimentos
- [ ] Multi-idioma (EN, ES)

## 🐛 Troubleshooting

### Erro ao processar OFX
- Verifique se o arquivo está no formato correto (.ofx)
- Confirme se é do Banco do Brasil ou Itaú
- Tente fazer download novamente do arquivo do banco

### IA não está classificando
- Verifique se a `OPENAI_API_KEY` está configurada
- Confirme se há créditos na sua conta OpenAI
- Verifique os logs em `src/log/`
- Teste a conectividade com a API OpenAI

### Erro de timeout na API
- Aumente o timeout nas requisições
- Verifique sua conexão com a internet
- Considere processar em lotes menores

### Interface não carrega
- Confirme se o Flask está rodando (`python app.py`)
- Verifique se a porta 5000 não está em uso
- Limpe o cache do navegador

## 📚 Documentação Adicional

- **Prompts da IA**: `src/prompts/` - Configuração de categorias e regras
- **Logs**: `src/log/` - Histórico de decisões da IA
- **Templates**: `src/models/` - Estruturas de dados

## 👥 Equipe

Desenvolvido por **TAG Business Solutions**

- **Análise de Requisitos**: Especialistas em finanças
- **Desenvolvimento**: Engenheiros de Software
- **Design**: UI/UX Designers
- **IA**: Machine Learning Engineers

## 📄 Licença

Este projeto é proprietário da **TAG Business Solutions**.
Todos os direitos reservados © 2025.

## 🌟 Agradecimentos

- OpenAI pela API GPT-4
- Comunidade Python
- Instituições bancárias pela documentação OFX
- Contribuidores open-source

---

<div align="center">
  <strong>🏦 Sistema de Classificação Financeira com IA - v2.0</strong>
  
  Desenvolvido com ❤️ pela TAG Business Solutions
  
  [Website](https://tag-bss.com) • Documentação • Suporte
</div>
