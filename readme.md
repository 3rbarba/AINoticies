# 📰 Projeto de Apuração de Notícias com Agentes de IA 🤖

Este projeto utiliza agentes de inteligência artificial para automatizar o processo de geração de notícias. Ele identifica tópicos em alta, coleta informações de diversas fontes, edita o conteúdo para diferentes formatos (título, chamada, resumo, texto completo) e revisa o resultado final, tudo isso focado em entregar notícias relevantes e bem estruturadas.

**Aviso:** Este projeto foi desenvolvido como um exercício acadêmico e é disponibilizado sob uma licença de uso livre. Sinta-se à vontade para explorar, modificar e utilizar o código para aprendizado ou projetos pessoais! 🎉

## Visão Geral 🧐

O sistema é construído utilizando o framework Flask (Python 🐍) e a API do Google Generative AI (Gemini) ♊ para alimentar os agentes de IA. Cada etapa do processo de geração de notícias é realizada por um agente especializado, otimizando a eficiência e a qualidade do resultado final.

## Arquitetura 🏛️

A arquitetura do sistema é baseada em uma série de agentes que se comunicam e operam em conjunto para realizar as diferentes tarefas do fluxo de geração de notícias:

1.  **Agente Buscador de Tópicos:** Responsável por identificar os tópicos mais relevantes da semana, utilizando a busca do Google e outras fontes de tendências. 📈
2.  **Agente Pesquisador de Notícias:** Coleta as últimas notícias sobre um tópico específico, priorizando fontes confiáveis e diversificadas. 📰
3.  **Agente Editor de Conteúdo:** Edita e resume as notícias coletadas, gerando diferentes formatos como título, chamada, resumo e texto completo. ✂️
4.  **Agente Gerador de Imagens (Placeholder):** Gera URLs de placeholder para imagens relacionadas ao conteúdo da notícia. (Funcionalidade a ser aprimorada) 🎨
5.  **Agente Revisor Geral:** Realiza a revisão do conteúdo gerado, assegurando qualidade, coerência, correção gramatical e adequação ao público. 🕵️‍♀️
6.  **Agente Publicador (Simulação):** Simula a publicação da notícia final em uma plataforma online. 📢
7.  **Agente Coletor Detalhado:** Coleta informações detalhadas e contextuais das notícias, enriquecendo o conteúdo final. 📚

## Tecnologias Utilizadas 🛠️

* **Python:** Linguagem de programação principal para o desenvolvimento do sistema. 🐍
* **Flask:** Framework web Python utilizado para construir a API e servir a aplicação. 🌐
* **Flask-CORS:** Extensão Flask para habilitar o CORS (Cross-Origin Resource Sharing), permitindo a comunicação entre diferentes domínios. ↔️
* **Google Generative AI (Gemini):** Modelo de linguagem avançado utilizado para alimentar os agentes de IA. ♊
* **Google ADK (Agent Development Kit):** Framework para criar, gerenciar e orquestrar os agentes de IA. ⚙️
* **Pytrends:** Biblioteca Python para obter dados de tendências do Google, auxiliando na identificação de tópicos relevantes. 📊
* **python-dotenv:** Biblioteca para carregar variáveis de ambiente de um arquivo `.env`, mantendo informações sensíveis seguras. 🔑

## Configuração ⚙️

1.  **Pré-requisitos:**
    * Python 3.x instalado no sistema. 🐍
    * pip (Gerenciador de Pacotes do Python) para instalar as dependências. 📦

2.  **Instalação:**

    ```bash
    git clone <repositório_do_projeto> 📥
    cd <diretório_do_projeto> 📂
    python -m venv venv 🧪
    # Ativar o ambiente virtual (Windows)
    venv\Scripts\activate 🪟
    # Ativar o ambiente virtual (Linux/macOS)
    source venv/bin/activate 🐧🍎
    pip install -r requirements.txt ✅
    ```

    **Importante:** Certifique-se de que o arquivo `requirements.txt` esteja presente no diretório do projeto.

3.  **Configuração das Variáveis de Ambiente:**

    * Crie um arquivo `.env` na raiz do projeto. 📂
    * Adicione a seguinte variável ao arquivo `.env`:

        ```
        GOOGLE_API_KEY=YOUR_GOOGLE_GENAI_API_KEY 🔑
        ```

        Substitua `YOUR_GOOGLE_GENAI_API_KEY` pela sua chave da API do Google Generative AI.

4.  **Execução:**

    ```bash
    python app.py ▶️
    ```

    A aplicação estará disponível em `http://127.0.0.1:5000/` por padrão. 📍

## Endpoints da API 📡

