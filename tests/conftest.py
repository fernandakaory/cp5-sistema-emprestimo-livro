import pytest
import mongomock

from src.service import BibliotecaService


@pytest.fixture
def db():
    client = mongomock.MongoClient()
    database = client["biblioteca_teste"]

    database.livros.create_index("isbn", unique=True)
    database.alunos.create_index("matricula", unique=True)

    return database


@pytest.fixture
def service(db):
    return BibliotecaService(db)


@pytest.fixture
def livro_padrao(service):
    return service.cadastrar_livro(
        isbn="9780000000001",
        titulo="MongoDB na Prática",
        autor="Ana Silva",
        ano=2025,
        categoria="Tecnologia",
        exemplares_total=2
    )


@pytest.fixture
def aluno_padrao(service):
    return service.cadastrar_aluno(
        matricula="RM001",
        nome="João Souza",
        curso="Engenharia de Software",
        email="joao@email.com"
    )
