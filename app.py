"""Interface Streamlit do SOE-BlackLion."""
import os
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu

from config import DISCIPLINAS
from database import (consulta, criar_concurso, executar_grupo, excluir_concurso, excluir_topico, importar_topicos, sugerir_topicos_texto,
                      inicializar, registrar_aula, registrar_questoes, registrar_sessao, reiniciar_concurso)

st.set_page_config(page_title="SOE-BlackLion", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"], [data-testid="stApp"] { background: #dce3eb !important; }
    [data-testid="stMainBlockContainer"], .main .block-container { max-width: 1400px !important; padding-top: 1.5rem !important; }
    .stApp { background: #dce3eb; font-family: ui-rounded, 'Avenir Next', 'Segoe UI', sans-serif; }
    h1, h2, h3 { font-family: ui-rounded, 'Avenir Next', 'Segoe UI', sans-serif !important; color: #1f2937; }
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background: #123d61 !important; border-right: 1px solid #0f334f; min-width: 270px; }
    [data-testid="stSidebar"] * { color: #eef4f8; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div { background: #0f334f; border: 1px solid #2a587a; border-radius: 4px; }
    [data-testid="stSidebar"] input { background: #0f334f !important; border-radius: 4px !important; }
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div { background: #0f334f; border-radius: 4px; }
    [data-testid="stSidebar"] [role="radiogroup"] { gap: 7px; }
    [data-testid="stSidebar"] [role="radiogroup"] label { padding: 9px 12px; border-radius: 5px; transition: .15s; }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background: #1b4b70; }
    [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] { background: #f59e0b; color: #123d61 !important; font-weight: 700; }
    [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] * { color: #fff !important; }
    [data-testid="stMetric"] { background: #ffffff; border: 1px solid #d7dde4; border-radius: 3px; padding: 18px 20px; box-shadow: 0 8px 16px rgba(45, 58, 72, .22); }
    [data-testid="stColumn"]:has([data-testid="stMetric"]) { background: #ffffff; border: 1px solid #d7dde4; border-radius: 4px; padding: 5px 7px; box-shadow: 0 9px 18px rgba(45, 58, 72, .20); }
    [data-testid="stMetricLabel"] { color: #64748b; }
    [data-testid="stMetricValue"] { color: #123d61; }
    .home-title { padding: 8px 0 16px; }
    .home-title span { color: #d97706; font-size: .78rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
    .home-title h1 { color: #1f2937; font-size: 1.8rem; margin: 4px 0; }
    .home-title p { color: #64748b; margin: 0; }
    .stPlotlyChart { background: #fff; border: 1px solid #d7dde4; border-radius: 3px; padding: 6px; box-shadow: 0 8px 16px rgba(45, 58, 72, .20); }
    .sidebar-brand { padding: 15px 7px 21px; border-bottom: 1px solid #2a587a; margin-bottom: 14px; }
    .sidebar-brand .mark { display: inline-block; width: 38px; height: 38px; line-height: 38px; text-align: center; border-radius: 50%; background: #f59e0b; font-size: 20px; }
    .sidebar-brand h2 { display: inline; margin-left: 9px; color: white !important; font-size: 1.2rem; vertical-align: middle; }
    .sidebar-brand p { margin: 5px 0 0 48px; color: #d4c8ee; font-size: .73rem; }
    .stButton > button, [data-testid="stFormSubmitButton"] > button { border: 0; border-radius: 4px; background: #f59e0b; color: #123d61; font-weight: 800; box-shadow: 0 3px 7px rgba(126, 81, 8, .22); }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { border: 0; color: white; filter: brightness(1.07); }
    [data-testid="stExpander"] { border: 1px solid #d7dde4; border-radius: 3px; background: #fff; box-shadow: 0 8px 16px rgba(45,58,72,.18); }
    [data-testid="stDataFrame"], [data-testid="stForm"] { border-radius: 3px; box-shadow: 0 8px 16px rgba(45,58,72,.18); }
    .topbar { display: flex; align-items: center; justify-content: space-between; background: #fff; border: 1px solid #d7dde4; border-radius: 3px; padding: 11px 16px; margin: 0 0 18px; box-shadow: 0 7px 14px rgba(45,58,72,.16); }
    .topbar .crumb { color: #64748b; font-size: .86rem; }.topbar b { color: #123d61; }.topbar .user { color: #d97706; font-weight: 700; font-size: .86rem; }
    .nav-caption { color: #a9c0d3; font-size: .66rem; font-weight: 800; letter-spacing: .08em; margin: 20px 8px 6px; }
</style>
""", unsafe_allow_html=True)


def login():
    if st.session_state.get("autenticado"):
        return True
    st.title("📚 SOE-BlackLion")
    st.caption("Sistema Operacional de Estudos — Banco Central | Tecnologia da Informação")
    with st.form("login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)
    if entrar:
        usuario_valido = os.getenv("SOE_USUARIO", "admin")
        senha_valida = os.getenv("SOE_SENHA", "bacen2024")
        if usuario == usuario_valido and senha == senha_valida:
            st.session_state.autenticado = True
            st.rerun()
        st.error("Usuário ou senha inválidos.")
    st.info("Acesso inicial: usuário `admin` · senha `bacen2024`. Altere por meio das variáveis `SOE_USUARIO` e `SOE_SENHA` antes de publicar.")
    return False


def filtros(concurso_id):
    disciplinas = [r["disciplina"] for r in consulta("SELECT DISTINCT disciplina FROM topicos WHERE concurso_id=? ORDER BY disciplina", (concurso_id,))]
    with st.sidebar:
        st.header("Filtros")
        selecionadas = st.multiselect("Disciplinas", disciplinas, default=disciplinas)
        termo = st.text_input("Pesquisar assunto")
    return selecionadas, termo


def aplicar_filtros(df, disciplinas, termo):
    if df.empty:
        return df
    if "disciplina" in df:
        df = df[df["disciplina"].isin(disciplinas)]
    if termo and "assunto" in df:
        df = df[df["assunto"].fillna("").str.contains(termo, case=False, na=False)]
    return df


def _anel(valor, titulo, cor):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=valor, number={"suffix": "%", "font": {"size": 28, "color": "#123d61"}},
        title={"text": titulo, "font": {"size": 13, "color": "#64748b"}},
        gauge={"axis": {"range": [0, 100], "visible": False}, "bar": {"color": cor, "thickness": 0.22},
               "bgcolor": "#e5e7eb", "borderwidth": 0}))
    fig.update_layout(height=155, margin=dict(l=8, r=8, t=30, b=5), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", font_color="#1f2937")
    return fig


def _cartao_indicador(rotulo, valor):
    st.markdown(
        f"""<div style="background:#ffffff;border:1px solid #d7dde4;border-radius:4px;
        padding:18px 20px;min-height:104px;box-shadow:0 10px 20px rgba(45,58,72,.24);">
        <div style="font-size:13px;color:#64748b;margin-bottom:8px;">{rotulo}</div>
        <div style="font-size:30px;font-weight:700;color:#123d61;line-height:1.1;">{valor}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def dashboard(concurso_id, disciplinas, termo):
    st.markdown("""<div style="background:#ffffff;border:1px solid #d7dde4;border-radius:4px;
        padding:22px 24px;margin-bottom:18px;box-shadow:0 10px 20px rgba(45,58,72,.20);">
        <div style="color:#d97706;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;">Visão geral</div>
        <div style="color:#1f2937;font-size:30px;font-weight:800;margin:6px 0 12px;">Seu ritmo de estudos</div>
        <div style="color:#64748b;font-size:15px;">Acompanhe seu progresso no concurso ativo.</div>
        </div>""", unsafe_allow_html=True)
    topicos = pd.DataFrame(consulta("SELECT * FROM topicos WHERE concurso_id=?", (concurso_id,)))
    grupos_feitos = pd.DataFrame(consulta("""SELECT g.*, t.disciplina, t.assunto FROM grupos_executados g
                                            JOIN estudos e ON e.id=g.estudo_id JOIN topicos t ON t.id=e.topico_id WHERE t.concurso_id=?""", (concurso_id,)))
    sessoes = pd.DataFrame(consulta("SELECT * FROM sessoes WHERE concurso_id=?", (concurso_id,)))
    questoes = pd.DataFrame(consulta("SELECT * FROM questoes WHERE concurso_id=?", (concurso_id,)))
    topicos = aplicar_filtros(topicos, disciplinas, termo); grupos_feitos = aplicar_filtros(grupos_feitos, disciplinas, termo)
    sessoes = aplicar_filtros(sessoes, disciplinas, termo); questoes = aplicar_filtros(questoes, disciplinas, termo)
    total_horas = 0 if sessoes.empty else sessoes.tempo_min.sum() / 60
    total_q = 0 if questoes.empty else int(questoes.quantidade.sum())
    acertos = 0 if questoes.empty else int(questoes.acertos.sum())
    erros = 0 if questoes.empty else int(questoes.erros.sum())
    concluidas = len(grupos_feitos)
    aproveitamento = (acertos / total_q * 100) if total_q else 0
    estudos = pd.DataFrame(consulta("""SELECT e.id, t.disciplina, t.assunto FROM estudos e
                                      JOIN topicos t ON t.id=e.topico_id WHERE t.concurso_id=?""", (concurso_id,)))
    estudos = aplicar_filtros(estudos, disciplinas, termo)
    progresso_geral = (len(estudos) / len(topicos) * 100) if len(topicos) else 0
    c1, c2, c3, c4 = st.columns(4)
    with c1: _cartao_indicador("Horas estudadas", f"{total_horas:.1f} h")
    with c2: _cartao_indicador("Questões resolvidas", total_q)
    with c3: _cartao_indicador("Nota líquida Cebraspe", acertos - erros)
    with c4: _cartao_indicador("Grupos executados", concluidas)
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    if topicos.empty:
        st.warning("Nenhum tópico encontrado com os filtros atuais.")
        return
    progresso = topicos.groupby("disciplina", as_index=False).agg(topicos=("id", "count"), dominio=("dominio", "mean"))
    if not sessoes.empty:
        horas = sessoes.groupby("disciplina", as_index=False).tempo_min.sum(); horas["horas"] = horas.tempo_min / 60
        progresso = progresso.merge(horas[["disciplina", "horas"]], on="disciplina", how="left")
    else: progresso["horas"] = 0
    progresso["horas"] = progresso["horas"].fillna(0)
    a, b, c = st.columns(3)
    with a:
        with st.container(border=True): st.plotly_chart(_anel(progresso_geral, "PROGRESSO DO EDITAL", "#123d61"), use_container_width=True, config={"displayModeBar": False})
    with b:
        with st.container(border=True): st.plotly_chart(_anel(aproveitamento, "APROVEITAMENTO", "#f59e0b"), use_container_width=True, config={"displayModeBar": False})
    with c:
        with st.container(border=True): st.plotly_chart(_anel(min(concluidas / max(len(estudos) * 4, 1) * 100, 100), "CICLO 4 GRUPOS", "#457b9d"), use_container_width=True, config={"displayModeBar": False})
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    g1, g2 = st.columns((1.35, 1))
    with g1:
        fig = px.bar(progresso.sort_values("horas", ascending=True), x="horas", y="disciplina", orientation="h", color="horas", color_continuous_scale=["#c4d9e8", "#123d61"], title="Horas por disciplina")
        fig.update_layout(coloraxis_showscale=False, height=300, margin=dict(l=0, r=0, t=45, b=0), plot_bgcolor="#fff", paper_bgcolor="#fff", font_color="#475569")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with g2:
        if sessoes.empty:
            dias = pd.DataFrame({"dia": ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"], "horas": [0] * 7})
        else:
            copia = sessoes.copy(); copia["dia"] = pd.to_datetime(copia.data).dt.day_name().map({"Monday":"Seg", "Tuesday":"Ter", "Wednesday":"Qua", "Thursday":"Qui", "Friday":"Sex", "Saturday":"Sáb", "Sunday":"Dom"}); dias = copia.groupby("dia", as_index=False).tempo_min.sum(); dias["horas"] = dias.tempo_min / 60
        fig = px.area(dias, x="dia", y="horas", title="Ritmo semanal", color_discrete_sequence=["#f59e0b"])
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=45, b=0), plot_bgcolor="#fff", paper_bgcolor="#fff", font_color="#475569")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def quatro_grupos(concurso_id, disciplinas, termo):
    st.title("Método dos 4 Grupos")
    st.info("A fila é por sequência, não por data: ao concluir uma aula, ela usa o Grupo A; as três aulas anteriores da mesma disciplina entram nos Grupos B, C e D.")
    todos = pd.DataFrame(consulta("SELECT id, disciplina, assunto FROM topicos WHERE concurso_id=? ORDER BY disciplina, assunto", (concurso_id,)))
    feitos = pd.DataFrame(consulta("SELECT e.topico_id FROM estudos e JOIN topicos t ON t.id=e.topico_id WHERE t.concurso_id=?", (concurso_id,)))
    disponiveis = todos if feitos.empty else todos[~todos.id.isin(feitos.topico_id)]
    disponiveis = aplicar_filtros(disponiveis, disciplinas, termo)
    with st.expander("Concluir nova aula/unidade e gerar a fila", expanded=True):
        if disponiveis.empty:
            st.warning("Não há unidades disponíveis para os filtros atuais.")
        else:
            opcoes = {f"{r.disciplina} — {r.assunto}": r.id for r in disponiveis.itertuples()}
            with st.form("nova_aula"):
                chave = st.selectbox("Aula/unidade concluída", list(opcoes))
                total = st.number_input("Quantidade total de questões dessa aula", min_value=4, value=20, step=1)
                data_aula = st.date_input("Data de conclusão", value=date.today())
                if st.form_submit_button("Concluir aula e montar ciclo", type="primary"):
                    registrar_aula(opcoes[chave], total, data_aula)
                    st.success("Aula inserida na sequência. A fila A–D foi atualizada."); st.rerun()
    st.subheader("Fila atual por disciplina")
    estudos = pd.DataFrame(consulta("""SELECT e.id AS estudo_id, e.ordem, e.total_questoes, e.data, t.disciplina, t.assunto
                                      FROM estudos e JOIN topicos t ON t.id=e.topico_id WHERE t.concurso_id=? ORDER BY t.disciplina, e.ordem DESC""", (concurso_id,)))
    estudos = aplicar_filtros(estudos, disciplinas, termo)
    if estudos.empty:
        st.caption("Conclua a primeira aula/unidade para iniciar a esteira de questões.")
        return
    executados = pd.DataFrame(consulta("SELECT estudo_id, grupo, data, acertos, erros, brancos, tempo_min FROM grupos_executados"))
    fila = []
    for disciplina, grupo_df in estudos.groupby("disciplina", sort=True):
        for indice, linha in enumerate(grupo_df.head(4).itertuples()):
            grupo = "ABCD"[indice]
            numeros = list(range(indice + 1, linha.total_questoes + 1, 4))
            feito = False if executados.empty else ((executados.estudo_id == linha.estudo_id) & (executados.grupo == grupo)).any()
            fila.append({"estudo_id": linha.estudo_id, "disciplina": disciplina, "grupo": grupo, "assunto": linha.assunto,
                         "questoes": ", ".join(map(str, numeros)), "quantidade": len(numeros), "status": "Concluído" if feito else "Pendente"})
    fila = pd.DataFrame(fila)
    st.dataframe(fila[["disciplina", "grupo", "assunto", "quantidade", "questoes", "status"]], use_container_width=True, hide_index=True)
    with st.expander("Registrar execução de um grupo"):
        pendentes = fila[fila.status == "Pendente"]
        if pendentes.empty: st.success("Todos os grupos da fila atual foram executados.")
        else:
            opcoes = {f"{r.disciplina} | Grupo {r.grupo} | {r.assunto} ({r.quantidade} questões)": (r.estudo_id, r.grupo, r.quantidade) for r in pendentes.itertuples()}
            with st.form("executar_grupo"):
                chave = st.selectbox("Grupo executado", list(opcoes)); limite = opcoes[chave][2]
                acertos = st.number_input("Acertos", min_value=0, max_value=limite, value=0); erros = st.number_input("Erros", min_value=0, max_value=limite, value=0); brancos = st.number_input("Brancos", min_value=0, max_value=limite, value=0); tempo = st.number_input("Tempo (minutos)", min_value=0, step=5); obs = st.text_area("Observações")
                if st.form_submit_button("Registrar grupo", type="primary"):
                    if acertos + erros + brancos != limite: st.error(f"Informe o resultado das {limite} questões do grupo.")
                    else: executar_grupo(opcoes[chave][0], opcoes[chave][1], acertos, erros, brancos, tempo, obs); st.success("Grupo registrado."); st.rerun()


def registros(concurso_id, disciplinas):
    st.title("Registrar estudo")
    tab1, tab2 = st.tabs(["Sessão de estudo", "Banco de questões"])
    nomes = disciplinas
    if not nomes:
        st.info("Este concurso ainda não possui tópicos. Importe ou cadastre o edital em Concursos antes de registrar estudos.")
        return
    with tab1:
        with st.form("sessao"):
            data = st.date_input("Data", value=date.today()); disciplina = st.selectbox("Disciplina", nomes)
            atividade = st.text_input("Atividade", placeholder="Ex.: Anki, teoria, prova Cebraspe")
            grupo = st.selectbox("Grupo", ["Sem grupo / teoria", "Grupo A", "Grupo B", "Grupo C", "Grupo D"])
            tempo = st.number_input("Tempo (minutos)", min_value=1, value=60, step=5); q = st.number_input("Questões", min_value=0, step=1); obs = st.text_area("Observações")
            if st.form_submit_button("Registrar sessão", type="primary"):
                registrar_sessao(concurso_id, data, disciplina, atividade, grupo, tempo, q, obs); st.success("Sessão registrada.")
    with tab2:
        with st.form("questoes"):
            data = st.date_input("Data da lista", value=date.today(), key="qdata"); disciplina = st.selectbox("Disciplina", nomes, key="qdisc")
            assunto = st.text_input("Assunto"); fonte = st.text_input("Fonte"); ano = st.number_input("Ano", min_value=2000, max_value=2100, value=2024)
            quantidade = st.number_input("Quantidade", min_value=1, value=10); acertos = st.number_input("Acertos", min_value=0, value=0); erros = st.number_input("Erros", min_value=0, value=0); brancos = st.number_input("Brancos", min_value=0, value=0); tempo = st.number_input("Tempo (minutos)", min_value=0, value=0, step=5)
            if st.form_submit_button("Registrar questões", type="primary"):
                if acertos + erros + brancos > quantidade: st.error("Acertos, erros e brancos não podem superar a quantidade.")
                else: registrar_questoes(concurso_id, data, disciplina, assunto, fonte, ano, quantidade, acertos, erros, brancos, tempo); st.success("Questões registradas.")


def edital(concurso_id, disciplinas, termo):
    st.title("Edital e tópicos")
    df = pd.DataFrame(consulta("SELECT id, disciplina, assunto, prioridade, status, dominio, observacoes FROM topicos WHERE concurso_id=?", (concurso_id,)))
    df = aplicar_filtros(df, disciplinas, termo)
    st.caption(f"{len(df)} tópicos exibidos. O domínio é atualizado conforme sua autoavaliação.")
    if not df.empty:
        tabela = df.copy()
        tabela.insert(0, "Excluir", False)
        selecionados = st.data_editor(
            tabela, use_container_width=True, hide_index=True, key="editor_excluir_topicos",
            disabled=["id", "disciplina", "assunto", "prioridade", "status", "dominio", "observacoes"],
            column_config={"Excluir": st.column_config.CheckboxColumn("Excluir", help="Marque os tópicos que deseja remover"), "id": None},
        )
        marcados = selecionados[selecionados["Excluir"]]
        if not marcados.empty:
            st.warning(f"{len(marcados)} tópico(s) marcado(s) para exclusão. Aulas e grupos vinculados também serão removidos.")
            confirmar = st.checkbox("Confirmo a exclusão dos tópicos marcados", key="confirmar_topicos_lote")
            if st.button("Excluir tópicos marcados", type="secondary", disabled=not confirmar):
                for topico_id in marcados["id"]:
                    excluir_topico(int(topico_id), concurso_id)
                st.success(f"{len(marcados)} tópico(s) excluído(s).")
                st.rerun()


def concursos(concurso_id):
    st.title("Concursos")
    lista = consulta("SELECT id, nome, descricao, criado_em FROM concursos ORDER BY criado_em DESC")
    concurso_atual = next(item for item in lista if item["id"] == concurso_id)
    st.dataframe(pd.DataFrame(lista), use_container_width=True, hide_index=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Criar concurso")
        with st.form("criar_concurso"):
            nome = st.text_input("Nome", placeholder="Ex.: TCU 2026 — Auditor de TI")
            descricao = st.text_area("Descrição")
            if st.form_submit_button("Criar", type="primary"):
                try: criar_concurso(nome, descricao); st.success("Concurso criado. Selecione-o no menu lateral."); st.rerun()
                except Exception: st.error("Informe um nome único para o concurso.")
    with c2:
        st.subheader("Reiniciar estudos")
        st.warning("Apaga sessões, questões, aulas concluídas e grupos executados do concurso selecionado. O edital permanece.")
        confirmar = st.checkbox("Entendo que os registros de estudo serão apagados")
        if st.button("Reiniciar este concurso", type="secondary", disabled=not confirmar):
            reiniciar_concurso(concurso_id); st.success("Registros apagados; edital preservado."); st.rerun()
    with st.expander("Excluir concurso", expanded=False):
        st.error(f"Esta ação remove definitivamente “{concurso_atual['nome']}”, incluindo edital, tópicos e histórico.")
        confirmar_nome = st.text_input("Digite o nome do concurso para confirmar", key="confirmar_exclusao")
        if st.button("Excluir concurso definitivamente", type="secondary", disabled=confirmar_nome != concurso_atual["nome"]):
            excluir_concurso(concurso_id)
            st.success("Concurso excluído definitivamente.")
            st.rerun()
    st.divider(); st.subheader("Montar estrutura pelo conteúdo do edital")
    st.caption("Cole o trecho do edital. A leitura ocorre localmente: o sistema reconhece disciplinas em caixa alta e tópicos numerados, como 1, 1.1 e 1.1.1.")
    conteudo = st.text_area("Conteúdo do edital", placeholder="LÍNGUA PORTUGUESA: 1 Leitura. 1.1 Compreensão literal, coesão e coerência textual...", height=220)
    if st.button("Sugerir tópicos", type="primary", disabled=not conteudo.strip()):
        sugestoes = sugerir_topicos_texto(conteudo)
        st.session_state.topicos_sugeridos = pd.DataFrame(sugestoes)
        if sugestoes: st.success(f"Foram sugeridos {len(sugestoes)} tópicos. Revise e edite antes de importar.")
        else: st.warning("Não identifiquei tópicos numerados. Revise o texto colado.")
    if "topicos_sugeridos" in st.session_state:
        revisao = st.data_editor(st.session_state.topicos_sugeridos, use_container_width=True, hide_index=True,
                                 column_config={"Importar": st.column_config.CheckboxColumn("Importar"), "Disciplina": st.column_config.TextColumn("Disciplina"), "Assunto": st.column_config.TextColumn("Assunto", width="large")}, key="editor_topicos")
        if st.button("Importar tópicos aprovados"):
            aprovados = revisao[revisao["Importar"]]
            itens = list(zip(aprovados["Disciplina"], aprovados["Assunto"]))
            importar_topicos(concurso_id, itens); st.success(f"{len(itens)} tópicos importados para o concurso."); st.session_state.pop("topicos_sugeridos", None); st.rerun()


def executar():
    inicializar()
    if not login(): return
    lista = consulta("SELECT id, nome FROM concursos ORDER BY criado_em DESC")
    with st.sidebar:
        st.markdown("""<div class='sidebar-brand'><span class='mark'>📚</span><h2>SOE-BlackLion</h2><p>Seu sistema de estudos</p></div>""", unsafe_allow_html=True)
        nomes = {f"{x['nome']}": x["id"] for x in lista}
        escolha = st.selectbox("Concurso ativo", list(nomes))
        concurso_id = nomes[escolha]
        st.divider()
        st.markdown("<div class='nav-caption'>MENU PRINCIPAL</div>", unsafe_allow_html=True)
        pagina = option_menu(
            menu_title=None,
            options=["Home", "Método dos 4 Grupos", "Registrar estudo", "Edital e tópicos", "Concursos"],
            icons=["house-door-fill", "layers-fill", "journal-plus", "book-fill", "briefcase-fill"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#9fb3c8", "font-size": "16px"},
                "nav-link": {"font-size": "14px", "font-weight": "600", "text-align": "left", "margin": "2px 0", "padding": "9px 12px", "border-radius": "5px", "color": "#d8e2ef"},
                "nav-link-selected": {"background-color": "#2c7be5", "color": "#ffffff"},
            },
        )
    disciplinas, termo = filtros(concurso_id)
    with st.sidebar:
        st.markdown("<div class='nav-caption'>CONTA</div>", unsafe_allow_html=True)
        if st.button("Sair"): st.session_state.clear(); st.rerun()
    st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;background:#ffffff;
        border:1px solid #d7dde4;border-radius:4px;padding:12px 16px;margin:0 0 18px;
        box-shadow:0 8px 16px rgba(45,58,72,.18);">
        <div style="color:#64748b;font-size:14px;">SOE-BlackLion &nbsp;/&nbsp; <b style="color:#123d61;">{pagina}</b></div>
        <div style="color:#d97706;font-size:13px;font-weight:700;">● Estudo em andamento</div>
        </div>""", unsafe_allow_html=True)
    if pagina == "Home": dashboard(concurso_id, disciplinas, termo)
    elif pagina == "Método dos 4 Grupos": quatro_grupos(concurso_id, disciplinas, termo)
    elif pagina == "Registrar estudo": registros(concurso_id, disciplinas)
    elif pagina == "Edital e tópicos": edital(concurso_id, disciplinas, termo)
    else: concursos(concurso_id)
