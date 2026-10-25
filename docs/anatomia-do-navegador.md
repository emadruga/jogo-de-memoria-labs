# Anatomia do Navegador: Armazenamentos, Escopos e Sessão
### Material de aula — Bloco II — Segurança Ofensiva em Aplicações Web

> **Escopo.** Todas as atividades deste material são feitas **exclusivamente** em alvos de laboratório autorizados (OWASP Juice Shop, DVWA, WebGoat ou contêineres providos pelo docente).
>
> **Material complementar:** `http-headers-cookies-burp.md` — cabeçalhos HTTP, anatomia do cookie e ferramentas do Burp. Este documento assume aquele conteúdo como pré-requisito.

---

## 1. A pergunta que organiza tudo

Um navegador moderno não tem "um banco de dados". Tem **uma coleção de armazenamentos com origens históricas distintas**, cada um com regras próprias de escopo e tempo de vida.

Diante de qualquer dado guardado no cliente, faça sempre três perguntas:

1. **Qual o escopo?** (a aba? a origem? o perfil inteiro do navegador?)
2. **Qual o tempo de vida?** (a aba? a sessão do navegador? indefinido?)
3. **Quem consegue lê-lo?** (só o servidor? o JavaScript da página? um script de terceiro injetado?)

As respostas explicam quase todo comportamento aparentemente misterioso — inclusive as três situações da Seção 5.

---

## 2. Que padrão define os armazenamentos do navegador

Não existe um único padrão. É um mosaico construído ao longo de duas décadas:

| Mecanismo | Especificação de origem |
|---|---|
| **Cookies** | IETF — RFC 6265 (e o rascunho de atualização 6265bis) |
| **localStorage / sessionStorage** | WHATWG HTML Living Standard, seção *Web Storage* |
| **IndexedDB** | Especificação própria (trabalho W3C/WHATWG) |
| **Cache Storage** | Especificação de *Service Workers* |
| **Cota, persistência, particionamento** | WHATWG **Storage Standard** |
| **OPFS** (*Origin Private File System*) | *File System Standard* |
| **Web SQL** | Descontinuado e **removido** dos navegadores |

**Consequência pedagógica:** a inconsistência entre os mecanismos não é acidente de implementação — é herança histórica. Cookies nasceram na Netscape em 1994, como extensão do HTTP; Web Storage e IndexedDB nasceram como APIs de JavaScript, quinze anos depois, sem qualquer relação com o protocolo. O Storage Standard só unificou parte disso, e tardiamente.

---

## 3. Os armazenamentos, um a um

| Armazenamento | Escopo | Tempo de vida | Enviado ao servidor? | Acessível ao JS? |
|---|---|---|---|---|
| **Cookie** | Origem/domínio (perfil do navegador) | `Expires`/`Max-Age`, ou a sessão do navegador | **Sim, automaticamente** | Sim, salvo `HttpOnly` |
| **localStorage** | Origem | Indefinido, até ser apagado | Não | Sim |
| **sessionStorage** | **Origem + aba** | Fecha a aba, acaba | Não | Sim |
| **IndexedDB** | Origem | Indefinido | Não | Sim |
| **Cache Storage** | Origem | Indefinido | Não | Sim (via Service Worker) |
| **OPFS** | Origem | Indefinido | Não | Sim |
| **Cache HTTP** | Origem (particionado) | Cabeçalhos de cache | Não (é resposta armazenada) | Não diretamente |
| **BFCache** | Aba/histórico | Enquanto a entrada de histórico existir | Não | Não |

### 3.1 A distinção que mais confunde
**localStorage e sessionStorage têm APIs idênticas e escopos completamente diferentes.** O nome sugere que `sessionStorage` esteja ligado à "sessão do usuário" — não está. Está ligado à **aba**. É o único armazenamento da lista com esse escopo.

### 3.2 Por que isso importa para segurança
- Tudo que é **acessível ao JavaScript** é exfiltrável por XSS. Um token em `localStorage` não tem equivalente ao `HttpOnly`.
- Tudo que é **enviado automaticamente** (cookie) é vulnerável a CSRF se `SameSite` não estiver adequado.
- Não existe armazenamento perfeito: cookie `HttpOnly` resiste ao XSS mas exige defesa contra CSRF; `localStorage` resiste ao CSRF mas cai com qualquer XSS. **É uma escolha de trade-off, não de "melhor prática" universal.**

---

## 4. Origem e particionamento

