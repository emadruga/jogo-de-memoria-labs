# S4-Roteiro — Vídeo da Semana 4

### Laboratório filmado: **S4.4 — Caso: histórico privado residual** · 5 min

> **Escopo.** Exclusivamente no jogo da memória, versões vulnerável e robusta, perfil de navegador
> de laboratório. Nunca inspecione o perfil de navegador de outra pessoa.

Antes de gravar, faça o [S4.4](S4.4-caso-historico-residual.md) inteiro, sem gravar, e tenha
concluído o [S4.2](S4.2-indexeddb-via-script.md).

---

## Valor individual

A **partida que você jogou durante a gravação** tem um registro com carimbo de data e hora próprio
no IndexedDB. Esse registro é sua marca: o mesmo carimbo deve aparecer antes e depois do logout, e
precisa coincidir com o relógio do sistema visível na tela.

Defina também o **tema** com um valor reconhecível antes do logout (por exemplo, o tema escuro),
para poder mostrar o que sobreviveu e o que não deveria.

---

## Segmentos

| Tempo | O que fazer e dizer |
|---|---|
| **0:00–0:30** | Identificação (nome, matrícula, S4.4, relógio visível). |
| **0:30–1:00** | **Previsão, antes de agir:** depois do logout de Ana, o que você espera encontrar no IndexedDB e no `localStorage`, nas duas versões? O que deveria permanecer e o que não? |
| **1:00–3:30** | **Execução sem cortes.** Versão vulnerável: login como Ana; defina o tema; jogue uma partida e abra **Meu histórico**; mostre o seu registro com carimbo no IndexedDB; logout; atualize a visualização; login como Bruno **no mesmo perfil**. Mostre separadamente: (a) o registro ainda está na base? (b) a interface o mostra a Bruno? Repita o percurso na versão robusta, incluindo a chave do tema. |
| **3:30–4:30** | **Conclusão com evidência.** Diferencie "escondido na interface" de "removido da base" com o que a tela mostrou. Diga o que sobreviveu e o que deveria ter sobrevivido em cada versão. Compare com sua previsão. |
| **4:30–5:00** | **Fechamento defensivo + registro de IA.** Remediação (o que apagar e o que preservar no logout) e a **limitação** da detecção por log de servidor para este caso. Registro de Colaboração com IA. |

---

## Pergunta de transferência (responda dentro do segmento 4:30–5:00)

- **Matrícula terminada em dígito par:** `Cache-Control: no-store` na resposta do histórico teria
  evitado o problema? Por quê?
- **Matrícula terminada em dígito ímpar:** se o histórico nunca fosse gravado no IndexedDB, o que
  melhoraria na segurança e o que se perderia na experiência do jogador?

---

## Checklist antes de enviar

- [ ] Identificação e relógio nos primeiros 30 s
- [ ] Previsão dita antes de agir
- [ ] Registro com **seu** carimbo de tempo visível antes e depois do logout
- [ ] Verificação de (a) existência na base e (b) exibição na interface, separadas
- [ ] Tema verificado nas duas versões
- [ ] Remediação, limitação da detecção, pergunta de transferência e registro de IA
- [ ] Duração ≤ 5:00
