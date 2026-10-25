# HTTP na Prática: Cabeçalhos, Cookies e Exploração com Burp Suite
### Material de aula — Bloco II — Segurança Ofensiva em Aplicações Web

> **Escopo.** Todas as atividades deste material são feitas **exclusivamente** em alvos de laboratório autorizados (OWASP Juice Shop, DVWA, WebGoat ou contêineres providos pelo docente). Nada aqui deve ser aplicado a sistemas de terceiros.

---

## 1. Por que começar pelo HTTP

Antes de qualquer vulnerabilidade, o estudante precisa **ler uma conversa HTTP crua** e entender o que cada linha significa. Toda falha de aplicação web se manifesta em uma mensagem HTTP — na requisição que sai do cliente ou na resposta que volta do servidor. Quem lê essas mensagens com fluência já enxerga metade da superfície de ataque.

**Princípio que orienta o material inteiro:** existem centenas de cabeçalhos. Você não decora a lista. Você aprende a fazer, diante de qualquer cabeçalho, duas perguntas:

1. **Quem controla este valor?** (o cliente, o servidor, um proxy no caminho?)
2. **O que o servidor faz com ele?** (confia? usa para decidir acesso? reflete de volta?)

Quando o valor é controlado pelo cliente **e** o servidor confia nele para uma decisão, existe uma vulnerabilidade em potencial.

---

## 2. Anatomia da mensagem HTTP

Toda mensagem HTTP tem a mesma estrutura:

```
LINHA INICIAL          (requisição: método + caminho + versão / resposta: versão + status)
CABEÇALHOS             (uma por linha, nome: valor)
<linha em branco>
CORPO                  (opcional)
```

**Exemplo de requisição:**

```http
POST /rest/user/login HTTP/1.1
Host: loja.exemplo
Cookie: session=a1b2c3...
Content-Type: application/json
Content-Length: 47

{"email":"ana@exemplo","password":"senha123"}
```

**Exemplo de resposta:**

```http
HTTP/1.1 200 OK
Set-Cookie: session=x9y8z7...; Secure; HttpOnly; SameSite=Lax
Content-Type: application/json
Content-Security-Policy: default-src 'self'

{"authentication":{"token":"..."}}
```

**Primeira atividade (antes de qualquer ferramenta gráfica):** os alunos leem essa estrutura crua no histórico do Burp Proxy. Só depois passam às ferramentas.

---

## 3. Cabeçalhos de requisição (cliente → servidor)

O cliente controla **todos** estes valores. Essa é a lente de leitura.

| Cabeçalho | O que carrega | Nuance de segurança |
|---|---|---|
| `Host` | Domínio pretendido | Base do *Host header injection* e de envenenamento de cache quando a aplicação o usa para montar links ou validar acesso. |
| `Authorization` | Credencial (Basic, Bearer) | `Basic` é **Base64 — codificação, não criptografia**. Decodificar no Decoder é um momento didático forte. |
| `Cookie` | Estado da sessão | O cabeçalho que mais carrega identidade. Tratado em detalhe na Seção 6. |
| `Referer` | Origem da navegação | Vaza contexto para terceiros; aplicações que o usam como controle de acesso confiam em dado do cliente. |
| `User-Agent` | Identificação do cliente | Totalmente forjável. Lógica que ramifica por ele cria superfície de ataque. |
| `Content-Type` | Formato do corpo | Trocar `application/json` por outro tipo pode mudar o parser do servidor e revelar caminhos alternativos. |
| `X-Forwarded-For` | IP original atrás de proxy | Injetável pelo cliente. Usado para *rate limiting* ou allowlist de IP, quebra por completo. |
| `Origin` | Origem cross-site | Chave para entender CORS e CSRF. |
| `Range` | Faixa de bytes solicitada | Historicamente ligado a falhas de exaustão de recursos. |

---

## 4. Cabeçalhos de resposta (servidor → cliente)

Aqui a leitura se inverte: o que o servidor **deixou de enviar** costuma ser o achado.

| Cabeçalho | O que carrega | Nuance de segurança |
|---|---|---|
| `Set-Cookie` | Emissão de cookie e atributos | Núcleo da Seção 6. |
| `Strict-Transport-Security` | Obrigatoriedade de HTTPS | Ausência permite rebaixamento para HTTP na primeira visita. |
| `Content-Security-Policy` | Origens permitidas para scripts | Mitigação principal de XSS. `unsafe-inline` dá falsa sensação de proteção. |
| `X-Content-Type-Options` | Bloqueio de *MIME sniffing* | Ausência transforma upload de arquivo em vetor de execução. |
| `X-Frame-Options` / `frame-ancestors` | Permissão de enquadramento | Defesa contra clickjacking. |
| `Access-Control-Allow-Origin` | Política CORS | Refletir a `Origin` do cliente com `Allow-Credentials: true` é falha grave e comum. |
| `Server`, `X-Powered-By` | Tecnologia e versão | Vazamento de informação que orienta o atacante. Mapeia a A02 — Security Misconfiguration. |
| `Cache-Control` | Política de cache | Resposta autenticada cacheável em proxy compartilhado vaza dados entre usuários. |
| `Location` | Destino de redirecionamento | Base do *open redirect* quando o destino vem de parâmetro controlado. |

