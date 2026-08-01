"""Aba de estatísticas consolidadas."""
from config import CORES, DISCIPLINAS


def criar_estatisticas(workbook):
    ws = workbook.add_worksheet("Estatísticas")
    ws.set_tab_color(CORES["destaque"]); ws.hide_gridlines(2); ws.set_column("A:A", 28); ws.set_column("B:F", 16)
    cab = workbook.add_format({"bold": True, "font_color": "FFFFFF", "bg_color": CORES["primaria"], "border": 1}); pct = workbook.add_format({"num_format": "0.0%"})
    ws.merge_range("A1:F1", "Estatísticas por disciplina", workbook.add_format({"bold": True, "font_size": 18, "font_color": "FFFFFF", "bg_color": CORES["primaria"]}))
    ws.write_row("A3", ["Disciplina", "Horas", "Questões", "Acertos", "% acerto", "Revisões"], cab)
    for r, (disciplina, _, _) in enumerate(DISCIPLINAS, 3):
        n = r + 1; ws.write(r, 0, disciplina)
        ws.write_formula(r, 1, f'=SUMIF(Planejamento!$D$2:$D$337,A{n},Planejamento!$H$2:$H$337)')
        ws.write_formula(r, 2, f'=SUMIF(\'Banco de Questões\'!$B$2:$B$1001,A{n},\'Banco de Questões\'!$G$2:$G$1001)')
        ws.write_formula(r, 3, f'=SUMIF(\'Banco de Questões\'!$B$2:$B$1001,A{n},\'Banco de Questões\'!$H$2:$H$1001)')
        ws.write_formula(r, 4, f'=IFERROR(D{n}/C{n},"")', pct)
        ws.write_formula(r, 5, f'=COUNTIF(\'Método 4 Grupos\'!$B$2:$B$301,A{n})')
    ultima_linha = 3 + len(DISCIPLINAS)
    ws.conditional_format(f"E4:E{ultima_linha}", {"type": "data_bar", "bar_color": CORES["destaque"]})
    chart = workbook.add_chart({"type": "bar"}); chart.add_series({"name": "Questões", "categories": f"=Estatísticas!$A$4:$A${ultima_linha}", "values": f"=Estatísticas!$C$4:$C${ultima_linha}", "fill": {"color": CORES["destaque"]}}); chart.set_title({"name": "Questões por disciplina"}); chart.set_legend({"none": True}); ws.insert_chart("H3", chart)
