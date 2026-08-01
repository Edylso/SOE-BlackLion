"""Abas de simulados e discursivas."""
from config import CORES


def criar_simulados(workbook):
    ws = workbook.add_worksheet("Simulados")
    h = ["Data", "Nome / prova", "Tempo (min)", "Questões", "Acertos", "Erros", "Brancos", "Nota líquida", "Percentual", "Observações"]
    cab = workbook.add_format({"bold": True, "font_color": "FFFFFF", "bg_color": CORES["primaria"], "border": 1}); date = workbook.add_format({"num_format": "dd/mm/yyyy"}); pct = workbook.add_format({"num_format": "0.0%"})
    ws.set_tab_color(CORES["destaque"]); ws.set_column("A:A", 13); ws.set_column("B:B", 32); ws.set_column("C:I", 16); ws.set_column("J:J", 38); ws.write_row("A1", h, cab)
    for r in range(1, 101):
        n = r + 1; ws.write_blank(r, 0, None, date); ws.write_formula(r, 7, f'=IF(D{n}="","",E{n}-F{n})'); ws.write_formula(r, 8, f'=IFERROR(E{n}/D{n},"")', pct)
    ws.add_table(0, 0, 100, 9, {"name": "tb_simulados", "columns": [{"header": x} for x in h], "style": "Table Style Medium 2"})
    chart = workbook.add_chart({"type": "line"}); chart.add_series({"name": "Nota líquida", "categories": "=Simulados!$A$2:$A$101", "values": "=Simulados!$H$2:$H$101", "line": {"color": CORES["destaque"]}}); chart.set_title({"name": "Evolução nos simulados"}); chart.set_legend({"none": True}); ws.insert_chart("L2", chart)
    ws.freeze_panes(1, 0)

    d = workbook.add_worksheet("Discursivas")
    dh = ["Data", "Tema", "Nota", "Comentários", "Erros a corrigir", "Próxima ação"]
    d.set_tab_color(CORES["alerta"]); d.set_column("A:A", 13); d.set_column("B:B", 35); d.set_column("C:C", 12); d.set_column("D:F", 45); d.write_row("A1", dh, cab)
    for r in range(1, 101): d.write_blank(r, 0, None, date)
    d.add_table(0, 0, 100, 5, {"name": "tb_discursivas", "columns": [{"header": x} for x in dh], "style": "Table Style Medium 2"}); d.freeze_panes(1, 0)
