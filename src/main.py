from pprint import pprint

from src.db import get_db
from src.service import BibliotecaService
from src.exceptions import BibliotecaError
from datetime import datetime, timezone


def mostrar_menu():
    print("""
================ BIBLIOTECA ================

1  - Cadastrar livro
2  - Buscar livro por ISBN
3  - Listar livros
4  - Atualizar livro
5  - Remover livro

6  - Cadastrar aluno
7  - Buscar aluno por matrícula

8  - Buscar livros por título/autor/categoria

9  - Emprestar livro
10 - Devolver livro
11 - Listar todos os empréstimos

12 - Top 5 livros mais emprestados
13 - Empréstimos por curso
14 - Alunos com empréstimos atrasados
15 - Total arrecadado em multas

0  - Sair
""")

def solicitar_data(mensagem):
    valor = input(mensagem).strip()

    if not valor:
        return None

    try:
        data = datetime.strptime(valor, "%d/%m/%Y")
        return data.replace(tzinfo=timezone.utc)
    except ValueError:
        raise ValueError("Data inválida. Use o formato DD/MM/AAAA.")
    
def main():
    db = get_db()
    service = BibliotecaService(db)

    while True:
        mostrar_menu()
        opcao = input("Escolha uma opção: ").strip()
        print()

        try:
            if opcao == "1":
                livro = service.cadastrar_livro(
                    isbn=input("ISBN: "),
                    titulo=input("Título: "),
                    autor=input("Autor: "),
                    ano=int(input("Ano: ")),
                    categoria=input("Categoria: "),
                    exemplares_total=int(input("Quantidade de exemplares: "))
                )
                print()
                pprint(livro)
                print()
                print("Livro cadastrado com sucesso.")

            elif opcao == "2":
                pprint(service.buscar_livro_por_isbn(input("ISBN: ")))
                print()

            elif opcao == "3":
                for livro in service.listar_livros():
                    pprint(livro)
                    print()

            elif opcao == "4":
                isbn = input("ISBN: ")
                print("Informe apenas os campos que deseja alterar.")
                titulo = input("Novo título (ENTER para manter): ").strip()
                autor = input("Novo autor (ENTER para manter): ").strip()
                categoria = input("Nova categoria (ENTER para manter): ").strip()
                ano = input("Novo ano (ENTER para manter): ").strip()
                total = input("Novo total de exemplares (ENTER para manter): ").strip()

                dados = {}
                if titulo:
                    dados["titulo"] = titulo
                if autor:
                    dados["autor"] = autor
                if categoria:
                    dados["categoria"] = categoria
                if ano:
                    dados["ano"] = int(ano)
                if total:
                    dados["exemplares_total"] = int(total)

                pprint(service.atualizar_livro(isbn, dados))
                print()
                print("Livro atualizado com sucesso.")

            elif opcao == "5":
                service.remover_livro(input("ISBN: "))
                print("Livro removido com sucesso.")

            elif opcao == "6":
                aluno = service.cadastrar_aluno(
                    matricula=input("Matrícula: "),
                    nome=input("Nome: "),
                    curso=input("Curso: "),
                    email=input("E-mail: ")
                )
                pprint(aluno)
                print()
                print("Aluno cadastrado com sucesso.")

            elif opcao == "7":
                pprint(
                    service.buscar_aluno_por_matricula(
                        input("Matrícula: ")
                    )
                )

            elif opcao == "8":
                texto = input(
                    "Parte do título/autor (ENTER para ignorar): "
                ).strip()
                categoria = input(
                    "Categoria (ENTER para ignorar): "
                ).strip()

                resultados = service.buscar_livros(
                    texto=texto or None,
                    categoria=categoria or None
                )

                for livro in resultados:
                    pprint(livro)
                    print()

            elif opcao == "9":
                isbn = input("ISBN: ")
                matricula = input("Matrícula: ")

                data = solicitar_data(
                    "Data do empréstimo (DD/MM/AAAA ou ENTER para hoje): "
                )

                emprestimo = service.emprestar_livro(
                    isbn=isbn,
                    matricula=matricula,
                    data_atual=data
                )

                print()
                pprint(emprestimo)
                print()
                print("Empréstimo realizado com sucesso.")

            elif opcao == "10":
                emprestimo_id = input("ID do empréstimo: ")

                data = solicitar_data(
                    "Data da devolução (DD/MM/AAAA ou ENTER para hoje): "
                )

                pprint(
                    service.devolver_livro(
                        emprestimo_id,
                        data_atual=data
                    )
                )
                print()
                print("Devolução realizada com sucesso.")

            elif opcao == "11":
                emprestimos = service.listar_emprestimos()

                if not emprestimos:
                    print("Nenhum empréstimo cadastrado.")
                else:
                    for emprestimo in emprestimos:
                        pprint(emprestimo)
                        print()

            elif opcao == "12":
                pprint(service.top_5_livros_mais_emprestados())

            elif opcao == "13":
                pprint(service.quantidade_emprestimos_por_curso())

            elif opcao == "14":
                pprint(service.alunos_com_emprestimos_atrasados())

            elif opcao == "15":
                total = service.total_arrecadado_multas()
                print(f"Total arrecadado: R$ {total:.2f}")

            elif opcao == "0":
                print("Encerrando...")
                break

            else:
                print("Opção inválida.")

        except BibliotecaError as erro:
            print(f"Erro: {erro}")
        except ValueError:
            print("Erro: valor numérico inválido.")
        except Exception as erro:
            print(f"Erro inesperado: {erro}")


if __name__ == "__main__":
    main()
