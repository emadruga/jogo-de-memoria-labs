"""Camada de dados (SQLite) do jogo da memória. Sem ORM, consultas diretas."""

import os
import sqlite3
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'dados.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS contas (
    usuario_id TEXT PRIMARY KEY,
    senha TEXT NOT NULL,
    nome TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessoes (
    token TEXT PRIMARY KEY,
    usuario_id TEXT NOT NULL,
    criada_em TEXT NOT NULL,
    ativa INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id TEXT NOT NULL,
    pontos INTEGER NOT NULL,
    tempo_s INTEGER,
    data TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS partidas_em_curso (
    token TEXT PRIMARY KEY,
    pares_esperados INTEGER NOT NULL,
    iniciada_em TEXT NOT NULL
);
"""

SEED_CONTAS = [
    ('ana', 'senha123', 'Ana'),
    ('bruno', 'senha123', 'Bruno'),
]

SEED_HISTORICO = [
    ('ana', 8, 47, '2026-09-01T10:00:00+00:00'),
    ('ana', 6, 63, '2026-09-02T11:00:00+00:00'),
    ('bruno', 7, 55, '2026-09-01T14:00:00+00:00'),
]


@contextmanager
def conectar():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    try:
        yield con
        con.commit()
    finally:
        con.close()


def inicializar(resetar=False):
    """Cria o schema e popula as contas/histórico de laboratório.

    resetar=True apaga o banco existente primeiro — uso do docente entre turmas.
    """
    if resetar and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    with conectar() as con:
        con.executescript(SCHEMA)

        existentes = {r['usuario_id'] for r in con.execute('SELECT usuario_id FROM contas')}
        for usuario_id, senha, nome in SEED_CONTAS:
            if usuario_id not in existentes:
                con.execute(
                    'INSERT INTO contas (usuario_id, senha, nome) VALUES (?, ?, ?)',
                    (usuario_id, senha, nome),
                )

        tem_historico = con.execute('SELECT COUNT(*) AS n FROM historico').fetchone()['n']
        if not tem_historico:
            con.executemany(
                'INSERT INTO historico (usuario_id, pontos, tempo_s, data) VALUES (?, ?, ?, ?)',
                SEED_HISTORICO,
            )


if __name__ == '__main__':
    inicializar(resetar=True)
    print(f'Banco inicializado em {DB_PATH}')
