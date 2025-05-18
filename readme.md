# 📰 Projeto de Apuração de Notícias com Agentes de IA 🤖

Este projeto utiliza agentes de inteligência artificial para automatizar o processo de geração de notícias. Ele identifica tópicos em alta , coleta informações de notícias , edita o conteúdo e revisa o resultado final, escolhendo um tema em alta e buscando uma noticia em alta sobre esse tema.

**Aviso:** Este projeto foi desenvolvido como um exercício divertido proposto pela Alura e é oferecido sem licença. Sinta-se à vontade para explorar, modificar e usar o código como desejar! 🎉

## Visão Geral 🧐

O sistema é construído usando Flask (um framework web em Python 🐍) e utiliza a API do Google Generative AI (Gemini) ♊ para alimentar os agentes. Cada etapa do processo de geração de notícias é realizada por um agente especializado.

## Arquitetura 🏛️

A arquitetura do sistema é baseada em uma série de agentes que se comunicam para realizar diferentes tarefas:

1.  **Agente Buscador de Tópicos:** Identifica os tópicos mais relevantes da semana usando a busca do Google. 📈
2.  **Agente Pesquisador de Notícias:** Coleta as últimas notícias sobre um determinado tópico. 📰
3.  **Agente Editor de Conteúdo:** Edita e resume as notícias coletadas, criando título, chamada e resumo. ✂️
4.  **Agente Gerador de Imagens:** Gera URLs de placeholder para imagens relacionadas ao conteúdo. 🎨
5.  **Agente Revisor Geral:** Revisa o conteúdo gerado para garantir qualidade e coerência. 🕵️‍♀️
6.  **Agente Publicador:** Simula a publicação da notícia final. 📢
7.  **Agente Coletor Detalhado:** Coleta informações detalhadas de notícias. 📚

## Tecnologias Utilizadas 🛠️

* **Python:** Linguagem de programação principal. 🐍
* **Flask:** Framework web para construir a API. 🌐
* **Flask-CORS:** Extensão Flask para habilitar o CORS (Cross-Origin Resource Sharing). ↔️
* **Google Generative AI (Gemini):** Modelo de linguagem para os agentes. ♊
* **Google ADK (Agent Development Kit):** Framework para criar e gerenciar agentes. ⚙️
* **Pytrends:** Biblioteca Python para obter dados de tendências do Google. 📊
* **python-dotenv:** Biblioteca para carregar variáveis de ambiente de um arquivo .env. 🔑

## Configuração ⚙️

1.  **Pré-requisitos:**
    * Python 3.x 🐍
    * pip (Gerenciador de Pacotes do Python) 📦

2.  **Instalação:**

    ```bash
    git clone <repositório_do_projeto> 📥
    cd <diretório_do_projeto> 📂
    python -m venv venv 🧪
    venv\Scripts\activate  # No Windows 🪟
    source venv/bin/activate # No Linux/macOS 🐧🍎
    pip install -r requirements.txt ✅
    ```

    **Importante:** Certifique-se de ter o arquivo `requirements.txt` no diretório do projeto para instalar todas as dependências corretamente.

3.  **Configuração das Variáveis de Ambiente:**

    * Crie um arquivo `.env` na raiz do projeto. 📂
    * Adicione as seguintes variáveis ao arquivo `.env`:

        ```
        GOOGLE_API_KEY=YOUR_GOOGLE_GENAI_API_KEY 🔑
        ```

        Substitua `YOUR_GOOGLE_GENAI_API_KEY` pela sua chave da API do Google Generative AI. 🤫

4.  **Execução:**

    ```bash
    python app.py ▶️
    ```

    A aplicação estará disponível em `http://127.0.0.1:5000/` por padrão. 📍

## Endpoints da API 📡

* `/`: Renderiza a página inicial (`index.html`). 🏠
* `/gerar_noticia`: Gera o conteúdo editado de uma notícia (título, chamada, resumo). Retorna um JSON com o resultado. ✨
* `/gerar_noticia_completa`: Executa o fluxo completo de geração de notícias (incluindo edição, geração de imagem, revisão e publicação simulada). Retorna um JSON com a notícia final. 🚀

## Estrutura do Código 📂

* `app.py`: Arquivo principal da aplicação Flask, contendo a lógica para inicializar os agentes, definir as rotas da API e orquestrar o fluxo de geração de notícias. 🧠
* `templates/index.html`: Página inicial da aplicação (pode ser uma página simples ou uma interface mais elaborada). 🎨
* `requirements.txt`: Lista de dependências do projeto. 📋
* `.env`: Arquivo para armazenar as variáveis de ambiente (não deve ser versionado). 🙈

## Agentes Detalhados 🕵️

###   1. Agente Buscador de Tópicos (`agente_buscador_topicos`) 📈

* **Responsabilidade:** Identificar os tópicos mais relevantes e comentados da semana usando a ferramenta de busca do Google. 🔍
* **Modelo:** Gemini 2.0-flash ♊
* **Ferramentas:** `google_search` 🌐
* **Instruções:**
    * Utiliza a busca do Google para listar os 50 tópicos mais comentados. 📝
    * Organiza os tópicos por relevância e atualidade. 🥇
    * Filtra temas sensíveis ou ofensivos. 🚫
    * Identifica a categoria principal de cada tópico. 🏷️
    * Formato de saída: `[Número]. **[Tópico]** (Categoria: [categoria]): [Informações adicionais]` 📄

###   2. Agente Pesquisador de Notícias (`agente_pesquisador_noticias`) 📰