* `/`: Renderiza a página inicial da aplicação (`index.html`). 🏠
* `/gerar_noticia`: Endpoint para gerar o conteúdo editado de uma notícia (título, chamada, resumo). Retorna um JSON com o resultado. ✨
* `/gerar_noticia_completa`: Endpoint para executar o fluxo completo de geração de notícias (incluindo edição, geração de imagem (placeholder), revisão e publicação simulada). Retorna um JSON com a notícia final. 🚀

## Estrutura do Código 📂

* `app.py`: Arquivo principal da aplicação Flask, responsável pela inicialização dos agentes, definição das rotas da API e orquestração do fluxo de geração de notícias. 🧠
* `templates/index.html`: Página inicial da aplicação, que pode ser uma interface de usuário para interagir com o sistema. 🎨
* `requirements.txt`: Arquivo que lista todas as dependências do projeto, facilitando a instalação. 📋
* `.env`: Arquivo para armazenar as variáveis de ambiente, mantendo-as separadas do código-fonte. 🙈

## Agentes Detalhados 🕵️

### 1. Agente Buscador de Tópicos (`agente_buscador_topicos`) 📈

* **Responsabilidade:** Identificar os tópicos mais relevantes e comentados da semana, utilizando ferramentas de busca e análise de tendências. 🔍
* **Modelo de IA:** Gemini 2.0-flash ♊
* **Ferramentas:** `google_search`, `pytrends` 🌐
* **Instruções:**
    * Utiliza a busca do Google e outras fontes para listar os 50 tópicos mais comentados. 📝
    * Organiza os tópicos por relevância e atualidade, considerando a quantidade e o engajamento das notícias e discussões. 🥇
    * Filtra temas sensíveis ou potencialmente ofensivos, garantindo a adequação do conteúdo. 🚫
    * Identifica a categoria principal de cada tópico para facilitar a organização e o contexto. 🏷️
    * Formato de saída: `[Número]. **[Tópico]** (Categoria: [categoria]): [Informações adicionais]` 📄

### 2. Agente Pesquisador de Notícias (`agente_pesquisador_noticias`) 📰

* **Responsabilidade:** Pesquisar as últimas notícias relevantes sobre um tópico e categoria específicos. 🧐
* **Modelo de IA:** Gemini 2.0-flash ♊
* **Ferramentas:** `google_search` 🌐
* **Instruções:**
    * Encontra as 3 notícias mais relevantes e recentes sobre um tópico e categoria específicos. 🕵️‍♀️
    * Prioriza fontes confiáveis, diversas e atuais, buscando diferentes perspectivas sobre o mesmo evento. ✅
    * Apresenta o título, resumo, fonte e data de publicação de cada notícia. ✍️
    * Formato de saída:

        ```
        - Título: [título da notícia] 📰
          Fonte: [nome da fonte] 🏢
          Resumo: [breve resumo da notícia] 📝
          Data: [data da notícia] 📅
        ```

### 3. Agente Editor de Conteúdo (`agente_editor_conteudo`) ✂️

* **Responsabilidade:** Editar e resumir as notícias, gerando diferentes formatos de conteúdo. ✍️
* **Modelo de IA:** Gemini 2.0-flash ♊
* **Ferramentas:** Nenhuma 🚫
* **Instruções:**
    * Gera um título principal chamativo e informativo (máximo 10 palavras). 💥
    * Cria uma breve chamada de capa (máximo 20 palavras) que atraia o leitor. 📣
    * Escreve um resumo conciso do conteúdo (máximo 50 palavras). 📝
    * Gera um texto completo da notícia, combinando informações das diferentes fontes. 📖
    * Gera palavras-chave e emoção para orientar a geração de uma imagem relevante. 🎨
    * Formato de saída:

        ```
        Título: [título] 📰
        Chamada de Capa: [chamada] 📢
        Resumo: [resumo] 📝
        Texto Completo: [texto completo] 📖
        Palavras-chave para imagem: [palavras-chave] 🔑
        Emoção desejada para imagem: [emoção] 😊
        Data: [data da notícia] 📅
        ```

### 4. Agente Gerador de Imagens (`agente_gerador_imagem`) 🖼️

* **Responsabilidade:** Gerar URLs de placeholder para imagens relacionadas ao conteúdo da notícia. 🎨
* **Modelo de IA:** Gemini 2.0-flash ♊ (Substituir pelo modelo de geração de imagem correto)
* **Ferramentas:** Nenhuma 🚫
* **Instruções:**
    * Gera uma imagem relacionada ao conteúdo editado, utilizando as palavras-chave e a emoção desejada. 🖼️
    * Retorna a URL da imagem gerada (placeholder). 📍
    * **Observação:** Atualmente, gera apenas placeholders. A lógica real de geração de imagens precisa ser implementada utilizando um modelo de IA de geração de imagens. 🚧

### 5. Agente Revisor Geral (`agente_revisor_geral`) ✅

