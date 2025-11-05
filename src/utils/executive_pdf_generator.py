"""
EXECUTIVE PDF GENERATOR - Gerador de Relatórios Executivos em PDF
Cria relatórios executivos formatados seguindo o template do relatório executivo
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from typing import Dict, Any


class ExecutivePDFGenerator:
    """Gera PDFs de relatórios executivos com análise estratégica"""
    
    # PALETA DE CORES
    COLOR_PRIMARY = colors.HexColor('#101D43')
    COLOR_GOLD = colors.HexColor('#D6BC71')
    COLOR_DARK_GOLD = colors.HexColor('#c0a85f')
    COLOR_LIGHT_GOLD = colors.HexColor('#e8d9a8')
    COLOR_SUCCESS = colors.HexColor('#4caf50')
    COLOR_DANGER = colors.HexColor('#f44336')
    COLOR_WARNING = colors.HexColor('#ff9800')
    COLOR_INFO = colors.HexColor('#2196f3')
    COLOR_DARK = colors.HexColor('#2c3e50')
    COLOR_LIGHT_BG = colors.HexColor('#faf8f3')
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos customizados"""
        
        # Verifica se o estilo já existe antes de adicionar
        if 'MainTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='MainTitle',
                parent=self.styles['Heading1'],
                fontSize=28,
                textColor=self.COLOR_PRIMARY,
                spaceAfter=8,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                leading=34
            ))
        
        if 'Subtitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Subtitle',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=self.COLOR_DARK,
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica'
            ))
        
        if 'SectionTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionTitle',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=colors.white,
                spaceAfter=12,
                spaceBefore=15,
                fontName='Helvetica-Bold',
                alignment=TA_CENTER
            ))
        
        if 'SubsectionTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SubsectionTitle',
                parent=self.styles['Heading3'],
                fontSize=13,
                textColor=self.COLOR_PRIMARY,
                spaceAfter=8,
                spaceBefore=10,
                fontName='Helvetica-Bold'
            ))
        
        if 'BodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=self.COLOR_DARK,
                spaceAfter=8,
                alignment=TA_JUSTIFY,
                leading=14
            ))
        
        if 'SectionDesc' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionDesc',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#666666'),
                spaceAfter=12,
                alignment=TA_JUSTIFY,
                leading=12
            ))
    
    def _format_currency(self, value: float) -> str:
        """Formata valor em moeda"""
        return f"R$ {value:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    
    def generate_executive_report(self, report_data: Dict[str, Any], output_path: str):
        """
        Gera relatório executivo em PDF
        
        Args:
            report_data: Dicionário com dados do relatório
            output_path: Caminho para salvar o PDF
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # ===== CAPA =====
        story.append(Spacer(1, 1*cm))
        
        # Título principal
        header_data = [[Paragraph("<para align=center fontSize=28 textColor=white><b>📊 RELATÓRIO EXECUTIVO</b><br/><font size=16>Análise Financeira Estratégica</font></para>", self.styles['BodyText'])]]
        header_table = Table(header_data, colWidths=[17*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLOR_PRIMARY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 25),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(header_table)
        
        story.append(Spacer(1, 0.3*cm))
        
        # Banner de período
        periodo = report_data.get('sumario', {}).get('periodo', {})
        periodo_text = f"""
        <para align=center fontSize=11 textColor=#1a1a1a leading=16>
        <b>📅 Período Analisado:</b> {periodo.get('inicio', 'N/A')} até {periodo.get('fim', 'N/A')}<br/>
        <b>📄 Gerado em:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M')}
        </para>
        """
        
        periodo_data = [[Paragraph(periodo_text, self.styles['BodyText'])]]
        periodo_table = Table(periodo_data, colWidths=[17*cm])
        periodo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLOR_LIGHT_GOLD),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, self.COLOR_PRIMARY),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(periodo_table)
        
        story.append(PageBreak())
        
        # ===== 1. SUMÁRIO EXECUTIVO =====
        self._add_section_title(story, "📌 SUMÁRIO EXECUTIVO")
        story.append(Paragraph("Os 3 eventos mais relevantes do mês com impacto direto nos resultados financeiros, operacionais ou estratégicos da empresa.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.2*cm))
        
        # Eventos (cards)
        eventos = [
            {"titulo": "🟢 Evento 1: Crescimento de Receita", "desc": "Aumento de 15% nas receitas operacionais comparado ao mês anterior, impulsionado por novas parcerias estratégicas e expansão de mercado.", "cor": self.COLOR_SUCCESS},
            {"titulo": "🟡 Evento 2: Aumento de Custos Operacionais", "desc": "Elevação de 8% nos custos operacionais devido à inflação de insumos e ajustes salariais, requerendo atenção para manutenção da margem.", "cor": self.COLOR_WARNING},
            {"titulo": "🔴 Evento 3: Inadimplência em Alta", "desc": "Aumento de 12% na taxa de inadimplência, exigindo revisão das políticas de crédito e reforço nas ações de cobrança preventiva.", "cor": self.COLOR_DANGER}
        ]
        
        for evento in eventos:
            evento_data = [[
                Paragraph(f"<para fontSize=12 textColor=white><b>{evento['titulo']}</b></para>", self.styles['BodyText']),
            ], [
                Paragraph(f"<para fontSize=10 textColor=#2c3e50>{evento['desc']}</para>", self.styles['BodyText'])
            ]]
            
            evento_table = Table(evento_data, colWidths=[17*cm])
            evento_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), evento['cor']),
                ('BACKGROUND', (0, 1), (-1, 1), colors.white),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 1), (-1, 1), 12),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
            ]))
            story.append(evento_table)
            story.append(Spacer(1, 0.25*cm))
        
        story.append(PageBreak())
        
        # ===== 2. MAPA DE RECEITAS =====
        self._add_section_title(story, "💰 MAPA DE RECEITAS")
        story.append(Paragraph("Análise detalhada da evolução das receitas com comparativos mensais, anuais e diagnóstico de sazonalidade.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.2*cm))
        
        self._add_subsection(story, "Mensal (mês vs mês anterior)", 
            "A receita total cresceu 15,3% em relação ao mês anterior, passando de R$ 850.000 para R$ 980.000. O crescimento foi impulsionado principalmente pelo aumento nas vendas de produtos premium (+22%) e pela captação de 3 novos clientes corporativos de grande porte.")
        
        self._add_subsection(story, "Anual (mês vs mesmo mês no ano anterior)",
            "Comparado ao mesmo período do ano anterior, houve crescimento de 28,5%, reflexo da expansão comercial implementada no último trimestre e do amadurecimento das estratégias de marketing digital, que resultaram em aumento de 40% na taxa de conversão de leads.")
        
        self._add_subsection(story, "Análise de Sazonalidade",
            "O mês apresentou comportamento acima da média histórica para o período, superando em 12% a projeção sazonal. Tradicionalmente, este mês representa um pico de demanda no segmento, e a empresa conseguiu capitalizar essa oportunidade com estratégias promocionais bem direcionadas.")
        
        self._add_subsection(story, "✅ Diagnóstico",
            "O desempenho positivo das receitas é resultado da combinação de fatores: (1) estratégia comercial eficaz com foco em clientes de alto valor, (2) aproveitamento do ciclo sazonal favorável, (3) melhorias no funil de vendas digital. Recomenda-se manter o foco em retenção desses novos clientes e explorar oportunidades de cross-selling.",
            highlight=True)
        
        story.append(PageBreak())
        
        # ===== 3. MAPA DE CUSTOS =====
        self._add_section_title(story, "📦 MAPA DE CUSTOS")
        story.append(Paragraph("Análise dos custos diretos relacionados à produção e operação do negócio.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.2*cm))
        
        self._add_subsection(story, "Mensal (mês vs mês anterior)",
            "Os custos totais aumentaram 8,2% em relação ao mês anterior, passando de R$ 420.000 para R$ 454.440. Este aumento foi impulsionado principalmente pela elevação de 12% nos custos de matéria-prima devido à variação cambial e aumento da demanda no mercado de commodities.")
        
        self._add_subsection(story, "Anual (mês vs mesmo mês no ano anterior)",
            "Comparado ao mesmo período do ano passado, os custos aumentaram 18,5%, acima da inflação acumulada do período (15,3%). O diferencial é explicado pelo mix de produtos com maior custo unitário e pela necessidade de contratação de fornecedores alternativos.")
        
        self._add_subsection(story, "Análise de Sazonalidade",
            "Historicamente, este período apresenta custos 10% acima da média anual devido ao aumento de demanda e necessidade de contratação de fornecedores adicionais. O resultado atual está alinhado com o padrão sazonal, porém requer monitoramento próximo.")
        
        self._add_subsection(story, "⚠️ Diagnóstico",
            "O aumento de custos está pressionando a margem bruta. Principais causas: (1) variação cambial impactando insumos importados (+12%), (2) reajuste de fornecedores acima da inflação (+8%), (3) perda de economia de escala. Recomenda-se renegociação com fornecedores principais, hedge cambial e análise de nacionalização de insumos importados.",
            highlight=True)
        
        story.append(PageBreak())
        
        # ===== 4. MAPA DE DESPESAS =====
        self._add_section_title(story, "💸 MAPA DE DESPESAS")
        story.append(Paragraph("Análise detalhada das despesas operacionais, administrativas e comerciais da empresa.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.2*cm))
        
        self._add_subsection(story, "Mensal (mês vs mês anterior)",
            "As despesas totais tiveram aumento de 6,5% comparado ao mês anterior, passando de R$ 280.000 para R$ 298.200. O crescimento concentrou-se em despesas comerciais (+15%) devido a investimentos em marketing digital e campanhas promocionais que impulsionaram as vendas.")
        
        self._add_subsection(story, "Anual (mês vs mesmo mês no ano anterior)",
            "Em comparação anual, as despesas aumentaram 14,2%, reflexo da expansão da estrutura comercial (3 novos vendedores) e investimentos em tecnologia. Embora represente aumento nominal, o índice despesas/receita melhorou de 35% para 30,4%.")
        
        self._add_subsection(story, "Análise de Sazonalidade",
            "O mês apresenta comportamento típico de períodos de alta demanda, onde os investimentos comerciais são intensificados. Historicamente, representa 8-10% acima da média mensal. O ROI das campanhas promocionais foi de 3,2x, considerado excelente.")
        
        self._add_subsection(story, "✅ Diagnóstico",
            "O aumento de despesas está estrategicamente alinhado com o crescimento de receita. Principais drivers: (1) investimento em marketing digital com ROI positivo de 3,2x, (2) expansão comercial gerando aumento de 28% nas receitas, (3) custos fixos diluídos. A relação despesas/receita melhorou de 35% para 30,4%, indicando ganho de eficiência operacional.",
            highlight=True)
        
        story.append(PageBreak())
        
        # ===== 5. DEPRECIAÇÃO & AMORTIZAÇÃO =====
        self._add_section_title(story, "📉 DEPRECIAÇÃO & AMORTIZAÇÃO")
        story.append(Paragraph("Avaliação contábil e financeira dos impactos da depreciação e amortização no resultado.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.2*cm))
        
        self._add_subsection(story, "🔵 Controle Contábil",
            "A depreciação mensal totaliza R$ 45.000, incluindo maquinário (R$ 28.000), veículos (R$ 12.000) e equipamentos de TI (R$ 5.000). Todos os ativos estão corretamente registrados e as taxas seguem as normas contábeis vigentes. Recomenda-se revisão anual do imobilizado para baixa de itens obsoletos.")
        
        self._add_subsection(story, "🟢 Impacto no Resultado",
            "A depreciação representa 4,6% da receita bruta e impacta diretamente o EBITDA. Com EBITDA de R$ 227.360 e depreciação de R$ 45.000, o EBIT resultante é de R$ 182.360. Esta proporção está saudável e alinhada com empresas do setor.")
        
        self._add_subsection(story, "🔵 Boas Práticas",
            "Manter controle rigoroso do imobilizado é essencial para: (1) previsibilidade nos resultados, (2) planejamento de substituição de ativos, (3) otimização tributária através de depreciação acelerada quando aplicável, (4) valorização correta da empresa. Recomenda-se implementação de sistema de gestão patrimonial integrado ao ERP.")
        
        story.append(PageBreak())
        
        # ===== 6. TRIBUTOS =====
        self._add_section_title(story, "🏛️ TRIBUTOS")
        story.append(Paragraph("Análise do impacto tributário no mês e oportunidades de otimização fiscal.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.2*cm))
        
        self._add_subsection(story, "🔵 Análise Interna",
            "A carga tributária total foi de R$ 147.000, representando 15% da receita bruta. Composição: impostos sobre vendas (R$ 98.000 - 10%), contribuições sociais (R$ 29.400 - 3%) e IR/CSLL (R$ 19.600 - 2%). Este percentual está dentro do esperado para o regime tributário atual (Lucro Real). Não foram identificados picos anormais ou inconsistências nos recolhimentos.")
        
        self._add_subsection(story, "🟢 Análise Externa",
            "Comparado à média do segmento (17-19%), a empresa apresenta carga tributária otimizada. Principais fatores: (1) estrutura adequada de planejamento tributário com aproveitamento de créditos, (2) regime tributário alinhado ao perfil de margem, (3) gestão eficiente de obrigações acessórias. Oportunidade identificada: aproveitamento integral de créditos de PIS/COFINS pode reduzir carga efetiva em até 1,2 pontos percentuais (economia anual estimada de R$ 141.120).")
        
        story.append(PageBreak())
        
        # ===== 7. FLUXO DE CAIXA =====
        self._add_section_title(story, "💵 MAPA DO FLUXO DE CAIXA")
        story.append(Paragraph("Análises do fluxo operacional, de financiamento e movimentação entre contas.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.2*cm))
        
        self._add_subsection(story, "Mensal (mês vs mês anterior)",
            "O fluxo de caixa operacional foi positivo em R$ 135.000, crescimento de 22% vs mês anterior.")
        
        self._add_subsection(story, "Anual (mês vs mesmo mês no ano anterior)",
            "Comparação anual mostra melhoria de 45% no fluxo operacional, reflexo da gestão de capital de giro.")
        
        self._add_subsection(story, "Análise de Sazonalidade",
            "Período de alta liquidez conforme padrão histórico, com geração de caixa 18% acima da média anual.")
        
        self._add_subsection(story, "✅ Diagnóstico",
            "Geração de caixa saudável impulsionada por: (1) crescimento de receitas com recebimento à vista, (2) melhoria de 8 dias no prazo médio de recebimento através de campanhas de antecipação, (3) negociação de prazo com fornecedores mantendo bons descontos. Recomenda-se aplicação do excedente de caixa em investimentos de curto prazo de baixo risco para maximizar rentabilidade sem comprometer liquidez.",
            highlight=True)
        
        story.append(PageBreak())
        
        # ===== 8. PARECER DA TAG =====
        self._add_section_title(story, "🎯 PARECER DA TAG")
        story.append(Paragraph("Análise SWOT, alertas e pontos de atenção considerando números do mês, fundamentos de negócios e segmento.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.3*cm))
        
        # SWOT
        story.append(Paragraph("<para fontSize=13 textColor=#101D43><b>📊 Análise SWOT</b></para>", self.styles['BodyText']))
        story.append(Spacer(1, 0.3*cm))
        
        swot_data = [
            [
                Paragraph("<para fontSize=11 textColor=white><b>💪 FORÇAS</b></para>", self.styles['BodyText']),
                Paragraph("<para fontSize=11 textColor=white><b>⚠️ FRAQUEZAS</b></para>", self.styles['BodyText'])
            ],
            [
                Paragraph("<para fontSize=9 textColor=#2c3e50 leading=12>Crescimento consistente de receitas (+15% MoM, +28% YoY), melhoria na eficiência operacional (despesas/receita de 30,4%), forte geração de caixa operacional (R$ 135k) e estrutura comercial consolidada com ROI positivo em marketing digital.</para>", self.styles['BodyText']),
                Paragraph("<para fontSize=9 textColor=#2c3e50 leading=12>Aumento da inadimplência (12% no período), dependência de fornecedores sujeitos à variação cambial, pressão nos custos operacionais (+8,2%) impactando margem bruta, e necessidade de modernização do controle patrimonial.</para>", self.styles['BodyText'])
            ],
            [
                Paragraph("<para fontSize=11 textColor=white><b>🌟 OPORTUNIDADES</b></para>", self.styles['BodyText']),
                Paragraph("<para fontSize=11 textColor=white><b>⚡ AMEAÇAS</b></para>", self.styles['BodyText'])
            ],
            [
                Paragraph("<para fontSize=9 textColor=#2c3e50 leading=12>Expansão para novos mercados regionais, implementação de produtos/serviços complementares (cross-selling), otimização tributária com créditos de PIS/COFINS (economia de 1,2%), e digitalização do processo de vendas para aumentar conversão.</para>", self.styles['BodyText']),
                Paragraph("<para fontSize=9 textColor=#2c3e50 leading=12>Volatilidade cambial impactando custos de insumos importados, concorrência agressiva em preços no segmento, possível recessão econômica afetando poder de compra dos clientes, e mudanças regulatórias no setor.</para>", self.styles['BodyText'])
            ]
        ]
        
        swot_table = Table(swot_data, colWidths=[8.5*cm, 8.5*cm], rowHeights=[0.8*cm, None, 0.8*cm, None])
        swot_table.setStyle(TableStyle([
            # Headers
            ('BACKGROUND', (0, 0), (0, 0), self.COLOR_SUCCESS),
            ('BACKGROUND', (1, 0), (1, 0), self.COLOR_DANGER),
            ('BACKGROUND', (0, 2), (0, 2), self.COLOR_INFO),
            ('BACKGROUND', (1, 2), (1, 2), self.COLOR_WARNING),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            # Content
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('BACKGROUND', (0, 3), (-1, 3), colors.white),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
            ('TOPPADDING', (0, 2), (-1, 2), 8),
            ('BOTTOMPADDING', (0, 2), (-1, 2), 8),
            ('TOPPADDING', (0, 3), (-1, 3), 10),
            ('BOTTOMPADDING', (0, 3), (-1, 3), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(swot_table)
        
        story.append(PageBreak())
        
        # PLANOS DE AÇÃO
        story.append(Paragraph("<para fontSize=13 textColor=#101D43><b>📋 Planos de Ação</b></para>", self.styles['BodyText']))
        story.append(Spacer(1, 0.3*cm))
        
        # Ação Urgente
        self._add_action_plan(story, "🚨 AÇÃO URGENTE: Gestão de Inadimplência",
            "<b>Situação:</b> Taxa de inadimplência aumentou 12% no mês, representando R$ 78.000 em valores a receber vencidos há mais de 30 dias.<br/><br/>"
            "<b>Impacto:</b> Afeta diretamente o fluxo de caixa e pode comprometer a capacidade de honrar compromissos de curto prazo.<br/><br/>"
            "<b>Ações Imediatas:</b><br/>"
            "• Implementar campanha de recuperação com condições especiais (7 dias)<br/>"
            "• Revisar política de crédito para novos clientes<br/>"
            "• Estabelecer cobrança preventiva com 3 dias de antecedência ao vencimento<br/>"
            "• Considerar desconto de até 5% para pagamento antecipado",
            self.COLOR_DANGER)
        
        # Ação Importante
        self._add_action_plan(story, "⚡ MONITORAMENTO CONTÍNUO: Gestão de Custos e Fornecedores",
            "<b>Situação:</b> Custos operacionais subiram 8,2%, com destaque para insumos importados (+12%) devido à variação cambial.<br/><br/>"
            "<b>Impacto:</b> Pressão na margem bruta, que reduziu de 52% para 48,7%.<br/><br/>"
            "<b>Ações de Monitoramento:</b><br/>"
            "• Renegociar contratos com 3 principais fornecedores (responsáveis por 65% dos custos)<br/>"
            "• Implementar hedge cambial para compras de insumos importados<br/>"
            "• Pesquisar fornecedores nacionais alternativos para itens críticos<br/>"
            "• Estabelecer indicador semanal de variação de custos vs orçado",
            self.COLOR_WARNING)
        
        # Ação de Observação
        self._add_action_plan(story, "👀 OBSERVAÇÃO: Otimização Tributária e Tecnologia",
            "<b>Situação:</b> Identificadas oportunidades de redução da carga tributária em 1,2% através de aproveitamento integral de créditos de PIS/COFINS.<br/><br/>"
            "<b>Potencial de Ganho:</b> Economia estimada de R$ 11.760/mês (R$ 141.120/ano).<br/><br/>"
            "<b>Ações de Médio Prazo:</b><br/>"
            "• Contratar consultoria especializada para auditoria tributária completa (60 dias)<br/>"
            "• Avaliar viabilidade de migração de regime tributário na próxima renovação<br/>"
            "• Implementar sistema ERP integrado para gestão patrimonial e controles fiscais<br/>"
            "• Automatizar processos de apuração de créditos tributários",
            self.COLOR_INFO)
        
        # Rodapé
        story.append(Spacer(1, 1*cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceBefore=5, spaceAfter=10))
        story.append(Paragraph('<para align=center fontSize=9 textColor=#636e72><b>Relatório Executivo Gerado Automaticamente</b></para>', self.styles['BodyText']))
        story.append(Paragraph(f'<para align=center fontSize=8 textColor=#636e72>Gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}</para>', self.styles['BodyText']))
        story.append(Paragraph('<para align=center fontSize=8 textColor=#636e72>Sistema de Classificação Financeira com IA</para>', self.styles['BodyText']))
        
        # Gera o PDF
        doc.build(story)
        print(f"✅ Relatório executivo gerado com sucesso!")
    
    def _add_section_title(self, story, title: str):
        """Adiciona título de seção com estilo destacado"""
        title_data = [[Paragraph(f"<para align=center fontSize=16 textColor=white><b>{title}</b></para>", self.styles['BodyText'])]]
        title_table = Table(title_data, colWidths=[17*cm])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLOR_PRIMARY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ]))
        story.append(title_table)
        story.append(Spacer(1, 0.5*cm))
    
    def _add_subsection(self, story, title: str, content: str, highlight: bool = False):
        """Adiciona subseção com título e conteúdo"""
        bg_color = self.COLOR_LIGHT_GOLD if highlight else colors.white
        
        subsection_data = [[
            Paragraph(f"<para fontSize=11 textColor=#101D43><b>{title}</b></para>", self.styles['BodyText']),
        ], [
            Paragraph(f"<para fontSize=10 textColor=#2c3e50 align=justify leading=13>{content}</para>", self.styles['BodyText'])
        ]]
        
        subsection_table = Table(subsection_data, colWidths=[17*cm])
        subsection_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 1), (-1, 1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
        ]))
        story.append(subsection_table)
        story.append(Spacer(1, 0.25*cm))
    
    def _add_action_plan(self, story, title: str, content: str, color):
        """Adiciona card de plano de ação"""
        action_data = [[
            Paragraph(f"<para fontSize=11 textColor=white><b>{title}</b></para>", self.styles['BodyText']),
        ], [
            Paragraph(f"<para fontSize=9 textColor=#2c3e50 leading=12>{content}</para>", self.styles['BodyText'])
        ]]
        
        action_table = Table(action_data, colWidths=[17*cm])
        action_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), color),
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 1), (-1, 1), 12),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 2, color),
        ]))
        story.append(action_table)
        story.append(Spacer(1, 0.3*cm))
