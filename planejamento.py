"""Abas de planejamento, cronograma diário e fila inteligente."""
from datetime import date, timedelta
from config import CORES, SEMANAS, HORAS_DIA, DISCIPLINAS


def _cabecalho(workbook):
    return workbook.add_format({"bold": True, "font_color": "FFFFFF", "bg_color": CORES["primaria"], "border": 1, "align": "center"})


def criar_planejamento(workbook):
    ws = workbook.add_worksheet("Planejamento")
    ws.set_tab_color(CORES["destaque"])
    headers = ["Data", "Semana", "Dia", "Disciplina", "Atividade", "Grupo", "Tempo planejado (h)", "Tempo realizado (h)", "Status", "Questões planejadas", "Questões realizadas", "Observações"]
    ws.set_column("A:A", 13); ws.set_column("B:C", 11); ws.set_column("D:D", 27); ws.set_column("E:E", 30); ws.set_column("F:F", 12); ws.set_column("G:H", 20); ws.set_column("I:I", 15); ws.set_column("J:K", 21); ws.set_column("L:L", 36)
    ws.write_row("A1", headers, _cabecalho(workbook))
    inicio = date.today()
    date_fmt = workbook.add_format({"num_format": "dd/mm/yyyy"})
    disciplina_por_dia = [x[0] for x in DISCIPLINAS]
    atividade = {nome: objeto for nome, _, objeto in DISCIPLINAS}
    for i in range(SEMANAS * 7):
        row = i + 1; dia = inicio + timedelta(days=i); disc = disciplina_por_dia[i % 7]
        ws.write_datetime(row, 0, dia, date_fmt); ws.write_number(row, 1, i // 7 + 1); ws.write(row, 2, dia.strftime("%A").capitalize())
        ws.write(row, 3, disc); ws.write(row, 4, atividade[disc]); ws.write(row, 5, "A" if i < len(disciplina_por_dia) * 2 else "Revisão")
        ws.write_formula(row, 6, "=Configurações!$B$2"); ws.write_blank(row, 7, None); ws.write(row, 8, "Planejado"); ws.write_formula(row, 9, "=ROUND(Configurações!$B$5/7,0)"); ws.write_blank(row, 10, None); ws.write_blank(row, 11, None)
    ws.add_table(0, 0, SEMANAS * 7, len(headers) - 1, {"name": "tb_planejamento", "columns": [{"header": h} for h in headers], "style": "Table Style Medium 2"})
    ws.data_validation(1, 8, SEMANAS * 7, 8, {"validate": "list", "source": ["Planejado", "Em andamento", "Concluído", "Adiado"]})
    ws.conditional_format(1, 8, SEMANAS * 7, 8, {"type": "text", "criteria": "containing", "value": "Concluído", "format": workbook.add_format({"bg_color": CORES["sucesso"]})})
    ws.freeze_panes(1, 0)


def criar_cronograma(workbook):
    ws = workbook.add_worksheet("Cronograma Diário")
    ws.set_tab_color(CORES["secundaria"])
    cab = _cabecalho(workbook); title = workbook.add_format({"bold": True, "font_size": 18, "font_color": "FFFFFF", "bg_color": CORES["primaria"]})
    ws.set_column("A:A", 18); ws.set_column("B:B", 28); ws.set_column("C:C", 32); ws.set_column("D:E", 18); ws.set_column("F:F", 22)
    ws.merge_range("A1:F1", "Cronograma Diário", title)
    ws.write("A3", "Data selecionada", cab); ws.write_formula("B3", "=TODAY()", workbook.add_format({"num_format": "dd/mm/yyyy"}))
    ws.write_row("A5", ["Horário", "Disciplina", "Atividade", "Grupo", "Duração", "Questões"], cab)
    for row in range(5, 10):
        r = row + 1
        ws.write_formula(row, 0, f'=IFERROR(TEXT(INDEX(Planejamento!$A$2:$A$337,MATCH($B$3,Planejamento!$A$2:$A$337,0)),"ddd dd/mm"),"")')
        if row == 5:
            ws.write_formula(row, 1, '=IFERROR(INDEX(Planejamento!$D$2:$D$337,MATCH($B$3,Planejamento!$A$2:$A$337,0)),"")')
            ws.write_formula(row, 2, '=IFERROR(INDEX(Planejamento!$E$2:$E$337,MATCH($B$3,Planejamento!$A$2:$A$337,0)),"")')
            ws.write_formula(row, 3, '=IFERROR(INDEX(Planejamento!$F$2:$F$337,MATCH($B$3,Planejamento!$A$2:$A$337,0)),"")')
            ws.write_formula(row, 4, '=IFERROR(INDEX(Planejamento!$G$2:$G$337,MATCH($B$3,Planejamento!$A$2:$A$337,0)),"")')
            ws.write_formula(row, 5, '=IFERROR(INDEX(Planejamento!$J$2:$J$337,MATCH($B$3,Planejamento!$A$2:$A$337,0)),"")')
    ws.data_validation("B3", {"validate": "date", "criteria": "between", "minimum": date.today(), "maximum": date.today() + timedelta(days=SEMANAS * 7 - 1)})


def criar_fila_inteligente(workbook):
    ws = workbook.add_worksheet("Fila Inteligente")
    ws.set_tab_color(CORES["alerta"])
    cab = _cabecalho(workbook); ws.set_column("A:A", 10); ws.set_column("B:B", 28); ws.set_column("C:D", 20); ws.set_column("E:E", 20); ws.set_column("F:F", 42)
    ws.merge_range("A1:F1", "Fila Inteligente de Revisões", workbook.add_format({"bold": True, "font_size": 18, "font_color": "FFFFFF", "bg_color": CORES["primaria"]}))
    ws.write("A2", "Ordene por prioridade e data de próxima revisão. Itens vencidos devem ser estudados primeiro.", workbook.add_format({"italic": True, "font_color": "666666"}))
    ws.write_row("A4", ["Prioridade", "Disciplina", "Assunto / Objeto", "Grupo", "Tempo sugerido", "Motivo"], cab)
    for row in range(4, 24):
        n = row + 1
        ws.write_formula(row, 0, f'=IF(B{n}="","",ROW()-4)')
        ws.write_formula(row, 1, f'=IFERROR(INDEX(\'Banco Mestre\'!$B$2:$B$501,MATCH(SMALL(\'Banco Mestre\'!$I$2:$I$501,ROW()-4),\'Banco Mestre\'!$I$2:$I$501,0)),"")')
        ws.write_formula(row, 2, f'=IFERROR(INDEX(\'Banco Mestre\'!$C$2:$C$501,MATCH(SMALL(\'Banco Mestre\'!$I$2:$I$501,ROW()-4),\'Banco Mestre\'!$I$2:$I$501,0)),"")')
        ws.write_formula(row, 3, f'=IFERROR(INDEX(\'Banco Mestre\'!$F$2:$F$501,MATCH(SMALL(\'Banco Mestre\'!$I$2:$I$501,ROW()-4),\'Banco Mestre\'!$I$2:$I$501,0)),"")')
        ws.write(row, 4, "30 min")
        ws.write_formula(row, 5, f'=IF(B{n}="","",IF(TODAY()>INDEX(\'Banco Mestre\'!$I$2:$I$501,MATCH(SMALL(\'Banco Mestre\'!$I$2:$I$501,ROW()-4),\'Banco Mestre\'!$I$2:$I$501,0)),"Revisão vencida","Próxima revisão"))')
    ws.freeze_panes(4, 0)
