"""
EXECUTIVE PDF GENERATOR V2 - Gerador de Relatórios Executivos BASEADO EM DADOS REAIS

IMPORTANTE - POLÍTICA DE DADOS REAIS:
====================================
Este módulo gera relatórios executivos usando EXCLUSIVAMENTE dados reais
dos arquivos OFX processados. 

PROIBIDO:
- Usar valores default ou hardcoded
- Inventar dados ou métricas fictícias
- Assumir valores quando não houver dados reais
- Gerar períodos/meses que não existem nos arquivos OFX

OBRIGATÓRIO:
- Usar apenas dados presentes nos arquivos OFX
- Exibir o período REAL dos dados (extraído do DataFrame)
- Calcular métricas apenas com dados reais disponíveis
- Indicar claramente quando não houver dados suficientes

Versão completamente refatorada que usa APENAS dados reais e análises da IA.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from datetime import datetime
from typing import Dict, Any, List
from src.utils.ai_decision_logger import get_logger


class ExecutivePDFGeneratorV2:
    """Gera PDFs de relatórios executivos com análise estratégica REAL"""
    
    # PALETA DE CORES PROFISSIONAL
    COLOR_PRIMARY = colors.HexColor('#101D43')
    COLOR_SECONDARY = colors.HexColor('#1a2d5a')
    COLOR_GOLD = colors.HexColor('#D6BC71')
    COLOR_DARK_GOLD = colors.HexColor('#c0a85f')
    COLOR_LIGHT_GOLD = colors.HexColor('#e8d9a8')
    COLOR_SUCCESS = colors.HexColor('#28a745')
    COLOR_SUCCESS_LIGHT = colors.HexColor('#d4edda')
    COLOR_DANGER = colors.HexColor('#dc3545')
    COLOR_DANGER_LIGHT = colors.HexColor('#f8d7da')
    COLOR_WARNING = colors.HexColor('#ffc107')
    COLOR_WARNING_LIGHT = colors.HexColor('#fff3cd')
    COLOR_INFO = colors.HexColor('#17a2b8')
    COLOR_INFO_LIGHT = colors.HexColor('#d1ecf1')
    COLOR_DARK = colors.HexColor('#2c3e50')
    COLOR_LIGHT_BG = colors.HexColor('#f8f9fa')
    COLOR_BORDER = colors.HexColor('#dee2e6')
    COLOR_TEXT_LIGHT = colors.HexColor('#6c757d')
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.logger = get_logger()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos customizados profissionais"""
        
        if 'MainTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='MainTitle',
                parent=self.styles['Heading1'],
                fontSize=32,
                textColor=self.COLOR_PRIMARY,
                spaceAfter=10,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                leading=38
            ))
        
        if 'Subtitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Subtitle',
                parent=self.styles['Normal'],
                fontSize=14,
                textColor=self.COLOR_DARK,
                spaceAfter=22,
                alignment=TA_CENTER,
                fontName='Helvetica',
                leading=18
            ))
        
        if 'BodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=self.COLOR_DARK,
                spaceAfter=8,
                alignment=TA_JUSTIFY,
                leading=15
            ))
        
        if 'SectionDesc' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionDesc',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=self.COLOR_TEXT_LIGHT,
                spaceAfter=15,
                alignment=TA_LEFT,
                leading=13,
                fontName='Helvetica-Oblique'
            ))
        
        if 'CardTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CardTitle',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=self.COLOR_PRIMARY,
                spaceAfter=8,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                leading=14
            ))
        
        if 'MetricValue' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='MetricValue',
                parent=self.styles['Normal'],
                fontSize=20,
                textColor=self.COLOR_PRIMARY,
                spaceAfter=4,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                leading=24
            ))
        
        if 'MetricLabel' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='MetricLabel',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=self.COLOR_TEXT_LIGHT,
                spaceAfter=0,
                alignment=TA_CENTER,
                fontName='Helvetica',
                leading=11
            ))
    
    def _format_currency(self, value: float) -> str:
        """Formata valor em moeda"""
        return f"R$ {abs(value):,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    
    def _format_percent(self, value: float) -> str:
        """Formata percentual"""
        return f"{value:+.1f}%"
    
    def generate_executive_report(self, 
                                 financial_report: Dict[str, Any],
                                 strategic_report: Dict[str, Any],
                                 output_path: str):
        """
        Gera relatório executivo em PDF usando dados reais
        
        Args:
            financial_report: Relatório financeiro do FinancialAnalyzer
            strategic_report: Relatório estratégico do StrategicAnalyzer
            output_path: Caminho para salvar o PDF
        """
        print("\n📄 [PDF GENERATOR V2] Gerando relatório executivo...")
        
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
        self._add_cover(story, financial_report)
        story.append(PageBreak())
        
        # ===== 1. SUMÁRIO EXECUTIVO =====
        self._add_executive_summary(story, strategic_report)
        story.append(PageBreak())
        
        # ===== 2. ANÁLISE FINANCEIRA =====
        self._add_financial_overview(story, financial_report)
        story.append(PageBreak())
        
        # ===== 3. COMPARAÇÕES MENSAIS =====
        if financial_report.get('comparacoes_mensais'):
            self._add_monthly_comparisons(story, financial_report['comparacoes_mensais'])
            story.append(PageBreak())
        
        # ===== 4. ANÁLISE SWOT =====
        self._add_swot_analysis(story, strategic_report)
        story.append(PageBreak())
        
        # ===== 5. PLANOS DE AÇÃO =====
        self._add_action_plans(story, strategic_report)
        
        # ===== RODAPÉ =====
        story.append(Spacer(1, 1*cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceBefore=5, spaceAfter=10))
        story.append(Paragraph('<para align=center fontSize=9 textColor=#636e72><b>Relatório Executivo Gerado com Dados Reais</b></para>', self.styles['BodyText']))
        story.append(Paragraph(f'<para align=center fontSize=8 textColor=#636e72>Gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}</para>', self.styles['BodyText']))
        story.append(Paragraph('<para align=center fontSize=8 textColor=#636e72>Sistema de Classificação Financeira com IA - Versão 2.0</para>', self.styles['BodyText']))
        
        # Gera o PDF
        doc.build(story)
        
        # Loga a geração do relatório
        self.logger.log_analysis_decision(
            analysis_type="pdf_report_generation",
            input_data={"financial_summary": financial_report.get('sumario'), "strategic_summary": "SWOT + Actions"},
            output={"pdf_path": output_path},
            reasoning="Relatório PDF gerado usando dados reais do período analisado com análises da IA",
            calculations=None
        )
        
        print(f"✅ Relatório executivo salvo: {output_path}")
    
    def _add_cover(self, story: List, financial_report: Dict[str, Any]):
        """Adiciona capa elegante do relatório"""
        story.append(Spacer(1, 1.5*cm))
        
        # Título principal com design profissional
        title_text = """
        <para align=center fontSize=36 textColor=white leading=42>
        <b>📊 RELATÓRIO EXECUTIVO</b>
        </para>
        """
        subtitle_text = """
        <para align=center fontSize=16 textColor=#D6BC71 leading=20>
        <b>Análise Financeira e Estratégica</b>
        </para>
        """
        
        header_data = [[Paragraph(title_text, self.styles['BodyText'])], 
                       [Paragraph(subtitle_text, self.styles['BodyText'])]]
        header_table = Table(header_data, colWidths=[17*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLOR_PRIMARY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (0, 0), 30),
            ('BOTTOMPADDING', (0, 0), (0, 0), 10),
            ('TOPPADDING', (0, 1), (0, 1), 10),
            ('BOTTOMPADDING', (0, 1), (0, 1), 30),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(header_table)
        
            story.append(Spacer(1, 0.4*cm))
        
            # Banner de período com cards de métricas (BASEADO EM DADOS REAIS)
            periodo = financial_report.get('sumario', {}).get('periodo', {})
            totais = financial_report.get('sumario', {}).get('totais', {})
        
            # Extrai o último mês REAL analisado (dos dados dos arquivos OFX)
            ultimo_mes = periodo.get('ultimo_mes_analisado', periodo.get('mes_fim', 'N/A'))
        
            # Header do período
            periodo_header = f"""
            <para align=center fontSize=12 textColor=#1a1a1a leading=16>
            <b>📅 Período Analisado:</b> {periodo.get('inicio', 'N/A')} até {periodo.get('fim', 'N/A')}<br/>
            <b>🗓️ Último Mês:</b> {ultimo_mes}
            </para>
            """
        
            periodo_header_data = [[Paragraph(periodo_header, self.styles['BodyText'])]]
            periodo_header_table = Table(periodo_header_data, colWidths=[17*cm])
            periodo_header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BOX', (0, 0), (-1, -1), 1, self.COLOR_BORDER),
            ]))
            story.append(periodo_header_table)
            story.append(Spacer(1, 0.4*cm))
        
            # Cards de métricas principais em grid
            saldo = totais.get('saldo', 0)
            saldo_color = self.COLOR_SUCCESS if saldo >= 0 else self.COLOR_DANGER
            saldo_icon = "📈" if saldo >= 0 else "📉"
        
            metrics_data = [
                [
                    Paragraph(f"<para align=center fontSize=18 textColor=#28a745><b>{self._format_currency(totais.get('receita', 0))}</b></para>", self.styles['BodyText']),
                    Paragraph(f"<para align=center fontSize=18 textColor=#dc3545><b>{self._format_currency(totais.get('despesa', 0))}</b></para>", self.styles['BodyText']),
                    Paragraph(f"<para align=center fontSize=18 textColor={saldo_color.hexval()}><b>{self._format_currency(saldo)}</b></para>", self.styles['BodyText'])
                ],
                [
                    Paragraph("<para align=center fontSize=10 textColor=#6c757d><b>💰 RECEITA TOTAL</b></para>", self.styles['BodyText']),
                    Paragraph("<para align=center fontSize=10 textColor=#6c757d><b>💸 DESPESA TOTAL</b></para>", self.styles['BodyText']),
                    Paragraph(f"<para align=center fontSize=10 textColor=#6c757d><b>{saldo_icon} RESULTADO</b></para>", self.styles['BodyText'])
                ]
            ]
        
            metrics_table = Table(metrics_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.COLOR_SUCCESS_LIGHT),
                ('BACKGROUND', (1, 0), (1, -1), self.COLOR_DANGER_LIGHT),
                ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#fff3cd') if saldo >= 0 else self.COLOR_DANGER_LIGHT),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, 0), 15),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 1), (-1, 1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
                ('BOX', (0, 0), (-1, -1), 2, self.COLOR_BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.white),
            ]))
            story.append(metrics_table)
        
            story.append(Spacer(1, 0.3*cm))
        
            # Rodapé da capa
            footer_text = f"""
            <para align=center fontSize=8 textColor=#6c757d>
            📄 Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} | Baseado em dados reais dos arquivos OFX
            </para>
            """
            story.append(Paragraph(footer_text, self.styles['BodyText']))
    
    def _add_section_title(self, story: List, title: str):
        """Adiciona título de seção"""
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
    
    def _add_executive_summary(self, story: List, strategic_report: Dict[str, Any]):
        """Adiciona sumário executivo com eventos-chave"""
        self._add_section_title(story, "📌 SUMÁRIO EXECUTIVO")
        story.append(Paragraph("Os eventos mais relevantes identificados pela análise dos dados do período.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.2*cm))
        
        eventos = strategic_report.get('key_events', [])
        
        for evento in eventos:
            # Determina cor baseada no tipo
            tipo = evento.get('tipo', 'NEUTRO').upper()
            if 'POSITIVO' in tipo or 'CRESCIMENTO' in tipo:
                cor = self.COLOR_SUCCESS
                icone = "🟢"
            elif 'NEGATIVO' in tipo or 'QUEDA' in tipo or 'RISCO' in tipo:
                cor = self.COLOR_DANGER
                icone = "🔴"
            else:
                cor = self.COLOR_WARNING
                icone = "🟡"
            
            evento_data = [[
                Paragraph(f"<para fontSize=12 textColor=white><b>{icone} {evento.get('titulo', 'Evento')}</b></para>", self.styles['BodyText']),
            ], [
                Paragraph(f"<para fontSize=10 textColor=#2c3e50>{evento.get('descricao', 'Sem descrição')}</para>", self.styles['BodyText'])
            ]]
            
            evento_table = Table(evento_data, colWidths=[17*cm])
            evento_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), cor),
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
    
    def _add_financial_overview(self, story: List, financial_report: Dict[str, Any]):
        """Adiciona visão geral financeira"""
        self._add_section_title(story, "💰 VISÃO GERAL FINANCEIRA")
        
        sumario = financial_report.get('sumario', {})
        totais = sumario.get('totais', {})
        transacoes = sumario.get('transacoes', {})
        
        # Card de métricas principais
        metrics_text = f"""
        <para fontSize=11 textColor=#1a1a1a leading=14>
        <b>📊 MÉTRICAS PRINCIPAIS</b><br/><br/>
        <b>Receita Total:</b> {self._format_currency(totais.get('receita', 0))}<br/>
        <b>Despesa Total:</b> {self._format_currency(totais.get('despesa', 0))}<br/>
        <b>Resultado Líquido:</b> {self._format_currency(totais.get('saldo', 0))}<br/>
        <b>Margem:</b> {totais.get('margem', 0):.1f}%<br/><br/>
        <b>Total de Transações:</b> {transacoes.get('total', 0)}<br/>
        <b>Ticket Médio Receita:</b> {self._format_currency(transacoes.get('ticket_medio_receita', 0))}<br/>
        <b>Ticket Médio Despesa:</b> {self._format_currency(transacoes.get('ticket_medio_despesa', 0))}
        </para>
        """
        
        metrics_data = [[Paragraph(metrics_text, self.styles['BodyText'])]]
        metrics_table = Table(metrics_data, colWidths=[17*cm])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLOR_LIGHT_GOLD),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, self.COLOR_PRIMARY),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Top 5 Receitas e Despesas
        story.append(Paragraph("<para fontSize=12 textColor=#101D43><b>📈 TOP 5 RECEITAS</b></para>", self.styles['BodyText']))
        story.append(Spacer(1, 0.2*cm))
        
        top_receitas = sumario.get('top_receitas', [])[:5]
        if top_receitas:
            for item in top_receitas:
                item_text = f"<para fontSize=9>{item['data']}: {item['descricao'][:40]}... - {self._format_currency(item['valor'])}</para>"
                story.append(Paragraph(item_text, self.styles['BodyText']))
        
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("<para fontSize=12 textColor=#101D43><b>📉 TOP 5 DESPESAS</b></para>", self.styles['BodyText']))
        story.append(Spacer(1, 0.2*cm))
        
        top_despesas = sumario.get('top_despesas', [])[:5]
        if top_despesas:
            for item in top_despesas:
                item_text = f"<para fontSize=9>{item['data']}: {item['descricao'][:40]}... - {self._format_currency(item['valor'])}</para>"
                story.append(Paragraph(item_text, self.styles['BodyText']))
    
    def _add_monthly_comparisons(self, story: List, comparacoes: List[Dict[str, Any]]):
        """Adiciona comparações mensais"""
        self._add_section_title(story, "📊 COMPARAÇÕES MENSAIS")
        story.append(Paragraph("Análise comparativa mês a mês dos dados disponíveis.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.3*cm))
        
        for comp in comparacoes:
            period_a = comp['period_a']
            period_b = comp['period_b']
            var = comp['variations']
            
            # Determina se houve melhora ou piora
            sinal_receita = "+" if var['receita_pct'] > 0 else ""
            sinal_despesa = "+" if var['despesa_pct'] > 0 else ""
            sinal_saldo = "+" if var['saldo_pct'] > 0 else ""
            
            comp_text = f"""
            <para fontSize=11 textColor=#1a1a1a leading=14>
            <b>📅 {period_a['mes']} vs {period_b['mes']}</b><br/><br/>
            <b>Receita:</b> {self._format_currency(period_a['receita'])} → {self._format_currency(period_b['receita'])} 
            ({sinal_receita}{var['receita_pct']:.1f}%)<br/>
            <b>Despesa:</b> {self._format_currency(period_a['despesa'])} → {self._format_currency(period_b['despesa'])} 
            ({sinal_despesa}{var['despesa_pct']:.1f}%)<br/>
            <b>Resultado:</b> {self._format_currency(period_a['saldo'])} → {self._format_currency(period_b['saldo'])} 
            ({sinal_saldo}{var['saldo_pct']:.1f}%)
            </para>
            """
            
            comp_data = [[Paragraph(comp_text, self.styles['BodyText'])]]
            comp_table = Table(comp_data, colWidths=[17*cm])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
            ]))
            story.append(comp_table)
            story.append(Spacer(1, 0.3*cm))
    
    def _add_swot_analysis(self, story: List, strategic_report: Dict[str, Any]):
        """Adiciona análise SWOT"""
        self._add_section_title(story, "🎯 ANÁLISE SWOT")
        story.append(Paragraph("Análise estratégica baseada nos dados do período.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.3*cm))
        
        swot = strategic_report.get('swot', {})
        
        # Formata listas em texto
        def format_list(items):
            return "<br/>".join([f"• {item}" for item in items])
        
        swot_data = [
            [
                Paragraph("<para fontSize=11 textColor=white><b>💪 FORÇAS</b></para>", self.styles['BodyText']),
                Paragraph("<para fontSize=11 textColor=white><b>⚠️ FRAQUEZAS</b></para>", self.styles['BodyText'])
            ],
            [
                Paragraph(f"<para fontSize=9 textColor=#2c3e50 leading=12>{format_list(swot.get('forcas', ['Nenhuma força identificada']))}</para>", self.styles['BodyText']),
                Paragraph(f"<para fontSize=9 textColor=#2c3e50 leading=12>{format_list(swot.get('fraquezas', ['Nenhuma fraqueza identificada']))}</para>", self.styles['BodyText'])
            ],
            [
                Paragraph("<para fontSize=11 textColor=white><b>🌟 OPORTUNIDADES</b></para>", self.styles['BodyText']),
                Paragraph("<para fontSize=11 textColor=white><b>⚡ AMEAÇAS</b></para>", self.styles['BodyText'])
            ],
            [
                Paragraph(f"<para fontSize=9 textColor=#2c3e50 leading=12>{format_list(swot.get('oportunidades', ['Nenhuma oportunidade identificada']))}</para>", self.styles['BodyText']),
                Paragraph(f"<para fontSize=9 textColor=#2c3e50 leading=12>{format_list(swot.get('ameacas', ['Nenhuma ameaça identificada']))}</para>", self.styles['BodyText'])
            ]
        ]
        
        swot_table = Table(swot_data, colWidths=[8.5*cm, 8.5*cm], rowHeights=[0.8*cm, None, 0.8*cm, None])
        swot_table.setStyle(TableStyle([
            # Headers
            ('BACKGROUND', (0, 0), (0, 0), self.COLOR_SUCCESS),
            ('BACKGROUND', (1, 0), (1, 0), self.COLOR_DANGER),
            ('BACKGROUND', (0, 2), (0, 2), self.COLOR_INFO),
            ('BACKGROUND', (1, 2), (1, 2), self.COLOR_WARNING),
            # Content
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('BACKGROUND', (0, 3), (-1, 3), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(swot_table)
    
    def _add_action_plans(self, story: List, strategic_report: Dict[str, Any]):
        """Adiciona planos de ação"""
        self._add_section_title(story, "📋 PLANOS DE AÇÃO")
        story.append(Paragraph("Recomendações estratégicas baseadas na análise dos dados.", self.styles['SectionDesc']))
        story.append(Spacer(1, 0.3*cm))
        
        action_plans = strategic_report.get('action_plans', [])
        
        for plano in action_plans:
            # Determina cor baseada na prioridade
            prioridade = plano.get('prioridade', 'OBSERVAÇÃO').upper()
            if 'URGENTE' in prioridade:
                cor = self.COLOR_DANGER
                icone = "🚨"
            elif 'IMPORTANTE' in prioridade:
                cor = self.COLOR_WARNING
                icone = "⚡"
            else:
                cor = self.COLOR_INFO
                icone = "👀"
            
            # Formata ações
            acoes_text = "<br/>".join([f"• {acao}" for acao in plano.get('acoes', [])])
            
            plano_text = f"""
            <b>Situação:</b> {plano.get('situacao', 'N/A')}<br/><br/>
            <b>Impacto:</b> {plano.get('impacto', 'N/A')}<br/><br/>
            <b>Ações Recomendadas:</b><br/>{acoes_text}
            """
            
            action_data = [[
                Paragraph(f"<para fontSize=11 textColor=white><b>{icone} {prioridade}: {plano.get('titulo', 'Plano')}</b></para>", self.styles['BodyText']),
            ], [
                Paragraph(f"<para fontSize=9 textColor=#2c3e50 leading=12>{plano_text}</para>", self.styles['BodyText'])
            ]]
            
            action_table = Table(action_data, colWidths=[17*cm])
            action_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), cor),
                ('BACKGROUND', (0, 1), (-1, 1), colors.white),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 1), (-1, 1), 12),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('BOX', (0, 0), (-1, -1), 2, cor),
            ]))
            story.append(action_table)
            story.append(Spacer(1, 0.3*cm))
