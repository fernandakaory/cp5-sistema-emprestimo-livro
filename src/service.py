from datetime import datetime, timedelta, timezone, time

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from src.exceptions import (
    LivroNaoEncontrado,
    AlunoNaoEncontrado,
    LivroIndisponivel,
    LimiteEmprestimos,
    AlunoComAtraso,
    EmprestimoNaoEncontrado,
    EmprestimoJaDevolvido,
    LivroComEmprestimoAberto,
    DadoInvalido,
)


def agora_utc():
    return datetime.now(timezone.utc)


class BibliotecaService:
    def __init__(self, db):
        self.db = db
        self.livros = db.livros
        self.alunos = db.alunos
        self.emprestimos = db.emprestimos

    # ----------------------------
    # R1 - CRUD DE LIVROS
    # ----------------------------
    def cadastrar_livro(
        self,
        isbn,
        titulo,
        autor,
        ano,
        categoria,
        exemplares_total
    ):
        if exemplares_total < 0:
            raise DadoInvalido("exemplares_total não pode ser negativo.")

        documento = {
            "isbn": isbn,
            "titulo": titulo,
            "autor": autor,
            "ano": ano,
            "categoria": categoria,
            "exemplares_total": exemplares_total,
            "exemplares_disponiveis": exemplares_total,
        }

        try:
            resultado = self.livros.insert_one(documento)
            return self.livros.find_one({"_id": resultado.inserted_id})
        except DuplicateKeyError:
            raise DadoInvalido("Já existe um livro cadastrado com esse ISBN.")

    def buscar_livro_por_isbn(self, isbn):
        livro = self.livros.find_one({"isbn": isbn})
        if not livro:
            raise LivroNaoEncontrado(f"Livro com ISBN {isbn} não encontrado.")
        return livro

    def listar_livros(self):
        return list(self.livros.find().sort("titulo", 1))

    def atualizar_livro(self, isbn, dados):
        dados = dict(dados)

        # Evita alterar o identificador único pela atualização genérica.
        dados.pop("isbn", None)

        livro_atual = self.buscar_livro_por_isbn(isbn)

        if "exemplares_total" in dados:
            novo_total = dados["exemplares_total"]
            emprestados = (
                livro_atual["exemplares_total"]
                - livro_atual["exemplares_disponiveis"]
            )

            if novo_total < emprestados:
                raise DadoInvalido(
                    "O total de exemplares não pode ser menor "
                    "que a quantidade atualmente emprestada."
                )

            dados["exemplares_disponiveis"] = novo_total - emprestados

        self.livros.update_one({"isbn": isbn}, {"$set": dados})
        return self.buscar_livro_por_isbn(isbn)

    def remover_livro(self, isbn):
        self.buscar_livro_por_isbn(isbn)

        existe_emprestimo_aberto = self.emprestimos.find_one({
            "isbn": isbn,
            "data_devolucao": None
        })

        if existe_emprestimo_aberto:
            raise LivroComEmprestimoAberto(
                "O livro não pode ser removido porque possui empréstimo em aberto."
            )

        self.livros.delete_one({"isbn": isbn})
        return True

    # ----------------------------
    # R2 - CADASTRO DE ALUNOS
    # ----------------------------
    def cadastrar_aluno(self, matricula, nome, curso, email):
        if "@" not in email:
            raise DadoInvalido("E-mail inválido: deve conter @.")

        documento = {
            "matricula": matricula,
            "nome": nome,
            "curso": curso,
            "email": email,
        }

        try:
            resultado = self.alunos.insert_one(documento)
            return self.alunos.find_one({"_id": resultado.inserted_id})
        except DuplicateKeyError:
            raise DadoInvalido(
                "Já existe um aluno cadastrado com essa matrícula."
            )

    def buscar_aluno_por_matricula(self, matricula):
        aluno = self.alunos.find_one({"matricula": matricula})
        if not aluno:
            raise AlunoNaoEncontrado(
                f"Aluno com matrícula {matricula} não encontrado."
            )
        return aluno

    # ----------------------------
    # R3 - BUSCA DE LIVROS
    # ----------------------------
    def buscar_livros(self, texto=None, categoria=None):
        filtro = {}

        if texto:
            filtro["$or"] = [
                {"titulo": {"$regex": texto, "$options": "i"}},
                {"autor": {"$regex": texto, "$options": "i"}},
            ]

        if categoria:
            filtro["categoria"] = categoria

        return list(self.livros.find(filtro).sort("titulo", 1))

    # ----------------------------
    # R4 - EMPRÉSTIMO
    # ----------------------------
    def emprestar_livro(self, isbn, matricula, data_atual=None):
        data_atual = data_atual or agora_utc()

        self.buscar_livro_por_isbn(isbn)
        self.buscar_aluno_por_matricula(matricula)

        quantidade_abertos = self.emprestimos.count_documents({
            "matricula": matricula,
            "data_devolucao": None
        })

        if quantidade_abertos >= 3:
            raise LimiteEmprestimos(
                "O aluno já possui 3 empréstimos em aberto."
            )

        emprestimo_atrasado = self.emprestimos.find_one({
            "matricula": matricula,
            "data_devolucao": None,
            "data_prevista": {"$lt": data_atual}
        })

        if emprestimo_atrasado:
            raise AlunoComAtraso(
                "O aluno possui empréstimo atrasado e não pode pegar outro livro."
            )

        # Atualização atômica para impedir estoque negativo em concorrência.
        livro_atualizado = self.livros.find_one_and_update(
            {
                "isbn": isbn,
                "exemplares_disponiveis": {"$gt": 0}
            },
            {"$inc": {"exemplares_disponiveis": -1}},
            return_document=ReturnDocument.AFTER
        )

        if not livro_atualizado:
            raise LivroIndisponivel(
                "Não há exemplares disponíveis para empréstimo."
            )

        emprestimo = {
            "isbn": isbn,
            "matricula": matricula,
            "data_emprestimo": data_atual,
            "data_prevista": data_atual + timedelta(days=7),
            "data_devolucao": None,
            "multa": 0.0,
        }

        try:
            resultado = self.emprestimos.insert_one(emprestimo)
            return self.emprestimos.find_one({"_id": resultado.inserted_id})
        except Exception:
            # Compensação caso a criação do empréstimo falhe após baixar estoque.
            self.livros.update_one(
                {"isbn": isbn},
                {"$inc": {"exemplares_disponiveis": 1}}
            )
            raise

    # ----------------------------
    # R5 - DEVOLUÇÃO
    # ----------------------------
    def devolver_livro(self, emprestimo_id, data_atual=None):
        from bson import ObjectId

        data_atual = data_atual or agora_utc()

        if isinstance(emprestimo_id, str):
            try:
                emprestimo_id = ObjectId(emprestimo_id)
            except Exception:
                raise EmprestimoNaoEncontrado("ID de empréstimo inválido.")

        emprestimo = self.emprestimos.find_one({"_id": emprestimo_id})

        if not emprestimo:
            raise EmprestimoNaoEncontrado("Empréstimo não encontrado.")

        if emprestimo["data_devolucao"] is not None:
            raise EmprestimoJaDevolvido(
                "Esse empréstimo já foi devolvido."
            )

        dias_atraso = max(
            0,
            (data_atual.date() - emprestimo["data_prevista"].date()).days
        )
        multa = dias_atraso * 2.0

        resultado = self.emprestimos.update_one(
            {
                "_id": emprestimo_id,
                "data_devolucao": None
            },
            {
                "$set": {
                    "data_devolucao": data_atual,
                    "multa": multa
                }
            }
        )

        if resultado.modified_count != 1:
            raise EmprestimoJaDevolvido(
                "Esse empréstimo já foi devolvido."
            )

        self.livros.update_one(
            {"isbn": emprestimo["isbn"]},
            {"$inc": {"exemplares_disponiveis": 1}}
        )

        return self.emprestimos.find_one({"_id": emprestimo_id})

    # ----------------------------
    # R6 - RELATÓRIOS
    # ----------------------------
    def top_5_livros_mais_emprestados(self):
        pipeline = [
            {
                "$group": {
                    "_id": "$isbn",
                    "total_emprestimos": {"$sum": 1}
                }
            },
            {"$sort": {"total_emprestimos": -1}},
            {"$limit": 5},
            {
                "$lookup": {
                    "from": "livros",
                    "localField": "_id",
                    "foreignField": "isbn",
                    "as": "livro"
                }
            },
            {"$unwind": "$livro"},
            {
                "$project": {
                    "_id": 0,
                    "isbn": "$_id",
                    "titulo": "$livro.titulo",
                    "total_emprestimos": 1
                }
            }
        ]

        return list(self.emprestimos.aggregate(pipeline))

    def quantidade_emprestimos_por_curso(self):
        pipeline = [
            {
                "$lookup": {
                    "from": "alunos",
                    "localField": "matricula",
                    "foreignField": "matricula",
                    "as": "aluno"
                }
            },
            {"$unwind": "$aluno"},
            {
                "$group": {
                    "_id": "$aluno.curso",
                    "quantidade_emprestimos": {"$sum": 1}
                }
            },
            {"$sort": {"quantidade_emprestimos": -1}},
            {
                "$project": {
                    "_id": 0,
                    "curso": "$_id",
                    "quantidade_emprestimos": 1
                }
            }
        ]

        return list(self.emprestimos.aggregate(pipeline))

    def alunos_com_emprestimos_atrasados(self, data_atual=None):
        data_atual = data_atual or agora_utc()

        data_referencia = datetime.combine(
            data_atual.date(),
            time.min
        )

        pipeline = [
            {
                "$match": {
                    "data_devolucao": None,
                    "data_prevista": {"$lt": data_referencia}
                }
            },
            {
                "$lookup": {
                    "from": "alunos",
                    "localField": "matricula",
                    "foreignField": "matricula",
                    "as": "aluno"
                }
            },
            {"$unwind": "$aluno"},
            {
                "$lookup": {
                    "from": "livros",
                    "localField": "isbn",
                    "foreignField": "isbn",
                    "as": "livro"
                }
            },
            {"$unwind": "$livro"},
            {
                "$addFields": {
                    "dias_atraso": {
                        "$floor": {
                            "$divide": [
                                {
                                    "$subtract": [
                                        data_referencia,
                                        "$data_prevista"
                                    ]
                                },
                                1000 * 60 * 60 * 24
                            ]
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "matricula": 1,
                    "nome": "$aluno.nome",
                    "isbn": 1,
                    "livro": "$livro.titulo",
                    "dias_atraso": 1
                }
            },
            {"$sort": {"dias_atraso": -1}}
        ]

        return list(self.emprestimos.aggregate(pipeline))

    def total_arrecadado_multas(self):
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_multas": {"$sum": "$multa"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "total_multas": 1
                }
            }
        ]

        resultado = list(self.emprestimos.aggregate(pipeline))
        return resultado[0]["total_multas"] if resultado else 0.0

    def listar_emprestimos(self):
        pipeline = [
            {
                "$lookup": {
                    "from": "alunos",
                    "localField": "matricula",
                    "foreignField": "matricula",
                    "as": "aluno"
                }
            },
            {"$unwind": "$aluno"},
            {
                "$lookup": {
                    "from": "livros",
                    "localField": "isbn",
                    "foreignField": "isbn",
                    "as": "livro"
                }
            },
            {"$unwind": "$livro"},
            {
                "$project": {
                    "_id": 1,
                    "isbn": 1,
                    "titulo": "$livro.titulo",
                    "matricula": 1,
                    "aluno": "$aluno.nome",
                    "data_emprestimo": 1,
                    "data_prevista": 1,
                    "data_devolucao": 1,
                    "multa": 1
                }
            },
            {
                "$sort": {
                    "data_emprestimo": -1
                }
            }
        ]

        return list(self.emprestimos.aggregate(pipeline))