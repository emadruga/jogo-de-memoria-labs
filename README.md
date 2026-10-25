# Laboratórios do Bloco II — Segurança Ofensiva em Aplicações Web

### Semanas 1–5 · jogo da memória → OWASP Juice Shop

> **Escopo.** Todos os laboratórios são executados **exclusivamente** em alvos de laboratório
> locais e autorizados: o **jogo da memória** (`jogo-da-memoria/`) e, na Semana 5, o **OWASP Juice
> Shop** local. Nenhum sistema de terceiros, em nenhuma hipótese.

**Antes da Semana 1:** siga o [`INSTALAR.md`](INSTALAR.md) e confirme que o jogo sobe na sua máquina
([`jogo-da-memoria/README.md`](jogo-da-memoria/README.md)).

**Teoria de referência** (leia conforme os laboratórios pedirem):

- [HTTP na Prática: Cabeçalhos, Cookies e Burp Suite](docs/http-headers-cookies-burp.md)
- [Anatomia do Navegador: Armazenamentos, Escopos e Sessão](docs/anatomia-do-navegador.md)

---

## A pergunta que guia as quatro semanas

> **O que chegou pela rede, onde ficou, e quando voltou ao servidor?**

Cada semana usa Burp (dados em trânsito) e DevTools (dados em repouso no navegador) **juntos**. Cada
semana termina em um **caso**: uma investigação completa (previsão → ação → evidência → conclusão),
comparada entre a versão com falha e a versão robusta do mesmo jogo.

---

## Grade de laboratórios

| # | Laboratório | Habilidade | Ferramentas | Alvo | Gancho OWASP 2025 |
|---|---|---|---|---|---|
| **S1.1** | Ler a conversa HTTP crua | Observar o HTTP history; identificar linha inicial, cabeçalhos, corpo | Burp | Jogo da memória | fundação |
| **S1.2** | Inventário no navegador | Navegar DevTools → Application; ler cookies, storages, IndexedDB | DevTools | Jogo da memória | fundação |
| **S1.3** | Cache HTTP e revalidação | `Cache-Control`, `ETag`/`If-None-Match`, `304` — o que foi de fato retransferido | Burp + DevTools (Network) | Jogo da memória | fundação |
| **S2.1** | Quem controla este valor? | Matriz `cabeçalho → quem controla → o que muda se eu alterar` | Burp | Jogo da memória | fundação |
| **S2.2** | O cookie de sessão, ponta a ponta | Seguir um cookie: emissão → armazenamento → envio → decisão do servidor | Burp + DevTools | Jogo da memória | A07 |
| **S2.3** | Caso: logout incompleto | Provar (ou refutar) que uma sessão encerrada continua sendo aceita pelo servidor | Burp (Repeater) | Jogo da memória (vulnerável × robusta) | **A07:2025 — Authentication Failures** |
| **S3.1** | Um valor por vez no Repeater | Modificar **uma** variável por teste e observar o efeito, com disciplina de isolamento | Burp (Repeater) | Jogo da memória | A02, A01 |
| **S3.2** | Decodificar o opaco | Decoder: `Authorization: Basic`, Base64, estrutura de um JWT/token opaco | Burp (Decoder) | Jogo da memória | A02 |
| **S3.3** | Caso: histórico de outro jogador | Trocar um identificador numa requisição autenticada e ver o que o servidor entrega | Burp (Repeater) | Jogo da memória (vulnerável × robusta) | **A01:2025 — Broken Access Control** |
| **S3.4** | Caso: pontuação inventada | Interceptar e alterar um valor de negócio no corpo da requisição; verificar o que o servidor aceita | Burp (Proxy/Intercept) | Jogo da memória (vulnerável × robusta) | **A06:2025 — Insecure Design** |
| **S4.1** | Escopo: o experimento das abas | Provar empiricamente `sessionStorage` (aba) vs. `localStorage`/cookie (origem) | DevTools (Console) | Jogo da memória | fundação |
| **S4.2** | Ler IndexedDB por script | Abrir base, listar object stores, ler registros via console assíncrono | DevTools (Console) | Jogo da memória | fundação |
| **S4.3** | Cache Storage e modo offline | Inspecionar Cache Storage, ativar modo offline, distinguir de Cache HTTP e de IndexedDB | DevTools (Application + Network offline) | Jogo da memória | fundação |
| **S4.4** | Caso: histórico privado residual | Verificar se dado privado sobrevive ao logout num perfil de navegador compartilhado | DevTools (Application) | Jogo da memória (vulnerável × robusta) | **A01:2025 — Broken Access Control** |
| **S5.1** | O que vive no cliente vs. o que vai pro servidor | Burp + DevTools juntos, agora no alvo real; replicar ao menos dois dos quatro casos | Burp + DevTools | **Juice Shop** | consolida A01, A06, A07 |

