"""Aba Dashboard."""
from config import CORES


def criar_dashboard(workbook):
    ws = workbook.add_worksheet("Dashboard")
    ws.hide_gridlines(2)
    ws.set_tab_color(CORES["primaria"])
    ws.set_column("A:A", 3)
    ws.set_column("B:G", 18)
    ws.set_column("H:N", 14)

    titulo = workbook.add_format({"bold": True, "font_size": 22, "font_color": "FFFFFF",
                                  "bg_color": CORES["primaria"], "align": "left", "valign": "vcenter"})
    subtitulo = workbook.add_format({"font_color": "D9EAF7", "bg_color": CORES["primaria"], "italic": True})
    rotulo = workbook.add_format({"bold": True, "font_color": "FFFFFF", "bg_color": CORES["destaque"],
                                  "align": "center", "valign": "vcenter"})
    valor = workbook.add_format({"bold": True, "font_size": 18, "font_color": CORES["texto"],
                                 "bg_color": "FFFFFF", "align": "center", "valign": "vcenter", "border": 1,
                                 "border_color": "D9E2F3"})
    secao = workbook.add_format({"bold": True, "font_color": "FFFFFF", "bg_color": CORES["primaria"]})
    percentual = workbook.add_format({"num_format": "0.0%", "align": "center"})

    ws.set_row(0, 32)
    ws.merge_range("B1:N1", "SOE-BlackLion | Sistema Operacional de Estudos", titulo)
    ws.merge_range("B2:N2", "Painel de acompanhamento diário — dados alimentados nas abas de registro.", subtitulo)

    indicadores = [
        ("Horas estudadas", "=SUM(Planejamento!$H$2:$H$337)"),
        ("Questões resolvidas", "=SUM('Banco de Questões'!$G$2:$G$1000)"),
        ("Acertos", "=SUM('Banco de Questões'!$H$2:$H$1000)"),
        ("Nota líquida Cebraspe", "=SUM('Banco de Questões'!$H$2:$H$1000)-SUM('Banco de Questões'!$I$2:$I$1000)"),
        ("Horas da semana", '=SUMIFS(Planejamento!$H$2:$H$337,Planejamento!$A$2:$A$337,">="&TODAY()-WEEKDAY(TODAY(),2)+1,Planejamento!$A$2:$A$337,"<="&TODAY())'),
        ("Meta semanal", "=Configurações!$B$6"),
        ("Meta mensal", "=Configurações!$B$7"),
        ("Progresso do plano", "=COUNTIF(Planejamento!$I$2:$I$337,\"Concluído\")/COUNTA(Planejamento!$A$2:$A$337)"),
    ]
    for i, (nome, formula) in enumerate(indicadores):
        col = 1 + (i % 4) * 3
        row = 4 + (i // 4) * 3
        ws.merge_range(row, col, row, col + 1, nome, rotulo)
        ws.merge_range(row + 1, col, row + 1, col + 1, formula, percentual if nome == "Progresso do plano" else valor)
        ws.set_row(row + 1, 30)

    ws.merge_range("B12:G12", "Progresso por disciplina", secao)
    ws.write_row("B13", ["Disciplina", "Horas", "Questões", "Acertos", "% acerto", "Revisões"], secao)
    for row in range(13, 24):
        excel_row = row + 1
        ws.write_formula(row, 1, f"=Estatísticas!A{excel_row}")
        ws.write_formula(row, 2, f"=Estatísticas!B{excel_row}")
        ws.write_formula(row, 3, f"=Estatísticas!C{excel_row}")
        ws.write_formula(row, 4, f"=Estatísticas!D{excel_row}")
        ws.write_formula(row, 5, f"=Estatísticas!E{excel_row}", percentual)
        ws.write_formula(row, 6, f"=Estatísticas!F{excel_row}")
    ws.conditional_format("G14:G24", {"type": "data_bar", "bar_color": CORES["destaque"]})

    chart = workbook.add_chart({"type": "column"})
    chart.add_series({"name": "Horas por disciplina", "categories": "=Dashboard!$B$14:$B$24", "values": "=Dashboard!$C$14:$C$24", "fill": {"color": CORES["destaque"]}})
    chart.set_title({"name": "Horas por disciplina"})
    chart.set_legend({"none": True})
    chart.set_style(10)
    ws.insert_chart("I12", chart, {"x_scale": 1.25, "y_scale": 1.1})
    ws.freeze_panes(3, 1)
