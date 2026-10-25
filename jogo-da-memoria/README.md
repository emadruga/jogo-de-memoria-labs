# Jogo da memória — como instalar e rodar

Alvo dos laboratórios S1 a S4. Roda **na sua própria máquina**, em `http://localhost:3000`.
Contas de laboratório: `ana` / `senha123` e `bruno` / `senha123`.

Todos os comandos abaixo são executados no terminal, dentro deste diretório (`jogo-da-memoria/`).
No Windows, use o **Git Bash**.

---

## Opção A — Sem Docker (Python)

Requer Python 3.10 ou mais recente. Não há nenhuma biblioteca para instalar (`pip install`).

```bash
python3 --version     # no Windows, pode ser: python --version
python3 db.py         # cria e popula o banco dados.db (só na primeira vez)
python3 server.py     # sobe o jogo em http://localhost:3000
```

Pare o servidor com `Ctrl+C`.

## Opção B — Com Docker

Requer o Docker instalado e em execução (`docker run hello-world` deve funcionar).

```bash
docker build -t jogo-da-memoria .
docker run --rm -p 3000:3000 jogo-da-memoria
```

Pare o contêiner com `Ctrl+C`. O banco é criado durante o `docker build`, e o `--rm` descarta o
contêiner ao parar. Cada `docker run` parte, portanto, do estado inicial (Ana e Bruno com o
histórico pré-carregado). Só é preciso refazer o `docker build` se você mudar o código.

---

## Começar do zero (resetar o estado)

- **Sem Docker:** pare o servidor, apague o banco e recrie-o.
  ```bash
  rm dados.db && python3 db.py
  ```
- **Com Docker:** basta parar o contêiner e rodar `docker run` de novo.

Isso limpa só o servidor. O navegador (cookies, storages, Service Worker) e o Burp guardam estado
próprio — veja "Recomeçando do zero" no [`README.md`](../README.md) da raiz.

---

## Rodar uma versão com falha ativa

Os laboratórios-caso comparam duas versões do mesmo jogo. A versão sem nenhuma variável é a
robusta. Para cada caso, o jogo lê uma variável de ambiente, e você liga **uma por vez**:

| Laboratório | Variável |
|---|---|
| S2.3 | `FALHA_LOGOUT=1` |
| S3.3 | `FALHA_IDOR=1` |
| S3.4 | `FALHA_PONTUACAO=1` |
| S4.4 | `FALHA_RESIDUO=1` |

Sem Docker (exemplo para o S2.3):

```bash
FALHA_LOGOUT=1 python3 server.py
```

Com Docker (exemplo para o S2.3):

```bash
docker run --rm -p 3000:3000 -e FALHA_LOGOUT=1 jogo-da-memoria
```

**Rode uma versão de cada vez.** Cookies de `localhost` não são separados por porta, então duas
instâncias simultâneas no mesmo navegador compartilham o cookie de sessão e confundem o
experimento. Para comparar as versões, pare uma, suba a outra e limpe o navegador entre elas.

---

## Se algo der errado

| Sintoma | Causa provável |
|---|---|
| `Address already in use` / porta 3000 ocupada | Há outra instância rodando. Pare-a com `Ctrl+C`, ou use `PORT=3001 python3 server.py` (Docker: `-p 3001:3000`). |
| Página antiga depois de mudar algo | Cache do navegador ou Service Worker: veja "Recomeçando do zero" no `README.md` da raiz. |
| `docker: command not found` | Docker não instalado ou fora do PATH. Veja o [`INSTALAR.md`](../INSTALAR.md). |
