from datetime import datetime, timedelta, timezone

import pytest

from src.exceptions import EmprestimoJaDevolvido


def dt(dias=0):
    return datetime(2026, 10, 1, tzinfo=timezone.utc) + timedelta(days=dias)


def test_r5_devolucao_com_multa(service, livro_padrao, aluno_padrao):
    emprestimo = service.emprestar_livro(
        "9780000000001",
        "RM001",
        data_atual=dt()
    )

    devolvido = service.devolver_livro(
        emprestimo["_id"],
        data_atual=dt(10)
    )

    livro = service.buscar_livro_por_isbn("9780000000001")

    assert devolvido["multa"] == 6.0
    assert livro["exemplares_disponiveis"] == 2


def test_r5_nao_pode_devolver_duas_vezes(
    service, livro_padrao, aluno_padrao
):
    emprestimo = service.emprestar_livro(
        "9780000000001",
        "RM001",
        data_atual=dt()
    )

    service.devolver_livro(emprestimo["_id"], data_atual=dt(1))

    with pytest.raises(EmprestimoJaDevolvido):
        service.devolver_livro(emprestimo["_id"], data_atual=dt(2))
