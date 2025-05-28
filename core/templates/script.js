class NewsGenerator {
    constructor() {
        this.elements = {
            searchInput: document.getElementById('search-input'),
            searchBtn: document.getElementById('search-btn'),
            //trendingBtn: document.getElementById('trending-btn'),
            historyLimit: document.getElementById('history-limit'), // NOVO
            showHistoryBtn: document.getElementById('show-history-btn'), // NOVO
            autoTrending: document.getElementById('auto-trending'),
            autoAudio: document.getElementById('auto-audio'),
            loading: document.getElementById('loading'),
            audioLoading: document.getElementById('audio-loading'),
            newsContainer: document.getElementById('news-container'),
            trendingTopics: document.getElementById('trending-topics'),
            trendingList: document.getElementById('trending-list')
        };

        this.config = {
            apiUrl: 'http://127.0.0.1:5000',
            maxRetries: 3,
            retryDelay: 1000,
            fetchTimeout: 30000000
        };

        this.trendingTopics = [];
        this.isLoading = false;
        this.isAudioLoading = false;
        this.currentNewsData = null; // Armazena a notícia atualmente exibida em detalhe
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadTrendingTopics();
        this.showNewsHistory(); // Carrega o histórico ao iniciar
    }

    setupEventListeners() {
        this.elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isLoading) {
                this.searchNews();
            }
        });

        this.elements.searchBtn.addEventListener('click', () => {
            if (!this.isLoading) {
                this.searchNews();
            }
        });

        /* // Comentado ou removido pois 'trending-btn' não existe no HTML
        this.elements.trendingBtn.addEventListener('click', () => {
            if (!this.isLoading) {
                this.generateFromTrending();
            }
        });
        */

        // NOVO: Event listener para o botão "Ver Histórico"
        if (this.elements.showHistoryBtn) {
            this.elements.showHistoryBtn.addEventListener('click', () => {
                if (!this.isLoading) {
                    this.showNewsHistory();
                }
            });
        }
    }

    // --- Funções de Carregamento (Tópicos) ---
    // loadCategories e renderCategories foram removidas, pois não há mais filtro por categoria

    async loadTrendingTopics() {
        try {
            const response = await fetch(`${this.config.apiUrl}/api/topics`);
            if (response.ok) {
                const data = await response.json();
                this.trendingTopics = data.topics || [];
            } else {
                this.loadFallbackTopics();
            }
        } catch (error) {
            console.warn('Servidor não disponível para tópicos, usando fallback:', error);
            this.loadFallbackTopics();
        }
        this.renderTrendingTopics();
    }

    loadFallbackTopics() {
        const warningDiv = document.createElement('div');
        warningDiv.className = 'api-warning';
        warningDiv.innerHTML = '⚠️ Servidor indisponível - tópicos de exemplo.';
        warningDiv.style.cssText = `background-color: #fff3cd; color: #856404; padding: 8px; border-radius: 4px; margin-bottom: 10px; text-align: center; font-size: 14px;`;
        this.elements.trendingTopics.insertBefore(warningDiv, this.elements.trendingList);
        this.trendingTopics = [
            { topico: "Política Brasil", categoria: "Política" },
            { topico: "Inteligência Artificial", categoria: "Tecnologia" },
            { topico: "Economia Global", categoria: "Economia" },
        ];
    }

    renderTrendingTopics() {
        if (this.trendingTopics.length > 0) {
            this.elements.trendingList.innerHTML = this.trendingTopics
                .map(topic => `<span class="trending-tag clickable" data-topic="${topic.topico}" data-category="${topic.categoria}">${topic.topico}</span>`)
                .join('');
            this.elements.trendingTopics.style.display = 'block';
            this.setupTrendingClickHandlers();
        }
    }

    setupTrendingClickHandlers() {
        this.elements.trendingList.querySelectorAll('.trending-tag.clickable').forEach(tag => {
            tag.addEventListener('click', async (e) => {
                if (this.isLoading) return;
                const topic = e.target.dataset.topic;
                const category = e.target.dataset.category;
                this.elements.searchInput.value = topic; // Preenche o input de busca com o tópico
                e.target.classList.add('clicked');
                setTimeout(() => e.target.classList.remove('clicked'), 200);
                await this.searchNews(category); // Passa a categoria para a busca
            });
        });
    }

    // --- Funções de Histórico (NOVO) ---

    async showNewsHistory() {
        this.setLoading(true);
        try {
            const limit = this.elements.historyLimit.value;
            const response = await fetch(`${this.config.apiUrl}/api/news/history?limit=${limit}`);
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.history && data.history.length > 0) {
                    this.renderMultipleNews(data.history, `Últimas ${data.count} Notícias Geradas`);
                } else {
                    this.showError('Nenhuma notícia no histórico ainda. Gere algumas notícias para vê-las aqui!');
                }
            } else {
                this.showError('Erro ao carregar histórico de notícias.');
            }
        } catch (error) {
            this.showError('⚠️ Erro de conexão ao carregar histórico. Verifique o servidor.');
        } finally {
            this.setLoading(false);
        }
    }

    // --- Funções de Geração e Renderização de Notícias ---

    // `renderMultipleNews` agora é usada tanto para o histórico quanto para notícias filtradas (se ainda existisse)
    renderMultipleNews(newsArray, title) {
        const newsHTML = `
            <div class="news-section-title"><h2>${title}</h2></div>
            ${newsArray.map(item => {
                const noticia = item.noticia || item;
                // Formata a data se for uma string ISO
                let formattedDate = noticia.data || 'Data Desconhecida';
                try {
                    if (noticia.data && !isNaN(new Date(noticia.data))) {
                        formattedDate = new Date(noticia.data).toLocaleDateString('pt-BR');
                    } else if (item.created_at) { // Usa created_at do histórico se a notícia não tiver data
                        formattedDate = new Date(item.created_at).toLocaleDateString('pt-BR');
                    }
                } catch (e) { /* ignore */ }

                // O 'topico' para carregar/gerar áudio/notícia completa é o topico original do cache
                // ou o título da notícia se não houver um tópico original explícito
                const topicForApi = item.topico || noticia.titulo || 'desconhecido';
                const categoryForApi = item.categoria || noticia.categoria || 'Geral';

                const audioBtnHtml = item.audio_data_available
                    ? `<button class="btn btn-tertiary btn-play-audio" data-topic="${encodeURIComponent(topicForApi)}" data-category="${encodeURIComponent(categoryForApi)}">▶️ Ouvir Áudio</button>`
                    : `<button class="btn btn-secondary btn-generate-audio" data-topic="${encodeURIComponent(topicForApi)}" data-category="${encodeURIComponent(categoryForApi)}">🔊 Gerar Áudio</button>`;

                return `
                    <div class="news-card multiple">
                        <div class="news-header">
                            <div class="news-source">${noticia.fonte || 'Fonte Desconhecida'}</div>
                            <div class="news-date">📅 ${formattedDate}</div>
                        </div>
                        <h3 class="news-title">${noticia.titulo || 'Sem título'}</h3>
                        <p>${(noticia.noticia_completa || '').substring(0, 150)}...</p>
                        <div class="news-actions">
                            <button class="btn btn-primary btn-read-more" data-topic="${encodeURIComponent(topicForApi)}" data-category="${encodeURIComponent(categoryForApi)}">Ler Notícia Completa</button>
                            ${audioBtnHtml}
                        </div>
                    </div>`;
            }).join('')}
        `;
        this.elements.newsContainer.innerHTML = newsHTML;
        this.elements.newsContainer.style.display = 'block';
        this.setupReadMoreHandlers();
        this.setupAudioButtons(); // Configura os novos botões de áudio
        this.scrollToNews();
    }

    setupReadMoreHandlers() {
        this.elements.newsContainer.querySelectorAll('.btn-read-more').forEach(button => {
            button.addEventListener('click', async (e) => {
                if (this.isLoading) return;
                // Usa os atributos data-topic e data-category para buscar a notícia completa
                const topic = decodeURIComponent(e.target.dataset.topic);
                const category = decodeURIComponent(e.target.dataset.category);
                if (topic) {
                    this.elements.searchInput.value = topic; // Preenche o campo de busca
                    // Não há mais categoriaSelect no HTML, mas podemos passar para o backend
                    await this.generateNews(topic, category);
                } else {
                    this.showError("Não foi possível carregar a notícia completa. Tópico não encontrado.");
                }
            });
        });
    }

    setupAudioButtons() {
        // Botões de áudio para notícias na lista (histórico)
        this.elements.newsContainer.querySelectorAll('.btn-play-audio').forEach(button => {
            button.addEventListener('click', async (e) => {
                if (this.isAudioLoading) return;
                const topic = decodeURIComponent(e.target.dataset.topic);
                const category = decodeURIComponent(e.target.dataset.category);
                await this.playCachedAudio(topic, category);
            });
        });

        this.elements.newsContainer.querySelectorAll('.btn-generate-audio').forEach(button => {
            button.addEventListener('click', async (e) => {
                if (this.isAudioLoading) return;
                const topic = decodeURIComponent(e.target.dataset.topic);
                const category = decodeURIComponent(e.target.dataset.category);
                
                // Para gerar áudio de uma notícia na lista, precisamos primeiro carregar a notícia completa
                // para ter o 'noticia_completa' para o TTS.
                // Esta lógica assume que a `generateNews` já popula `currentNewsData`.
                // Se o usuário clicar em gerar áudio de uma notícia do histórico sem antes "Ler Notícia Completa",
                // precisaremos buscar a notícia completa primeiro.
                // Para simplificar, vamos fazer uma busca rápida e then gerar o áudio.
                this.setAudioLoading(true); // Temporário
                try {
                    const response = await fetch(`${this.config.apiUrl}/api/news/${encodeURIComponent(topic)}?categoria=${encodeURIComponent(category)}`);
                    if (response.ok) {
                        const data = await response.json();
                        if (data.noticia) {
                            await this.generateAudio(data.noticia, topic, category);
                        } else {
                            this.showAudioError("Não foi possível obter os detalhes da notícia para gerar áudio.");
                        }
                    } else {
                        this.showAudioError("Erro ao carregar notícia para gerar áudio.");
                    }
                } catch (error) {
                    this.showAudioError("Erro de rede ao carregar notícia para áudio.");
                } finally {
                    this.setAudioLoading(false);
                }
            });
        });
    }


    async searchNews(category = 'Geral') { // Categoria agora é um parâmetro, não vem do select
        const query = this.elements.searchInput.value.trim();

        if (query) {
            await this.generateNews(query, category);
        } else if (this.elements.autoTrending.checked && this.trendingTopics.length > 0) {
            const randomTopic = this.trendingTopics[Math.floor(Math.random() * this.trendingTopics.length)];
            this.elements.searchInput.value = randomTopic.topico;
            await this.generateNews(randomTopic.topico, randomTopic.categoria); // Passa a categoria do tópico em alta
        } else {
            this.showError('Digite um assunto para pesquisar, ou ative os tópicos automáticos.');
        }
    }

    async generateFromTrending() {
        if (this.trendingTopics.length > 0) {
            const randomTopic = this.trendingTopics[Math.floor(Math.random() * this.trendingTopics.length)];
            this.elements.searchInput.value = randomTopic.topico;
            await this.generateNews(randomTopic.topico, randomTopic.categoria);
        } else {
            this.showError('Nenhum tópico em alta disponível.');
        }
    }

    async generateNews(topic, category) {
        if (this.isLoading) return;
        this.setLoading(true);
        this.hideError();
        try {
            // Garante que o topic é o título da notícia para buscar corretamente do backend
            const response = await fetch(`${this.config.apiUrl}/api/news/${encodeURIComponent(topic)}?categoria=${encodeURIComponent(category)}`);
            if (response.ok) {
                const newsData = await response.json();
                if (newsData && newsData.noticia) {
                    this.currentNewsData = newsData; // Guarda a notícia atual
                    this.renderNews(newsData);
                    // Se o áudio já está disponível no cache, toca. Senão, gera (se autoAudio estiver marcado).
                    if (newsData.audio_data_available) {
                        // Usa o topico_original_do_cache e categoria_original_do_cache para buscar o áudio
                        await this.playCachedAudio(newsData.topico_original_do_cache, newsData.categoria_original_do_cache);
                    } else if (this.elements.autoAudio.checked) {
                        await this.generateAudio(newsData.noticia, newsData.topico_original_do_cache, newsData.categoria_original_do_cache);
                    }
                } else {
                    this.showError('⚠️ Notícia não encontrada ou gerada. Tente um tópico diferente.');
                }
            } else {
                const errorData = await response.json().catch(() => ({ error: `Erro ${response.status}` }));
                this.showError(`⚠️ Erro ao buscar notícia: ${errorData.error || response.statusText}.`);
            }
        } catch (error) {
            this.showError('⚠️ Erro de conexão. Verifique sua internet e o backend.');
            console.error(error);
        } finally {
            this.setLoading(false);
        }
    }

    renderNews(data) {
        const news = data.noticia;
        const paragraphs = (news.noticia_completa || '').split('\n\n').filter(p => p.trim());
        let formattedDate = news.data || 'Data Desconhecida';
        try {
            if (news.data && !isNaN(new Date(news.data))) {
                formattedDate = new Date(news.data).toLocaleDateString('pt-BR');
            }
        } catch (e) { /* ignore */ }

        // Os valores `topico_original_do_cache` e `categoria_original_do_cache` são usados para os `data-` atributos
        // para que a API de áudio e a de "Ler Mais" possam buscar a notícia correta no cache.
        const topicForApi = data.topico_original_do_cache || news.titulo || 'desconhecido';
        const categoryForApi = data.categoria_original_do_cache || news.categoria || 'Geral';

        // Decide qual botão de áudio mostrar
        const audioButtonHtml = data.audio_data_available
            ? `<button id="play-cached-audio-btn" class="btn btn-tertiary" data-topic="${encodeURIComponent(topicForApi)}" data-category="${encodeURIComponent(categoryForApi)}">▶️ Ouvir Áudio</button>`
            : `<button id="generate-audio-btn" class="btn btn-secondary" data-topic="${encodeURIComponent(topicForApi)}" data-category="${encodeURIComponent(categoryForApi)}">🔊 Gerar Áudio</button>`;

        const newsHTML = `
            <div class="news-card">
                <div class="news-header">
                    <div class="news-source">${news.fonte || 'Fonte Desconhecida'}</div>
                    <div class="news-date">📅 ${formattedDate}</div>
                </div>
                <h2 class="news-title">${news.titulo || 'Sem título'}</h2>
                <div class="news-content">
                    ${paragraphs.map(p => `<p>${p}</p>`).join('')}
                </div>
                <div class="news-actions">
                    ${audioButtonHtml}
                    <div id="audio-loading-inline" style="display: none; margin-left: 10px; color: #555;">Gerando Áudio</div>
                </div>
            </div>
        `;
        this.elements.newsContainer.innerHTML = newsHTML;
        this.elements.newsContainer.style.display = 'block';
        this.scrollToNews();
        this.attachMainAudioButtonListeners(); // Anexa listeners aqui
    }

    attachMainAudioButtonListeners() {
        const playCachedBtn = document.getElementById('play-cached-audio-btn');
        const generateAudioBtn = document.getElementById('generate-audio-btn');

        if (playCachedBtn) {
            playCachedBtn.addEventListener('click', async () => {
                if (this.isAudioLoading) return;
                const topic = decodeURIComponent(playCachedBtn.dataset.topic);
                const category = decodeURIComponent(playCachedBtn.dataset.category);
                await this.playCachedAudio(topic, category);
            });
        } else if (generateAudioBtn) {
            generateAudioBtn.addEventListener('click', async () => {
                if (this.isAudioLoading || !this.currentNewsData || !this.currentNewsData.noticia) return;
                const topic = decodeURIComponent(generateAudioBtn.dataset.topic);
                const category = decodeURIComponent(generateAudioBtn.dataset.category);
                await this.generateAudio(this.currentNewsData.noticia, topic, category);
            });
        }
    }

    // --- Funções de Geração e Gestão de Áudio (ATUALIZADAS) ---

    prepareTextForSpeech(newsData) {
        let text = `${newsData.titulo}. `;
        text += (newsData.noticia_completa || '').replace(/\n\n/g, '. ');
        text = text.replace(/[^\w\s\.,!?áéíóúàèìòùâêîôûãõçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ]/gi, ' ');
        text = text.replace(/\s+/g, ' ').trim();
        return text.substring(0, 5000);
    }

    async generateAudio(newsData, topicForSave, categoryForSave) {
        if (!newsData || this.isAudioLoading) return;
        this.setAudioLoading(true);
        this.removeAudioPlayerAndError();

        try {
            const textToSpeak = this.prepareTextForSpeech(newsData);
            const response = await fetch(`${this.config.apiUrl}/api/gemini-tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: textToSpeak,
                    voice: 'Zephyr',
                    topico: topicForSave,     // Passa o topico original do cache
                    categoria: categoryForSave // Passa a categoria original do cache
                }),
                signal: AbortSignal.timeout(this.config.fetchTimeout)
            });

            if (response.ok) {
                const audioBlob = await response.blob();
                this.addAudioPlayer(audioBlob);
                // Uma vez que o áudio foi gerado e salvo no backend,
                // atualizamos o estado da notícia atual para indicar que agora tem áudio.
                // Isso é importante para que o botão mude para "Ouvir Áudio"
                if (this.currentNewsData && 
                    this.currentNewsData.topico_original_do_cache === topicForSave && 
                    this.currentNewsData.categoria_original_do_cache === categoryForSave) {
                    this.currentNewsData.audio_data_available = true;
                    // Re-renderiza a notícia para atualizar o botão de áudio
                    this.renderNews(this.currentNewsData);
                }
            } else {
                const errorData = await response.json().catch(() => ({ error: `Erro ${response.status}` }));
                this.showAudioError(`Falha ao gerar áudio: ${errorData.error}`);
            }
        } catch (error) {
            console.error('Erro na chamada TTS:', error);
            this.showAudioError('⚠️ Erro de conexão ao gerar áudio.');
        } finally {
            this.setAudioLoading(false);
        }
    }

    async playCachedAudio(topic, category) {
        if (this.isAudioLoading) return;
        this.setAudioLoading(true);
        this.removeAudioPlayerAndError();

        try {
            const encodedTopic = encodeURIComponent(topic);
            const encodedCategory = encodeURIComponent(category);
            const audioUrl = `${this.config.apiUrl}/api/news/audio/${encodedTopic}/${encodedCategory}`;
            
            const response = await fetch(audioUrl, {
                signal: AbortSignal.timeout(this.config.fetchTimeout)
            });

            if (response.ok) {
                const audioBlob = await response.blob();
                this.addAudioPlayer(audioBlob);
            } else {
                const errorData = await response.json().catch(() => ({ error: `Erro ${response.status}` }));
                this.showAudioError(`Falha ao carregar áudio do cache: ${errorData.error}`);
            }
        } catch (error) {
            console.error('Erro ao buscar áudio do cache:', error);
            this.showAudioError('⚠️ Erro de conexão ao carregar áudio do cache.');
        } finally {
            this.setAudioLoading(false);
        }
    }

    addAudioPlayer(audioBlob) {
        const audioUrl = URL.createObjectURL(audioBlob);
        const audioPlayerHTML = `
            <div class="audio-player-container">
                <div class="audio-header">
                    <span style="font-size: 24px;">🔊</span><h3>Áudio da Notícia</h3>
                </div>
                <audio controls autoplay>
                    <source src="${audioUrl}" type="${audioBlob.type || 'audio/wav'}">
                    Seu navegador não suporta áudio.
                </audio>
                <button onclick="this.parentElement.remove()">✕ Fechar</button>
            </div>`;

        const newsCard = this.elements.newsContainer.querySelector('.news-card');
        if (newsCard) {
            newsCard.insertAdjacentHTML('beforeend', audioPlayerHTML);
        }
    }

    showAudioError(message) {
        const errorHTML = `<div class="audio-error">🔇 ${message}</div>`;
        const newsCard = this.elements.newsContainer.querySelector('.news-card');
        if (newsCard) {
            newsCard.insertAdjacentHTML('beforeend', errorHTML);
        }
    }

    removeAudioPlayerAndError() {
        this.elements.newsContainer.querySelectorAll('.audio-player-container, .audio-error')
            .forEach(el => el.remove());
    }

    // --- Funções Auxiliares (Loading, Erro, Scroll) ---
    setLoading(loading) {
        this.isLoading = loading;
        this.elements.loading.style.display = loading ? 'block' : 'none';
        this.elements.searchBtn.disabled = loading;
        // this.elements.trendingBtn.disabled = loading; // Removido pois 'trending-btn' não existe
        if (this.elements.showHistoryBtn) { // Atualiza também o botão de histórico
            this.elements.showHistoryBtn.disabled = loading;
        }

        if (!loading) {
            this.hideError();
        } else {
            this.elements.newsContainer.style.display = 'none';
        }
    }

    setAudioLoading(loading) {
        this.isAudioLoading = loading;
        const audioBtn = document.getElementById('generate-audio-btn');
        const playCachedBtn = document.getElementById('play-cached-audio-btn');
        const audioLoadingInline = document.getElementById('audio-loading-inline');

        if (audioBtn) audioBtn.disabled = loading;
        if (playCachedBtn) playCachedBtn.disabled = loading;
        if (audioLoadingInline) audioLoadingInline.style.display = loading ? 'inline-block' : 'none';
        this.elements.audioLoading.style.display = loading ? 'block' : 'none';
    }

    showError(message) {
        this.elements.newsContainer.innerHTML = `<div class="error-message">${message}</div>`;
        this.elements.newsContainer.style.display = 'block';
        this.scrollToNews();
    }

    hideError() {
        const errorMsg = this.elements.newsContainer.querySelector('.error-message');
        if (errorMsg) errorMsg.remove();
    }

    scrollToNews() {
        setTimeout(() => {
            this.elements.newsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
}

// --- Inicialização da Aplicação ---
let newsGenerator;
document.addEventListener('DOMContentLoaded', () => {
    newsGenerator = new NewsGenerator();
});