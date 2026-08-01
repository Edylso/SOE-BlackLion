# SOE-BlackLion

Aplicativo local para organizar os estudos do concurso de Analista — Área: Tecnologia da Informação do Banco Central.

## Como executar

```bash
python3 -m pip install -r requirements.txt
streamlit run main.py
```

Abra o endereço exibido pelo Streamlit, normalmente `http://localhost:8501`.

Credenciais iniciais: `admin` / `bacen2024`.

Antes de publicar o aplicativo, defina variáveis de ambiente para substituir essas credenciais:

```bash
export SOE_USUARIO="seu_usuario"
export SOE_SENHA="uma_senha_forte"
```

Os dados ficam somente neste computador, no arquivo `data/soe_bacen.db`. O banco é criado automaticamente com os 70 tópicos do edital do BACEN já estruturados.

Para continuar gerando a versão Excel, execute `python3 gerar_excel.py`.

## Recursos

- Dashboard com métricas e gráficos interativos.
- Busca e filtro por disciplina/assunto.
- Método dos 4 Grupos por sequência de aulas: a atual recebe A e as três anteriores recebem B, C e D; as questões são distribuídas intercaladamente (1, 5, 9…; 2, 6, 10…). Português é controlado por prova Cebraspe completa, não por assunto gramatical.
- Registro de sessões de estudo e banco de questões.
- Login local.
- Vários concursos, cada qual com seu próprio edital e histórico.
- Reinicialização segura: apaga registros de estudo do concurso ativo e preserva seu edital.
- Geração local de tópicos a partir do conteúdo do edital colado, com revisão manual antes da importação; nenhum dado é enviado a serviço externo.
