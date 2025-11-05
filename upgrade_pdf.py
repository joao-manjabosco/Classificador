"""
Script para aplicar melhorias visuais no gerador de PDF
"""

# Lê o arquivo original
with open('src/utils/executive_pdf_generator_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Aplica as melhorias de cores
content = content.replace(
    "COLOR_LIGHT_BG = colors.HexColor('#faf8f3')",
    """COLOR_LIGHT_BG = colors.HexColor('#f8f9fa')
    COLOR_BORDER = colors.HexColor('#dee2e6')
    COLOR_TEXT_LIGHT = colors.HexColor('#6c757d')
    COLOR_SUCCESS_LIGHT = colors.HexColor('#d4edda')
    COLOR_DANGER_LIGHT = colors.HexColor('#f8d7da')
    COLOR_WARNING_LIGHT = colors.HexColor('#fff3cd')
    COLOR_INFO_LIGHT = colors.HexColor('#d1ecf1')
    COLOR_SECONDARY = colors.HexColor('#1a2d5a')"""
)

# Atualiza importações
content = content.replace(
    "from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY",
    "from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT"
)

# Melhora fontSize dos títulos
content = content.replace('fontSize=28', 'fontSize=36')
content = content.replace('fontSize=16>Análise Financeira Estratégica', 'fontSize=16 textColor=#D6BC71>Análise Financeira e Estratégica')

# Salva o arquivo atualizado
with open('src/utils/executive_pdf_generator_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Melhorias aplicadas com sucesso!")
