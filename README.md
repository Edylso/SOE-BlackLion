# SOE-BlackLion

Aplicativo local para organizar estudos de concursos. Ele inclui dashboard, controle do Método dos 4 Grupos, registro de questões, múltiplos concursos e criação de tópicos a partir de conteúdo de edital colado.

Os dados de estudo são locais: o banco SQLite é criado em `data/soe_bacen.db` e não é enviado para serviços externos.

## Pré-requisitos

- [Python 3.11 ou superior](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads/)

Verifique a instalação:

```bash
python --version
git --version
```

No macOS/Linux, caso `python` não exista, use `python3` nos comandos abaixo.

## Instalação

Clone o repositório e entre na pasta do projeto:

```bash
git clone https://github.com/Edylso/SOE-BlackLion.git
cd SOE-BlackLion
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
streamlit run main.py
```

Se o PowerShell bloquear a ativação do ambiente, execute uma vez, apenas na janela atual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### macOS e Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run main.py
```

Abra o endereço exibido pelo Streamlit, normalmente [http://localhost:8501](http://localhost:8501).

Para encerrar o aplicativo, pressione `Ctrl+C` no terminal.

## Primeiro acesso

Credenciais iniciais:

- Usuário: `admin`
- Senha: `bacen2024`

Antes de disponibilizar o app para outras pessoas, defina suas próprias credenciais.

No Windows (PowerShell):

```powershell
$env:SOE_USUARIO="seu_usuario"
$env:SOE_SENHA="uma_senha_forte"
streamlit run main.py
```

No macOS/Linux:

```bash
export SOE_USUARIO="seu_usuario"
export SOE_SENHA="uma_senha_forte"
streamlit run main.py
```

## Fluxo de uso

1. Escolha ou crie um concurso em **Concursos**.
2. Cole o conteúdo do edital para receber tópicos sugeridos e revise-os antes da importação.
3. Registre a conclusão de cada aula/unidade no **Método dos 4 Grupos**, informando a quantidade total de questões.
4. Registre grupos, sessões e questões resolvidas.
5. Acompanhe o progresso na **Home**.

No Método dos 4 Grupos, a aula atual usa o Grupo A e as três anteriores usam B, C e D. As questões são distribuídas intercaladamente: A = 1, 5, 9…; B = 2, 6, 10…; e assim por diante.

## Excel opcional

Para gerar a versão em Excel:

```bash
python gerar_excel.py
```

O arquivo é criado em `output/SOE_BlackLion.xlsx`.

## Publicar suas alterações no GitHub

O `.gitignore` já protege o banco local, as planilhas geradas, caches e segredos. Portanto, seus registros de estudo não são enviados por padrão.

Configure sua identidade Git uma única vez:

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

Depois de alterar o projeto:

```bash
git status
git add .
git commit -m "descreva sua alteração"
git push
```

Para publicar uma cópia em um novo repositório GitHub, crie um repositório vazio no GitHub e execute:

```bash
git remote add origin https://github.com/SEU_USUARIO/NOVO_REPOSITORIO.git
git branch -M main
git push -u origin main
```

Se já existir um remoto `origin`, atualize-o com:

```bash
git remote set-url origin https://github.com/SEU_USUARIO/NOVO_REPOSITORIO.git
```

## Recursos

- Home com dashboard e gráficos interativos.
- Busca, filtros e exclusão em lote de tópicos.
- Método dos 4 Grupos orientado pela sequência de aulas.
- Registro de sessões de estudo e banco de questões.
- Múltiplos concursos, cada um com seu próprio edital e histórico.
- Reinicialização ou exclusão de concurso com confirmação.
