"""Persistência local do aplicativo SOE-BlackLion."""
import sqlite3
import json
from contextlib import contextmanager
from datetime import date
import re

from config import BANCO_DADOS, CONCURSO_PADRAO, DATA_DIR, DISCIPLINAS, TOPICOS_EDITAL


@contextmanager
def conectar():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(BANCO_DADOS)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def inicializar():
    with conectar() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS concursos (
                id INTEGER PRIMARY KEY, nome TEXT NOT NULL UNIQUE, descricao TEXT DEFAULT '', criado_em TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS topicos (
                id INTEGER PRIMARY KEY, disciplina TEXT NOT NULL, assunto TEXT NOT NULL,
                prioridade TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Não iniciado',
                dominio INTEGER NOT NULL DEFAULT 0, observacoes TEXT DEFAULT '', concurso_id INTEGER NOT NULL,
                UNIQUE(concurso_id, disciplina, assunto)
            );
            CREATE TABLE IF NOT EXISTS revisoes (
                id INTEGER PRIMARY KEY, topico_id INTEGER NOT NULL, grupo TEXT NOT NULL,
                data_estudo TEXT, percentual REAL, questoes INTEGER, tempo_min INTEGER,
                status TEXT NOT NULL DEFAULT 'Pendente', proxima_revisao TEXT, observacoes TEXT DEFAULT '',
                UNIQUE(topico_id, grupo), FOREIGN KEY(topico_id) REFERENCES topicos(id)
            );
            CREATE TABLE IF NOT EXISTS questoes (
                id INTEGER PRIMARY KEY, data TEXT NOT NULL, disciplina TEXT NOT NULL, assunto TEXT,
                fonte TEXT, banca TEXT DEFAULT 'CEBRASPE', ano INTEGER, quantidade INTEGER NOT NULL,
                acertos INTEGER NOT NULL, erros INTEGER NOT NULL, brancos INTEGER NOT NULL DEFAULT 0, tempo_min INTEGER
            );
            CREATE TABLE IF NOT EXISTS sessoes (
                id INTEGER PRIMARY KEY, data TEXT NOT NULL, disciplina TEXT NOT NULL, atividade TEXT,
                grupo TEXT, tempo_min INTEGER NOT NULL, questoes INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'Concluído', observacoes TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS estudos (
                id INTEGER PRIMARY KEY, topico_id INTEGER NOT NULL, ordem INTEGER NOT NULL,
                total_questoes INTEGER NOT NULL, data TEXT NOT NULL, UNIQUE(topico_id),
                FOREIGN KEY(topico_id) REFERENCES topicos(id)
            );
            CREATE TABLE IF NOT EXISTS grupos_executados (
                id INTEGER PRIMARY KEY, estudo_id INTEGER NOT NULL, grupo TEXT NOT NULL,
                data TEXT NOT NULL, acertos INTEGER NOT NULL DEFAULT 0, erros INTEGER NOT NULL DEFAULT 0,
                brancos INTEGER NOT NULL DEFAULT 0, tempo_min INTEGER NOT NULL DEFAULT 0,
                observacoes TEXT DEFAULT '', UNIQUE(estudo_id, grupo),
                FOREIGN KEY(estudo_id) REFERENCES estudos(id)
            );
            CREATE TABLE IF NOT EXISTS provas_analisadas (
                id INTEGER PRIMARY KEY, concurso_id INTEGER NOT NULL, nome TEXT NOT NULL,
                total_questoes INTEGER NOT NULL, texto TEXT NOT NULL, criado_em TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ocorrencias_prova (
                id INTEGER PRIMARY KEY, prova_id INTEGER NOT NULL, topico_id INTEGER NOT NULL,
                ocorrencias INTEGER NOT NULL DEFAULT 0, percentual REAL NOT NULL DEFAULT 0,
                UNIQUE(prova_id, topico_id), FOREIGN KEY(prova_id) REFERENCES provas_analisadas(id),
                FOREIGN KEY(topico_id) REFERENCES topicos(id)
            );
            CREATE TABLE IF NOT EXISTS planejamentos_semanais (
                id INTEGER PRIMARY KEY, concurso_id INTEGER NOT NULL, semana TEXT NOT NULL,
                layout_json TEXT NOT NULL, copias_json TEXT NOT NULL DEFAULT '{}', atualizado_em TEXT NOT NULL,
                UNIQUE(concurso_id, semana)
            );
        """)
        concurso = conn.execute("SELECT id FROM concursos WHERE nome=?", (CONCURSO_PADRAO,)).fetchone()
        if not concurso:
            conn.execute("INSERT INTO concursos (nome, descricao, criado_em) VALUES (?, ?, ?)", (CONCURSO_PADRAO, "Edital 2024 — Área: Tecnologia da Informação", str(date.today())))
            concurso = conn.execute("SELECT id FROM concursos WHERE nome=?", (CONCURSO_PADRAO,)).fetchone()
        concurso_padrao_id = concurso[0]
        schema_topicos = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='topicos'").fetchone()[0]
        if "UNIQUE(disciplina, assunto)" in schema_topicos:
            # O esquema anterior impedia que dois concursos tivessem, por
            # exemplo, o mesmo tópico "Português". Reconstrói a tabela sem
            # tocar nos IDs ou nos registros já criados pelo usuário.
            conn.execute("ALTER TABLE topicos RENAME TO topicos_legado")
            conn.execute("""CREATE TABLE topicos (
                id INTEGER PRIMARY KEY, disciplina TEXT NOT NULL, assunto TEXT NOT NULL,
                prioridade TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Não iniciado',
                dominio INTEGER NOT NULL DEFAULT 0, observacoes TEXT DEFAULT '', concurso_id INTEGER NOT NULL,
                UNIQUE(concurso_id, disciplina, assunto))""")
            legado_cols = {row[1] for row in conn.execute("PRAGMA table_info(topicos_legado)")}
            origem_concurso = "COALESCE(concurso_id, ?)" if "concurso_id" in legado_cols else "?"
            conn.execute(f"""INSERT INTO topicos (id, disciplina, assunto, prioridade, status, dominio, observacoes, concurso_id)
                             SELECT id, disciplina, assunto, prioridade, status, dominio, observacoes, {origem_concurso}
                             FROM topicos_legado""", (concurso_padrao_id,))
            conn.execute("DROP TABLE topicos_legado")
        # Migra a base anterior (de concurso único) sem apagar registros.
        for tabela in ("topicos", "sessoes", "questoes"):
            colunas = {row[1] for row in conn.execute(f"PRAGMA table_info({tabela})")}
            if "concurso_id" not in colunas:
                conn.execute(f"ALTER TABLE {tabela} ADD COLUMN concurso_id INTEGER")
                conn.execute(f"UPDATE {tabela} SET concurso_id=? WHERE concurso_id IS NULL", (concurso_padrao_id,))
        colunas_sessoes = {row[1] for row in conn.execute("PRAGMA table_info(sessoes)")}
        if "grupo" not in colunas_sessoes:
            conn.execute("ALTER TABLE sessoes ADD COLUMN grupo TEXT")
        if "topico_id" not in colunas_sessoes:
            conn.execute("ALTER TABLE sessoes ADD COLUMN topico_id INTEGER")
        # Migração da versão inicial: Português deixou de ser fracionado em
        # tópicos, pois o estudo será feito por provas completas. Só remove a
        # antiga carga automática se o usuário ainda não registrou uma aula.
        antigos_portugues = conn.execute("""SELECT t.id FROM topicos t
                                            LEFT JOIN estudos e ON e.topico_id=t.id
                                            WHERE t.disciplina='Língua Portuguesa'
                                            GROUP BY t.id HAVING COUNT(e.id)=0""").fetchall()
        total_portugues = conn.execute("SELECT COUNT(*) FROM topicos WHERE disciplina='Língua Portuguesa'").fetchone()[0]
        if total_portugues > 1 and len(antigos_portugues) == total_portugues:
            ids = [row[0] for row in antigos_portugues]
            marcadores = ",".join("?" for _ in ids)
            conn.execute(f"DELETE FROM revisoes WHERE topico_id IN ({marcadores})", ids)
            conn.execute(f"DELETE FROM topicos WHERE id IN ({marcadores})", ids)
        prioridades = {nome: prioridade for nome, prioridade, _ in DISCIPLINAS}
        for disciplina, assunto in TOPICOS_EDITAL:
            conn.execute("INSERT OR IGNORE INTO topicos (disciplina, assunto, prioridade, concurso_id) VALUES (?, ?, ?, ?)", (disciplina, assunto, prioridades[disciplina], concurso_padrao_id))


def consulta(sql, parametros=()):
    with conectar() as conn:
        return [dict(row) for row in conn.execute(sql, parametros).fetchall()]


def executar(sql, parametros=()):
    with conectar() as conn:
        conn.execute(sql, parametros)


def registrar_sessao(concurso_id, data, disciplina, topico_id, atividade, grupo, tempo_min, questoes, observacoes):
    executar("""INSERT INTO sessoes (data, disciplina, topico_id, atividade, grupo, tempo_min, questoes, observacoes, concurso_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
             (str(data), disciplina, topico_id, atividade, grupo, tempo_min, questoes, observacoes, concurso_id))


def registrar_questoes(concurso_id, data, disciplina, assunto, fonte, ano, quantidade, acertos, erros, brancos, tempo_min):
    executar("""INSERT INTO questoes (data, disciplina, assunto, fonte, ano, quantidade, acertos, erros, brancos, tempo_min, concurso_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
             (str(data), disciplina, assunto, fonte, ano or None, quantidade, acertos, erros, brancos, tempo_min, concurso_id))


def atualizar_revisao(revisao_id, percentual, questoes, tempo_min, status, proxima_revisao, observacoes):
    executar("""UPDATE revisoes SET data_estudo=?, percentual=?, questoes=?, tempo_min=?, status=?, proxima_revisao=?, observacoes=? WHERE id=?""", (str(date.today()) if status == "Concluído" else None, percentual, questoes, tempo_min, status, str(proxima_revisao) if proxima_revisao else None, observacoes, revisao_id))


def registrar_aula(topico_id, total_questoes, data_estudo):
    """Insere uma unidade na sequência da sua disciplina.

    A sequência, e não uma data de revisão, é a base do Método dos 4 Grupos.
    """
    with conectar() as conn:
        disciplina = conn.execute("SELECT disciplina FROM topicos WHERE id=?", (topico_id,)).fetchone()[0]
        ordem = conn.execute("""SELECT COALESCE(MAX(e.ordem), 0) + 1 FROM estudos e
                               JOIN topicos t ON t.id=e.topico_id WHERE t.disciplina=?""", (disciplina,)).fetchone()[0]
        conn.execute("INSERT INTO estudos (topico_id, ordem, total_questoes, data) VALUES (?, ?, ?, ?)", (topico_id, ordem, total_questoes, str(data_estudo)))


def executar_grupo(estudo_id, grupo, acertos, erros, brancos, tempo_min, observacoes):
    executar("""INSERT INTO grupos_executados (estudo_id, grupo, data, acertos, erros, brancos, tempo_min, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(estudo_id, grupo) DO UPDATE SET data=excluded.data, acertos=excluded.acertos,
                erros=excluded.erros, brancos=excluded.brancos, tempo_min=excluded.tempo_min, observacoes=excluded.observacoes""",
             (estudo_id, grupo, str(date.today()), acertos, erros, brancos, tempo_min, observacoes))


def criar_concurso(nome, descricao=""):
    with conectar() as conn:
        conn.execute("INSERT INTO concursos (nome, descricao, criado_em) VALUES (?, ?, ?)", (nome.strip(), descricao.strip(), str(date.today())))


def reiniciar_concurso(concurso_id):
    """Remove somente registros de uso e preserva o edital/tópicos do concurso."""
    with conectar() as conn:
        ids = [r[0] for r in conn.execute("SELECT id FROM estudos WHERE topico_id IN (SELECT id FROM topicos WHERE concurso_id=?)", (concurso_id,))]
        if ids:
            marcadores = ",".join("?" for _ in ids)
            conn.execute(f"DELETE FROM grupos_executados WHERE estudo_id IN ({marcadores})", ids)
            conn.execute(f"DELETE FROM estudos WHERE id IN ({marcadores})", ids)
        conn.execute("DELETE FROM sessoes WHERE concurso_id=?", (concurso_id,))
        conn.execute("DELETE FROM questoes WHERE concurso_id=?", (concurso_id,))
        conn.execute("UPDATE topicos SET status='Não iniciado', dominio=0, observacoes='' WHERE concurso_id=?", (concurso_id,))


def excluir_concurso(concurso_id):
    """Remove o concurso e todos os seus dados associados."""
    with conectar() as conn:
        topicos = [r[0] for r in conn.execute("SELECT id FROM topicos WHERE concurso_id=?", (concurso_id,))]
        if topicos:
            marcadores_topicos = ",".join("?" for _ in topicos)
            estudos = [r[0] for r in conn.execute(f"SELECT id FROM estudos WHERE topico_id IN ({marcadores_topicos})", topicos)]
            if estudos:
                marcadores_estudos = ",".join("?" for _ in estudos)
                conn.execute(f"DELETE FROM grupos_executados WHERE estudo_id IN ({marcadores_estudos})", estudos)
                conn.execute(f"DELETE FROM estudos WHERE id IN ({marcadores_estudos})", estudos)
            conn.execute(f"DELETE FROM revisoes WHERE topico_id IN ({marcadores_topicos})", topicos)
            conn.execute(f"DELETE FROM topicos WHERE id IN ({marcadores_topicos})", topicos)
        conn.execute("DELETE FROM sessoes WHERE concurso_id=?", (concurso_id,))
        conn.execute("DELETE FROM questoes WHERE concurso_id=?", (concurso_id,))
        provas = [r[0] for r in conn.execute("SELECT id FROM provas_analisadas WHERE concurso_id=?", (concurso_id,))]
        if provas:
            marcadores_provas = ",".join("?" for _ in provas)
            conn.execute(f"DELETE FROM ocorrencias_prova WHERE prova_id IN ({marcadores_provas})", provas)
        conn.execute("DELETE FROM provas_analisadas WHERE concurso_id=?", (concurso_id,))
        conn.execute("DELETE FROM planejamentos_semanais WHERE concurso_id=?", (concurso_id,))
        conn.execute("DELETE FROM concursos WHERE id=?", (concurso_id,))


def excluir_topico(topico_id, concurso_id):
    """Exclui um tópico somente se ele pertencer ao concurso informado."""
    with conectar() as conn:
        estudo = conn.execute("SELECT id FROM estudos WHERE topico_id=?", (topico_id,)).fetchone()
        if estudo:
            conn.execute("DELETE FROM grupos_executados WHERE estudo_id=?", (estudo[0],))
            conn.execute("DELETE FROM estudos WHERE id=?", (estudo[0],))
        conn.execute("DELETE FROM revisoes WHERE topico_id=?", (topico_id,))
        conn.execute("DELETE FROM ocorrencias_prova WHERE topico_id=?", (topico_id,))
        conn.execute("DELETE FROM topicos WHERE id=? AND concurso_id=?", (topico_id, concurso_id))


def excluir_registros_historico(concurso_id, registros):
    """Remove sessões, listas de questões ou grupos, sempre dentro do concurso."""
    comandos = {
        "Sessão": "DELETE FROM sessoes WHERE id=? AND concurso_id=?",
        "Questões": "DELETE FROM questoes WHERE id=? AND concurso_id=?",
        "Revisão": """DELETE FROM grupos_executados WHERE id=? AND estudo_id IN
                      (SELECT e.id FROM estudos e JOIN topicos t ON t.id=e.topico_id WHERE t.concurso_id=?)""",
    }
    with conectar() as conn:
        for tipo, registro_id in registros:
            comando = comandos.get(tipo)
            if comando:
                conn.execute(comando, (int(registro_id), concurso_id))


def atualizar_sessao_historico(concurso_id, registro_id, data_registro, disciplina, topico_id, atividade, grupo, tempo_min, questoes, observacoes):
    executar("""UPDATE sessoes SET data=?, disciplina=?, topico_id=?, atividade=?, grupo=?, tempo_min=?, questoes=?, observacoes=?
               WHERE id=? AND concurso_id=?""",
             (str(data_registro), disciplina, topico_id, atividade, grupo, tempo_min, questoes, observacoes, registro_id, concurso_id))


def atualizar_questoes_historico(concurso_id, registro_id, data_registro, disciplina, assunto, fonte, ano, quantidade, acertos, erros, brancos, tempo_min):
    executar("""UPDATE questoes SET data=?, disciplina=?, assunto=?, fonte=?, ano=?, quantidade=?, acertos=?, erros=?, brancos=?, tempo_min=?
               WHERE id=? AND concurso_id=?""",
             (str(data_registro), disciplina, assunto, fonte, ano, quantidade, acertos, erros, brancos, tempo_min, registro_id, concurso_id))


def atualizar_grupo_historico(concurso_id, registro_id, data_registro, grupo, acertos, erros, brancos, tempo_min, observacoes):
    with conectar() as conn:
        conn.execute("""UPDATE grupos_executados SET data=?, grupo=?, acertos=?, erros=?, brancos=?, tempo_min=?, observacoes=?
                        WHERE id=? AND estudo_id IN
                        (SELECT e.id FROM estudos e JOIN topicos t ON t.id=e.topico_id WHERE t.concurso_id=?)""",
                     (str(data_registro), grupo, acertos, erros, brancos, tempo_min, observacoes, registro_id, concurso_id))


def salvar_analise_prova(concurso_id, nome, texto, total_questoes, ocorrencias):
    """Persiste uma prova e sua distribuição de incidência por tópico."""
    with conectar() as conn:
        cursor = conn.execute(
            "INSERT INTO provas_analisadas (concurso_id, nome, total_questoes, texto, criado_em) VALUES (?, ?, ?, ?, ?)",
            (concurso_id, nome.strip() or "Prova sem título", total_questoes, texto, str(date.today())),
        )
        prova_id = cursor.lastrowid
        conn.executemany(
            "INSERT INTO ocorrencias_prova (prova_id, topico_id, ocorrencias, percentual) VALUES (?, ?, ?, ?)",
            [(prova_id, item["topico_id"], item["ocorrencias"], item["percentual"]) for item in ocorrencias],
        )
        return prova_id


def carregar_planejamento_semana(concurso_id, semana):
    with conectar() as conn:
        registro = conn.execute("SELECT layout_json, copias_json FROM planejamentos_semanais WHERE concurso_id=? AND semana=?", (concurso_id, str(semana))).fetchone()
        if not registro:
            return None
        try:
            return {"layout": json.loads(registro["layout_json"]), "copias": json.loads(registro["copias_json"])}
        except (TypeError, json.JSONDecodeError):
            return None


def salvar_planejamento_semana(concurso_id, semana, layout, copias):
    with conectar() as conn:
        conn.execute("""INSERT INTO planejamentos_semanais (concurso_id, semana, layout_json, copias_json, atualizado_em)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(concurso_id, semana) DO UPDATE SET layout_json=excluded.layout_json,
                        copias_json=excluded.copias_json, atualizado_em=excluded.atualizado_em""",
                     (concurso_id, str(semana), json.dumps(layout, ensure_ascii=False), json.dumps(copias, ensure_ascii=False), str(date.today())))


def importar_topicos(concurso_id, itens):
    """Itens são pares (disciplina, assunto), aprovados manualmente no app."""
    with conectar() as conn:
        for disciplina, assunto in itens:
            if disciplina.strip() and assunto.strip():
                conn.execute("INSERT OR IGNORE INTO topicos (disciplina, assunto, prioridade, concurso_id) VALUES (?, ?, 'Média', ?)", (disciplina.strip(), assunto.strip(), concurso_id))


def sugerir_topicos_texto(texto):
    """Sugere pares disciplina/tópico a partir do texto colado do edital.

    Reconhece títulos em caixa alta terminados por ':' e a numeração hierárquica
    usual de editais (1, 1.1, 1.1.1...). A revisão no app continua obrigatória.
    """
    texto = re.sub(r"[\t\r]+", " ", texto).strip()
    # Cabeçalhos precisam começar uma linha (ou o texto), o que evita tratar
    # expressões como "Poderes Administrativos:" dentro de um tópico como nova
    # disciplina. Aceita caixa alta ou título normal, ex.: "Direito Administrativo:".
    cabecalhos = list(re.finditer(r"(?m)^\s*([A-Za-zÁÀÃÂáàãâÉÊéêÍíÓÔÕóôõÚúÇç][A-Za-zÁÀÃÂáàãâÉÊéêÍíÓÔÕóôõÚúÇç\s]{2,80}):", texto))
    blocos = []
    if not cabecalhos:
        blocos = [("Conteúdo do edital", texto)]
    else:
        for i, cabecalho in enumerate(cabecalhos):
            inicio = cabecalho.end(); fim = cabecalhos[i + 1].start() if i + 1 < len(cabecalhos) else len(texto)
            blocos.append((cabecalho.group(1).strip(), texto[inicio:fim]))
    resultado, vistos = [], set()
    # Somente a numeração de primeiro nível abre uma nova unidade. Os
    # subitens (1.1, 1.1.1...) ficam no mesmo tópico da entrada "1".
    # Em editais, o nível principal costuma vir como "1. Assunto". O ponto
    # precisa não ser seguido de dígito para não confundir "8.666"; no máximo
    # dois dígitos também impede que anos como 1993 entrem na lista.
    padrao_principal = re.compile(r"(?<![\d.])(\d{1,2})\.(?!\d)\s+")
    for disciplina, bloco in blocos:
        encontrados = list(padrao_principal.finditer(bloco))
        if not encontrados and bloco.strip():
            encontrados = [None]
        for indice, encontrado in enumerate(encontrados):
            if encontrado:
                numero = encontrado.group(1)
                fim = encontrados[indice + 1].start() if indice + 1 < len(encontrados) else len(bloco)
                assunto = bloco[encontrado.end():fim]
            else:
                numero, assunto = "", bloco
            assunto = re.sub(r"\s+", " ", assunto).strip(" .;:-")
            if len(assunto) < 3:
                continue
            item = f"{numero} {assunto}".strip()
            chave = (disciplina.lower(), item.lower())
            if chave not in vistos:
                vistos.add(chave); resultado.append({"Importar": True, "Disciplina": disciplina, "Assunto": item})
    return resultado[:400]
