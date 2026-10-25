# S1-Roteiro — Vídeo da Semana 1

### Laboratório filmado: **S1.3 — Cache HTTP e revalidação** · 5 min

> **Escopo.** Exclusivamente no jogo da memória local e autorizado.

Antes de gravar, faça o [S1.3](S1.3-cache-http.md) inteiro, sem gravar. O vídeo é a demonstração
de quem já entendeu, não a primeira tentativa.

---

## Valor individual

Seu **marcador** é o número formado pelos **dois últimos dígitos da sua matrícula** (`NN`). Você o
usa como parâmetro de consulta em um dos recursos (`/script.js?v=NN`), conforme o segmento 3.

---

## Segmentos

| Tempo | O que fazer e dizer |
|---|---|
| **0:00–0:30** | Identificação (nome, matrícula, S1.3, versão do alvo, relógio visível). |
| **0:30–1:00** | **Previsão, antes de recarregar:** para `/`, `/styles.css` e `/script.js`, diga qual dos três comportamentos (a, b ou c do enunciado) você espera no segundo acesso e por quê. |
| **1:00–3:30** | **Execução sem cortes.** Network e Burp visíveis lado a lado. (1) Limpe os históricos e carregue a página; mostre `Cache-Control` e `ETag` dos três recursos. (2) Recarregue normalmente; mostre, para cada recurso, o que o Network indica e se o Burp registrou ou não uma requisição. (3) Peça `/script.js?v=NN` duas vezes seguidas e mostre o comportamento de cada pedido. |
| **3:30–4:30** | **Conclusão com evidência.** Diga em que caso (a/b/c) caiu cada um dos três recursos **apontando o cabeçalho** que explica a diferença. Compare com sua previsão: onde errou, se errou. Diga o que aconteceu com `?v=NN` e por quê. |
| **4:30–5:00** | **Fechamento defensivo + registro de IA.** Qual `Cache-Control` você usaria para uma resposta com dado privado de usuário e por quê; que sinal de detecção faria sentido (ou por que aqui não há). Registro de Colaboração com IA. |

O S1.3 é de observação pura: **não há versão vulnerável × robusta** nesta semana. Mostre a versão
indicada pelo docente.

---

## Pergunta de transferência (responda dentro do segmento 4:30–5:00)

- **Matrícula terminada em dígito par:** uma resposta `304` traz corpo? Então por que ela ainda
  conta como comunicação com o servidor?
- **Matrícula terminada em dígito ímpar:** se o `ETag` de `/script.js` fosse o mesmo para conteúdos
  diferentes, o que quebraria para o usuário?

---

## Checklist antes de enviar

- [ ] Identificação e relógio nos primeiros 30 s
- [ ] Previsão dita **antes** do recarregamento
- [ ] Segmento de execução contínuo, com Network **e** Burp visíveis
- [ ] `?v=NN` com os **seus** dois dígitos
- [ ] Os três recursos classificados com o cabeçalho apontado
- [ ] Defesa, pergunta de transferência e registro de IA
- [ ] Duração ≤ 5:00
