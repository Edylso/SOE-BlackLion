"""Abas Banco de Questões e Caderno de Erros."""
from config import CORES, DISCIPLINAS


def _cab(workbook): return workbook.add_format({"bold": True, "font_color": "FFFFFF", "bg_color": CORES["primaria"], "border": 1})


def criar_questoes(workbook):
    ws = workbook.add_worksheet("Banco de Questões")
    headers = ["Data", "Disciplina", "Assunto", "Fonte", "Banca", "Ano", "Quantidade", "Acertos", "Erros", "Brancos", "Tempo (min)", "Nota líquida Cebraspe", "Percentual"]
    ws.set_tab_color(CORES["secundaria"]); ws.set_column("A:A", 13); ws.set_column("B:B", 26); ws.set_column("C:D", 30); ws.set_column("E:F", 13); ws.set_column("G:M", 18)
    ws.write_row("A1", headers, _cab(workbook))
    date = workbook.add_format({"num_format": "dd/mm/yyyy"}); pct = workbook.add_format({"num_format": "0.0%"})
    for r in range(1, 1001):
        n = r + 1; ws.write_blank(r, 0, None, date)
        ws.write_formula(r, 11, f'=IF(G{n}="","",H{n}-I{n})')
        ws.write_formula(r, 12, f'=IFERROR(H{n}/G{n},"")', pct)
    ws.add_table(0, 0, 1000, 12, {"name": "tb_questoes", "columns": [{"header": h} for h in headers], "style": "Table Style Medium 2"})
    ws.data_validation(1, 1, 1000, 1, {"validate": "list", "source": [x[0] for x in DISCIPLINAS]})
    ws.data_validation(1, 4, 1000, 4, {"validate": "list", "source": ["CEBRASPE", "FGV", "CESGRANRIO", "Outra"]})
    ws.freeze_panes(1, 0)

    erros = workbook.add_worksheet("Caderno de Erros")
    h = ["Data", "Disciplina", "Assunto", "Erro", "Correção", "Resumo / gatilho", "Última revisão", "Domínio (0-5)", "Observações"]
    erros.set_tab_color(CORES["alerta"]); erros.set_column("A:A", 13); erros.set_column("B:B", 26); erros.set_column("C:C", 30); erros.set_column("D:F", 42); erros.set_column("G:H", 16); erros.set_column("I:I", 36)
    erros.write_row("A1", h, _cab(workbook))
    for r in range(1, 501): erros.write_blank(r, 0, None, date); erros.write_blank(r, 6, None, date)
    erros.add_table(0, 0, 500, 8, {"name": "tb_erros", "columns": [{"header": x} for x in h], "style": "Table Style Medium 2"})
    erros.data_validation(1, 1, 500, 1, {"validate": "list", "source": [x[0] for x in DISCIPLINAS]})
    erros.data_validation(1, 7, 500, 7, {"validate": "integer", "criteria": "between", "minimum": 0, "maximum": 5})
    erros.freeze_panes(1, 0)
