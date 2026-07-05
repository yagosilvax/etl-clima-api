# ETL Clima — SP x RJ (Open-Meteo)
 
Pipeline de ETL em Python que extrai dados históricos de clima da API pública [Open-Meteo](https://open-meteo.com/), trata e padroniza os dados, e carrega em um banco de dados PostgreSQL para posterior análise em dashboard.
 
Projeto desenvolvido como exercício prático de Engenharia de Dados, com foco em lidar com dados reais de API (estrutura aninhada, múltiplas fontes, tratamento de erro) e trabalhar com arquivos em formato JSON em vez de datasets já limpos.
 
## Objetivo do projeto:
 
Construir um pipeline de ETL completo e robusto, não apenas um script de extração, cobrindo:
- Extração de dados via API REST
- Transformação de JSON aninhado em formato tabular
- Carga incremental em um data warehouse(PostgreSQL)
- Boas práticas de engenharia (variáveis de ambiente, controle de versão, tratamento de erro)
## Arquitetura do pipeline:
 
```
Open-Meteo API  →  Extract (get_data)  →  Transform (transform_data)  →  Load (load_db)  →  PostgreSQL
```
 
- **Extract:** requisição HTTP para a API, com múltiplas coordenadas (São Paulo e Rio de Janeiro) em uma única chamada, salvando um backup local em JSON.
- **Transform:** parseamento da resposta (lista de objetos, um por cidade), criação de colunas derivadas (`estado`, `hora`) e conversão de tipos (datetime).
- **Load:** conexão configurável via variáveis de ambiente, carga incremental no banco PostgreSQL.
## Dados coletados
 
| Coluna | Descrição |
|---|---|
| `date_time` | Data e hora da medição |
| `hora` | Hora extraída de `date_time` (0-23) |
| `temperature` | Temperatura do ar a 2m (°C) |
| `apparent_temp` | Sensação térmica (°C) |
| `umidity` | Umidade relativa do ar (%) |
| `precipitation` | Precipitação acumulada (mm) |
| `estado` | Estado de referência (SP ou RJ) |
 
## Stack Tech:
 
- **Python 3**
- **Pandas** — transformação e estruturação dos dados
- **Requests** — consumo da API
- **SQLAlchemy** — conexão e carga no banco
- **PostgreSQL** — armazenamento
- **python-dotenv** — gerenciamento de credenciais via variáveis de ambiente
## Estrutura do projeto:
 
```
ETL-clima/
├── src/
│   └── etl_clima.py       # Script principal do pipeline (extract, transform, load)
├── config.env              # Variáveis de ambiente (não versionado)
├── .gitignore
└── README.md
```
 
## Como executar:
 
1. Clone o repositório:
```bash
git clone https://github.com/SEU-USUARIO/etl-clima-api.git
cd etl-clima
```
 
2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
```
 
3. Instale as dependências:
```bash
pip install pandas requests sqlalchemy psycopg2-binary python-dotenv
```
 
4. Crie um arquivo `config.env` na raiz do projeto com suas credenciais de banco:
```env
host=127.0.0.1
database=postgres
usuario=postgres
port=5432
senha_banco=sua_senha
```
 
5. Execute o pipeline:
```bash
python src/etl_clima.py
```
 
## Desafios técnicos resolvidos
 
Durante o desenvolvimento, alguns problemas reais de engenharia de dados foram enfrentados e resolvidos:
 
- **Estrutura de API com múltiplas localizações:** a API retorna uma lista de objetos (um por coordenada), sem identificar explicitamente a cidade — foi necessário mapear os dados manualmente à ordem dos parâmetros enviados.
- **Dados de previsão misturados com histórico:** ajuste dos parâmetros `past_days` e `forecast_days` para garantir apenas dados históricos reais, sem previsão futura.
- **Evolução de schema no banco:** ao adicionar novas colunas ao pipeline, foi necessário lidar com o desalinhamento entre o schema já existente na tabela e o novo formato dos dados.
- **Gerenciamento seguro de credenciais:** uso de variáveis de ambiente (`.env`) para nunca expor senha e host do banco no código versionado.
## Próximos passos do pipeline:
 
- [ ] Automatizar execução diária por meio de uma ferramenta de orquestração
- [ ] Adicionar logging estruturado (substituir `print` por `logging`)
- [ ] Construir dashboard de visualização no Power BI

