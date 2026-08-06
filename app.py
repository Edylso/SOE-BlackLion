"""Interface Streamlit do SOE-BlackLion."""
import os
import hashlib
import html
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from streamlit_dnd import dnd, apply_move

from analise_prova import analisar_prova
from config import DISCIPLINAS
from database import (consulta, criar_concurso, executar_grupo, excluir_concurso, excluir_topico, importar_topicos, sugerir_topicos_texto,
                      inicializar, registrar_aula, registrar_questoes, registrar_sessao, reiniciar_concurso, salvar_analise_prova,
                      excluir_registros_historico, atualizar_sessao_historico, atualizar_questoes_historico,
                      atualizar_grupo_historico, carregar_planejamento_semana, salvar_planejamento_semana)

st.set_page_config(page_title="SOE-BlackLion", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"], [data-testid="stApp"] { background: #dce3eb !important; }
    [data-testid="stMainBlockContainer"], .main .block-container { max-width: 1400px !important; padding-top: 1.5rem !important; }
    .stApp { background: #dce3eb; font-family: ui-rounded, 'Avenir Next', 'Segoe UI', sans-serif; }
    h1, h2, h3 { font-family: ui-rounded, 'Avenir Next', 'Segoe UI', sans-serif !important; color: #1f2937; }
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background: #0b1f33 !important; border-right: 1px solid #081827; min-width: 270px; }
    [data-testid="stSidebar"] * { color: #eef4f8; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div { background: #123a5c; border: 1px solid #285477; border-radius: 4px; }
    [data-testid="stSidebar"] input { background: #123a5c !important; border-radius: 4px !important; }
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div { background: #123a5c; border: 1px solid #285477; border-radius: 4px; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div > div:last-child { background: #123a5c !important; }
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
    .sidebar-brand { padding: 15px 7px 21px; border-bottom: 1px solid #21425e; margin-bottom: 14px; }
    .sidebar-brand .mark { display: inline-block; width: 38px; height: 38px; line-height: 38px; text-align: center; border-radius: 50%; background: #f59e0b; font-size: 20px; }
    .sidebar-brand h2 { display: inline; margin-left: 9px; color: white !important; font-size: 1.2rem; vertical-align: middle; }
    .sidebar-brand p { margin: 5px 0 0 48px; color: #d4c8ee; font-size: .73rem; }
    .stButton > button, [data-testid="stFormSubmitButton"] > button { border: 0; border-radius: 4px; background: #f59e0b; color: #123d61; font-weight: 800; box-shadow: 0 3px 7px rgba(126, 81, 8, .22); }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { border: 0; color: white; filter: brightness(1.07); }
    [data-testid="stExpander"] { border: 1px solid #d7dde4; border-radius: 3px; background: #fff; box-shadow: 0 8px 16px rgba(45,58,72,.18); }
    [data-testid="stDataFrame"], [data-testid="stForm"] { border-radius: 3px; box-shadow: 0 8px 16px rgba(45,58,72,.18); }
    .topbar { display: flex; align-items: center; justify-content: space-between; background: #fff; border: 1px solid #d7dde4; border-radius: 3px; padding: 11px 16px; margin: 0 0 18px; box-shadow: 0 7px 14px rgba(45,58,72,.16); }
    .topbar .crumb { color: #64748b; font-size: .86rem; }.topbar b { color: #123d61; }.topbar .user { color: #d97706; font-weight: 700; font-size: .86rem; }
    .nav-caption { color: #a9c0d3 !important; font-size: .66rem; font-weight: 700; letter-spacing: .08em; margin: 20px 8px 6px; }
    [data-testid="stSidebar"] .stButton > button { background: #123a5c !important; color: #d8e7f3 !important; border: 1px solid #285477 !important; box-shadow: none !important; font-weight: 600; }
    [data-testid="stSidebar"] .stButton > button:hover { background: #1a4a70 !important; color: #fff !important; }
    [class*="st-key-disponiveis_"] [data-testid="stVerticalBlock"]:has([class*="st-key-card_"]) { display: flex !important; flex-flow: row wrap !important; align-items: flex-start !important; align-content: flex-start !important; gap: 8px !important; }
    [class*="st-key-disponiveis_"] [data-testid="stElementContainer"]:has([class*="st-key-card_"]) { flex: 0 0 116px !important; width: 116px !important; margin: 0 !important; }
    [class*="st-key-disponiveis_"] > [data-testid="stLayoutWrapper"] { flex: 0 0 116px !important; width: 116px !important; max-width: 116px !important; margin: 0 !important; }
</style>
""", unsafe_allow_html=True)


def aplicar_estilo_sidebar():
    """Aplica a paleta na camada própria da barra lateral do Streamlit."""
    components.html("""
    <script>
      const aplicar = () => {
        try {
          const doc = window.parent.document;
          const sidebar = doc.querySelector('[data-testid="stSidebar"]');
          if (!sidebar) return;
          sidebar.style.setProperty('background', '#0b1f33', 'important');
          sidebar.style.setProperty('border-right', '1px solid #081827', 'important');
          const painel = sidebar.querySelector('[data-testid="stSidebarContent"]') || sidebar.firstElementChild;
          if (painel) painel.style.setProperty('background', '#0b1f33', 'important');
          // Os widgets recebem fundos próprios do BaseWeb; somente os campos
          // editáveis ficam um tom acima do painel, nunca cinza ou branco.
          sidebar.querySelectorAll('[data-baseweb="select"] > div, [data-baseweb="input"] > div, input').forEach((el) => {
            el.style.setProperty('background', '#123a5c', 'important');
            el.style.setProperty('border-color', '#285477', 'important');
            el.style.setProperty('color', '#eef4f8', 'important');
          });
          sidebar.querySelectorAll('[data-baseweb="select"] > div > div:last-child, [data-baseweb="select"] button').forEach((el) => {
            el.style.setProperty('background', '#123a5c', 'important');
            el.style.setProperty('color', '#eef4f8', 'important');
          });
          sidebar.querySelectorAll('button').forEach((el) => {
            if (el.innerText.trim() === 'Sair') {
              el.style.setProperty('background', '#123a5c', 'important');
              el.style.setProperty('border', '1px solid #285477', 'important');
              el.style.setProperty('box-shadow', 'none', 'important');
              el.style.setProperty('color', '#d8e7f3', 'important');
            }
          });
          sidebar.querySelectorAll('iframe').forEach((frame) => {
            try {
              const frameDoc = frame.contentDocument;
              if (!frameDoc || frameDoc.getElementById('soe-menu-palette')) return;
              const style = frameDoc.createElement('style');
              style.id = 'soe-menu-palette';
              style.textContent = `html, body, .nav, .nav-pills { background: #0b1f33 !important; }
                .nav-link { color: #d8e2ef !important; background: transparent !important; }
                .nav-link:hover { background: #123a5c !important; }
                .nav-link.active { background: #2c7be5 !important; color: #fff !important; }
                .nav-link i { color: #9fb3c8 !important; }
                .nav-link.active i { color: #fff !important; }`;
              frameDoc.head.appendChild(style);
            } catch (_) {}
          });
          sidebar.querySelectorAll('p, label, h1, h2, h3, h4, span').forEach((el) => {
            if (!el.closest('[data-baseweb="select"]')) el.style.setProperty('color', '#eef4f8', 'important');
          });
          sidebar.querySelectorAll('.nav-caption').forEach((el) => {
            el.style.setProperty('color', '#a9c0d3', 'important');
            el.style.setProperty('font-weight', '700', 'important');
          });
          doc.querySelectorAll('[class*="st-key-disponiveis_"]').forEach((area) => {
            const listas = [area, ...area.querySelectorAll('[data-testid="stVerticalBlock"]')];
            listas.forEach((lista) => {
              if (!lista.querySelector('[class*="st-key-card_"]')) return;
              lista.style.setProperty('display', 'flex', 'important');
              lista.style.setProperty('flex-flow', 'row wrap', 'important');
              lista.style.setProperty('align-items', 'flex-start', 'important');
              lista.style.setProperty('align-content', 'flex-start', 'important');
              lista.style.setProperty('gap', '8px', 'important');
            });
            area.querySelectorAll('[class*="st-key-card_"]').forEach((card) => {
              card.style.setProperty('flex', '0 0 116px', 'important');
              card.style.setProperty('width', '116px', 'important');
              const envoltorio = card.closest('[data-testid="stElementContainer"]');
              if (envoltorio) {
                envoltorio.style.setProperty('flex', '0 0 116px', 'important');
                envoltorio.style.setProperty('width', '116px', 'important');
                envoltorio.style.setProperty('margin', '0', 'important');
              }
              let ancestral = card.parentElement;
              while (ancestral && ancestral !== area) {
                if (ancestral.getAttribute('data-testid') === 'stLayoutWrapper') {
                  ancestral.style.setProperty('flex', '0 0 116px', 'important');
                  ancestral.style.setProperty('width', '116px', 'important');
                  ancestral.style.setProperty('max-width', '116px', 'important');
                  ancestral.style.setProperty('margin', '0', 'important');
                }
                ancestral = ancestral.parentElement;
              }
            });
          });
        } catch (_) {}
      };
      aplicar();
      setInterval(aplicar, 400);
    </script>
    """, height=0, width=0)


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


def _grafico_vazio(titulo, mensagem):
    fig = go.Figure()
    fig.add_annotation(text=mensagem, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
                       font={"size": 15, "color": "#64748b"}, align="center")
    fig.update_layout(title=titulo, height=300, margin=dict(l=4, r=4, t=45, b=4), paper_bgcolor="#ffffff",
                      plot_bgcolor="#ffffff", font_color="#1f2937", xaxis={"visible": False}, yaxis={"visible": False})
    return fig


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
        with st.container(border=True):
            if progresso["horas"].sum() == 0:
                fig = _grafico_vazio("Horas por disciplina", "Registre uma sessão de estudo<br>para acompanhar as horas por disciplina.")
            else:
                fig = px.bar(progresso.sort_values("horas", ascending=True), x="horas", y="disciplina", orientation="h", color="horas", color_continuous_scale=["#c4d9e8", "#123d61"], title="Horas por disciplina")
                fig.update_layout(coloraxis_showscale=False, height=300, margin=dict(l=0, r=0, t=45, b=0), plot_bgcolor="#fff", paper_bgcolor="#fff", font_color="#475569")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with g2:
        with st.container(border=True):
            if sessoes.empty:
                fig = _grafico_vazio("Ritmo semanal", "Registre uma sessão de estudo<br>para visualizar seu ritmo semanal.")
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
        st.caption("Selecione a disciplina e o tópico exato para que seu histórico e seus indicadores fiquem mais úteis.")
        data = st.date_input("Data", value=date.today(), key="sessao_data")
        disciplina = st.selectbox("Disciplina", nomes, key="sessao_disciplina")
        topicos_disciplina = consulta("SELECT id, assunto FROM topicos WHERE concurso_id=? AND disciplina=? ORDER BY assunto", (concurso_id, disciplina))
        opcoes_topicos = {item["assunto"]: item["id"] for item in topicos_disciplina}
        topico = st.selectbox("Tópico estudado", list(opcoes_topicos), key="sessao_topico")
        atividade = st.text_input("Atividade", placeholder="Ex.: Anki, teoria, prova Cebraspe", key="sessao_atividade")
        grupo = st.selectbox("Grupo", ["Sem grupo / teoria", "Grupo A", "Grupo B", "Grupo C", "Grupo D"], key="sessao_grupo")
        c1, c2 = st.columns(2)
        tempo = c1.number_input("Tempo (minutos)", min_value=1, value=60, step=5, key="sessao_tempo")
        q = c2.number_input("Questões", min_value=0, step=1, key="sessao_questoes")
        obs = st.text_area("Observações", key="sessao_observacoes")
        if st.button("Registrar sessão", type="primary", key="salvar_sessao"):
            registrar_sessao(concurso_id, data, disciplina, opcoes_topicos[topico], atividade, grupo, tempo, q, obs)
            st.success("Sessão registrada com o tópico selecionado.")
    with tab2:
        with st.form("questoes"):
            data = st.date_input("Data da lista", value=date.today(), key="qdata"); disciplina = st.selectbox("Disciplina", nomes, key="qdisc")
            assunto = st.text_input("Assunto"); fonte = st.text_input("Fonte"); ano = st.number_input("Ano", min_value=2000, max_value=2100, value=2024)
            quantidade = st.number_input("Quantidade", min_value=1, value=10); acertos = st.number_input("Acertos", min_value=0, value=0); erros = st.number_input("Erros", min_value=0, value=0); brancos = st.number_input("Brancos", min_value=0, value=0); tempo = st.number_input("Tempo (minutos)", min_value=0, value=0, step=5)
            if st.form_submit_button("Registrar questões", type="primary"):
                if acertos + erros + brancos > quantidade: st.error("Acertos, erros e brancos não podem superar a quantidade.")
                else: registrar_questoes(concurso_id, data, disciplina, assunto, fonte, ano, quantidade, acertos, erros, brancos, tempo); st.success("Questões registradas.")


def historico(concurso_id, disciplinas, termo):
    st.title("Histórico de estudos")
    st.caption("Uma visão organizada de tudo o que você registrou neste concurso.")
    sessoes = pd.DataFrame(consulta("""SELECT s.id, s.topico_id, s.data, 'Sessão' AS tipo, s.disciplina,
        COALESCE(t.assunto, 'Tópico não informado') AS assunto, COALESCE(s.atividade, '') AS atividade,
        COALESCE(s.grupo, 'Sem grupo') AS grupo, s.tempo_min, s.questoes, NULL AS ano, NULL AS acertos, NULL AS erros,
        NULL AS brancos, COALESCE(s.observacoes, '') AS observacoes
        FROM sessoes s LEFT JOIN topicos t ON t.id=s.topico_id
        WHERE s.concurso_id=?""", (concurso_id,)))
    questoes = pd.DataFrame(consulta("""SELECT q.id, NULL AS topico_id, q.data, 'Questões' AS tipo, q.disciplina,
        COALESCE(q.assunto, 'Assunto não informado') AS assunto, COALESCE(q.fonte, 'Banco de questões') AS atividade,
        'Sem grupo' AS grupo, COALESCE(q.tempo_min, 0) AS tempo_min, q.quantidade AS questoes, q.ano,
        q.acertos, q.erros, q.brancos, ('Acertos: ' || q.acertos || ' · Erros: ' || q.erros || ' · Brancos: ' || q.brancos) AS observacoes
        FROM questoes q WHERE q.concurso_id=?""", (concurso_id,)))
    grupos = pd.DataFrame(consulta("""SELECT g.id, e.topico_id, g.data, 'Revisão' AS tipo, t.disciplina, t.assunto,
        'Método dos 4 Grupos' AS atividade, ('Grupo ' || g.grupo) AS grupo, g.tempo_min,
        (g.acertos + g.erros + g.brancos) AS questoes, NULL AS ano,
        g.acertos, g.erros, g.brancos, ('Acertos: ' || g.acertos || ' · Erros: ' || g.erros || ' · Brancos: ' || g.brancos) AS observacoes
        FROM grupos_executados g JOIN estudos e ON e.id=g.estudo_id JOIN topicos t ON t.id=e.topico_id
        WHERE t.concurso_id=?""", (concurso_id,)))
    blocos = [item for item in (sessoes, questoes, grupos) if not item.empty]
    if not blocos:
        st.info("Você ainda não possui registros neste concurso. Comece em “Registrar estudo”.")
        return
    tabela = pd.concat(blocos, ignore_index=True)
    tabela["data"] = pd.to_datetime(tabela["data"], errors="coerce")
    tabela = aplicar_filtros(tabela, disciplinas, termo)
    tabela = tabela.sort_values(["data", "tipo"], ascending=[False, True])
    horas = tabela["tempo_min"].fillna(0).sum() / 60
    c1, c2, c3 = st.columns(3)
    c1.metric("Registros", len(tabela))
    c2.metric("Horas registradas", f"{horas:.1f} h")
    c3.metric("Questões registradas", int(tabela["questoes"].fillna(0).sum()))
    st.markdown("#### Sua linha do tempo")
    st.caption("Marque uma ou mais linhas para excluir registros incorretos.")
    exibicao = tabela.copy()
    exibicao["data"] = exibicao["data"].dt.strftime("%d/%m/%Y")
    exibicao.insert(0, "Excluir", False)
    exibicao.insert(1, "Editar", False)
    selecionados = st.data_editor(
        exibicao[["Excluir", "Editar", "id", "data", "tipo", "disciplina", "assunto", "atividade", "grupo", "tempo_min", "questoes", "observacoes"]],
        use_container_width=True, hide_index=True, key=f"historico_editor_{concurso_id}",
        disabled=["id", "data", "tipo", "disciplina", "assunto", "atividade", "grupo", "tempo_min", "questoes", "observacoes"],
        column_config={"Excluir": st.column_config.CheckboxColumn("Excluir", help="Marque o registro que deseja remover"),
                       "Editar": st.column_config.CheckboxColumn("Editar", help="Marque um registro para alterar seus dados"),
                       "id": None, "data": "Data", "tipo": "Registro", "assunto": "Tópico", "atividade": "Atividade",
                       "grupo": "Grupo", "tempo_min": st.column_config.NumberColumn("Minutos", format="%d min"),
                       "questoes": st.column_config.NumberColumn("Questões", format="%d")},
    )
    marcados = selecionados[selecionados["Excluir"]]
    if not marcados.empty:
        st.warning(f"{len(marcados)} registro(s) marcado(s) para exclusão.")
        confirmar = st.checkbox("Confirmo a exclusão dos registros marcados", key=f"confirmar_historico_{concurso_id}")
        if st.button("Excluir registros marcados", type="secondary", disabled=not confirmar, key=f"excluir_historico_{concurso_id}"):
            excluir_registros_historico(concurso_id, list(zip(marcados["tipo"], marcados["id"])))
            st.success(f"{len(marcados)} registro(s) excluído(s).")
            st.rerun()
    para_editar = selecionados[selecionados["Editar"]]
    if len(para_editar) > 1:
        st.info("Para editar, marque apenas um registro por vez.")
    elif len(para_editar) == 1:
        registro_exibido = para_editar.iloc[0]
        tipo, registro_id = registro_exibido["tipo"], int(registro_exibido["id"])
        # A tabela de tela oculta campos técnicos (como topico_id). Recupera
        # o registro completo antes de montar o formulário de edição.
        registro = tabela[(tabela["tipo"] == tipo) & (tabela["id"] == registro_id)].iloc[0]
        chave = f"editar_{concurso_id}_{tipo}_{registro_id}"
        st.markdown("#### Editar registro selecionado")
        with st.form(chave):
            data_registro = st.date_input("Data", value=pd.to_datetime(registro["data"], dayfirst=True).date())
            if tipo == "Sessão":
                topicos_opcoes = consulta("SELECT id, disciplina, assunto FROM topicos WHERE concurso_id=? ORDER BY disciplina, assunto", (concurso_id,))
                mapa_topicos = {f"{item['disciplina']} — {item['assunto']}": item for item in topicos_opcoes}
                if not mapa_topicos:
                    mapa_topicos["Tópico removido / não informado"] = {"id": None, "disciplina": registro["disciplina"]}
                valor_atual = next((nome for nome, item in mapa_topicos.items() if item["id"] == registro["topico_id"]), list(mapa_topicos)[0])
                topico_escolhido = st.selectbox("Tópico estudado", list(mapa_topicos), index=list(mapa_topicos).index(valor_atual))
                atividade = st.text_input("Atividade", value=registro["atividade"])
                grupo = st.selectbox("Grupo", ["Sem grupo / teoria", "Grupo A", "Grupo B", "Grupo C", "Grupo D"],
                                     index=["Sem grupo / teoria", "Grupo A", "Grupo B", "Grupo C", "Grupo D"].index(registro["grupo"]) if registro["grupo"] in ["Sem grupo / teoria", "Grupo A", "Grupo B", "Grupo C", "Grupo D"] else 0)
                c1, c2 = st.columns(2)
                tempo = c1.number_input("Tempo (minutos)", min_value=1, value=int(registro["tempo_min"]))
                quantidade = c2.number_input("Questões", min_value=0, value=int(registro["questoes"]))
                observacoes = st.text_area("Observações", value=registro["observacoes"])
                salvar = st.form_submit_button("Salvar alterações", type="primary")
                if salvar:
                    topico = mapa_topicos[topico_escolhido]
                    atualizar_sessao_historico(concurso_id, registro_id, data_registro, topico["disciplina"], topico["id"], atividade, grupo, tempo, quantidade, observacoes)
                    st.success("Sessão atualizada."); st.rerun()
            elif tipo == "Questões":
                opcoes_disciplina = sorted(set(disciplinas) | {registro["disciplina"]})
                disciplina = st.selectbox("Disciplina", opcoes_disciplina, index=opcoes_disciplina.index(registro["disciplina"]))
                assunto = st.text_input("Assunto", value=registro["assunto"])
                fonte = st.text_input("Fonte", value=registro["atividade"])
                ano = st.number_input("Ano", min_value=1900, max_value=2100, value=int(registro["ano"]) if pd.notna(registro["ano"]) else date.today().year)
                quantidade = st.number_input("Quantidade", min_value=1, value=int(registro["questoes"]))
                c1, c2, c3 = st.columns(3)
                acertos = c1.number_input("Acertos", min_value=0, value=int(registro["acertos"]))
                erros = c2.number_input("Erros", min_value=0, value=int(registro["erros"]))
                brancos = c3.number_input("Brancos", min_value=0, value=int(registro["brancos"]))
                tempo = st.number_input("Tempo (minutos)", min_value=0, value=int(registro["tempo_min"]))
                salvar = st.form_submit_button("Salvar alterações", type="primary")
                if salvar:
                    if acertos + erros + brancos > quantidade:
                        st.error("Acertos, erros e brancos não podem superar a quantidade.")
                    else:
                        atualizar_questoes_historico(concurso_id, registro_id, data_registro, disciplina, assunto, fonte, ano, quantidade, acertos, erros, brancos, tempo)
                        st.success("Registro de questões atualizado."); st.rerun()
            else:
                grupo_atual = str(registro["grupo"]).replace("Grupo ", "")
                grupo = st.selectbox("Grupo", ["A", "B", "C", "D"], index=["A", "B", "C", "D"].index(grupo_atual) if grupo_atual in "ABCD" else 0)
                c1, c2, c3 = st.columns(3)
                acertos = c1.number_input("Acertos", min_value=0, value=int(registro["acertos"]))
                erros = c2.number_input("Erros", min_value=0, value=int(registro["erros"]))
                brancos = c3.number_input("Brancos", min_value=0, value=int(registro["brancos"]))
                tempo = st.number_input("Tempo (minutos)", min_value=0, value=int(registro["tempo_min"]))
                observacoes = st.text_area("Observações", value=registro["observacoes"])
                salvar = st.form_submit_button("Salvar alterações", type="primary")
                if salvar:
                    atualizar_grupo_historico(concurso_id, registro_id, data_registro, grupo, acertos, erros, brancos, tempo, observacoes)
                    st.success("Revisão atualizada."); st.rerun()


def planejamento(concurso_id, disciplinas, termo):
    st.title("Planejamento")
    st.caption("Veja, em uma única tela, quais tópicos já entraram no seu ciclo de estudos e como seu tempo está distribuído.")
    topicos = pd.DataFrame(consulta("SELECT id, disciplina, assunto FROM topicos WHERE concurso_id=?", (concurso_id,)))
    if topicos.empty:
        st.info("Este concurso ainda não possui tópicos. Cadastre ou importe o edital para montar seu planejamento.")
        return
    sessoes = pd.DataFrame(consulta("""SELECT topico_id, SUM(tempo_min) AS minutos_sessao
        FROM sessoes WHERE concurso_id=? AND topico_id IS NOT NULL GROUP BY topico_id""", (concurso_id,)))
    grupos = pd.DataFrame(consulta("""SELECT e.topico_id, SUM(g.tempo_min) AS minutos_grupo
        FROM grupos_executados g JOIN estudos e ON e.id=g.estudo_id JOIN topicos t ON t.id=e.topico_id
        WHERE t.concurso_id=? GROUP BY e.topico_id""", (concurso_id,)))
    aulas = pd.DataFrame(consulta("""SELECT e.topico_id, COUNT(*) AS aulas_concluidas
        FROM estudos e JOIN topicos t ON t.id=e.topico_id WHERE t.concurso_id=? GROUP BY e.topico_id""", (concurso_id,)))
    for origem, coluna in ((sessoes, "minutos_sessao"), (grupos, "minutos_grupo"), (aulas, "aulas_concluidas")):
        if origem.empty:
            topicos[coluna] = 0
        else:
            topicos = topicos.merge(origem, how="left", left_on="id", right_on="topico_id").drop(columns=["topico_id"])
            topicos[coluna] = topicos[coluna].fillna(0)
    topicos["minutos"] = topicos["minutos_sessao"] + topicos["minutos_grupo"]
    topicos["estudado"] = (topicos["minutos"] > 0) | (topicos["aulas_concluidas"] > 0)
    topicos = aplicar_filtros(topicos, disciplinas, termo)
    topicos = topicos.sort_values(["disciplina", "assunto"]).reset_index(drop=True)
    topicos["numero_topico"] = topicos.groupby("disciplina").cumcount() + 1
    estudados = topicos[topicos["estudado"]].sort_values(["minutos", "disciplina", "assunto"], ascending=[False, True, True])
    percentual = (len(estudados) / len(topicos) * 100) if len(topicos) else 0
    total_minutos = int(topicos["minutos"].sum())
    c1, c2, c3 = st.columns(3)
    c1.metric("Tópicos estudados", f"{len(estudados)} de {len(topicos)}")
    c2.metric("Progresso do edital", f"{percentual:.0f}%")
    c3.metric("Tempo nos tópicos", f"{total_minutos // 60}h {total_minutos % 60:02d}min")
    st.progress(percentual / 100, text=f"Progresso do ciclo: {len(estudados)} tópicos já estudados")
    esquerda, direita = st.columns([1.2, 1])
    with esquerda:
        with st.container(border=True):
            st.subheader("Sequência dos tópicos estudados")
            if estudados.empty:
                st.info("Ainda não há tópicos vinculados a sessões, aulas ou grupos. Registre seu próximo estudo para iniciar o gráfico.")
            else:
                maior_tempo = max(float(estudados["minutos"].max()), 1)
                for item in estudados.head(16).itertuples():
                    linha, tempo = st.columns([4, 1])
                    linha.markdown(f"**{item.disciplina} · Tópico {int(item.numero_topico)}**")
                    tempo.caption(f"{int(item.minutos) // 60}h {int(item.minutos) % 60:02d}min")
                    st.progress(min(float(item.minutos) / maior_tempo, 1.0))
                if len(estudados) > 16:
                    st.caption(f"Exibindo 16 de {len(estudados)} tópicos estudados. Use os filtros laterais para refinar a lista.")
    with direita:
        with st.container(border=True):
            st.subheader("Distribuição do tempo")
            com_tempo = estudados[estudados["minutos"] > 0].copy()
            if com_tempo.empty:
                st.info("O gráfico aparecerá quando você registrar tempo em uma sessão ou revisão.")
            else:
                com_tempo = com_tempo.head(14)
                figura = px.pie(com_tempo, values="minutos", names="assunto", hole=.62,
                                color="disciplina", color_discrete_sequence=["#2c7be5", "#00b5ad", "#f59e0b", "#8b5cf6", "#ef6c73", "#4c9f70", "#7c94b0"])
                figura.update_traces(textinfo="none", hovertemplate="<b>%{label}</b><br>%{value:.0f} min (%{percent})<extra></extra>")
                figura.update_layout(height=430, margin=dict(l=8, r=8, t=18, b=8), legend=dict(orientation="h", y=-.12),
                                     paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
                                     annotations=[dict(text=f"<b>{total_minutos // 60}h<br>{total_minutos % 60:02d}min</b>", x=.5, y=.5, showarrow=False, font=dict(size=20, color="#123d61"))])
                st.plotly_chart(figura, use_container_width=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.subheader("Agenda sugerida")
    st.caption("São 2 horas por dia, todos os dias: dois blocos de 1 hora. Revisões dos Grupos A–D têm prioridade e somem automaticamente ao serem concluídas.")
    pendentes_grupo = _grupos_pendentes_planejamento(concurso_id, disciplinas, termo)
    grupos_concluidos = _grupos_concluidos_planejamento(concurso_id, disciplinas, termo)
    numeros_topicos = {(item.disciplina, item.assunto): int(item.numero_topico) for item in topicos.itertuples()}
    for item in pendentes_grupo + grupos_concluidos:
        item["numero"] = numeros_topicos.get((item["disciplina"], item["assunto"]), "—")
    conclusoes_topicos = {item["topico_id"]: item["data"] for item in consulta("""SELECT e.topico_id, e.data FROM estudos e
                                                                                      JOIN topicos t ON t.id=e.topico_id
                                                                                      WHERE t.concurso_id=?""", (concurso_id,))}
    estudados_ids = set(conclusoes_topicos)
    sugestoes = pendentes_grupo + grupos_concluidos + [
        {"id": f"topico_{item.id}", "tipo": "Tópico", "disciplina": item.disciplina, "assunto": item.assunto, "grupo": "Teoria", "numero": int(item.numero_topico),
         "concluido": item.id in estudados_ids, "data_conclusao": conclusoes_topicos.get(item.id)}
        for item in topicos.sort_values(["disciplina", "assunto"]).itertuples()
    ]
    inicio = st.date_input("Iniciar cronograma em", value=date(date.today().year, 8, 3), key="agenda_inicio")
    cronograma = _montar_cronograma_completo(sugestoes)
    agenda = {}
    restantes = []
    for item in cronograma:
        data_conclusao = item.get("data_conclusao")
        if item["concluido"] and data_conclusao:
            try:
                dia = max(date.fromisoformat(str(data_conclusao)), inicio)
                agenda.setdefault(dia, []).append(item)
                continue
            except ValueError:
                pass
        restantes.append(item)
    dia_atual = inicio
    for item in restantes:
        while len(agenda.get(dia_atual, [])) >= 2:
            dia_atual += timedelta(days=1)
        agenda.setdefault(dia_atual, []).append(item)
    resumo_1, resumo_2, resumo_3, resumo_4 = st.columns(4)
    resumo_1.metric("Horas do cronograma", f"{len(cronograma)} h")
    resumo_2.metric("Carga pendente", f"{sum(not item['concluido'] for item in cronograma)} h")
    resumo_3.metric("Revisões", sum(item["tipo"] == "Revisão" for item in cronograma))
    resumo_4.metric("Itens concluídos", sum(item["concluido"] for item in cronograma))
    nomes_dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    cores = ["#2c7be5", "#00b5ad", "#f59e0b", "#8b5cf6", "#ef6c73", "#4c9f70", "#5c6ac4", "#e67e22", "#147d92", "#a85bd7", "#bc6c25"]
    cor_materia = {materia: cores[indice % len(cores)] for indice, materia in enumerate(sorted(topicos["disciplina"].unique()))}
    primeiro_dia = min(agenda)
    ultimo_dia = max(agenda)
    primeira_semana = primeiro_dia - timedelta(days=primeiro_dia.weekday())
    ultima_semana = ultimo_dia - timedelta(days=ultimo_dia.weekday())
    chave_origem = f"agenda_inicio_origem_{concurso_id}"
    chave_semana = f"agenda_semana_{concurso_id}"
    if st.session_state.get(chave_origem) != inicio:
        st.session_state[chave_origem] = inicio
        st.session_state[chave_semana] = primeira_semana
    semana_atual = st.session_state.get(chave_semana, primeira_semana)
    semana_atual = min(max(semana_atual, primeira_semana), ultima_semana)
    navegacao_esq, navegacao_meio, navegacao_dir = st.columns([1, 2, 1])
    with navegacao_esq:
        if st.button("← Semana anterior", disabled=semana_atual <= primeira_semana, key=f"agenda_anterior_{concurso_id}"):
            st.session_state[chave_semana] = semana_atual - timedelta(days=7)
            st.rerun()
    with navegacao_meio:
        total_semanas = ((ultima_semana - primeira_semana).days // 7) + 1
        indice_semana = ((semana_atual - primeira_semana).days // 7) + 1
        st.markdown(f"<div style='text-align:center;padding:7px 0;font-weight:800;color:#123d61;'>Semana {indice_semana} de {total_semanas} · {semana_atual.strftime('%d/%m')} a {(semana_atual + timedelta(days=6)).strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)
    with navegacao_dir:
        if st.button("Próxima semana →", disabled=semana_atual >= ultima_semana, key=f"agenda_proxima_{concurso_id}"):
            st.session_state[chave_semana] = semana_atual + timedelta(days=7)
            st.rerun()
    dias_semana = [semana_atual + timedelta(days=deslocamento) for deslocamento in range(7)]
    itens_semana = [item for dia in dias_semana for item in agenda.get(dia, [])]
    itens_por_id = {item["id"]: item for item in itens_semana}
    revisoes_disponiveis = [item for item in pendentes_grupo if item["id"] not in itens_por_id]
    itens_por_id.update({item["id"]: item for item in revisoes_disponiveis})
    chave_layout = f"agenda_layout_{concurso_id}_{semana_atual.isoformat()}"
    chave_copias = f"agenda_copias_{concurso_id}_{semana_atual.isoformat()}"
    chave_contador = f"agenda_contador_copias_{concurso_id}_{semana_atual.isoformat()}"
    chave_disponiveis = f"disponiveis_{semana_atual.isoformat()}"
    chaves_dias = {dia: f"dia_{dia.isoformat()}" for dia in dias_semana}
    layout_base = {chave_disponiveis: [item["id"] for item in revisoes_disponiveis]}
    layout_base.update({chaves_dias[dia]: [item["id"] for item in agenda.get(dia, [])] for dia in dias_semana})
    if chave_layout not in st.session_state:
        gravado = carregar_planejamento_semana(concurso_id, semana_atual)
        st.session_state[chave_layout] = gravado["layout"] if gravado else layout_base
        st.session_state[chave_copias] = gravado["copias"] if gravado else {}
    layout = st.session_state[chave_layout]
    copias = st.session_state.setdefault(chave_copias, {})
    # Mantém os movimentos já feitos e inclui automaticamente novos cartões
    # que tenham entrado na semana por uma nova revisão ou alteração de filtro.
    ids_validos = set(itens_por_id)
    for chave in layout_base:
        layout.setdefault(chave, [])
        layout[chave] = [item_id for item_id in layout[chave] if copias.get(item_id, item_id) in ids_validos]
    copias = {item_id: origem for item_id, origem in copias.items() if origem in ids_validos}
    st.session_state[chave_copias] = copias
    ids_presentes = {item_id for lista in layout.values() for item_id in lista}
    for chave, itens in layout_base.items():
        layout[chave].extend(item_id for item_id in itens if item_id not in ids_presentes)
    st.markdown("##### Cartões disponíveis")
    st.caption("Arraste um cartão para um dia ou retire um cartão do calendário para adiá-lo. Clique em gravar para manter a organização nas próximas visitas.")
    acao_gravar, acao_liberar = st.columns([1, 1.8])
    if acao_gravar.button("Gravar plano da semana", type="primary", key=f"agenda_gravar_{concurso_id}_{semana_atual.isoformat()}"):
        salvar_planejamento_semana(concurso_id, semana_atual, layout, copias)
        st.success("Plano semanal gravado.")
    if acao_liberar.button("Mover todos os cartões da semana para a área disponível", key=f"agenda_liberar_{concurso_id}_{semana_atual.isoformat()}"):
        layout[chave_disponiveis] = [item_id for dia in dias_semana for item_id in layout[chaves_dias[dia]]]
        for dia in dias_semana:
            layout[chaves_dias[dia]] = []
        st.rerun()
    with st.container(key=chave_disponiveis, border=True):
        if not layout[chave_disponiveis]:
            st.caption("Arraste cartões do calendário para esta área quando quiser reorganizar a semana.")
        duplicar = None
        for item_id in layout[chave_disponiveis]:
            if _cartao_arrastavel_planejamento(itens_por_id[copias.get(item_id, item_id)], cor_materia, item_id, compacto=True):
                duplicar = item_id
    colunas = st.columns(7)
    for dia, coluna in zip(dias_semana, colunas):
        with coluna:
            st.markdown(f"**{nomes_dias[dia.weekday()]}**")
            st.caption(dia.strftime("%d/%m"))
            with st.container(key=chaves_dias[dia], border=True):
                for item_id in layout[chaves_dias[dia]]:
                    if _cartao_arrastavel_planejamento(itens_por_id[copias.get(item_id, item_id)], cor_materia, item_id):
                        duplicar = item_id
    if duplicar:
        base_id = copias.get(duplicar, duplicar)
        proximo = st.session_state.get(chave_contador, 0) + 1
        st.session_state[chave_contador] = proximo
        nova_copia = f"{base_id}__copia_{proximo}"
        copias[nova_copia] = base_id
        layout[chave_disponiveis].append(nova_copia)
        st.rerun()
    evento = dnd([chave_disponiveis, *[chaves_dias[dia] for dia in dias_semana]], color="#2c7be5", key=f"arrastar_{concurso_id}_{semana_atual.isoformat()}")
    if evento:
        apply_move(evento, layout)
        st.rerun()
    st.caption("Os cartões concluídos permanecem como histórico visual e não entram na carga pendente. A marca é atualizada automaticamente ao concluir tópico ou revisão.")


def _cartao_arrastavel_planejamento(item, cor_materia, instancia_id, compacto=False):
    """Renderiza um cartão compacto; a chave permite seu arrasto entre dias."""
    cor = cor_materia.get(item["disciplina"], "#64748b")
    concluido = item["concluido"]
    fundo = "#edf7f0" if concluido else "#f8fafc"
    marca = "✓ CONCLUÍDO" if concluido else ""
    tipo = f"REVISÃO · {item['grupo']}" if item["tipo"] == "Revisão" else ""
    with st.container(key=f"card_{instancia_id}", border=not compacto):
        dimensoes = "width:116px;min-height:76px;display:inline-block;" if compacto else "min-height:84px;"
        detalhes = "" if compacto else "<div style='font-size:10px;color:#64748b;margin-top:3px;'>⏱ 1h</div>"
        st.markdown(
            f"<div style='border-left:4px solid {cor};background:{fundo};border-radius:5px;padding:8px 7px;margin:1px 0;{dimensoes}'>"
            f"<div style='font-size:10px;font-weight:800;color:{'#27834a' if concluido else '#0ea5a4'};min-height:13px;'>{marca or tipo}</div>"
            f"<div style='font-size:12px;font-weight:700;color:#1f2937;'>{html.escape(item['disciplina'])}</div>"
            f"{detalhes}</div>",
            unsafe_allow_html=True,
        )
        if compacto:
            return False
        return st.button("⧉ Duplicar", key=f"duplicar_{instancia_id}", use_container_width=True)


def _grupos_pendentes_planejamento(concurso_id, disciplinas, termo):
    """Monta os grupos pendentes com a mesma regra da fila A–D."""
    estudos = pd.DataFrame(consulta("""SELECT e.id AS estudo_id, e.ordem, t.disciplina, t.assunto
                                      FROM estudos e JOIN topicos t ON t.id=e.topico_id
                                      WHERE t.concurso_id=? ORDER BY t.disciplina, e.ordem DESC""", (concurso_id,)))
    if estudos.empty:
        return []
    estudos = aplicar_filtros(estudos, disciplinas, termo)
    executados = pd.DataFrame(consulta("SELECT estudo_id, grupo FROM grupos_executados"))
    pendentes = []
    for disciplina, grupo_df in estudos.groupby("disciplina", sort=True):
        for indice, linha in enumerate(grupo_df.head(4).itertuples()):
            grupo = "ABCD"[indice]
            concluido = not executados.empty and ((executados["estudo_id"] == linha.estudo_id) & (executados["grupo"] == grupo)).any()
            if not concluido:
                pendentes.append({"id": f"grupo_{linha.estudo_id}_{grupo}", "tipo": "Revisão", "disciplina": disciplina, "assunto": linha.assunto,
                                  "grupo": f"Grupo {grupo}", "concluido": False})
    return pendentes


def _grupos_concluidos_planejamento(concurso_id, disciplinas, termo):
    """Inclui revisões feitas no calendário com uma marca de conclusão."""
    feitos = pd.DataFrame(consulta("""SELECT e.id AS estudo_id, t.disciplina, t.assunto, g.grupo, g.data
                                     FROM grupos_executados g JOIN estudos e ON e.id=g.estudo_id
                                     JOIN topicos t ON t.id=e.topico_id WHERE t.concurso_id=?""", (concurso_id,)))
    if feitos.empty:
        return []
    feitos = aplicar_filtros(feitos, disciplinas, termo)
    return [{"id": f"grupo_{item.estudo_id}_{item.grupo}", "tipo": "Revisão", "disciplina": item.disciplina, "assunto": item.assunto,
             "grupo": f"Grupo {item.grupo}", "concluido": True, "data_conclusao": item.data} for item in feitos.itertuples()]


def _montar_cronograma_completo(itens):
    """Alterna disciplinas, garantindo presença de todas no cronograma."""
    por_disciplina = {}
    for item in itens:
        por_disciplina.setdefault(item["disciplina"], []).append(item)
    resultado = []
    while any(por_disciplina.values()):
        for disciplina in sorted(por_disciplina):
            if por_disciplina[disciplina]:
                resultado.append(por_disciplina[disciplina].pop(0))
    return resultado


def _texto_da_prova(arquivo):
    """Extrai texto localmente de .txt ou PDF com texto selecionável."""
    if arquivo is None:
        return "", None
    if arquivo.name.lower().endswith(".txt"):
        return arquivo.getvalue().decode("utf-8", errors="replace"), None
    try:
        from pypdf import PdfReader
        leitor = PdfReader(arquivo)
        texto = "\n".join(pagina.extract_text() or "" for pagina in leitor.pages)
        return texto, None if texto.strip() else "Não foi possível extrair texto deste PDF. Se ele for escaneado, cole o texto da prova abaixo."
    except Exception as erro:
        return "", f"Não consegui ler este PDF: {erro}. Tente um PDF com texto selecionável ou cole o conteúdo abaixo."


def analisar_relevancia_prova(concurso_id):
    st.divider()
    st.subheader("Analisar incidência de uma prova")
    st.caption("Envie uma prova em PDF/TXT ou cole o texto. A análise é feita localmente e compara cada questão aos tópicos deste edital.")
    arquivo = st.file_uploader("Prova do concurso", type=["pdf", "txt"], key="arquivo_prova")
    texto_extraido, erro = _texto_da_prova(arquivo)
    if arquivo and texto_extraido:
        # Um widget com chave própria preserva o conteúdo anterior entre os
        # reruns. Atualizamos somente quando o usuário escolhe outro arquivo,
        # mantendo intactas eventuais correções manuais no texto extraído.
        assinatura = hashlib.sha256(arquivo.getvalue()).hexdigest()
        if st.session_state.get("arquivo_prova_assinatura") != assinatura:
            st.session_state["texto_prova"] = texto_extraido
            st.session_state["arquivo_prova_assinatura"] = assinatura
    if erro:
        st.warning(erro)
    if arquivo and texto_extraido:
        st.success(f"Texto extraído de “{arquivo.name}”. Revise-o se o PDF tiver tabelas, imagens ou questões em colunas.")
    nome_padrao = arquivo.name.rsplit(".", 1)[0] if arquivo else ""
    nome = st.text_input("Identificação da prova", value=nome_padrao, placeholder="Ex.: BACEN 2024 — Analista TI", key="nome_prova")
    texto = st.text_area("Texto da prova", height=220, placeholder="Cole aqui o enunciado das questões se não enviar um arquivo.", key="texto_prova")
    if st.button("Calcular relevância dos tópicos", type="primary", disabled=not texto.strip(), key="analisar_prova"):
        topicos = consulta("SELECT id, disciplina, assunto FROM topicos WHERE concurso_id=? ORDER BY disciplina, assunto", (concurso_id,))
        if not topicos:
            st.error("Cadastre os tópicos do edital antes de analisar uma prova.")
        else:
            resultado, total = analisar_prova(texto, topicos)
            salvar_analise_prova(concurso_id, nome, texto, total, resultado)
            st.session_state[f"analise_prova_{concurso_id}"] = resultado, total, nome or "Prova sem título"
            st.success("Análise concluída e salva neste concurso.")
    analise = st.session_state.get(f"analise_prova_{concurso_id}")
    if analise:
        resultado, total, nome_analise = analise
        tabela = pd.DataFrame(resultado).sort_values(["ocorrencias", "disciplina", "assunto"], ascending=[False, True, True])
        c1, c2, c3 = st.columns(3)
        c1.metric("Questões identificadas", total)
        c2.metric("Tópicos com incidência", int((tabela["ocorrencias"] > 0).sum()))
        c3.metric("Tópico mais recorrente", tabela.iloc[0]["assunto"] if not tabela.empty and tabela.iloc[0]["ocorrencias"] else "Sem correspondência")
        st.caption(f"Resultado da prova: {nome_analise}. “Alta” significa 15% ou mais das questões; “Média”, de 5% a 14,9%.")
        st.dataframe(tabela[["disciplina", "assunto", "ocorrencias", "percentual", "relevancia"]], use_container_width=True, hide_index=True,
                     column_config={"ocorrencias": st.column_config.NumberColumn("Ocorrências", format="%d questões"), "percentual": st.column_config.NumberColumn("Peso na prova", format="%.1f%%")})
        mais_relevantes = tabela[tabela["ocorrencias"] > 0].head(15)
        if not mais_relevantes.empty:
            figura = px.bar(mais_relevantes.sort_values("ocorrencias"), x="ocorrencias", y="assunto", color="disciplina", orientation="h", title="Tópicos mais recorrentes na prova")
            figura.update_layout(height=max(330, len(mais_relevantes) * 36), margin=dict(l=10, r=10, t=48, b=10))
            st.plotly_chart(figura, use_container_width=True)
        else:
            st.info("Nenhuma palavra-chave do edital foi encontrada. Confira se o texto contém os enunciados e se os tópicos estão bem detalhados.")


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
    analisar_relevancia_prova(concurso_id)


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
    aplicar_estilo_sidebar()
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
            options=["Home", "Planejamento", "Método dos 4 Grupos", "Registrar estudo", "Histórico", "Edital e tópicos", "Concursos"],
            icons=["house-door-fill", "pie-chart-fill", "layers-fill", "journal-plus", "clock-history", "book-fill", "briefcase-fill"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#0b1f33"},
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
    elif pagina == "Planejamento": planejamento(concurso_id, disciplinas, termo)
    elif pagina == "Método dos 4 Grupos": quatro_grupos(concurso_id, disciplinas, termo)
    elif pagina == "Registrar estudo": registros(concurso_id, disciplinas)
    elif pagina == "Histórico": historico(concurso_id, disciplinas, termo)
    elif pagina == "Edital e tópicos": edital(concurso_id, disciplinas, termo)
    else: concursos(concurso_id)
