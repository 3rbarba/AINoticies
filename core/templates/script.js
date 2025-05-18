document.addEventListener('DOMContentLoaded', () => {
    const NoticiaManager = {
        config: {
            apiUrl: 'http://127.0.0.1:5000/gerar_noticia_completa',
            maxTentativas: Infinity
        },

        elementos: {
            container: document.getElementById('noticias-container'),
            gerarBtn: document.getElementById('gerar-noticia-btn'),
            carregando: document.getElementById('carregando-noticia')
        },

        criarElementoNoticia(noticia) {
            return `
                <div class="noticia-bloco">
                    <h2>${noticia.Título || 'Título não encontrado'}</h2>
                    <p><strong>${noticia.Chamada || 'Chamada não encontrada'}</strong></p>
                    <p>${noticia['Notícia Completa'] || 'Notícia completa não encontrada'}</p>
                    <p><em>${noticia.categoria || 'Sem categoria'}</em> - ${noticia.fonte || 'Fonte não encontrada'}</p>
                    <p>Data: ${noticia.data || 'Data não encontrada'}</p>
                    ${noticia['URL da Imagem'] ? `<img src="${noticia['URL da Imagem']}" alt="${noticia.Título || 'Imagem'}" class="noticia-imagem">` : ''}
                    <button id="gerar-noticia-btn" style="margin-top: 10px;">Gerar Nova Notícia</button>
                </div>
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
            this.elementos.container.innerHTML = ''; // Limpa o container
            let noticiaRenderizada = false;
            if (data && data.noticia) {
                const noticiaElemento = this.criarElementoNoticia(data);
                this.elementos.container.innerHTML += noticiaElemento;
                noticiaRenderizada = true;
            } else if (data && data.resultados) {
                data.resultados.forEach(noticia => {
                    if (!noticia.erro) {
                        const noticiaElemento = this.criarElementoNoticia(noticia);
                        this.elementos.container.innerHTML += noticiaElemento;
                        noticiaRenderizada = true;
                    } else {
                        console.error("Erro ao processar notícia:", noticia.erro, "Tópico:", noticia.topico);
                        // Não exibe a mensagem de erro na tela
                    }
                });
            } else {
                // Não exibe a mensagem de erro na tela
            }
            if (noticiaRenderizada) {
                this.elementos.carregando.style.display = 'none'; // Esconde "Carregando..."
            }
            return noticiaRenderizada;
        },


        async buscarNoticia(tentativas = 0) {
            this.elementos.carregando.style.display = 'block';
            try {
                const response = await fetch(this.config.apiUrl);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();

                if (data.erro === "Não foi possível identificar tópicos em alta") {
                    console.warn(`Tentativa ${tentativas + 1}: tópicos não encontrados. Tentando novamente...`);
                    await this.aguardar(1000);
                    return this.buscarNoticia(tentativas + 1);
                }

                if (this.renderizarNoticia(data)) {
                    return;
                } else {
                    console.warn("Nenhuma notícia válida encontrada. Tentando novamente...");
                    await this.aguardar(1000);
                    return this.buscarNoticia(tentativas + 1);
                }

            } catch (err) {
                console.error(`Erro na tentativa ${tentativas + 1}:`, err);
                await this.aguardar(1000);
                return this.buscarNoticia(tentativas + 1);
            }
        },

        aguardar(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        },

        mostrarErro(mensagem = `Erro ao carregar notícia após tentativas.`) {
            const erroBloco = document.createElement('div');
            erroBloco.className = 'noticia-bloco';
            erroBloco.innerHTML = `<p class="erro">${mensagem}</p>`;
            this.elementos.container.appendChild(erroBloco);
        },

        inicializar() {
        this.elementos.container.addEventListener('click', (event) => {
            if (event.target && event.target.id === 'gerar-noticia-btn') {
                this.buscarNoticia();
            }
        });
        this.buscarNoticia();
    },
    };

    NoticiaManager.inicializar();
});