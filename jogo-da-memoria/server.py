#!/usr/bin/env python3
"""Servidor do jogo da memória — alvo de laboratório para labs-v2.

Pure Python (stdlib), sem Flask — mesmo princípio do conteiner-eco/ da v1:
determinístico e transparente. Uma única codebase serve as versões
"vulnerável" e "robusta": cada cenário é controlado por uma variável de
ambiente (flag), desligada por padrão. Rodar sem nenhuma flag = versão
robusta. Ativar as quatro flags = versão vulnerável usada nos labs S2.3,
S3.3, S3.4 e S4.4.

    FALHA_LOGOUT=1      não invalida a sessão no servidor ao fazer logout
    FALHA_IDOR=1        /api/historico não verifica o dono do identificador
    FALHA_PONTUACAO=1   aceita a pontuação enviada pelo cliente sem validar
    FALHA_RESIDUO=1      não limpa o histórico local do IndexedDB no logout
                          (esta flag só é lida pelo front-end via /api/config)

Ver README.md deste diretório para o contrato completo e o roteiro de
verificação antes da aula.
"""

import hashlib
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import db

PORT = int(os.environ.get('PORT', 3000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FALHAS = {
    'logout_incompleto': bool(os.environ.get('FALHA_LOGOUT')),
    'idor_historico': bool(os.environ.get('FALHA_IDOR')),
    'pontuacao_livre': bool(os.environ.get('FALHA_PONTUACAO')),
    'residuo_pos_logout': bool(os.environ.get('FALHA_RESIDUO')),
}

STATIC_FILES = {
    '/': 'index.html',
    '/index.html': 'index.html',
    '/script.js': 'script.js',
    '/styles.css': 'styles.css',
    '/sw.js': 'sw.js',
}

# Cache-Control deliberado por recurso, para o lab S1.3.
CACHE_CONTROL = {
    '/styles.css': 'public, max-age=3600',
    '/script.js': 'public, max-age=60, must-revalidate',
    '/sw.js': 'no-store',
    '/index.html': 'no-store',
    '/': 'no-store',
}

CONTENT_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
}

PARES_POR_PARTIDA = 8
COOKIE_NOME = 'sessao'


def agora_iso():
    return datetime.now(timezone.utc).isoformat()


def etag_de(body: bytes) -> str:
    return '"' + hashlib.sha256(body).hexdigest()[:16] + '"'


class MemoryGameHandler(BaseHTTPRequestHandler):
    server_version = 'JogoDaMemoria/1.0'

    # --- infraestrutura de resposta ---

    def _send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        for k, v in (extra_headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, filename):
        file_path = os.path.join(BASE_DIR, filename)
        if not os.path.isfile(file_path):
            self._send_json(HTTPStatus.NOT_FOUND, {'error': 'not found'})
            return

        with open(file_path, 'rb') as f:
            body = f.read()

        etag = etag_de(body)
        if_none_match = self.headers.get('If-None-Match')
        if if_none_match == etag:
            self.send_response(HTTPStatus.NOT_MODIFIED)
            self.send_header('ETag', etag)
            cache_control = CACHE_CONTROL.get(path)
            if cache_control:
                self.send_header('Cache-Control', cache_control)
            self.end_headers()
            return

        ext = os.path.splitext(filename)[1]
        content_type = CONTENT_TYPES.get(ext, 'application/octet-stream')

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('ETag', etag)
        cache_control = CACHE_CONTROL.get(path)
        if cache_control:
            self.send_header('Cache-Control', cache_control)
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length) if length else b''
        try:
            return json.loads(raw or b'{}')
        except json.JSONDecodeError:
            return None

    def _set_cookie(self, token):
        cookie = SimpleCookie()
        cookie[COOKIE_NOME] = token
        cookie[COOKIE_NOME]['httponly'] = True
        cookie[COOKIE_NOME]['path'] = '/'
        cookie[COOKIE_NOME]['samesite'] = 'Lax'
        # Secure fica de fora deliberadamente: o laboratório roda em HTTP puro
        # em localhost. Anote isso como achado ao inspecionar o Set-Cookie.
        return cookie[COOKIE_NOME].OutputString()

    def _clear_cookie(self):
        cookie = SimpleCookie()
        cookie[COOKIE_NOME] = ''
        cookie[COOKIE_NOME]['httponly'] = True
        cookie[COOKIE_NOME]['path'] = '/'
        cookie[COOKIE_NOME]['max-age'] = 0
        return cookie[COOKIE_NOME].OutputString()

    def _token_da_requisicao(self):
        raw = self.headers.get('Cookie')
        if not raw:
            return None
        cookie = SimpleCookie()
        cookie.load(raw)
        if COOKIE_NOME in cookie:
            return cookie[COOKIE_NOME].value
        return None

    def _sessao_ativa(self, con):
        """Devolve a linha de sessão ativa correspondente ao cookie, ou None."""
        token = self._token_da_requisicao()
        if not token:
            return None
        row = con.execute(
            'SELECT * FROM sessoes WHERE token = ? AND ativa = 1', (token,)
        ).fetchone()
        return row

    # --- roteamento ---

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        with db.conectar() as con:
            if path == '/api/me':
                return self._get_me(con)
            if path == '/api/historico':
                return self._get_historico(con, query)
            if path == '/api/ranking':
                return self._get_ranking(con)
            if path == '/api/config':
                return self._get_config()

        if path in STATIC_FILES:
            return self._send_file(path, STATIC_FILES[path])

        self._send_json(HTTPStatus.NOT_FOUND, {'error': 'not found'})

    def do_POST(self):
        path = urlparse(self.path).path

        with db.conectar() as con:
            if path == '/api/login':
                return self._post_login(con)
            if path == '/api/logout':
                return self._post_logout(con)
            if path == '/api/partida/iniciar':
                return self._post_partida_iniciar(con)
            if path == '/api/partida/resultado':
                return self._post_partida_resultado(con)

        self._send_json(HTTPStatus.NOT_FOUND, {'error': 'not found'})

    # --- handlers ---

    def _get_config(self):
        # Exposto só para o front-end decidir se deve limpar o IndexedDB no
        # logout (S4.4). Não é uma rota "de ataque" — é config pública de UI.
        self._send_json(HTTPStatus.OK, {
            'limpar_historico_local_no_logout': not FALHAS['residuo_pos_logout'],
        })

    def _post_login(self, con):
        data = self._read_json_body()
        if not data:
            return self._send_json(HTTPStatus.BAD_REQUEST, {'error': 'invalid json'})

        usuario_id = str(data.get('usuario', '')).strip().lower()
        senha = str(data.get('senha', ''))

        conta = con.execute(
            'SELECT * FROM contas WHERE usuario_id = ?', (usuario_id,)
        ).fetchone()

        if not conta or conta['senha'] != senha:
            return self._send_json(HTTPStatus.UNAUTHORIZED, {'error': 'credenciais inválidas'})

        token = secrets.token_urlsafe(24)
        con.execute(
            'INSERT INTO sessoes (token, usuario_id, criada_em, ativa) VALUES (?, ?, ?, 1)',
            (token, usuario_id, agora_iso()),
        )
        set_cookie = self._set_cookie(token)
        self._send_json(HTTPStatus.OK, {'usuario_id': usuario_id}, {'Set-Cookie': set_cookie})

    def _post_logout(self, con):
        token = self._token_da_requisicao()
        if token and not FALHAS['logout_incompleto']:
            con.execute('UPDATE sessoes SET ativa = 0 WHERE token = ?', (token,))
        # Com FALHA_LOGOUT ligada: a linha em `sessoes` continua ativa=1 no
        # servidor mesmo depois desta resposta remover o cookie do cliente —
        # é exatamente o que o lab S2.3 pede para provar com o Repeater.
        set_cookie = self._clear_cookie()
        self._send_json(HTTPStatus.OK, {'ok': True}, {'Set-Cookie': set_cookie})

    def _get_me(self, con):
        sessao = self._sessao_ativa(con)
        if not sessao:
            return self._send_json(HTTPStatus.UNAUTHORIZED, {'error': 'sem sessão válida'})
        self._send_json(HTTPStatus.OK, {'usuario_id': sessao['usuario_id']})

    def _get_historico(self, con, query):
        sessao = self._sessao_ativa(con)
        if not sessao:
            return self._send_json(HTTPStatus.UNAUTHORIZED, {'error': 'sem sessão válida'})

        usuario_da_sessao = sessao['usuario_id']
        usuario_solicitado = query.get('usuario_id', [usuario_da_sessao])[0]

        if FALHAS['idor_historico']:
            usuario_alvo = usuario_solicitado  # não verifica posse — é o achado do S3.3
        else:
            if usuario_solicitado != usuario_da_sessao:
                return self._send_json(HTTPStatus.FORBIDDEN, {'error': 'sem permissão para este histórico'})
            usuario_alvo = usuario_da_sessao

        linhas = con.execute(
            'SELECT id, pontos, tempo_s, data FROM historico WHERE usuario_id = ? ORDER BY data DESC',
            (usuario_alvo,),
        ).fetchall()
        self._send_json(HTTPStatus.OK, [dict(r) for r in linhas])

    def _get_ranking(self, con):
        # Sempre público: nome + pontuação, nunca email/senha/identificador de sessão.
        linhas = con.execute(
            '''
            SELECT c.nome AS nome, h.pontos AS pontos, h.tempo_s AS tempo_s
            FROM historico h
            JOIN contas c ON c.usuario_id = h.usuario_id
            ORDER BY h.pontos DESC, h.tempo_s ASC
            LIMIT 10
            '''
        ).fetchall()
        self._send_json(HTTPStatus.OK, [dict(r) for r in linhas])

    def _post_partida_iniciar(self, con):
        sessao = self._sessao_ativa(con)
        if not sessao:
            return self._send_json(HTTPStatus.UNAUTHORIZED, {'error': 'sem sessão válida'})

        token = self._token_da_requisicao()
        con.execute('DELETE FROM partidas_em_curso WHERE token = ?', (token,))
        con.execute(
            'INSERT INTO partidas_em_curso (token, pares_esperados, iniciada_em) VALUES (?, ?, ?)',
            (token, PARES_POR_PARTIDA, agora_iso()),
        )
        self._send_json(HTTPStatus.OK, {'pares_esperados': PARES_POR_PARTIDA})

    def _post_partida_resultado(self, con):
        sessao = self._sessao_ativa(con)
        if not sessao:
            return self._send_json(HTTPStatus.UNAUTHORIZED, {'error': 'sem sessão válida'})

        data = self._read_json_body()
        if data is None:
            return self._send_json(HTTPStatus.BAD_REQUEST, {'error': 'invalid json'})

        pontos_informados = data.get('pontos')
        tempo_s = data.get('tempo_s')
        if not isinstance(pontos_informados, (int, float)):
            return self._send_json(HTTPStatus.BAD_REQUEST, {'error': 'pontos é obrigatório'})

        token = self._token_da_requisicao()
        usuario_id = sessao['usuario_id']

        if FALHAS['pontuacao_livre']:
            # Aceita cego o que o cliente mandou — é o achado do S3.4.
            pontos_gravados = int(pontos_informados)
        else:
            partida = con.execute(
                'SELECT * FROM partidas_em_curso WHERE token = ?', (token,)
            ).fetchone()
            pares_esperados = partida['pares_esperados'] if partida else PARES_POR_PARTIDA
            # O servidor nunca confia num valor maior do que a partida permite.
            pontos_gravados = min(int(pontos_informados), pares_esperados)

        con.execute(
            'INSERT INTO historico (usuario_id, pontos, tempo_s, data) VALUES (?, ?, ?, ?)',
            (usuario_id, pontos_gravados, tempo_s if isinstance(tempo_s, (int, float)) else None, agora_iso()),
        )
        con.execute('DELETE FROM partidas_em_curso WHERE token = ?', (token,))
        self._send_json(HTTPStatus.OK, {'pontos_gravados': pontos_gravados})

    def log_message(self, format, *args):
        print(f'{self.address_string()} - {format % args}')


class ThreadingHTTPServerIPv4(ThreadingHTTPServer):
    address_family = socket.AF_INET
    daemon_threads = True


def main():
    db.inicializar(resetar=False)
    ativas = [nome for nome, ligada in FALHAS.items() if ligada]
    print(f'Jogo da memória rodando em http://localhost:{PORT}')
    print(f'Flags de falha ativas: {ativas or "nenhuma (versão robusta)"}')

    server = ThreadingHTTPServerIPv4(('0.0.0.0', PORT), MemoryGameHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == '__main__':
    main()