**Origem** = esquema + host + porta. `https://loja.exemplo` e `http://loja.exemplo` são origens distintas para Web Storage e IndexedDB.

**Cookies seguem regra própria e mais frouxa:** o escopo é definido por `Domain` + `Path`, e historicamente ignoram a porta e são pouco sensíveis ao esquema. Por isso um cookie definido em `.exemplo.com` acompanha todos os subdomínios — origem comum de exposição entre aplicações que deveriam estar isoladas. Os prefixos `__Host-` e `__Secure-` existem justamente para reimpor garantias que o modelo original não dava.

**Particionamento por site.** Navegadores passaram a particionar armazenamento (e cache) por site de topo, de modo que um mesmo terceiro incorporado em dois sites diferentes não compartilhe estado entre eles. O tema evolui rápido e varia por navegador — vale conferir o estado atual antes da aula.

---

## 5. Três situações cotidianas, explicadas

### 5.1 Por que a segunda aba já está autenticada

Porque **o cookie jar pertence ao perfil do navegador, não à aba**. O escopo do cookie é `Domain` + `Path` + esquema — a aba não entra na conta. Qualquer aba que faça requisição àquela origem recebe o cookie anexado automaticamente pelo navegador.

O mesmo vale para `localStorage`, IndexedDB e Cache Storage: todos por origem, compartilhados entre abas.

**A exceção é o `sessionStorage`**, que é por aba. Se uma aplicação guardasse o token apenas ali, a segunda aba estaria deslogada. Quase nenhuma guarda — daí a experiência universal de "abri outra aba e já estava logado".

> **Demonstração de um minuto:** abrir o DevTools, executar `sessionStorage.setItem('teste','abc')` numa aba e tentar ler na outra. Depois repetir com `localStorage`. O contraste dispensa explicação.

### 5.2 Por que fechar o navegador após acessar a Receita Federal

Não é superstição — são vários mecanismos empilhados, e cada um justifica o hábito por conta própria:

1. **Cookie de sessão.** Sem `Expires`/`Max-Age`, o cookie vive em memória e morre **com o navegador**, não com a aba. Fechar só a aba não encerra a sessão.
2. **Seleção de certificado cliente.** Em acesso com e-CPF/e-CNPJ, o navegador memoriza o certificado escolhido e mantém a chave destravada até ser reiniciado. **Este é o motivo mais forte no caso específico da Receita** — outra pessoa no mesmo computador poderia reautenticar sem apresentar o PIN.
3. **Cache HTTP e BFCache.** Páginas autenticadas podem ficar recuperáveis pelo botão "voltar" se a aplicação não marcou as respostas como não-cacheáveis.
4. **Retomada de sessão TLS e conexões keep-alive** ainda abertas com o servidor.

**O detalhe que quebra tudo isso:** navegadores configurados para "continuar de onde parei" **restauram cookies de sessão** ao reabrir, anulando a proteção do item 1. Excelente ponto de discussão: uma defesa que depende de configuração do usuário não é uma defesa confiável.

### 5.3 Por que o logout às vezes não funciona

Porque apagar o cookie no cliente **não invalida a sessão no servidor**. Se o servidor não destrói a sessão do seu lado, um token capturado antes do logout continua válido — e o Burp prova isso em trinta segundos (Lab 3, Seção 7).

---

## 6. O que o Burp vê e o que não vê

Esta é a lição metodológica central deste material:

> **O Burp Suite só enxerga o que trafega.** `localStorage`, `sessionStorage`, IndexedDB e OPFS **nunca aparecem no Burp** — a menos que a aplicação, por código, os coloque dentro de uma requisição.

| Quero inspecionar | Ferramenta correta |
|---|---|
| Cookies em trânsito, `Set-Cookie`, cabeçalhos | **Burp — Proxy / Repeater** |
| Cookies armazenados e seus atributos | DevTools → *Application* → *Cookies* (e o Burp, na resposta) |
| localStorage / sessionStorage | **DevTools** → *Application* → *Storage* |
| IndexedDB, Cache Storage | **DevTools** → *Application* |
| Se um valor local vira requisição | **Burp** (é a única forma de confirmar) |
| Entropia de token de sessão | **Burp — Sequencer** |

**Método de trabalho da disciplina: Burp e DevTools lado a lado.** A pergunta que os dois juntos respondem, e nenhum responde sozinho: *o que vive no cliente, e o que disso realmente vai para o servidor?*

---

## 7. Laboratórios

