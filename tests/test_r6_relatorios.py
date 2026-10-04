from datetime import datetime, timedelta, timezone


def dt(dias=0):
    return datetime(2026, 10, 1) + timedelta(days=dias)


def test_r6_relatorios(service):
    service.cadastrar_livro(
        "L1", "Livro Um", "Autor", 2026, "Tecnologia", 3
    )
    service.cadastrar_livro(
        "L2", "Livro Dois", "Autor", 2026, "Tecnologia", 2
    )

    service.cadastrar_aluno(
        "A1", "Aluno Um", "Engenharia de Software", "a1@email.com"
    )
    service.cadastrar_aluno(
        "A2", "Aluno Dois", "ADS", "a2@email.com"
    )

    e1 = service.emprestar_livro("L1", "A1", data_atual=dt())
    service.devolver_livro(e1["_id"], data_atual=dt(10))

    service.emprestar_livro("L1", "A2", data_atual=dt())
    service.emprestar_livro("L2", "A1", data_atual=dt())

    top = service.top_5_livros_mais_emprestados()
    por_curso = service.quantidade_emprestimos_por_curso()
    atrasados = service.alunos_com_emprestimos_atrasados(
        data_atual=dt(8)
    )
    total_multas = service.total_arrecadado_multas()

    assert top[0]["isbn"] == "L1"
    assert top[0]["total_emprestimos"] == 2

    cursos = {
        item["curso"]: item["quantidade_emprestimos"]
        for item in por_curso
    }
    assert cursos["Engenharia de Software"] == 2
    assert cursos["ADS"] == 1

    assert len(atrasados) == 2
    assert total_multas == 6.0
