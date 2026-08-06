"""Leitura local e classificação simples de provas pelo edital.

O algoritmo é deliberadamente explicável: ele compara palavras-chave dos
tópicos com o texto de cada questão. Não envia arquivos nem conteúdo a APIs.
"""
import re
import unicodedata


PALAVRAS_IGNORADAS = {
    "a", "as", "ao", "aos", "com", "como", "da", "das", "de", "do", "dos",
    "e", "em", "entre", "na", "nas", "no", "nos", "o", "os", "ou", "para",
    "por", "que", "se", "sem", "sob", "sobre", "um", "uma", "sua", "suas",
    "seu", "seus", "ser", "sao", "tambem", "mais", "menos", "processo",
    "sistemas", "sistema", "dados", "geral", "gerais", "conceito", "conceitos",
    "aspectos", "normas", "norma", "aplicacoes", "aplicacao", "tecnologia",
}

# Siglas muito frequentes em editais de TI continuam relevantes apesar de terem
# menos de quatro caracteres.
SIGLAS_RELEVANTES = {"ai", "bi", "ci", "dl", "dns", "etl", "git", "iam", "ids",
                     "ips", "lai", "ldap", "lgpd", "llm", "mlops", "nfs", "pki",
                     "saml", "sdn", "siem", "smb", "sql", "ssl", "tls", "tdd", "ux",
                     "ui", "wan", "lan"}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return texto.lower()


def palavras_chave(assunto):
    palavras = re.findall(r"[a-z0-9]+", normalizar(assunto))
    return {
        palavra for palavra in palavras
        if (len(palavra) >= 4 or palavra in SIGLAS_RELEVANTES)
        and palavra not in PALAVRAS_IGNORADAS
        and not palavra.isdigit()
    }


def separar_questoes(texto):
    """Separa enunciados numerados; caso não detecte, trata o arquivo como um bloco."""
    texto = re.sub(r"\r", "\n", texto or "")
    padrao = re.compile(r"(?im)(?:^|\n)\s*(?:quest[aã]o\s*)?(\d{1,3})\s*(?:[.º°)]|[-–])\s*")
    ocorrencias = list(padrao.finditer(texto))
    if not ocorrencias:
        return [texto.strip()] if texto.strip() else []
    questoes = []
    for indice, ocorrencia in enumerate(ocorrencias):
        fim = ocorrencias[indice + 1].start() if indice + 1 < len(ocorrencias) else len(texto)
        enunciado = texto[ocorrencia.end():fim].strip()
        if len(enunciado) >= 12:
            questoes.append(enunciado)
    return questoes or [texto.strip()]


def analisar_prova(texto, topicos):
    """Retorna a quantidade de questões associada a cada tópico.

    Um tópico é associado quando a questão contém uma palavra-chave específica
    do assunto. Para assuntos com várias palavras-chave, dois termos aumentam a
    confiança, mas uma sigla/termo técnico já é suficiente.
    """
    questoes = separar_questoes(texto)
    resultado = []
    for topico in topicos:
        assunto = topico["assunto"]
        disciplina = topico.get("disciplina", "")
        chaves = palavras_chave(assunto)
        ocorrencias = 0
        for questao in questoes:
            palavras = set(re.findall(r"[a-z0-9]+", normalizar(questao)))
            coincidencias = chaves & palavras
            # Português é cadastrado como uma prova completa no modelo atual.
            portuguesa_completa = "portugues" in normalizar(disciplina) and "prova" in normalizar(assunto)
            termo_tecnico = any(chave in SIGLAS_RELEVANTES or len(chave) >= 7 for chave in coincidencias)
            if portuguesa_completa or termo_tecnico or len(coincidencias) >= 2:
                ocorrencias += 1
        total = len(questoes)
        percentual = round((ocorrencias / total * 100), 1) if total else 0.0
        resultado.append({
            "topico_id": topico["id"], "disciplina": disciplina, "assunto": assunto,
            "ocorrencias": ocorrencias, "percentual": percentual,
            "relevancia": "Alta" if percentual >= 15 else "Média" if percentual >= 5 else "Baixa",
        })
    return resultado, len(questoes)