* **Responsabilidade:** Revisar o conteúdo gerado para garantir qualidade, coerência e adequação. 🧐
* **Modelo de IA:** Gemini 2.0-flash ♊
* **Ferramentas:** Nenhuma 🚫
* **Instruções:**
    * Revisa título, chamada, resumo, texto completo e descrição da imagem. 🕵️‍♀️
    * Verifica coerência, ortografia, gramática, tom adequado, formatação e consistência visual. 🧐
    * Realiza as correções necessárias para aprimorar o texto e garantir a qualidade da notícia. ✍️
    * Formato de saída:

        ```
        Título: [título revisado] 📰
        Chamada: [chamada revisada] 📢
        Resumo: [resumo revisado] 📝
        Texto Completo: [texto completo revisado] 📖
        URL da Imagem: [url_imagem] 📍
        Data: [data revisada] 📅
        ```

### 6. Agente Publicador (`agente_publicador`) 📢

* **Responsabilidade:** Simular a publicação da notícia em uma plataforma online. 📣
* **Modelo de IA:** Gemini 2.0-flash ♊
* **Ferramentas:** Nenhuma 🚫
* **Instruções:**
    * Simula a publicação da notícia final revisada, incluindo todos os elementos (título, chamada, resumo, texto completo, imagem, etc.). 📰
    * Retorna uma mensagem indicando o sucesso ou a falha da publicação (simulada). ✅ ou ❌

### 7. Agente Coletor Detalhado (`agente_coletor_detalhado`) 📚

* **Responsabilidade:** Coletar informações detalhadas e contextuais sobre as notícias. 🧐
* **Modelo de IA:** Gemini 2.0-flash ♊
* **Ferramentas:** `google_search` 🌐
* **Instruções:**
    * Encontra notícias mais completas e detalhadas sobre um tópico específico. 📰
    * Pode trazer o texto completo da notícia ou um resumo mais extenso, dependendo da disponibilidade. 📝
    * Busca informações adicionais, como citações, estatísticas, opiniões de especialistas, etc. 📊
    * Formato de saída:

        ```
        - Resumo Detalhado: ... 📝
        - Notícia Completa: ... (se aplicável) 📖
        - Fonte: ... 🏢
        - Informações Adicionais: ... ➕
        ```

## Fluxo de Geração de Notícias ⚙️

O fluxo principal de geração de notícias é orquestrado pelo endpoint `/gerar_noticia_completa`: 🚀

1.  O Agente Buscador de Tópicos identifica os tópicos em alta. 🔥
2.  O Agente Pesquisador de Notícias coleta as notícias sobre o primeiro tópico. 📰
3.  O Agente Editor de Conteúdo edita e resume as notícias, gerando os diferentes formatos de conteúdo. ✂️
4.  O Agente Gerador de Imagens gera a URL da imagem (placeholder). 🖼️
5.  O Agente Revisor Geral revisa o conteúdo, garantindo a qualidade final. ✅
6.  O Agente Publicador simula a publicação da notícia. 📢
7.  O Agente Coletor Detalhado é utilizado para enriquecer o conteúdo com informações adicionais, se necessário. 📚

## Próximos Passos ⏭️

* **Implementar a Geração Real de Imagens:** Substituir os placeholders de URL por um serviço ou modelo de IA de geração de imagens. 🎨➡️🖼️
* **Melhorar a Interface do Usuário:** Desenvolver uma interface mais completa e amigável para exibir as notícias e interagir com o sistema. 💻➡️📱
* **Persistir Dados:** Implementar um banco de dados para armazenar as notícias geradas, permitindo o acesso e a recuperação posterior. 💾
* **Otimizar o Desempenho:** Explorar técnicas de paralelização e otimização de código para acelerar o processo de geração de notícias. ⚡️
* **Adicionar Autenticação e Autorização:** Proteger a API com mecanismos de segurança, controlando o acesso e as permissões. 🔒
* **Implementar Testes Automatizados:** Desenvolver testes unitários e de integração para garantir a estabilidade e a confiabilidade do sistema. ✅

## Contribuição 🙏

Contribuições são bem-vindas! Se você tiver sugestões de melhorias, correções de bugs ou novas funcionalidades, sinta-se à vontade para abrir uma issue ou enviar um pull request no repositório do projeto. 🤝

## Licença 📜

Este projeto foi desenvolvido como um exercício acadêmico e é disponibilizado sob uma licença de uso livre. Sinta-se à vontade para explorar, modificar e utilizar o código para aprendizado ou projetos pessoais! 🎉

## Considerações Finais

O projeto ainda está em desenvolvimento, mas já demonstra um potencial significativo para automatizar e aprimorar o processo de geração de notícias. As próximas etapas se concentrarão em refinar as funcionalidades existentes, adicionar novas capacidades e garantir a qualidade e a confiabilidade do sistema.