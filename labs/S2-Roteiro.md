# S2-Roteiro — Vídeo da Semana 2

### Laboratório filmado: **S2.3 — Caso: logout incompleto** · 5 min

> **Escopo.** Exclusivamente no jogo da memória, versões vulnerável e robusta, conta fictícia de
> Ana. Reenvie apenas requisições da **sua** sessão.

Antes de gravar, faça o [S2.3](S2.3-caso-logout-incompleto.md) inteiro, sem gravar.

---

## Valor individual

Seu **identificador de sessão**: o cookie de sessão emitido no **seu** login é diferente do de
qualquer colega. Mostre na tela (em *Application → Cookies* ou no cabeçalho `Cookie` da requisição)
os **seis primeiros caracteres** do valor, antes do logout. Eles são sua marca de autoria: a mesma
sequência precisa aparecer na requisição que você reenviar depois.

---

## Segmentos

| Tempo | O que fazer e dizer |
|---|---|
| **0:00–0:30** | Identificação (nome, matrícula, S2.3, relógio visível). |
| **0:30–1:00** | **Previsão, antes de agir:** na versão vulnerável e na robusta, o que você espera que o servidor responda à requisição reenviada depois do logout? Diga a regra que está testando. |
| **1:00–3:30** | **Execução sem cortes.** Versão vulnerável: login como Ana; `GET /api/me` no Repeater com resposta autenticada e os 6 caracteres do cookie à vista; logout pela interface; cookie sumindo no navegador; reenvio da **mesma** requisição sem editar. Depois, repita na versão robusta. Em cada reenvio, mostre status e corpo. |
| **3:30–4:30** | **Conclusão com evidência.** Compare as duas versões apontando status e corpo. Responda: o que prova que foi o **servidor**, e não o navegador, quem decidiu? Compare com a previsão. |
| **4:30–5:00** | **Fechamento defensivo + registro de IA.** Remediação **e** detecção da versão vulnerável; confirme que na robusta o novo login de Ana ainda funciona. Registro de Colaboração com IA. |

---

## Pergunta de transferência (responda dentro do segmento 4:30–5:00)

- **Matrícula terminada em dígito par:** se o servidor passasse a expirar toda sessão em 5 minutos,
  isso substituiria a invalidação no logout? Por quê?
- **Matrícula terminada em dígito ímpar:** se a sessão fosse um token autocontido, validado só por
  assinatura e sem estado no servidor, o que tornaria o logout difícil de implementar?

---

## Checklist antes de enviar

- [ ] Identificação e relógio nos primeiros 30 s
- [ ] Previsão dita antes de agir
- [ ] Seis primeiros caracteres do **seu** cookie visíveis antes do logout
- [ ] Reenvio **sem edição**, nas **duas** versões, com status e corpo à vista
- [ ] Remediação e detecção ditas; nova autenticação na robusta confirmada
- [ ] Pergunta de transferência e registro de IA
- [ ] Duração ≤ 5:00
