document.addEventListener('DOMContentLoaded', function() {
    const carregandoNoticiaDiv = document.getElementById('carregando-noticia');
    const conteudoNoticiaDiv = document.getElementById('conteudo-noticia');

    fetch('http://127.0.0.1:5000/gerar_noticia_completa')
        .then(response => response.json())
        .then(data => {
            console.log("Dados recebidos:", data);
            carregandoNoticiaDiv.style.display = 'none'; // Oculta a mensagem de carregamento
            if (data.resultado) {
                const noticia = data.resultado;
                document.getElementById('titulo-noticia').textContent = noticia.Título || 'Título não encontrado';
                document.getElementById('chamada-noticia').textContent = noticia.Chamada || 'Chamada não encontrada';
                document.getElementById('resumo-noticia').textContent = noticia.Resumo || 'Resumo não encontrado';
                document.getElementById('categoria-noticia').textContent = noticia.categoria || 'Sem categoria';
                document.getElementById('imagem-noticia').src = noticia['URL da Imagem'] || '';
                document.getElementById('imagem-noticia').alt = noticia.Título || 'Imagem da Notícia';
                conteudoNoticiaDiv.style.display = 'block'; // Exibe o conteúdo da notícia

                // Se quisermos exibir outros tópicos (lembre-se que o endpoint atual retorna apenas 1 notícia)
                if (data.outros_topicos && Array.isArray(data.outros_topicos)) {
                    const listaOutrosTopicos = document.getElementById('lista-outros-topicos');
                    const outrosTopicosContainer = document.getElementById('outros-topicos-container');
                    listaOutrosTopicos.innerHTML = ''; // Limpa a lista anterior
                    data.outros_topicos.forEach(topico => {
                        const li = document.createElement('li');
                        li.textContent = `${topico.tópico} (Categoria: ${topico.categoria || 'A Definir'})`;
                        listaOutrosTopicos.appendChild(li);
                    });
                    outrosTopicosContainer.style.display = 'block';
                }
            } else if (data.erro) {
                document.querySelector('main').innerHTML = `<p class="erro">${data.erro}</p>`;
            }
        })
        .catch(error => {
            console.error("Erro ao buscar dados da API:", error);
            document.querySelector('main').innerHTML = `<p class="erro">Erro ao carregar a notícia.</p>`;
            carregandoNoticiaDiv.style.display = 'none'; // Garante que a mensagem de carregamento desapareça em caso de erro
        });
});