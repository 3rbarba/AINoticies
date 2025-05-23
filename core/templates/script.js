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
            apiUrl: 'http://127.0.0.1:5000',
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
            // Tenta buscar tópicos do servidor
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
        this.trendingTopics = [
            { topico: "Inteligência Artificial", categoria: "Tecnologia" },
            { topico: "Economia Global", categoria: "Economia" },
            { topico: "Sustentabilidade", categoria: "Meio Ambiente" },
            { topico: "Saúde Digital", categoria: "Saúde" },
            { topico: "Eleições 2024", categoria: "Política" },
            { topico: "Mercado Cripto", categoria: "Finanças" },
            { topico: "Mudanças Climáticas", categoria: "Ciência" },
            { topico: "Redes Sociais", categoria: "Tecnologia" },
            { topico: "Energia Renovável", categoria: "Energia" },
            { topico: "Medicina Preventiva", categoria: "Saúde" }
        ];
    }

    renderTrendingTopics() {
        if (this.trendingTopics.length > 0) {
            this.elements.trendingList.innerHTML = this.trendingTopics
                .map(topic => `<span class="trending-tag">${topic.topico}</span>`)
                .join('');
            this.elements.trendingTopics.style.display = 'block';
        }
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
            // Tenta buscar do servidor primeiro
            let newsData = await this.fetchFromServer(topic, category);
            
            // Se não conseguir do servidor, usa geração local
            if (!newsData) {
                console.log('Gerando notícia localmente...');
                await this.delay(2000); // Simula tempo de processamento
                newsData = this.generateFakeNews(topic, category);
            }

            this.renderNews(newsData);

        } catch (error) {
            console.error('Erro ao gerar notícia:', error);
            this.showError('Erro ao gerar notícia. Tente novamente.');
        } finally {
            this.setLoading(false);
        }
    }

    async fetchFromServer(topic, category) {
        try {
            // Tenta buscar notícia específica
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

            // Se não encontrar, tenta endpoint alternativo
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

    generateFakeNews(topic, category) {
        const sources = [
            'Reuters Brasil', 'G1 Notícias', 'Folha de S.Paulo', 
            'Estado de S.Paulo', 'UOL Notícias', 'CNN Brasil',
            'BBC Brasil', 'Valor Econômico', 'Exame', 'InfoMoney'
        ];

        const templates = [
            `Especialistas analisam as últimas tendências em ${topic.toLowerCase()} e seus impactos na sociedade atual. O tema tem ganhado destaque nos últimos meses devido à sua relevância crescente no cenário nacional e internacional.`,
            
            `Novas descobertas sobre ${topic.toLowerCase()} prometem revolucionar o setor nos próximos anos. Pesquisadores e analistas indicam que as mudanças podem ser sentidas em diversas áreas da economia e sociedade.`,
            
            `Governo e iniciativa privada anunciam investimentos significativos em ${topic.toLowerCase()}. As medidas visam fortalecer o desenvolvimento sustentável e a inovação tecnológica no país.`,
            
            `Mercado global demonstra otimismo com as perspectivas relacionadas a ${topic.toLowerCase()}. Investidores nacionais e internacionais mostram interesse crescente no setor brasileiro.`
        ];

        const paragraphs = [
            `As discussões em torno de ${topic.toLowerCase()} têm se intensificado nos últimos meses, com especialistas apontando tanto oportunidades quanto desafios significativos. A comunidade científica, empresarial e acadêmica tem demonstrado interesse crescente no tema, buscando soluções inovadoras e sustentáveis para os principais gargalos identificados.`,
            
            `Segundo dados recentes divulgados por institutos de pesquisa, o impacto de ${topic.toLowerCase()} na economia brasileira pode ser substancial. Estudos indicam que o setor tem potencial para gerar milhares de empregos diretos e indiretos, além de atrair investimentos estrangeiros significativos, contribuindo para o desenvolvimento nacional em médio e longo prazo.`,
            
            `A população brasileira tem demonstrado interesse crescente no assunto, com pesquisas recentes mostrando que ${topic.toLowerCase()} está entre os temas mais discutidos nas redes sociais e mídias tradicionais. Influenciadores digitais, formadores de opinião e especialistas têm contribuído para ampliar o debate público e conscientizar sobre sua importância.`,
            
            `Para os próximos anos, especialistas preveem transformações importantes relacionadas a ${topic.toLowerCase()} no Brasil e no mundo. As mudanças podem afetar diversos setores da economia, desde pequenas empresas até grandes corporações, exigindo adaptação estratégica e preparação adequada por parte de empresários, profissionais e consumidores.`,
            
            `Iniciativas governamentais e parcerias público-privadas estão sendo desenvolvidas para maximizar os benefícios de ${topic.toLowerCase()}, ao mesmo tempo em que se busca mitigar possíveis riscos e desafios. O planejamento estratégico e a cooperação entre diferentes setores são considerados fundamentais para o sucesso dessas implementações.`
        ];

        // Seleciona parágrafos aleatórios
        const selectedParagraphs = this.shuffleArray([...paragraphs]).slice(0, 4);
        const template = templates[Math.floor(Math.random() * templates.length)];

        return {
            noticia: {
                titulo: `${topic}: ${this.generateRandomTitle(topic)}`,
                fonte: sources[Math.floor(Math.random() * sources.length)],
                data: new Date().toLocaleDateString('pt-BR', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                }),
                categoria: category,
                noticia_completa: template + '\n\n' + selectedParagraphs.join('\n\n')
            }
        };
    }

    generateRandomTitle(topic) {
        const titleTemplates = [
            'Análise Completa das Últimas Tendências',
            'Perspectivas e Desafios para o Futuro',
            'Impactos na Economia e Sociedade Brasileira',
            'Inovações que Podem Transformar o Setor',
            'Especialistas Debatem Oportunidades e Riscos',
            'Novos Investimentos Movimentam o Mercado',
            'Tecnologia e Sustentabilidade em Foco'
        ];
        
        return titleTemplates[Math.floor(Math.random() * titleTemplates.length)];
    }

    shuffleArray(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
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
        
        // Scroll suave para a notícia
        this.elements.newsContainer.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
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
        const errorHTML = `<div class="error-message">⚠️ ${message}</div>`;
        this.elements.newsContainer.innerHTML = errorHTML;
        this.elements.newsContainer.style.display = 'block';
    }

    hideError() {
        // Erro será escondido automaticamente quando nova notícia for carregada
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Inicializar aplicação
document.addEventListener('DOMContentLoaded', () => {
    new NewsGenerator();
});