**Códigos de status como sinal.** Ler status como oráculo: a diferença entre `401`, `403` e `404` costuma revelar se um recurso existe; comportamento distinto entre `200` e `302` em telas de login permite enumeração de usuários.

---

## 5. Explorando cabeçalhos com o Burp Suite

Cada ferramenta do Burp tem um papel. O quadro abaixo liga **objetivo → ferramenta → o que observar**.

### 5.1 Proxy — observar
- **O quê:** capturar o tráfego real do navegador e ler as mensagens cruas.
- **Como:** configurar o navegador para o proxy do Burp, instalar o certificado CA, navegar pelo alvo e examinar o **HTTP history**.
- **Observar:** quais cabeçalhos o navegador envia sozinho; quais o servidor devolve; o que está **ausente** nas respostas (HSTS, CSP, `X-Content-Type-Options`).
- **Exercício:** montar a tabela *cabeçalho → quem controla → o que aconteceria se fosse alterado*.

### 5.2 Repeater — testar hipóteses uma a uma
- **O quê:** reenviar uma requisição com modificações controladas e comparar respostas.
- **Como:** enviar uma requisição do histórico para o Repeater (`Ctrl+R`), alterar **um** cabeçalho por vez, reenviar.
- **Observar:**
  - Alterar `Host` → a aplicação reflete o valor em links ou muda o comportamento?
  - Forjar `X-Forwarded-For` → some algum bloqueio por IP?
  - Remover `Authorization` ou `Cookie` → a resposta continua expondo dados?
  - Trocar `Content-Type` → o servidor aceita outro parser?
- **Regra:** um cabeçalho por teste. Mudar vários de uma vez esconde qual causou o efeito.

### 5.3 Decoder — revelar o que está codificado
- **O quê:** decodificar valores que parecem opacos.
- **Como:** colar o valor e aplicar Base64, URL, hex.
- **Observar:** `Authorization: Basic` revela usuário:senha; um valor de cookie pode revelar campos internos ou um JWT (cujo cabeçalho e payload são Base64URL legíveis).

### 5.4 Comparer — enxergar diferenças sutis
- **O quê:** comparar duas respostas byte a byte.
- **Como:** enviar duas respostas ao Comparer e usar a visão *words*.
- **Observar:** por que `usuario-existe` e `usuario-inexistente` respondem diferente; que cabeçalho ou trecho de corpo denuncia a enumeração.

### 5.5 Intruder — variar de forma sistemática (uso básico)
- **O quê:** repetir uma requisição variando um ponto de injeção com uma lista.
- **Como:** marcar a posição, carregar uma lista pequena e controlada, observar tamanho e status das respostas.
- **Observar:** anomalias de tamanho/status que se destacam do padrão.
- **Cuidado didático:** na Community Edition o Intruder é limitado (*throttled*). Use listas curtas — o objetivo é **entender o método**, não gerar volume.

---

## 6. Anatomia do cookie

### 6.1 O que é
Um par `nome=valor` que o servidor emite via `Set-Cookie` e o navegador devolve automaticamente a cada requisição para o domínio correspondente. Existe porque **HTTP é *stateless***: o cookie é a memória que o protocolo não tem.

### 6.2 Uso legítimo — o percurso de um comprador
Vale percorrer o caso concreto de uma loja online, porque mostra que o cookie é **infraestrutura de negócio** antes de ser alvo:

1. Visitante anônimo chega → a loja emite um identificador de sessão e associa um carrinho vazio **no servidor**.
2. Itens adicionados → **o carrinho vive no servidor**; o cookie carrega apenas a chave que o localiza.
3. Login → o servidor **rotaciona o identificador de sessão** (defesa contra *session fixation*) e vincula a sessão à conta.
4. Checkout → a sessão autentica cada passo; o cookie **nunca** carrega dado de pagamento.
5. Logout ou expiração → o servidor **invalida a sessão do seu lado**. Apagar o cookie no navegador não basta.

**Contraste central:** um cookie bem projetado é uma **referência opaca**; um cookie mal projetado é um **dado de confiança entregue ao cliente**. Um cookie `role=user` ou `user_id=1042` é o segundo caso — e é exatamente o que o laboratório de Broken Access Control vai explorar.

### 6.3 Atributos e o que cada um protege

