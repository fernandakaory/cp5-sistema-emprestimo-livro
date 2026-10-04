import pytest

from src.exceptions import DadoInvalido


def test_r2_cadastrar_e_buscar_aluno(service):
    service.cadastrar_aluno(
        "RM100",
        "Maria",
        "ADS",
        "maria@email.com"
    )

    aluno = service.buscar_aluno_por_matricula("RM100")
    assert aluno["nome"] == "Maria"


def test_r2_email_deve_conter_arroba(service):
    with pytest.raises(DadoInvalido):
        service.cadastrar_aluno(
            "RM101",
            "Carlos",
            "ADS",
            "email-invalido"
        )
