class NewsGenerator {
    constructor() {
        this.elements = {
            searchInput: document.getElementById('search-input'),
            searchBtn: document.getElementById('search-btn'),
            trendingBtn: document.getElementById('trending-btn'),
            autoTrending: document.getElementById('auto-trending'),
            loading: document.getElementById('loading'),
            newsContainer: document.getElementById('news-container'),
            trendingTopics: document.getElementById('trending-topics'),
            trendingList: document.getElementById('trending-list')
        };

        this.config = {
            apiUrl: 'http://127.0.0.1:5000', // URL do servidor Flask
            maxRetries: 3,
            retryDelay: 1000
        };

        this.trendingTopics = [];
        this.isLoading = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadTrendingTopics();
    }

    setupEventListeners() {
        // Pesquisa por enter
        this.elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isLoading) {
                this.searchNews();
            }
        });

        // Botão de pesquisa
        this.elements.searchBtn.addEventListener('click', () => {
            if (!this.isLoading) {
                this.searchNews();
            }
        });

        // Botão de tópicos em alta
        this.elements.trendingBtn.addEventListener('click', () => {
            if (!this.isLoading) {
                this.generateFromTrending();
            }
        });
    }

    async loadTrendingTopics() {
        try {
            const response = await fetch(`${this.config.apiUrl}/api/topics`);
            
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.topics) {
                    this.trendingTopics = data.topics;
                } else {
                    this.loadFallbackTopics();
                }
            } else {
                this.loadFallbackTopics();
            }
        } catch (error) {
            console.warn('Servidor não disponível, usando tópicos de fallback:', error);
            this.loadFallbackTopics();
        }

        this.renderTrendingTopics();
    }

    loadFallbackTopics() {
        // Tópicos de fallback quando o servidor não está disponível
        const warningDiv = document.createElement('div');
        warningDiv.className = 'api-warning';
        warningDiv.innerHTML = '⚠️ Servidor indisponível - esses topicos são apenas exemplos. Por favor, verifique sua conexão com a internet ou tente novamente mais tarde.';
        // Estilo do aviso
        warningDiv.style.cssText = `
            background-color: #fff3cd;
            color: #856404;
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 10px;
            text-align: center;
            font-size: 14px;
        `;
        this.elements.trendingTopics.insertBefore(warningDiv, this.elements.trendingList);
        this.trendingTopics = [
            { topico: "Politica Brasil", categoria: "Politica/Brasil" },
            { topico: "Inteligência Artificial", categoria: "Tecnologia" },
            { topico: "Economia Global", categoria: "Economia" },
            { topico: "Brics", categoria: "Economia" },
            { topico: "Saúde", categoria: "Saúde" },
            { topico: "Mercado financeiro", categoria: "Finanças" },
            { topico: "Climas", categoria: "Ciência" },
            { topico: "Redes Sociais", categoria: "Tecnologia" },
            { topico: "Energia Renovável", categoria: "Energia" },
            { topico: "Medicina Preventiva", categoria: "Saúde" }
        ];
    }

    renderTrendingTopics() {
        if (this.trendingTopics.length > 0) {
            this.elements.trendingList.innerHTML = this.trendingTopics
                .map((topic, index) => `
                    <span class="trending-tag clickable" 
                          data-topic="${topic.topico}" 
                          data-category="${topic.categoria}"
                          data-index="${index}">
                        ${topic.topico}
                    </span>
                `)
                .join('');
            this.elements.trendingTopics.style.display = 'block';
            
            // Adiciona event listeners para os tópicos clicáveis
            this.setupTrendingClickHandlers();
        }
    }

    setupTrendingClickHandlers() {
        const trendingTags = this.elements.trendingList.querySelectorAll('.trending-tag.clickable');
        
        trendingTags.forEach(tag => {
            tag.addEventListener('click', async (e) => {
                if (this.isLoading) return;
                
                const topic = e.target.dataset.topic;
                const category = e.target.dataset.category;
                
                // Efeito visual de clique
                e.target.classList.add('clicked');
                setTimeout(() => {
                    e.target.classList.remove('clicked');
                }, 200);
                
                // Gera a notícia para o tópico clicado
                await this.generateNews(topic, category);
            });

            // Efeito hover
            tag.addEventListener('mouseenter', (e) => {
                e.target.classList.add('hover');
            });

            tag.addEventListener('mouseleave', (e) => {
                e.target.classList.remove('hover');
            });
        });
    }

    async searchNews() {
        const query = this.elements.searchInput.value.trim();
        
        if (query) {
            await this.generateNews(query, 'Personalizado');
        } else if (this.elements.autoTrending.checked && this.trendingTopics.length > 0) {
            const randomTopic = this.trendingTopics[Math.floor(Math.random() * this.trendingTopics.length)];
            await this.generateNews(randomTopic.topico, randomTopic.categoria);
        } else {
            this.showError('Por favor, digite um assunto para pesquisar.');
        }
    }

    async generateFromTrending() {
        if (this.trendingTopics.length > 0) {
            const randomTopic = this.trendingTopics[Math.floor(Math.random() * this.trendingTopics.length)];
            await this.generateNews(randomTopic.topico, randomTopic.categoria);
        } else {
            this.showError('Nenhum tópico em alta disponível no momento.');
        }
    }

    async generateNews(topic, category) {
        if (this.isLoading) return;

        this.setLoading(true);
        this.hideError();

        try {
            const newsData = await this.fetchFromServer(topic, category);
            
            if (newsData) {
                this.renderNews(newsData);
            } else {
                this.showError('⚠️ Serviço temporariamente indisponível. Tente novamente em alguns instantes.');
            }

        } catch (error) {
            console.error('Erro ao gerar notícia:', error);
            this.showError('⚠️ Erro de conexão com o servidor. Verifique sua internet e tente novamente.');
        } finally {
            this.setLoading(false);
        }
    }

    async fetchFromServer(topic, category) {
        try {
            // Tenta buscar notícia específica (GET)
            const response = await fetch(
                `${this.config.apiUrl}/api/news/${encodeURIComponent(topic)}?categoria=${encodeURIComponent(category)}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );

            if (response.ok) {
                const data = await response.json();
                if (data.noticia) {
                    return data;
                }
            }

            // Se não encontrar, tenta endpoint alternativo (POST)
            const postResponse = await fetch(`${this.config.apiUrl}/api/news`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topico: topic,
                    categoria: category
                })
            });

            if (postResponse.ok) {
                const data = await postResponse.json();
                if (data.noticia) {
                    return data;
                }
            }

            return null;
        } catch (error) {
            console.warn('Erro ao conectar com servidor:', error);
            return null;
        }
    }

    renderNews(data) {
        if (!data || !data.noticia) {
            this.showError('Notícia não encontrada.');
            return;
        }

        const news = data.noticia;
        const paragraphs = news.noticia_completa.split('\n\n').filter(p => p.trim());

        const newsHTML = `
            <div class="news-card">
                <div class="news-header">
                    <div class="news-source">${news.fonte}</div>
                    <div class="news-date">📅 ${news.data}</div>
                </div>
                <h2 class="news-title">${news.titulo}</h2>
                <div class="news-content">
                    ${paragraphs.map(p => `<p>${p}</p>`).join('')}
                </div>
            </div>
        `;

        this.elements.newsContainer.innerHTML = newsHTML;
        this.elements.newsContainer.style.display = 'block';
        
        // Smooth scroll with delay and viewport check
        const elementRect = this.elements.newsContainer.getBoundingClientRect();
        const isInView = elementRect.top >= 0 && elementRect.bottom <= window.innerHeight;
        
        if (!isInView) {
            setTimeout(() => {
            this.elements.newsContainer.scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'nearest'
            });
            }, 100);
        }
    }

    setLoading(loading) {
        this.isLoading = loading;
        this.elements.loading.style.display = loading ? 'block' : 'none';
        this.elements.searchBtn.disabled = loading;
        this.elements.trendingBtn.disabled = loading;
        
        if (loading) {
            this.elements.newsContainer.style.display = 'none';
        }
    }

    showError(message) {
        const errorHTML = `<div class="error-message">${message}</div>`;
        this.elements.newsContainer.innerHTML = errorHTML;
        this.elements.newsContainer.style.display = 'block';
    }

    hideError() {
        // Erro será escondido automaticamente quando nova notícia for carregada
    }
}

// Inicializar aplicação
document.addEventListener('DOMContentLoaded', () => {
    new NewsGenerator();
});