# Instalar o ambiente de laboratório

### Guia do aluno — o que baixar e instalar antes da Semana 1

Este guia cobre **só a instalação das ferramentas**. O que fazer com elas está nos laboratórios de
cada semana, a partir de [`S1.1`](labs/S1.1-ler-http-cru.md). Se algo aqui já estiver instalado (ex.:
você já tem o Burp ou o Docker de outra disciplina), pule a etapa.

---

## O que você vai instalar

| Ferramenta | Para quê | Usada a partir de |
|---|---|---|
| **Git** | Baixar e atualizar o material do laboratório | Antes da Semana 1 |
| **Python 3.10+** | Rodar o jogo da memória localmente (`jogo-da-memoria/`) | Semana 1 |
| **Docker Desktop** | Alternativa ao Python para rodar o jogo da memória; obrigatório para o Juice Shop na Semana 5 | Semana 1 (opcional) / Semana 5 (obrigatório) |
| **Burp Suite Community Edition** | Interceptar e manipular tráfego HTTP | Semana 1 |
| **Navegador com perfil dedicado** | Isolar o laboratório do seu uso pessoal do navegador | Semana 1 |

Todas as ferramentas são gratuitas. Nenhuma exige licença paga para este curso.

---

## 1. Git

Usado para clonar o repositório do material e buscar atualizações ao longo do curso.

**macOS:** já vem instalado. Confirme abrindo o Terminal e digitando:
```bash
git --version
```
Se não estiver instalado, o próprio macOS oferece instalar as "Command Line Tools" na primeira vez
que você roda `git`.

**Windows:** baixe o [Git for Windows](https://git-scm.com/download/win) e instale com as opções
padrão. Isso também instala o **Git Bash**, um terminal compatível com os comandos deste guia —
use-o em vez do PowerShell para os comandos abaixo.

**Linux (Debian/Ubuntu):**
```bash
sudo apt update && sudo apt install git
```

### Clonar o repositório

```bash
git clone <URL do repositório fornecida pelo docente>
cd <pasta do repositório clonado>
```

Se o docente distribuir o material por outro meio (pendrive, zip), pule o `git clone` e apenas
extraia o material — mas combine com o docente como vai receber **atualizações** ao longo do curso.

---

## 2. Python 3

Necessário para rodar o jogo da memória (`jogo-da-memoria/server.py`) diretamente, sem Docker. Não
precisa de nenhuma biblioteca externa (`pip install`) — só o Python puro.

**macOS:** já vem instalado, mas normalmente numa versão antiga. Confirme a versão:
```bash
python3 --version
```
Se for menor que 3.10, instale uma versão atual com o [instalador oficial](https://www.python.org/downloads/macos/)
ou via [Homebrew](https://brew.sh/): `brew install python3`.

**Windows:** baixe o [instalador oficial](https://www.python.org/downloads/windows/). Na primeira
tela do instalador, **marque a caixa "Add python.exe to PATH"** antes de clicar em instalar — é o
erro mais comum de quem instala Python no Windows.

**Linux (Debian/Ubuntu):** geralmente já vem instalado. Confirme com `python3 --version`; se faltar,
`sudo apt install python3`.

Se preferir **não instalar Python** e usar só Docker, pule esta etapa — a Seção 4 abaixo mostra como
rodar o jogo da memória via container.

---

## 3. Docker Desktop

Necessário para o **Juice Shop** (Semana 5, lab `S5.1`) e é uma alternativa ao Python para rodar o
jogo da memória (Semanas 1–4).

**macOS e Windows:** baixe o [Docker Desktop](https://www.docker.com/products/docker-desktop/) e
instale com as opções padrão. No Windows, o instalador pode pedir para habilitar o **WSL 2**
(Windows Subsystem for Linux) — aceite, é um requisito do Docker Desktop no Windows, não algo
específico deste curso.

**Linux:** siga o guia oficial de instalação do [Docker Engine](https://docs.docker.com/engine/install/)
para a sua distribuição. Depois, adicione seu usuário ao grupo `docker` para não precisar de `sudo`
em todo comando:
```bash
sudo usermod -aG docker $USER
```
(É preciso encerrar a sessão e entrar de novo para o grupo valer.)

### Confirmar que está funcionando

Abra o Docker Desktop (ou, no Linux, confirme que o serviço está ativo) e rode:
```bash
docker run hello-world
```
Se aparecer uma mensagem começando com "Hello from Docker!", está pronto.

---

## 4. Rodar o jogo da memória — confira antes da Semana 1

Duas formas, escolha uma (não precisa das duas):

### Opção A — Python direto

```bash
cd jogo-da-memoria
python3 db.py
python3 server.py
```

Acesse `http://localhost:3000` no navegador. Se a página do jogo carregar, está pronto. Pare o
servidor com `Ctrl+C`.

### Opção B — Docker

```bash
cd jogo-da-memoria
docker build -t jogo-da-memoria .
docker run --rm -p 3000:3000 jogo-da-memoria
```

Acesse `http://localhost:3000`. Pare o container com `Ctrl+C` no terminal onde ele está rodando.

Detalhes de como alternar entre a versão vulnerável e a robusta (usadas lab a lab) estão no
[`README.md`](jogo-da-memoria/README.md) daquele diretório — não precisa ler agora, só confirmar que
uma das duas opções acima funciona na sua máquina.

---

## 5. Burp Suite Community Edition

Se você já tem o Burp Suite Community instalado, não precisa repetir.

1. Baixe em [portswigger.net/burp/communitydownload](https://portswigger.net/burp/communitydownload)
   (escolha Community Edition — é gratuita; não confunda com Professional).
2. Instale com as opções padrão.
3. Na primeira execução, configure o proxy do navegador para apontar para o Burp (normalmente
   `127.0.0.1:8080`) e instale o **certificado CA** do Burp no navegador — o roteiro exato está no
   material [HTTP na Prática](docs/http-headers-cookies-burp.md), Seção 2, e é reforçado no lab
   [`S1.1`](labs/S1.1-ler-http-cru.md).

---

## 6. Perfil de navegador dedicado ao laboratório

Antes da Semana 1, crie um **perfil separado** do navegador (Chrome, Firefox ou Edge) só para os
laboratórios — não seu perfil pessoal com e-mail, senhas e histórico reais.

- **Chrome/Edge:** ícone de perfil no canto superior direito → "Adicionar perfil".
- **Firefox:** digite `about:profiles` na barra de endereço → "Criar novo perfil".

Use esse perfil exclusivamente para os laboratórios, com o proxy do Burp configurado e o
certificado CA instalado **só nele**. Isso evita capturar tráfego de contas e serviços reais no
histórico do Burp, e mantém cookies/localStorage do laboratório isolados do seu uso pessoal.

---

## Checklist antes da Semana 1

- [ ] `git --version` funciona, e o repositório do material está clonado.
- [ ] `python3 --version` mostra 3.10 ou mais recente — **ou** `docker run hello-world` funciona.
- [ ] O jogo da memória sobe (Opção A ou B da Seção 4) e `http://localhost:3000` carrega no
      navegador.
- [ ] Burp Suite Community instalado, certificado CA instalado no **perfil de laboratório** do
      navegador (não no perfil pessoal).
- [ ] Perfil de navegador dedicado ao laboratório criado.

Se algum item falhar, procure o docente **antes** da primeira aula prática — a Semana 1 pressupõe
que o ambiente já está de pé.
