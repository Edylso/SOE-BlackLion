"""Aba Banco Mestre: cadastro central de tópicos do edital."""
from config import CORES, DISCIPLINAS, STATUS, GRUPOS, TOPICOS_EDITAL


def criar_banco_mestre(workbook):
    ws = workbook.add_worksheet("Banco Mestre")
    ws.set_tab_color(CORES["destaque"])
    headers = ["ID", "Disciplina", "Assunto", "Status", "Prioridade", "Grupo Atual", "Domínio (0-5)", "Última revisão", "Próxima revisão", "Observações"]
    cab = workbook.add_format({"bold": True, "font_color": "FFFFFF", "bg_color": CORES["primaria"], "border": 1})
    date = workbook.add_format({"num_format": "dd/mm/yyyy"})
    ws.set_column("A:A", 10); ws.set_column("B:B", 26); ws.set_column("C:C", 42)
    ws.set_column("D:F", 16); ws.set_column("G:G", 15); ws.set_column("H:I", 16); ws.set_column("J:J", 38)
    ws.write_row("A1", headers, cab)
    prioridades = {nome: prioridade for nome, prioridade, _ in DISCIPLINAS}
    for row in range(1, 501):
        ws.write_formula(row, 0, f'=IF(B{row+1}="","",ROW()-1)')
        ws.write_blank(row, 7, None, date); ws.write_blank(row, 8, None, date)
    for row, (disciplina, assunto) in enumerate(TOPICOS_EDITAL, 1):
        ws.write(row, 1, disciplina); ws.write(row, 2, assunto); ws.write(row, 3, "Não iniciado")
        ws.write(row, 4, prioridades[disciplina]); ws.write(row, 5, "A"); ws.write(row, 6, 0)
    ws.add_table(0, 0, 500, len(headers) - 1, {"name": "tb_banco_mestre", "columns": [{"header": h} for h in headers], "style": "Table Style Medium 2"})
    ws.data_validation(1, 1, 500, 1, {"validate": "list", "source": [d[0] for d in DISCIPLINAS]})
    ws.data_validation(1, 3, 500, 3, {"validate": "list", "source": STATUS})
    ws.data_validation(1, 4, 500, 4, {"validate": "list", "source": ["Alta", "Média", "Baixa"]})
    ws.data_validation(1, 5, 500, 5, {"validate": "list", "source": GRUPOS})
    ws.data_validation(1, 6, 500, 6, {"validate": "integer", "criteria": "between", "minimum": 0, "maximum": 5})
    ws.conditional_format("I2:I501", {"type": "formula", "criteria": '=AND(I2<>"",I2<TODAY())', "format": workbook.add_format({"bg_color": CORES["alerta"]})})
    ws.freeze_panes(1, 0)
