"""Exportação opcional da estrutura original para Excel.

Execute `python3 gerar_excel.py` quando precisar recriar o arquivo .xlsx.
"""
import xlsxwriter

from banco_mestre import criar_banco_mestre
from config import ARQUIVO_SAIDA, CORES, CONCURSO, DIAS_SEMANA, DISCIPLINAS, HORAS_DIA, META_QUESTOES_MENSAL, META_QUESTOES_SEMANAL, OUTPUT_DIR, SEMANAS
from dashboard import criar_dashboard
from estatisticas import criar_estatisticas
from grupos import criar_grupos
from planejamento import criar_cronograma, criar_fila_inteligente, criar_planejamento
from questoes import criar_questoes
from simulados import criar_simulados


def criar_configuracoes(workbook):
    ws = workbook.add_worksheet("Configurações")
    ws.set_tab_color(CORES["cinza"]); ws.set_column("A:A", 30); ws.set_column("B:B", 45)
    titulo = workbook.add_format({"bold": True, "font_size": 18, "font_color": "FFFFFF", "bg_color": CORES["primaria"]})
    cab = workbook.add_format({"bold": True, "font_color": "FFFFFF", "bg_color": CORES["destaque"]})
    ws.merge_range("A1:B1", "Configurações do plano", titulo)
    valores = [("Concurso", CONCURSO), ("Horas por dia", HORAS_DIA), ("Dias por semana", DIAS_SEMANA), ("Semanas do plano", SEMANAS), ("Meta semanal de questões", META_QUESTOES_SEMANAL), ("Meta mensal de questões", META_QUESTOES_MENSAL), ("Banca", "CEBRASPE")]
    ws.write_row("A3", ["Parâmetro", "Valor"], cab)
    for r, item in enumerate(valores, 3): ws.write_row(r, 0, item)
    ws.write_row("A12", ["Disciplina", "Prioridade / objeto"], cab)
    for r, (disciplina, prioridade, objeto) in enumerate(DISCIPLINAS, 12): ws.write_row(r, 0, [disciplina, f"{prioridade} — {objeto}"])


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    workbook = xlsxwriter.Workbook(ARQUIVO_SAIDA)
    criar_configuracoes(workbook); criar_dashboard(workbook); criar_banco_mestre(workbook); criar_planejamento(workbook)
    criar_cronograma(workbook); criar_fila_inteligente(workbook); criar_grupos(workbook); criar_questoes(workbook)
    criar_simulados(workbook); criar_estatisticas(workbook)
    workbook.close()
    print(f"Concluído: {ARQUIVO_SAIDA}")


if __name__ == "__main__": main()
