# 📰 Gerador de Notícias com IA 🤖

Este projeto utiliza inteligência artificial para automatizar a geração de notícias. Ele busca os tópicos mais relevantes, coleta informações e apresenta as notícias de forma organizada em uma interface web simples e funcional.
[![Watch the video](https://github.com/3rbarba/AINoticies/blob/main/image.png)](https://youtu.be/Y4y_oUvBDeQ)

**Aviso:** Este projeto é um exercício educacional e está sob licença de uso livre. Use, modifique e aprenda com o código! 🎉

## Visão Geral 🧐

O sistema utiliza a API do Google Gemini para gerar notícias a partir de tópicos em alta. A interface web, construída com HTML, CSS e JavaScript, oferece uma maneira fácil de visualizar as notícias geradas.

## Funcionalidades ⚙️

* **Geração de Notícias:** Gera notícias automaticamente ao clicar no botão "Gerar Nova Notícia".
* **Interface Simples:** Exibe as notícias em blocos organizados, com título, chamada, resumo, fonte e data.
* **Estilização Moderna:** Design limpo e responsivo com CSS, incluindo um cabeçalho com banner e um rodapé informativo.
* **Carregamento Dinâmico:** Atualiza a página com novas notícias sem recarregar.

## Configuração e Uso 🛠️

1. **Pré-requisitos:**
   * [Python 3.x instalado.(https://www.python.org/downloads/)] 
   * [Chave da API do Google Gemini. (https://makersuite.google.com/)]

2. **Instalação:**
   ```bash
   git clone https://github.com/3rbarba/AINoticies
   cd AINoticies
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

3. **Configurar a Chave da API:**
   ```bash
   export GOOGLE_API_KEY="SUA_CHAVE_AQUI"  # Linux/macOS
   set GOOGLE_API_KEY="SUA_CHAVE_AQUI"     # Windows
   ```

4. **Executar o Projeto:**
   ```bash
   cd core
   python app.py
   ```

5. **Utilização:**
   * Acesse `index.html` no navegador.
   * Clique em "Gerar Nova Notícia" para visualizar o conteúdo gerado.

## Arquitetura 🏛️

* **Backend (Python):** Flask + Google Gemini para geração de conteúdo.
* **Frontend (HTML, CSS, JavaScript):** Interface de usuário interativa.

## Endpoints 📌
```
/api/news [POST] #Processar notícia específica (via POST)
/api/news/<topic> [GET] #Processar notícia específica (via GET)
/api/topics [GET] #Buscar tópicos
/api/news/filter [GET] #Filtrar notícias por categoria
/api/news/categorias [GET] #Obter categorias disponíveis
/api/gemini-tts [POST] #Gerar áudio a partir de texto (Gemini TTS)
```

## Estrutura do Projeto 📂

```
AluraDesafio/
├── core/
│   ├── app.py           # Backend Flask
│   ├── config.py        # Configuração e chave da API
│   ├── utils.py         # Funções utilitárias
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Estilos da aplicação
│   │   ├── js/
│   │   │   ├── main.js      # Inicialização do frontend
│   │   │   └── utils.js     # Utilidades do frontend
│   │   └── images/
│   │       └── github.svg    # Ícones e imagens
│   └── templates/
│       ├── index.html        # Página principal
│       └── newsGenerator.js  # Lógica de geração de notícias
```

## Tecnologias Utilizadas 💻

* HTML5
* CSS3
* JavaScript
* Flask
* Google Gemini API

## Contribuição 🙏

Sinta-se à vontade para abrir issues, enviar PRs e compartilhar ideias!

## Licença 📜

Este projeto é livre para fins educacionais e pessoais.