| Atributo | Função | O que quebra se ausente ou errado |
|---|---|---|
| `Secure` | Só trafega sobre HTTPS | Cookie exposto em rede não confiável |
| `HttpOnly` | Invisível ao JavaScript | XSS passa a permitir roubo direto de sessão |
| `SameSite` (`Strict`/`Lax`/`None`) | Envio em contexto cross-site | `None` sem necessidade reabre a porta para CSRF |
| `Domain` | Escopo de domínio | Escopo amplo compartilha a sessão com subdomínios menos confiáveis |
| `Path` | Escopo de caminho | Isolamento insuficiente entre aplicações no mesmo host |
| `Expires` / `Max-Age` | Tempo de vida | Sessão eterna anula o logout e amplia a janela de roubo |
| `__Host-` / `__Secure-` | Garantias impostas pelo navegador | Sem eles, subdomínio comprometido pode sobrescrever o cookie |

### 6.4 Como se avalia se um cookie é frágil
Roteiro que o aluno aplica no laboratório, sempre em alvo autorizado:

1. **Inspecionar os atributos.** Faltam `Secure`, `HttpOnly` ou `SameSite`? A ausência já é achado (A02).
2. **Analisar a estrutura do valor.** É opaco e aleatório, ou codificado? Base64, hex e JWT são reconhecíveis de imediato — e frequentemente revelam campos internos.
3. **Avaliar a entropia.** Coletar várias emissões e comparar: valores sequenciais, com timestamp visível ou padrão previsível indicam identificadores forjáveis.
4. **Testar o significado semântico.** Se o valor contém papel ou identificador, alterá-lo e observar a resposta é o teste decisivo — *o servidor confia no cliente?*
5. **Verificar o ciclo de vida.** O identificador muda no login? A sessão antiga é invalidada no logout? Um cookie que ainda funciona após o logout é falha clássica.
6. **Verificar o escopo.** `Domain` mais amplo que o necessário; ausência de prefixo `__Host-`.

---

## 7. Explorando cookies com o Burp Suite

| Passo do roteiro (6.4) | Ferramenta do Burp | Procedimento e o que observar |
|---|---|---|
| Inspecionar atributos | **Proxy → HTTP history** | Ler o `Set-Cookie` na resposta de login. Anotar quais atributos existem e quais faltam. |
| Estrutura do valor | **Decoder** | Colar o valor e testar Base64/URL/hex. Um JWT se revela pelos três blocos separados por ponto. |
| Entropia | **Sequencer** | Capturar a resposta que emite o cookie, apontar o token e coletar uma amostra grande. O Sequencer estima a aleatoriedade; baixa entropia indica token previsível. |
| Significado semântico | **Repeater** | Alterar o valor (ex.: `role=user` → `role=admin`, ou incrementar um id) e reenviar. A mudança de resposta responde se o servidor confia no cliente. |
| Ciclo de vida | **Repeater + Proxy** | Capturar um cookie válido; fazer logout; reenviar a requisição antiga com o cookie no Repeater. Se ainda funciona, a sessão não foi invalidada. |
| Comparação de emissões | **Comparer** | Comparar vários valores emitidos em logins sucessivos para flagrar partes fixas vs. variáveis. |

**Atividade integradora (semana 4).** Cada dupla:
1. Captura o cookie de sessão do Juice Shop e preenche a matriz de atributos (6.3).
2. Decodifica o valor no Decoder e roda o Sequencer sobre uma amostra.
3. Escreve um parágrafo: *este cookie é referência opaca ou dado de confiança?*
4. Redige o `Set-Cookie` que a aplicação **deveria** emitir — fechamento defensivo já no Bloco II.

---

## 8. Uso ético de IA neste material

Este é o primeiro exercício do protocolo de IA da disciplina, e um bom lugar para calibrar a fronteira:

- **Uso legítimo e incentivado:** pedir ao modelo que **explique** o papel de cada atributo de cookie ou cabeçalho; que **critique** a análise do aluno; que ajude a **redigir a remediação**.
- **Uso vedado:** pedir que gere ataques prontos de sequestro de sessão ou payloads para uso indiscriminado.

Toda interação com IA que influenciar o trabalho vai no **Registro de Colaboração com IA**, anexo obrigatório do relatório. A diferença entre "explique por que este cookie é frágil" e "me dê o exploit" fica concreta aqui, na quarta semana — antes do primeiro laboratório.

---

## 9. Entrega do Bloco II

Relatório curto (2–3 páginas) contendo:
- **(a)** três requisições manipuladas no Repeater, com evidência e explicação do efeito de cada cabeçalho alterado;
- **(b)** a dissecação completa de um cookie de sessão capturado no laboratório: matriz de atributos, resultado do Decoder e do Sequencer, veredito *opaco vs. confiança*, e o `Set-Cookie` corrigido;
- **(c)** o Registro de Colaboração com IA.

---

## 10. Referências

- MDN Web Docs — HTTP headers e HTTP cookies
- OWASP Web Security Testing Guide (WSTG) — seções de sessão e cabeçalhos
- OWASP Cheat Sheet Series — *Session Management* e *HTTP Security Response Headers*
- PortSwigger Web Security Academy — labs de gestão de sessão
- Documentação do Burp Suite — Proxy, Repeater, Decoder, Comparer, Sequencer, Intruder
