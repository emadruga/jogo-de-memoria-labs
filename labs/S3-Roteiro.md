# S3-Roteiro — Vídeo da Semana 3

### Laboratório filmado: **S3.4 — Caso: pontuação inventada** · 5 min

> **Escopo.** Exclusivamente no jogo da memória, versões vulnerável e robusta. Altere apenas a
> **sua** requisição de resultado.

Antes de gravar, faça o [S3.4](S3.4-caso-pontuacao-inventada.md) inteiro, sem gravar. A interceptação
no Burp exige ajuste prévio: confirme com o docente.

---

## Valor individual

No lugar do `9999` do enunciado, use como pontuação inventada os **quatro últimos dígitos da sua
matrícula**. Eles devem aparecer (1) na requisição alterada no Intercept e (2) no ranking, se
persistidos.

---

## Segmentos

| Tempo | O que fazer e dizer |
|---|---|
| **0:00–0:30** | Identificação (nome, matrícula, S3.4, relógio visível). |
| **0:30–1:00** | **Previsão, antes de agir:** quem você espera que decida a pontuação publicada, nas duas versões? O que deve aparecer no ranking? |
| **1:00–3:30** | **Execução sem cortes.** Versão vulnerável: partida até faltar um par; *Intercept on*; último par; mostre o `POST` parado com o valor original e **altere só o número**, para os seus quatro dígitos; *Forward*; *Intercept off*; consulte o ranking. Repita na versão robusta e registre também uma partida legítima. |
| **3:30–4:30** | **Conclusão com evidência.** Mostre lado a lado valor original, valor alterado e valor no ranking, nas duas versões. Explique: este problema é de criptografia ou de **onde a regra é aplicada**? Compare com a previsão. |
| **4:30–5:00** | **Fechamento defensivo + registro de IA.** O que o servidor deve fazer em vez de aceitar o número; que sinal de log detectaria uma pontuação divergente. Registro de Colaboração com IA. |

---

## Pergunta de transferência (responda dentro do segmento 4:30–5:00)

- **Matrícula terminada em dígito par:** um limite máximo de pontos resolveria o problema? E uma
  pontuação falsa, mas plausível, como 7 pares em vez de 8?
- **Matrícula terminada em dígito ímpar:** se o navegador assinasse o corpo da requisição com uma
  chave embutida no `script.js`, o servidor poderia confiar no número? Por quê?

---

## Checklist antes de enviar

- [ ] Identificação e relógio nos primeiros 30 s
- [ ] Previsão dita antes de agir
- [ ] Valor original e **seus quatro dígitos** visíveis no Intercept
- [ ] Ranking consultado depois, nas **duas** versões, e uma partida legítima registrada na robusta
- [ ] Remediação e detecção ditas
- [ ] Pergunta de transferência e registro de IA
- [ ] Duração ≤ 5:00
