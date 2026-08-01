"""Configurações e catálogos usados pelo gerador SOE-BlackLion."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
ARQUIVO_SAIDA = OUTPUT_DIR / "SOE_BlackLion.xlsx"
DATA_DIR = BASE_DIR / "data"
BANCO_DADOS = DATA_DIR / "soe_bacen.db"
CONCURSO_PADRAO = "BACEN 2024 — Analista TI"

HORAS_DIA = 2
DIAS_SEMANA = 7
SEMANAS = 48
META_QUESTOES_SEMANAL = 140
META_QUESTOES_MENSAL = 560
CONCURSO = "Banco Central do Brasil — Tecnologia da Informação"
BANCA = "CEBRASPE"

CORES = {
    "primaria": "1F4E79", "secundaria": "D9EAD3", "destaque": "2F75B5",
    "fundo": "F4F7FA", "texto": "1F2937", "alerta": "FCE4D6",
    "sucesso": "E2F0D9", "cinza": "D9E1F2", "branco": "FFFFFF",
}

DISCIPLINAS = [
    ("Língua Portuguesa", "Média", "Provas Cebraspe"),
    ("Noções de Lógica e Estatística", "Alta", "Teoria + questões"),
    ("Direito Administrativo", "Baixa", "Flashcards + questões"),
    ("Fundamentos de Microeconomia", "Alta", "Teoria + questões"),
    ("Fundamentos de Macroeconomia", "Alta", "Teoria + questões"),
    ("Ciência de Dados", "Baixa", "Anki + questões"),
    ("Segurança da Informação", "Baixa", "Anki + questões"),
    ("Engenharia de Software", "Baixa", "Anki + questões"),
    ("Infraestrutura em TI", "Baixa", "Anki + questões"),
    ("Bancos de Dados", "Baixa", "Anki + questões"),
    ("Gestão em TI", "Baixa", "Anki + questões"),
]

# Tópicos dos conhecimentos básicos e específicos do Cargo 2 — Tecnologia da
# Informação, item 18.2.1 do Edital nº 1/2024 do BCB (versão retificada).
# Cada tupla cria um item independente de domínio e quatro revisões (A–D).
TOPICOS_EDITAL = [
    ("Língua Portuguesa", "Prova Cebraspe completa"),
    ("Noções de Lógica e Estatística", "Estruturas lógicas e lógica de argumentação"),
    ("Noções de Lógica e Estatística", "Lógica proposicional: proposições, tabelas-verdade, equivalências e Leis de Morgan"),
    ("Noções de Lógica e Estatística", "População, amostra, histogramas e curvas de frequência"),
    ("Noções de Lógica e Estatística", "Medidas de posição e dispersão"),
    ("Noções de Lógica e Estatística", "Probabilidade condicional e independência"),
    ("Noções de Lógica e Estatística", "Variável aleatória e funções de distribuição"),
    ("Direito Administrativo", "Princípios; administração direta e indireta"),
    ("Direito Administrativo", "Poderes administrativos; uso e abuso do poder"),
    ("Direito Administrativo", "Organização administrativa e serviços públicos"),
    ("Direito Administrativo", "Entidades administrativas: autarquias, agências, fundações e empresas estatais"),
    ("Direito Administrativo", "Ato administrativo: requisitos, atributos, comunicação, anulação, revogação e convalidação"),
    ("Direito Administrativo", "Discricionariedade e vinculação"),
    ("Direito Administrativo", "Servidores públicos e Lei nº 8.112/1990"),
    ("Direito Administrativo", "Improbidade, ética e conduta da alta administração"),
    ("Direito Administrativo", "Conflito de interesses, LAI e LGPD"),
    ("Fundamentos de Macroeconomia", "Contas nacionais"), ("Fundamentos de Macroeconomia", "Agregados monetários"),
    ("Fundamentos de Macroeconomia", "Multiplicador monetário; criação e destruição de moeda"),
    ("Fundamentos de Macroeconomia", "Contas do sistema monetário"), ("Fundamentos de Macroeconomia", "Balanço de pagamentos"),
    ("Fundamentos de Microeconomia", "Estruturas de mercado; preços, custo de oportunidade e FPP"),
    ("Fundamentos de Microeconomia", "Oferta e demanda"), ("Fundamentos de Microeconomia", "Curvas de indiferença e restrição orçamentária"),
    ("Fundamentos de Microeconomia", "Equilíbrio do consumidor; efeitos preço, renda e substituição"),
    ("Fundamentos de Microeconomia", "Curva e elasticidade da demanda"),
    ("Ciência de Dados", "Aprendizado de máquina"), ("Ciência de Dados", "Deep learning e redes neurais"),
    ("Ciência de Dados", "Processamento de linguagem natural"), ("Ciência de Dados", "Big data e qualidade de dados"),
    ("Ciência de Dados", "Aprendizado supervisionado, não supervisionado, semissupervisionado, por reforço e por transferência"),
    ("Ciência de Dados", "LLM e IA generativa"), ("Ciência de Dados", "MLOps"),
    ("Ciência de Dados", "Governança e ética em IA"),
    ("Segurança da Informação", "Gestão de identidades e acesso: autenticação, autorização, SSO, SAML, OAuth2 e OpenID Connect"),
    ("Segurança da Informação", "Privacidade e segurança por padrão; ataques e vulnerabilidades"),
    ("Segurança da Informação", "Controles e testes de segurança para aplicações web e web services; MFA"),
    ("Segurança da Informação", "Soluções: firewall, IDS/IPS, SIEM, proxy, IAM/PAM, antivírus e antispam"),
    ("Segurança da Informação", "MITRE ATT&CK, CIS Controls e NIST CSF"),
    ("Segurança da Informação", "Tratamento de incidentes cibernéticos"),
    ("Segurança da Informação", "Assinatura, certificação, criptografia e proteção de dados"),
    ("Segurança da Informação", "Segurança em nuvens e contêineres"),
    ("Engenharia de Software", "Arquitetura web: HTTP, HTTP/2, gRPC, WebSockets, TLS, proxy, cache e DNS"),
    ("Engenharia de Software", "Balanceamento, tolerância a falhas e escalabilidade em sistemas web"),
    ("Engenharia de Software", "DevOps, DevSecOps e CI/CD"), ("Engenharia de Software", "Desenvolvimento seguro"),
    ("Engenharia de Software", "Testes: unitários, integração, TDD e BDD"),
    ("Engenharia de Software", "Arquiteturas: camadas, serviços, microsserviços, eventos, cliente-servidor e serverless"),
    ("Engenharia de Software", "UX e UI design; programação assíncrona"),
    ("Engenharia de Software", "RESTful, GraphQL e web services"), ("Engenharia de Software", "Padrões GoF e GRASP; Git"),
    ("Engenharia de Software", "Python e Java"), ("Engenharia de Software", "Transações distribuídas e DLT"),
    ("Infraestrutura em TI", "Infraestrutura como código e automação"), ("Infraestrutura em TI", "Docker e Kubernetes"),
    ("Infraestrutura em TI", "Windows Server: DNS, DHCP, Radius, autenticação, certificados e Active Directory"),
    ("Infraestrutura em TI", "Monitoramento, observabilidade, logging, Nagios, Prometheus, Grafana, ELK e APM"),
    ("Infraestrutura em TI", "Protocolos SMTP, HTTP/HTTPS, SSL/TLS, LDAP, NFS e SMB"),
    ("Infraestrutura em TI", "Tolerância a falhas e continuidade de operação"),
    ("Infraestrutura em TI", "Nuvem: IaaS, PaaS e SaaS; virtualização"),
    ("Infraestrutura em TI", "Windows Server e Linux; LAN, WAN e SDN"),
    ("Infraestrutura em TI", "Puppet e Ansible"),
    ("Bancos de Dados", "SGBDs SQL e NoSQL"), ("Bancos de Dados", "Modelagem relacional, multidimensional e NoSQL"),
    ("Bancos de Dados", "SQL / Procedural Language"), ("Bancos de Dados", "BI: Data Warehouse, Data Mart, Data Lake e Data Mesh"),
    ("Gestão em TI", "Kanban"), ("Gestão em TI", "Scrum"), ("Gestão em TI", "Governança de Dados"), ("Gestão em TI", "ITIL v4"),
]

STATUS = ["Não iniciado", "Em andamento", "Revisar", "Consolidado"]
GRUPOS = ["A", "B", "C", "D", "Consolidado"]
