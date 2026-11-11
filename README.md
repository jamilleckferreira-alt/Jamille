# Sistema de gestão da festa do IFC Campus Blumenau

Este projeto é uma aplicação web em Streamlit para organizar a festa do IFC Campus Blumenau. O sistema permite cadastrar os alimentos que serão vendidos, os fornecedores dos insumos doados, as pessoas que vão atuar na festa (alunos, pais de alunos e servidores) e controlar os preços de venda.

## Funcionalidades

- CRUD completo para alimentos
- CRUD completo para fornecedores
- CRUD completo para insumos doados
- CRUD completo para pessoas envolvidas na festa
- Configuração de conexão com SQLite para ambiente local e MySQL para produção
- Interface em Streamlit para uso simples e rápida

## Tecnologias utilizadas

- Streamlit
- SQLAlchemy
- SQLite
- MySQL + PyMySQL
- Python-dotenv
- uv

## Requisitos

- Python 3.12+
- uv

## Como executar

1. Clone o repositório.
2. Entre na pasta do projeto.
3. Instale as dependências:

```bash
uv sync
```

4. Crie um arquivo `.env` com as variáveis do MySQL, ou copie o exemplo:

```bash
cp .env.example .env
```

5. Inicie a aplicação:

```bash
uv run streamlit run src/app.py
```

## Configuração do banco de dados

- Local/testes: a aplicação usa SQLite automaticamente quando nenhum valor do MySQL estiver configurado.
- Produção: a aplicação usa MySQL quando as variáveis `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD` e `MYSQL_DATABASE` estiverem definidas.

Exemplo de `.env`:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=festival_user
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=festival_ifc
MYSQL_SSL_CA=isrgrootx1.pem
STREAMLIT_ENV=production
```

`MYSQL_SSL_CA` aponta para o certificado CA em formato PEM usado para validar o certificado TLS do servidor MySQL. O caminho relativo é resolvido a partir da raiz do projeto. O arquivo `isrgrootx1.pem` está na raiz deste projeto; inclua-o no repositório para que também esteja disponível no deploy. Se o provedor do banco fornecer outro CA, use o arquivo indicado por ele.

No Streamlit Community Cloud, inclua o certificado CA no repositório e configure `MYSQL_SSL_CA` em **App settings > Secrets**, por exemplo:

```toml
MYSQL_SSL_CA = "isrgrootx1.pem"
```

Certificados CA públicos podem ser versionados. Nunca versione chaves privadas ou certificados de cliente que contenham material privado.

## Observação sobre deploy

O projeto foi pensado para funcionar no Streamlit Cloud. Quando implantado, o ambiente de produção deve receber as variáveis de ambiente do MySQL para que a aplicação conecte corretamente ao banco em nuvem.