---

## Ordem de execução

| Semana | Labs | Roteiro |
|---|---|---|
| **1** | S1.1, S1.2, S1.3 | [`labs/S1-Roteiro.md`](labs/S1-Roteiro.md) |
| **2** | S2.1, S2.2, S2.3 | [`labs/S2-Roteiro.md`](labs/S2-Roteiro.md) |
| **3** | S3.1, S3.2, S3.3, S3.4 | [`labs/S3-Roteiro.md`](labs/S3-Roteiro.md) |
| **4** | S4.1, S4.2, S4.3, S4.4 | [`labs/S4-Roteiro.md`](labs/S4-Roteiro.md) |
| **5** | S5.1 | [`labs/S5.1-juice-shop.md`](labs/S5.1-juice-shop.md) |

Dentro de cada semana, **observação antes de modificação**: os labs `.1` e `.2` são de leitura; o
caso no fim da semana é que exige alterar algo — e sempre comparando as duas versões, nunca só
atacando a versão com falha.

---

## Convenções de cada laboratório

1. **Objetivo** — a única habilidade que o lab treina.
2. **Pré-requisitos**
3. **Setup**
4. **Roteiro** — passos de execução.
5. **Perguntas-guia** — o que você deve conseguir responder ao final.
6. **Critérios de verificação** — como saber que fez certo.
7. **Fronteira ética** — o que é uso legítimo e o que é vedado.
8. **Fechamento defensivo** — a remediação e a detecção correspondentes.

Os labs de caso (S2.3, S3.3, S3.4, S4.4) têm ainda a **Regra violada**: a frase única que define o
comportamento correto, testada nas duas versões.

---

## Recomeçando do zero

Para repetir um exercício como se tudo tivesse acabado de ser instalado, limpe **três lugares**.
Limpar só um deixa estado residual nos outros.

| Onde | O que persiste | Como limpar |
|---|---|---|
| **Servidor** | Sessões, partidas e pontuações no SQLite | Veja "Começar do zero" em [`jogo-da-memoria/README.md`](jogo-da-memoria/README.md). |
| **Navegador** | Cookie de sessão, `localStorage`, `sessionStorage`, IndexedDB, Cache HTTP, Cache Storage e o Service Worker (`/sw.js`) | No Chrome, com o DevTools aberto no jogo: **Application > Storage**, marcar *Unregister service workers* e todas as caixas, clicar em **Clear site data** e recarregar com `Cmd+Shift+R` (`Ctrl+Shift+R` no Windows/Linux). |
| **Burp** | Histórico e Site map da sessão | Fechar o projeto temporário e abrir outro, ou limpar **Proxy > HTTP history** e o **Site map**. |

Alternativas para o navegador: uma **janela anônima nova** a cada exercício (confira se o proxy do
Burp funciona nela) ou um **perfil dedicado** ao laboratório. Limpe **antes de cada lab**, não só ao
final: estado de uma tentativa anterior contamina a seguinte e produz achados falsos.

---

## Uso de IA

A IA é tutora e par de raciocínio, nunca piloto automático. Registre como você a usou nos seus
relatórios e vídeos, conforme combinado com o docente.
