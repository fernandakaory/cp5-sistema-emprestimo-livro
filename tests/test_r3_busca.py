def test_r3_busca_parcial_case_insensitive_e_categoria(service):
    service.cadastrar_livro(
        "1", "Python para Dados", "Ana Silva", 2024, "Tecnologia", 1
    )
    service.cadastrar_livro(
        "2", "MongoDB Essencial", "Carlos Lima", 2024, "Tecnologia", 1
    )
    service.cadastrar_livro(
        "3", "História do Brasil", "Ana Costa", 2020, "História", 1
    )

    resultados = service.buscar_livros(
        texto="ana",
        categoria="Tecnologia"
    )

    assert len(resultados) == 1
    assert resultados[0]["titulo"] == "Python para Dados"
