# 📰 Gerador de Notícias com IA 🤖

Este projeto utiliza inteligência artificial para automatizar a geração de notícias. Ele busca os tópicos mais relevantes, coleta informações e apresenta as notícias de forma organizada em uma interface web simples e funcional.

**Aviso:** Este projeto é um exercício educacional e está sob licença de uso livre. Use, modifique e aprenda com o código! 🎉

## Visão Geral 🧐

O sistema utiliza a API do Google Gemini para gerar notícias a partir de tópicos em alta. A interface web, construída com HTML, CSS e JavaScript, oferece uma maneira fácil de visualizar as notícias geradas.

## Funcionalidades ⚙️

* **Geração de Notícias:** Gera notícias automaticamente ao clicar no botão "Gerar Nova Notícia".
* **Interface Simples:** Exibe as notícias em blocos organizados, com título, chamada, resumo, fonte e data.
* **Estilização Moderna:** Design limpo e responsivo com CSS, incluindo um cabeçalho com banner e um rodapé informativo.
* **Carregamento Dinâmico:** Atualiza a página com novas notícias sem recarregar.
## Configuração e Uso 🛠️

Para utilizar este projeto, siga os passos abaixo:

1.  **Pré-requisitos:**
    * Certifique-se de ter o Python 3.x instalado no seu sistema.
    * Você precisará de uma chave de API do Google Gemini. Obtenha uma chave em [https://makersuite.google.com/](https://makersuite.google.com/).

2.  **Instalação:**
    * Clone o repositório para o seu computador:
        ```bash
        git clone <URL_DO_REPOSITÓRIO>
        cd <NOME_DO_DIRETÓRIO_DO_PROJETO>
        ```
    * (Se houver um backend Python) Crie um ambiente virtual (recomendado):
        ```bash
        python3 -m venv venv
        source venv/bin/activate  # No Linux/macOS
        venv\\Scripts\\activate  # No Windows
        ```
    * (Se houver um backend Python) Instale as dependências:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Configurar a Chave da API:**
    * Exporte sua chave da API do Google Gemini como uma variável de ambiente:
        ```bash
        export GOOGLE_API_KEY="SUA_CHAVE_AQUI" # No Linux/macOS
        set GOOGLE_API_KEY="SUA_CHAVE_AQUI"    # No Windows
        ```
        * Substitua `"SUA_CHAVE_AQUI"` pela sua chave real.

4.  **Executar o Projeto:**
    * (Se houver um backend Python) Inicie o servidor Flask:
        ```bash
        python app.py  # Ou o nome do arquivo principal do seu backend
        ```
    * Abra o arquivo `index.html` em seu navegador web.

5.  **Utilização:**
    * Na página web, clique no botão "Gerar Nova Notícia" para acionar o processo de geração de notícias.
    * As notícias geradas serão exibidas na página.

**Observações:**

* Certifique-se de que o servidor Flask esteja em execução (se aplicável) antes de abrir o `index.html`.
* A URL da API no `script.js` (ou outro arquivo JavaScript) deve corresponder à URL do seu servidor Flask.
* Adapte os comandos e nomes de arquivos conforme a estrutura do seu projeto.

## Arquitetura 🏛️

O projeto é composto por:

* **Backend (Python):** Utiliza Flask e a API Gemini para processar a geração das notícias.
* **Frontend (HTML, CSS, JavaScript):** Apresenta as notícias no navegador e interage com o usuário.

## Configuração 🛠️

1.  **Instalação:**
    * Clone o repositório.
    * Instale as dependências do Python (se houver).
2.  **Chave da API:**
    * Configure sua chave da API do Google Gemini.
3.  **Execução:**
    * Inicie o servidor Flask (se aplicável).
    * Abra o `index.html` no seu navegador.

## Estrutura do Projeto 📂

├── index.html       # Estrutura da página web
├── style.css        # Estilos da página
├── script.js        # Lógica da página
├── readme.md        # Este arquivo
└── ...            # Outros arquivos (Python, etc.)


## Tecnologias Utilizadas 💻

* HTML5
* CSS3
* JavaScript
* Google Gemini API
* Flask (se aplicável)

## Próximos Passos 🚀

* **Melhorias na Interface:** Adicionar mais detalhes e opções de interação.
* **Categorização de Notícias:** Permitir a seleção de categorias específicas.
* **Otimização:** Melhorar o desempenho e a velocidade de geração.

## Contribuição 🙏

Sinta-se à vontade para contribuir com ideias, melhorias e correções!

## Licença 📜

Este projeto é de uso livre para fins educacionais e pessoais.