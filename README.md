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
STREAMLIT_ENV=production
```

## Observação sobre deploy

O projeto foi pensado para funcionar no Streamlit Cloud. Quando implantado, o ambiente de produção deve receber as variáveis de ambiente do MySQL para que a aplicação conecte corretamente ao banco em nuvem.
