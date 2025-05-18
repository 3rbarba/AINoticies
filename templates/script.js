document.addEventListener('DOMContentLoaded', () => {
    const NoticiaManager = {
        config: {
            apiUrl: 'http://127.0.0.1:5000/gerar_noticia_completa',
            maxTentativas: 3
        },

        elementos: {
            container: document.getElementById('noticias-container'),
            gerarBtn: document.getElementById('gerar-noticia-btn'),
            carregando: document.getElementById('carregando-noticia')
        },

        criarElementoNoticia(noticia) {
            return `
                <h2>${noticia.Título || 'Título não encontrado'}</h2>
                <p><strong>${noticia.Chamada || 'Chamada não encontrada'}</strong></p>
                <p>${noticia.Resumo || 'Resumo não encontrado'}</p>
                <p><em>${noticia.categoria || 'Sem categoria'}</em></p>
                ${noticia['URL da Imagem'] ? `<img src="${noticia['URL da Imagem']}" alt="${noticia.Título || 'Imagem'}">` : ''}
            `;
        },

        criarListaTopicos(topicos) {
            const ul = document.createElement('ul');
            topicos.forEach(topico => {
                const li = document.createElement('li');
                li.textContent = `${topico.tópico} (Categoria: ${topico.categoria || 'A Definir'})`;
                ul.appendChild(li);
            });
            return ul;
        },

        renderizarNoticia(data) {
            const bloco = document.createElement('div');
            bloco.className = 'noticia-bloco';
            bloco.innerHTML = this.criarElementoNoticia(data.resultado);

            if (data.outros_topicos?.length) {
                bloco.appendChild(this.criarListaTopicos(data.outros_topicos));
            }

            this.elementos.container.prepend(bloco);
        },

        async buscarNoticia(tentativas = 0) {
            this.elementos.carregando.style.display = 'block';

            try {
                const response = await fetch(this.config.apiUrl);
                const data = await response.json();

                if (data.erro === "Não foi possível identificar tópicos em alta") {
                    if (tentativas < this.config.maxTentativas) {
                        console.warn(`Tentativa ${tentativas + 1}: tópicos não encontrados. Tentando novamente...`);
                        return this.buscarNoticia(tentativas + 1);
                    }
                    throw new Error(data.erro);
                }

                this.renderizarNoticia(data);
            } catch (err) {
                console.error(`Erro na tentativa ${tentativas + 1}:`, err);
                if (tentativas < this.config.maxTentativas) {
                    return this.buscarNoticia(tentativas + 1);
                }
                this.mostrarErro();
            } finally {
                this.elementos.carregando.style.display = 'none';
            }
        },

        mostrarErro() {
            const erroBloco = document.createElement('div');
            erroBloco.className = 'noticia-bloco';
            erroBloco.innerHTML = `<p class="erro">Erro ao carregar notícia após ${this.config.maxTentativas} tentativas.</p>`;
            this.elementos.container.appendChild(erroBloco);
        },

        inicializar() {
            this.elementos.gerarBtn.addEventListener('click', () => this.buscarNoticia());
            this.buscarNoticia();
        }
    };

    NoticiaManager.inicializar();
});
