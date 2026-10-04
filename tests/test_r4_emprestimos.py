from datetime import datetime, timedelta, timezone

import pytest

from src.exceptions import LivroIndisponivel, LimiteEmprestimos, AlunoComAtraso


def dt(dias=0):
    return datetime(2026, 10, 1, tzinfo=timezone.utc) + timedelta(days=dias)


def test_r4_emprestimo_reduz_estoque(service, livro_padrao, aluno_padrao):
    emprestimo = service.emprestar_livro(
        "9780000000001",
        "RM001",
        data_atual=dt()
    )

    livro = service.buscar_livro_por_isbn("9780000000001")

    assert emprestimo["data_prevista"].replace(tzinfo=timezone.utc) == dt(7)
    assert livro["exemplares_disponiveis"] == 1


def test_r4_nao_empresta_sem_estoque(service, aluno_padrao):
    service.cadastrar_livro(
        "SEMESTOQUE",
        "Livro único",
        "Autor",
        2026,
        "Teste",
        0
    )

    with pytest.raises(LivroIndisponivel):
        service.emprestar_livro("SEMESTOQUE", "RM001", data_atual=dt())


def test_r4_limite_tres_emprestimos(service, aluno_padrao):
    for i in range(4):
        service.cadastrar_livro(
            f"ISBN{i}",
            f"Livro {i}",
            "Autor",
            2026,
            "Teste",
            1
        )

    for i in range(3):
        service.emprestar_livro(
            f"ISBN{i}",
            "RM001",
            data_atual=dt()
        )

    with pytest.raises(LimiteEmprestimos):
        service.emprestar_livro(
            "ISBN3",
            "RM001",
            data_atual=dt()
        )


def test_r4_aluno_com_atraso_nao_pode_emprestar(service, aluno_padrao):
    service.cadastrar_livro("A", "Livro A", "Autor", 2026, "Teste", 1)
    service.cadastrar_livro("B", "Livro B", "Autor", 2026, "Teste", 1)

    service.emprestar_livro("A", "RM001", data_atual=dt())

    with pytest.raises(AlunoComAtraso):
        service.emprestar_livro(
            "B",
            "RM001",
            data_atual=dt(8)
        )
