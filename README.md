# Sistema de Empréstimo de Livros

Backend simples para gerenciamento de uma biblioteca universitária utilizando Python e MongoDB.

## Funcionalidades

O sistema atende aos requisitos R1 a R7:

- CRUD de livros;
- Cadastro e consulta de alunos;
- Busca de livros por título, autor e categoria;
- Controle de empréstimos;
- Limite de três empréstimos por aluno;
- Bloqueio de aluno com atraso;
- Prazo de sete dias;
- Controle atômico de estoque no MongoDB;
- Devolução com cálculo de multa;
- Relatórios usando Aggregation Pipeline;
- Menu simples no terminal.

## Estrutura

```text
cp5_sistema_emprestimo_livros/
├── docker-compose.yml
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── db.py
│   ├── service.py
│   └── exceptions.py
└── tests/
    ├── conftest.py
    ├── test_r1_livros.py
    ├── test_r2_alunos.py
    ├── test_r3_busca.py
    ├── test_r4_emprestimos.py
    ├── test_r5_devolucao.py
    └── test_r6_relatorios.py
```

## Camadas

### db.py

Responsável pela conexão com o MongoDB e pela criação dos índices únicos de ISBN e matrícula.

### service.py

Contém as regras de negócio da biblioteca. A camada de serviço é responsável por validar disponibilidade, limite de empréstimos, atrasos, multas e restrições de exclusão.

### main.py

Contém a interface de terminal e chama os métodos da camada de serviço.

### exceptions.py

Contém exceções específicas do domínio, deixando os erros de negócio mais claros.

## Decisões principais

### MongoDB

Foram utilizadas três coleções:

- `livros`
- `alunos`
- `emprestimos`

Os empréstimos armazenam ISBN e matrícula em vez de duplicar os dados completos do livro e do aluno. Quando um relatório precisa das informações relacionadas, é utilizado `$lookup`.

### Índices únicos

Foram criados índices únicos para:

- `livros.isbn`
- `alunos.matricula`

Dessa forma, a própria camada de banco impede registros duplicados.

### Controle de estoque

Ao realizar um empréstimo, o estoque é atualizado de forma atômica utilizando um filtro:

```python
{
    "isbn": isbn,
    "exemplares_disponiveis": {"$gt": 0}
}
```

junto de:

```python
{"$inc": {"exemplares_disponiveis": -1}}
```

Assim, duas solicitações simultâneas não conseguem reduzir o estoque para um valor negativo.

### Data parametrizável

Os métodos de empréstimo, devolução e relatório de atrasos aceitam `data_atual` como parâmetro.

Isso permite testar cenários de atraso sem precisar esperar vários dias.

### Multa

A multa é calculada no momento da devolução:

```text
multa = dias_de_atraso × R$ 2,00
```

## Como executar

### 1. Subir o MongoDB

É necessário ter o Docker Desktop instalado e em execução.

Na raiz do projeto, execute:

```bash
docker compose up -d
```

Para verificar se o container está ativo:

```bash
docker ps
```

O MongoDB ficará disponível em:

```text
mongodb://localhost:27017
```

### 2. Criar o ambiente virtual

Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar as dependências

Mac/Linux:

```bash
python3 -m pip install -r requirements.txt
```

Windows:

```bash
python -m pip install -r requirements.txt
```

### 4. Executar o sistema

Como o código-fonte está dentro da pasta `src`, o sistema deve ser executado a partir da raiz do projeto.

Mac/Linux:

```bash
python3 -m src.main
```

Windows:

```bash
python -m src.main
```

## Executar os testes

Mac/Linux:

```bash
python3 -m pytest -v
```

Windows:

```bash
python -m pytest -v
```

Os testes utilizam `mongomock`, portanto não dependem do MongoDB do Docker para serem executados.

Há pelo menos um teste relacionado a cada requisito de R1 a R6.

## Exemplos de erros de negócio

O sistema possui exceções específicas como:

- `LivroIndisponivel`
- `LimiteEmprestimos`
- `AlunoComAtraso`
- `EmprestimoJaDevolvido`
- `LivroComEmprestimoAberto`
- `LivroNaoEncontrado`
- `AlunoNaoEncontrado`

Isso separa erros esperados da regra de negócio de erros técnicos inesperados.

## Membros do Grupo

| Nome | RM |
|---|---|
| 🍙 Fernanda Kaory Saito | RM551104 |
| ⚡ João Pedro Borsato Cruz | RM550294 |
| 💫 Maria Fernanda Vieira de Camargo | RM97956 |
| 🚀 Pedro Lucas de Andrade Nunes | RM550366 |
| 💥 Vinícius Bernardino de Souza | RM97888 |