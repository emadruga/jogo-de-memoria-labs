// script.js
document.addEventListener('DOMContentLoaded', () => {
    const MAX_TIME = 120;

    const symbols = ['🍎', '🍌', '🍇', '🍉', '🍓', '🍒', '🥝', '🍍'];
    const cardArray = symbols.flatMap((symbol) => [
        { name: symbol, img: symbol },
        { name: symbol, img: symbol },
    ]);

    const gameBoard = document.getElementById('game-board');
    const novaPartidaButton = document.getElementById('nova-partida-button');
    const historicoButton = document.getElementById('historico-button');
    const rankingButton = document.getElementById('ranking-button');
    const offlineButton = document.getElementById('offline-button');
    const temaButton = document.getElementById('tema-button');
    const logoutButton = document.getElementById('logout-button');
    const timerEl = document.getElementById('timer');
    const playerInfoEl = document.getElementById('player-info');
    const historicoPanel = document.getElementById('historico-panel');
    const historicoList = document.getElementById('historico-list');
    const rankingPanel = document.getElementById('ranking-panel');
    const rankingList = document.getElementById('ranking-list');
    const loginModal = document.getElementById('login-modal');
    const loginForm = document.getElementById('login-form');
    const loginErro = document.getElementById('login-erro');

    let cardsChosen = [];
    let cardsChosenId = [];
    let cardsMatched = [];
    let timeElapsed = 0;
    let timer = null;
    let gameEnded = false;
    let usuarioAtual = null;

    // --- IndexedDB: cópia local do histórico, para consulta rápida (S4.2/S4.4) ---
    const IDB_NOME = 'jogoDaMemoriaLocal';
    const IDB_STORE = 'historico_local';

    function abrirIndexedDB() {
        return new Promise((resolve, reject) => {
            const req = indexedDB.open(IDB_NOME, 1);
            req.onupgradeneeded = () => {
                const db = req.result;
                if (!db.objectStoreNames.contains(IDB_STORE)) {
                    db.createObjectStore(IDB_STORE, { keyPath: 'id' });
                }
            };
            req.onsuccess = () => resolve(req.result);
            req.onerror = () => reject(req.error);
        });
    }

    async function salvarHistoricoLocal(registros) {
        const db = await abrirIndexedDB();
        const tx = db.transaction(IDB_STORE, 'readwrite');
        const store = tx.objectStore(IDB_STORE);
        registros.forEach((r) => store.put(r));
        return new Promise((resolve) => { tx.oncomplete = resolve; });
    }

    async function limparHistoricoLocal() {
        const db = await abrirIndexedDB();
        const tx = db.transaction(IDB_STORE, 'readwrite');
        tx.objectStore(IDB_STORE).clear();
        return new Promise((resolve) => { tx.oncomplete = resolve; });
    }

    // --- Tema: preferência não sensível, guardada só no cliente (S1.2/S4.4) ---
    // A chave 'tema' em localStorage só passa a existir depois que o jogador alterna o tema.

    const TEMA_CHAVE = 'tema';

    function lerTemaSalvo() {
        try {
            return localStorage.getItem(TEMA_CHAVE) === 'escuro' ? 'escuro' : 'claro';
        } catch (err) {
            return 'claro';
        }
    }

    function aplicarTema(tema) {
        document.documentElement.dataset.tema = tema;
        temaButton.textContent = `Tema: ${tema}`;
    }

    temaButton.addEventListener('click', () => {
        const novo = document.documentElement.dataset.tema === 'escuro' ? 'claro' : 'escuro';
        aplicarTema(novo);
        try {
            localStorage.setItem(TEMA_CHAVE, novo);
        } catch (err) {
            console.error('Não foi possível gravar o tema:', err);
        }
    });

    aplicarTema(lerTemaSalvo());

    // --- Autenticação ---

    async function verificarSessao() {
        try {
            const resp = await fetch('/api/me');
            if (!resp.ok) return null;
            const data = await resp.json();
            return data.usuario_id;
        } catch (err) {
            return null;
        }
    }

    function updatePlayerInfo(usuarioId) {
        playerInfoEl.textContent = usuarioId ? `Jogando como: ${usuarioId}` : '';
    }

    function abrirLoginModal() {
        loginModal.classList.add('visible');
    }

    function fecharLoginModal() {
        loginModal.classList.remove('visible');
    }

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        loginErro.textContent = '';
        const usuario = document.getElementById('login-usuario').value.trim();
        const senha = document.getElementById('login-senha').value;

        try {
            const resp = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ usuario, senha }),
            });
            if (!resp.ok) {
                loginErro.textContent = 'Usuário ou senha inválidos.';
                return;
            }
            usuarioAtual = usuario;
            updatePlayerInfo(usuarioAtual);
            fecharLoginModal();
            loginForm.reset();
            await iniciarPartida();
        } catch (err) {
            loginErro.textContent = 'Erro ao entrar. Tente novamente.';
        }
    });

    logoutButton.addEventListener('click', async () => {
        clearInterval(timer);
        try {
            await fetch('/api/logout', { method: 'POST' });
        } catch (err) {
            // segue mesmo se falhar — o objetivo do lab é observar o resultado, não garantir sucesso
        }
        try {
            const resp = await fetch('/api/config');
            const config = await resp.json();
            if (config.limpar_historico_local_no_logout) {
                await limparHistoricoLocal();
            }
            // Se a config indicar que não deve limpar (cenário vulnerável do S4.4),
            // o IndexedDB local é deliberadamente preservado — é o que o lab observa.
        } catch (err) {
            console.error('Erro ao consultar config:', err);
        }
        usuarioAtual = null;
        updatePlayerInfo(null);
        gameBoard.innerHTML = '';
        historicoPanel.classList.add('hidden');
        rankingPanel.classList.add('hidden');
        abrirLoginModal();
    });

    // --- Tabuleiro ---

    function shuffle(array) {
        return array.sort(() => 0.5 - Math.random());
    }

    function createBoard() {
        gameBoard.innerHTML = '';
        shuffle(cardArray);
        cardArray.forEach((card, index) => {
            const cardElement = document.createElement('div');
            cardElement.setAttribute('class', 'card');
            cardElement.setAttribute('data-id', index);

            const frontFace = document.createElement('div');
            frontFace.classList.add('card-content', 'front');
            cardElement.appendChild(frontFace);

            const backFace = document.createElement('div');
            backFace.classList.add('card-content', 'back');
            backFace.textContent = card.img;
            cardElement.appendChild(backFace);

            cardElement.addEventListener('click', flipCard);
            gameBoard.appendChild(cardElement);
        });
        startTimer();
    }

    function checkForMatch() {
        const cards = document.querySelectorAll('.card');
        const [optionOneId, optionTwoId] = cardsChosenId;

        if (cardsChosen[0] === cardsChosen[1]) {
            cards[optionOneId].classList.add('matched');
            cards[optionTwoId].classList.add('matched');
            cardsMatched.push(cardsChosen);
        } else {
            cards[optionOneId].classList.remove('flipped');
            cards[optionTwoId].classList.remove('flipped');
        }

        cardsChosen = [];
        cardsChosenId = [];

        if (cardsMatched.length === cardArray.length / 2) {
            endGame('🎉 Parabéns! Você encontrou todos os pares! 🎉');
        }
    }

    function flipCard() {
        if (gameEnded) return;
        let cardId = this.getAttribute('data-id');
        if (!cardsChosenId.includes(cardId) && !this.classList.contains('matched')) {
            cardsChosen.push(cardArray[cardId].name);
            cardsChosenId.push(cardId);
            this.classList.add('flipped');
            if (cardsChosen.length === 2) {
                setTimeout(checkForMatch, 500);
            }
        }
    }

    function startTimer() {
        clearInterval(timer);
        timeElapsed = 0;
        updateTimerDisplay();
        timer = setInterval(() => {
            timeElapsed++;
            updateTimerDisplay();
            if (timeElapsed >= MAX_TIME) {
                endGame('⏰ Tempo esgotado! Fim de jogo! ⏰');
            }
        }, 1000);
    }

    function updateTimerDisplay() {
        timerEl.textContent = `Tempo: ${timeElapsed} segundos`;
    }

    function endGame(message) {
        if (gameEnded) return;
        gameEnded = true;
        clearInterval(timer);
        setTimeout(() => alert(message), 300);
        submitScore();
    }

    async function iniciarPartida() {
        cardsChosen = [];
        cardsChosenId = [];
        cardsMatched = [];
        gameEnded = false;
        try {
            await fetch('/api/partida/iniciar', { method: 'POST' });
        } catch (err) {
            console.error('Erro ao iniciar partida no servidor:', err);
        }
        createBoard();
    }

    async function submitScore() {
        try {
            const resp = await fetch('/api/partida/resultado', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pontos: cardsMatched.length,
                    tempo_s: timeElapsed,
                }),
            });
            if (resp.ok) {
                await carregarRanking();
            }
        } catch (err) {
            console.error('Erro ao enviar pontuação:', err);
        }
    }

    // --- Histórico e ranking ---

    async function carregarHistorico() {
        try {
            const resp = await fetch('/api/historico');
            if (!resp.ok) return;
            const historico = await resp.json();
            renderHistorico(historico);
            await salvarHistoricoLocal(historico);
        } catch (err) {
            console.error('Erro ao carregar histórico:', err);
        }
    }

    function renderHistorico(historico) {
        historicoList.innerHTML = '';
        historico.forEach((entry) => {
            const li = document.createElement('li');
            const tempoTexto = entry.tempo_s != null ? ` em ${entry.tempo_s}s` : '';
            li.textContent = `${entry.pontos} pares${tempoTexto} — ${entry.data}`;
            historicoList.appendChild(li);
        });
    }

    async function carregarRanking() {
        try {
            const resp = await fetch('/api/ranking');
            const ranking = await resp.json();
            renderRanking(ranking);
        } catch (err) {
            console.error('Erro ao carregar ranking:', err);
        }
    }

    function renderRanking(ranking) {
        rankingList.innerHTML = '';
        ranking.forEach((entry) => {
            const li = document.createElement('li');
            const tempoTexto = entry.tempo_s != null ? ` em ${entry.tempo_s}s` : '';
            li.textContent = `${entry.nome} — ${entry.pontos} pares${tempoTexto}`;
            rankingList.appendChild(li);
        });
    }

    historicoButton.addEventListener('click', async () => {
        rankingPanel.classList.add('hidden');
        historicoPanel.classList.toggle('hidden');
        if (!historicoPanel.classList.contains('hidden')) {
            await carregarHistorico();
        }
    });

    rankingButton.addEventListener('click', async () => {
        historicoPanel.classList.add('hidden');
        rankingPanel.classList.toggle('hidden');
        if (!rankingPanel.classList.contains('hidden')) {
            await carregarRanking();
        }
    });

    novaPartidaButton.addEventListener('click', () => {
        clearInterval(timer);
        iniciarPartida();
    });

    // --- Modo de treino offline (Cache Storage + service worker, S4.3) ---

    offlineButton.addEventListener('click', async () => {
        if (!('serviceWorker' in navigator)) {
            alert('Este navegador não suporta o modo offline.');
            return;
        }
        try {
            await navigator.serviceWorker.register('/sw.js');
            alert('Treino offline ativado. Os recursos públicos foram cacheados — desligue a rede e recarregue para testar.');
        } catch (err) {
            console.error('Erro ao ativar treino offline:', err);
        }
    });

    // --- Inicialização ---

    (async () => {
        const usuarioId = await verificarSessao();
        if (usuarioId) {
            usuarioAtual = usuarioId;
            updatePlayerInfo(usuarioAtual);
            await iniciarPartida();
        } else {
            abrirLoginModal();
        }
    })();
});