* **Responsabilidade:** Pesquisar as últimas notícias relevantes sobre um tópico específico. 🧐
* **Modelo:** Gemini 2.0-flash ♊
* **Ferramentas:** `google_search` 🌐
* **Instruções:**
    * Encontra as 3 notícias mais relevantes e recentes sobre um tópico e categoria específicos. 🕵️‍♀️
    * Prioriza fontes confiáveis e atuais. ✅
    * Apresenta o título, resumo e fonte de cada notícia. ✍️
    * Formato de saída:

        ```
        -   Título: [título da notícia] 📰
            Fonte: [nome da fonte] 🏢
            Resumo: [breve resumo da notícia] 📝
        ```

###   3. Agente Editor de Conteúdo (`agente_editor_conteudo`) ✂️

* **Responsabilidade:** Editar e resumir as notícias, criando título, chamada e resumo. ✍️
* **Modelo:** Gemini 2.0-flash ♊
* **Ferramentas:** Nenhuma 🚫
* **Instruções:**
    * Gera um título chamativo e informativo (máximo 10 palavras). 💥
    * Cria uma breve chamada de capa (máximo 20 palavras). 📣
    * Escreve um resumo conciso (máximo 50 palavras). 📝
    * Gera palavras-chave e emoção para uma imagem. 🎨
    * Formato de saída:

        ```
        Título: [título] 📰
        Chamada de Capa: [chamada] 📢
        Resumo: [resumo] 📝
        Palavras-chave para imagem: [palavras-chave] 🔑
        Emoção desejada para imagem: [emoção] 😊
        ```

###   4. Agente Gerador de Imagens (`agente_gerador_imagem`) 🖼️

* **Responsabilidade:** Gerar URLs de placeholder para imagens relacionadas ao conteúdo. 🎨
* **Modelo:** Gemini 2.0-flash ♊ (Substituir pelo modelo de geração de imagem correto)
* **Ferramentas:** Nenhuma 🚫
* **Instruções:**
    * Cria uma imagem relacionada ao conteúdo editado. 🖼️
    * Usa palavras-chave e emoção para gerar a URL da imagem. 🔑😊
    * Retorna a URL da imagem gerada (placeholder). 📍
    * **Observação:** Atualmente, gera apenas placeholders. A lógica real de geração de imagens precisa ser implementada. 🚧

###   5. Agente Revisor Geral (`agente_revisor_geral`) ✅

* **Responsabilidade:** Revisar o conteúdo gerado para garantir qualidade e coerência. 🧐
* **Modelo:** Gemini 2.0-flash ♊
* **Ferramentas:** Nenhuma 🚫
* **Instruções:**
    * Revisa título, chamada, resumo e descrição da imagem. 🕵️‍♀️
    * Verifica coerência, ortografia, tom adequado e consistência visual. 🧐
    * Faz as correções necessárias. ✍️
    * Formato de saída:

        ```
        Título: [título revisado] 📰
        Chamada: [chamada revisada] 📢
        Resumo: [resumo revisado] 📝
        URL da Imagem: [url_imagem] 📍
        ```

###   6. Agente Publicador (`agente_publicador`) 📢

* **Responsabilidade:** Simular a publicação da notícia. 📣
* **Modelo:** Gemini 2.0-flash ♊
* **Ferramentas:** Nenhuma 🚫
* **Instruções:**
    * Simula a publicação da notícia final revisada. 📰
    * Retorna "Publicado com sucesso." ✅ ou "Falha na publicação.". ❌

###   7. Agente Coletor Detalhado (`agente_coletor_detalhado`) 📚

* **Responsabilidade:** Coletar notícias detalhadas sobre um tópico. 🧐
* **Modelo:** Gemini 2.0-flash ♊
* **Ferramentas:** `google_search` 🌐
* **Instruções:**
    * Encontra notícias reais e recentes sobre um tópico. 📰
    * Pode trazer o texto completo ou apenas um resumo. 📝
    * Formato de saída:

        ```
        -   Resumo: ... 📝
        -   Notícia completa: ... (se aplicável) 📖
        -   Fonte: ... 🏢
        ```

## Fluxo de Geração de Notícias ⚙️

O fluxo principal de geração de notícias é orquestrado pela rota `/gerar_noticia_completa`: 🚀

1.  O Agente Buscador de Tópicos identifica os tópicos em alta. 🔥
2.  O Agente Pesquisador de Notícias coleta as notícias sobre o primeiro tópico. 📰
3.  O Agente Editor de Conteúdo edita e resume as notícias. ✂️
4.  O Agente Gerador de Imagens gera a URL da imagem (placeholder). 🖼️
5.  O Agente Revisor Geral revisa o conteúdo. ✅
6.  O Agente Publicador simula a publicação da notícia. 📢

## Próximos Passos ⏭️

* **Implementar a Geração Real de Imagens:** Substituir os placeholders de URL por um serviço real de geração de imagens. 🎨➡️🖼️
* **Melhorar a Interface do Usuário:** Desenvolver uma interface mais completa para exibir as notícias e interagir com o sistema. 💻➡️📱
* **Persistir Dados:** Implementar um banco de dados para armazenar as notícias geradas. 💾
* **Otimizar o Desempenho:** Explorar técnicas de paralelização para acelerar o processo. ⚡️
* **Adicionar Autenticação e Autorização:** Proteger a API com mecanismos de segurança. 🔒

## Contribuição 🙏

Contribuições são bem-vindas! Se você tiver sugestões de melhorias ou correções de bugs, sinta-se à vontade para abrir uma issue ou enviar um pull request. 🤝

## Licença 📜

Este projeto foi desenvolvido como um exercício divertido proposto pela Alura e é oferecido sem licença. Sinta-se à vontade para explorar, modificar e usar o código como desejar! 🎉

## Considerações finais

Infelizmente não vai ser possível deixar do jeito que eu queria pois eu comecei a fazer hoje.