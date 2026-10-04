import pytest

from src.exceptions import DadoInvalido, LivroComEmprestimoAberto


def test_r1_crud_livro(service, livro_padrao):
    encontrado = service.buscar_livro_por_isbn("9780000000001")
    assert encontrado["titulo"] == "MongoDB na Prática"

    atualizado = service.atualizar_livro(
        "9780000000001",
        {"titulo": "MongoDB Avançado"}
    )
    assert atualizado["titulo"] == "MongoDB Avançado"

    service.remover_livro("9780000000001")
    assert service.livros.find_one({"isbn": "9780000000001"}) is None


def test_r1_isbn_unico(service, livro_padrao):
    with pytest.raises(DadoInvalido):
        service.cadastrar_livro(
            isbn="9780000000001",
            titulo="Outro livro",
            autor="Autor",
            ano=2024,
            categoria="Tecnologia",
            exemplares_total=1
        )


def test_r1_nao_remove_livro_com_emprestimo_aberto(
    service, livro_padrao, aluno_padrao
):
    service.emprestar_livro("9780000000001", "RM001")

    with pytest.raises(LivroComEmprestimoAberto):
        service.remover_livro("9780000000001")
