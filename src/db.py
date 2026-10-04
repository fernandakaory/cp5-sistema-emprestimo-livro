import os
from pymongo import MongoClient, ASCENDING


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "biblioteca")


def get_db():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    criar_indices(db)
    return db


def criar_indices(db):
    db.livros.create_index(
        [("isbn", ASCENDING)],
        unique=True,
        name="uk_livros_isbn"
    )

    db.alunos.create_index(
        [("matricula", ASCENDING)],
        unique=True,
        name="uk_alunos_matricula"
    )

    db.emprestimos.create_index(
        [("isbn", ASCENDING), ("matricula", ASCENDING)]
    )

    db.emprestimos.create_index(
        [("data_devolucao", ASCENDING), ("data_prevista", ASCENDING)]
    )
