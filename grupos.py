"""Aba para execução do Método dos 4 Grupos."""
from config import CORES, DISCIPLINAS, GRUPOS, TOPICOS_EDITAL


def criar_grupos(workbook):
    ws = workbook.add_worksheet("Método 4 Grupos")
    headers = ["Data", "Disciplina", "Objeto estudado", "Grupo", "Percentual", "Questões", "Tempo (h)", "Status", "Próxima revisão", "Observações"]
    cab = workbook.add_format({"bold": True, "font_color": "FFFFFF", "bg_color": CORES["primaria"], "border": 1})
    ws.set_tab_color(CORES["destaque"]); ws.set_column("A:A", 14); ws.set_column("B:B", 26); ws.set_column("C:C", 38); ws.set_column("D:D", 14); ws.set_column("E:G", 15); ws.set_column("H:I", 18); ws.set_column("J:J", 38)
    ws.write_row("A1", headers, cab)
    date = workbook.add_format({"num_format": "dd/mm/yyyy"}); pct = workbook.add_format({"num_format": "0.0%"})
    total_linhas = max(500, len(TOPICOS_EDITAL) * 4)
    for r in range(1, total_linhas + 1):
        ws.write_blank(r, 0, None, date); ws.write_blank(r, 4, None, pct); ws.write_blank(r, 8, None, date)
    # Uma linha para cada etapa A, B, C e D de cada tópico: a revisão é por
    # assunto, não apenas pela disciplina inteira.
    linha = 1
    for disciplina, assunto in TOPICOS_EDITAL:
        for grupo in ("A", "B", "C", "D"):
            ws.write(linha, 1, disciplina); ws.write(linha, 2, assunto); ws.write(linha, 3, grupo)
            ws.write(linha, 7, "Pendente")
            linha += 1
    ws.add_table(0, 0, total_linhas, 9, {"name": "tb_grupos", "columns": [{"header": h} for h in headers], "style": "Table Style Medium 2"})
    ws.data_validation(1, 1, total_linhas, 1, {"validate": "list", "source": [x[0] for x in DISCIPLINAS]})
    ws.data_validation(1, 3, total_linhas, 3, {"validate": "list", "source": GRUPOS})
    ws.data_validation(1, 7, total_linhas, 7, {"validate": "list", "source": ["Pendente", "Concluído", "Revisar"]})
    ws.conditional_format(f"E2:E{total_linhas + 1}", {"type": "data_bar", "bar_color": CORES["destaque"]})
    ws.freeze_panes(1, 0)