### Lab 1 — Mapa de armazenamento
**Objetivo:** inventariar tudo que uma aplicação guarda no cliente e descobrir o que disso trafega.

1. Autenticar no Juice Shop com o Burp em captura.
2. No DevTools → *Application*, inventariar: cookies (com atributos), `localStorage`, `sessionStorage`, IndexedDB.
3. Para **cada** valor encontrado, procurar no histórico do Burp: ele aparece em alguma requisição?
4. Produzir a tabela: `valor → armazenamento → escopo → trafega? → em qual cabeçalho ou campo`.

**Discussão:** onde este site guarda o token de autenticação? Essa escolha o expõe mais a XSS ou a CSRF?

### Lab 2 — Experimento das abas
**Objetivo:** provar empiricamente a diferença de escopo.

1. Autenticar na aba A. Abrir a mesma aplicação na aba B.
2. No Burp, comparar as requisições das duas abas: **o mesmo cookie é enviado**.
3. No console da aba A: `sessionStorage.setItem('marcador','A')`. Tentar ler na aba B — ausente.
4. Repetir com `localStorage` — presente nas duas.
5. Registrar qual mecanismo tem escopo de aba e qual tem escopo de origem.

**Discussão:** o que aconteceria com a usabilidade do site se ele guardasse o token em `sessionStorage`? E com a segurança?

### Lab 3 — Persistência da sessão
**Objetivo:** distinguir estado do cliente de estado do servidor.

1. Capturar no Burp uma requisição autenticada válida.
2. **Fechar a aba.** Reenviar a requisição no Repeater. Funciona?
3. **Fazer logout** na aplicação. Reenviar a requisição antiga. Funciona? *(Se sim: a sessão não foi invalidada no servidor — achado.)*
4. **Fechar o navegador inteiro** e reabrir. O cookie voltou? Confrontar com o atributo `Expires`/`Max-Age` observado no `Set-Cookie`.
5. Se o navegador estiver configurado para restaurar abas, repetir com a opção desligada e comparar.

**Discussão:** conectar diretamente à matriz de atributos do cookie preenchida no material de HTTP. Qual atributo explica cada resultado?

### Lab 4 — Escopo de domínio (opcional, se houver subdomínios no ambiente)
**Objetivo:** ver o escopo frouxo do cookie na prática.

1. Observar o atributo `Domain` do cookie de sessão.
2. Verificar no Burp se ele é enviado a subdomínios distintos.
3. Propor a correção: `Domain` restrito e prefixo `__Host-`.

---

## 8. Fechamento defensivo

Todo laboratório termina com remediação. Para este bloco:

- **Escolha de armazenamento do token:** justificar cookie `HttpOnly` + `SameSite` + defesa CSRF, *versus* `localStorage` + defesa rigorosa contra XSS. Não existe resposta única — exige-se a justificativa do trade-off.
- **Invalidação de sessão no servidor** no logout, e não apenas remoção do cookie.
- **`Cache-Control: no-store`** em respostas autenticadas.
- **Escopo mínimo:** `Domain` restrito, prefixo `__Host-`, tempo de vida curto.
- **Orientação ao usuário final** (relevante em serviços com certificado digital): encerrar o navegador, e não apenas a aba.

---

## 9. Uso ético de IA neste material

- **Uso legítimo:** pedir ao modelo que **explique** o modelo de escopo de cada armazenamento; que **critique** a tabela de inventário do Lab 1; que ajude a **argumentar o trade-off** da Seção 8.
- **Uso vedado:** pedir scripts prontos de exfiltração de armazenamento ou de sequestro de sessão.

Toda interação que influenciar o trabalho vai no **Registro de Colaboração com IA**, anexo obrigatório.

---

## 10. Referências

- WHATWG — HTML Living Standard (*Web Storage*) e **Storage Standard**
- IETF — RFC 6265 e o rascunho 6265bis (cookies)
- Especificação do IndexedDB; especificação de *Service Workers* (Cache Storage)
- MDN Web Docs — *Client-side storage*, *Same-origin policy*
- OWASP Cheat Sheet Series — *Session Management*, *HTML5 Security*
- Documentação do Burp Suite e do DevTools (aba *Application*)

> **Nota ao docente:** particionamento de armazenamento, política de cookies de terceiros e detalhes de BFCache mudam com frequência e divergem entre navegadores. Verifique o estado atual e o comportamento do navegador adotado no laboratório antes da aula.
