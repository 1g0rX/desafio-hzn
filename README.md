BPA Ventures | Deal Flow Automation

Sistema desenvolvido para automatizar a triagem e análise de oportunidades da BPA Ventures. A ferramenta processa documentos de proponentes usando o modelo Gemini 3.1 para identificar se uma ideia tem fit com a tese da empresa, poupando tempo na análise manual.

O que o sistema faz
- Processamento de Arquivos: Extrai texto de PDFs e DOCXs enviados por empreendedores.
- Triagem via LLM: Usa o Gemini 3.1 Flash Lite para ler a proposta e extrair Score, Veredito (Avançar/Passar), Pontos Críticos (Red Flags) e Custo de Oportunidade.
- Painel de Gestão: Interface para busca por ID onde o avaliador revisa os dados da IA e decide o status final.
- Fluxo de Notificações: Envio de e-mails via SMTP para alertar a equipe sobre novos leads e informar o proponente sobre o resultado da avaliação.
- Logs de Auditoria: Salva as respostas brutas da IA em historico_ia.txt para conferência técnica e ajuste de prompt.

Decisões de Arquitetura
A escolha da stack priorizou simplicidade de manutenção e baixo overhead:
- Frontend (Vanilla JS + Tailwind): Optamos por não usar frameworks (React/Vue) para manter a aplicação extremamente leve e sem necessidade de build. O JavaScript puro é suficiente para o consumo das rotas da API e manipulação do DOM.
- Backend (FastAPI): Escolhido pela alta performance e suporte nativo a operações assíncronas, o que evita gargalos durante o processamento de arquivos e chamadas de API externas.
- Persistência (SQLite + SQLAlchemy): O SQLite foi escolhido pela portabilidade. O uso de SQLAlchemy permite escalar para um banco mais robusto (Postgres) apenas trocando a string de conexão.
- IA (Gemini 3.1 Flash Lite): Modelo selecionado pelo equilíbrio entre latência e precisão na extração de campos estruturados.

Estrutura do Repositório
.
├── backend/                # Lógica do servidor e IA
│   ├── main.py             # Rotas e orquestração
│   ├── services.py         # Integrações (IA e E-mail)
│   ├── models.py           # Tabelas do banco
│   ├── database.py         # Conexão e sessão
│   ├── schemas.py          # Validação Pydantic
│   ├── prompt.txt          # Prompt de sistema
│   └── requirements.txt    # Dependências
├── frontend/               # Interface web (estática)
│   ├── index.html          # Submissão
│   ├── login.html          # Acesso avaliador
│   └── dashboard.html      # Painel principal
├── README.md               # Documentação do projeto
└── uploads/                # Armazenamento temporário de documentos

Como rodar o projeto
Backend
1. Entre na pasta do servidor:
   cd backend
2. Crie e ative o ambiente virtual:
   # Windows
   python -m venv venv
   venv\Scripts\activate
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
3. Instale os pacotes:
   pip install -r requirements.txt
4. Configure o arquivo .env seguindo o .env.example:
   AI_API_KEY="SUA_CHAVE_AQUI"
   EMAIL_SENDER="email_que_envia@gmail.com"
   EMAIL_PASSWORD="senha_de_app"
   EVALUATOR_REAL_EMAIL="seu_email@pessoal.com"
5. Suba o servidor:
   uvicorn main:app --reload

Frontend
Abra a pasta frontend no seu editor e utilize o Live Server (ou similar) no arquivo index.html. O frontend deve rodar na porta 5500 para que os links de redirecionamento funcionem corretamente.
Nota: Também é possível abrir o arquivo index.html manualmente clicando duas vezes sobre ele no seu gerenciador de arquivos, mas o uso de um servidor local (Live Server) é recomendado para evitar problemas de caminhos relativos ao navegar entre as páginas.

Segurança e Auditoria
- O texto da tese de investimento fica no servidor (prompt.txt) e nunca é exposto ao cliente.
- Nenhuma chave de API ou senha está no código; tudo é lido via variáveis de ambiente.
- O arquivo historico_ia.txt serve para depuração e conferência do raciocínio do modelo, garantindo que a tese esteja sendo aplicada corretamente.