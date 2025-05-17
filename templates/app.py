import os
import time
import warnings
from datetime import date

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import errors as genai_errors
from google.genai import types
from pytrends.request import TrendReq

warnings.filterwarnings("ignore")

# Configuração Inicial do Flask e CORS
app = Flask(__name__)
CORS(app)

# Configurações de Retentativa
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # segundos

# Carregamento das Variáveis de Ambiente
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicialização do Modelo Gemini
gemini_model = None
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
        print("Modelo Gemini inicializado com sucesso.")
    except Exception as e:
        print(f"Erro ao inicializar o modelo Gemini: {e}")
else:
    print("Chave da API do Google Generative AI não encontrada no arquivo .env")

# Inicialização do Pytrends
pytrends = TrendReq(hl='pt-BR', tz=-180)

# Função Auxiliar para Chamar Agentes com Retentativa
def call_agent(agent: Agent, message_text: str) -> str:
    """Envia uma mensagem para um agente via Runner com lógica de retentativa."""
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            for event in runner.run(user_id="user1", session_id="session1", new_message=content):
                if event.is_final_response():
                    for part in event.content.parts:
                        if part.text is not None:
                            final_response += part.text
                            final_response += "\n"
            return final_response
        except genai_errors.ServerError as e:
            print(f"Erro de servidor ao chamar o agente '{agent.name}': {e}")
            retries += 1
            backoff_time = INITIAL_BACKOFF * (2 ** (retries - 1))
            print(f"Retentando em {backoff_time} segundos...")
            time.sleep(backoff_time)
        except Exception as e:
            print(f"Erro inesperado ao chamar o agente '{agent.name}': {e}")
            raise  # Relevanta outras exceções
    raise Exception(f"Falha ao chamar o agente '{agent.name}' após {MAX_RETRIES} tentativas.")

# -------------------- Agente 1: Buscador de Tópicos --------------------
def identificar_topicos_em_alta():
    """Identifica os tópicos mais relevantes da semana usando um Agente com busca do Google."""
    buscador = Agent(
        name="agente_buscador_topicos",
        model="gemini-2.0-flash",
        instruction="""
            Você é um assistente de pesquisa de tendências. A sua tarefa é usar a ferramenta de busca do google (google_search)
            para identificar os 50 tópicos mais relevantes e comentados da semana.
            Organize os tópicos por ordem de relevância e atualidade, com base na quantidade e no entusiasmo das notícias e discussões sobre eles.
            Filtre temas sensíveis ou potencialmente ofensivos.
            Para cada tópico, tente identificar sua categoria principal (ex: política, entretenimento, esportes, tecnologia, etc.).
            Formato de saída desejado:
            [Número]. **[Tópico]** (Categoria: [categoria]): [Informações adicionais]
        """,
        description="Agente que busca os tópicos em alta no Google e os categoriza.",
        tools=[google_search]
    )

    hoje = date.today().strftime("%Y-%m-%d")
    entrada_do_agente_buscador = f"Data de hoje: {hoje}"

    resposta_do_buscador = call_agent(buscador, entrada_do_agente_buscador)
    print("Resposta do Agente Buscador de Tópicos:")
    print(resposta_do_buscador)

    topicos_com_categoria = []
    if resposta_do_buscador:
        for linha in resposta_do_buscador.split('\n'):
            linha = linha.strip()
            if linha.startswith(tuple(f"{i}. **" for i in range(1, 51))):
                partes_topico = linha.split('**')
                if len(partes_topico) > 1:
                    topico_completo = partes_topico[1].strip()
                    topico = topico_completo
                    categoria = "Sem Categoria"
                    if "(" in topico_completo and ")" in topico_completo:
                        inicio_categoria = topico_completo.find('(') + 1
                        fim_categoria = topico_completo.find(')')
                        if inicio_categoria < fim_categoria:
                            categoria_part = topico_completo[inicio_categoria:fim_categoria]
                            if ":" in categoria_part:
                                chave, valor = map(str.strip, categoria_part.split(':'))
                                if chave.lower() == 'categoria':
                                    categoria = valor
                                    topico = topico_completo[:topico_completo.find('(')].strip()
                                else:
                                    topico = topico_completo[:topico_completo.find('(')].strip()
                            else:
                                categoria = categoria_part
                                topico = topico_completo[:topico_completo.find('(')].strip()
                        else:
                            topico = topico_completo
                    topicos_com_categoria.append({'tópico': topico, 'categoria': categoria})

    print("Tópicos identificados:", topicos_com_categoria)

    if not topicos_com_categoria:
        topicos_com_categoria.append({
            'tópico': 'Tecnologia no Brasil',
            'categoria': 'Tecnologia'
        })

    return topicos_com_categoria[:5]

# -------------------- Agente 2: Pesquisador de Notícias --------------------
def pesquisar_ultimas_noticias(topico):
    """Pesquisa as últimas notícias relevantes sobre um tópico usando um Agente com busca do Google."""
    buscador_noticias = Agent(
        name="agente_pesquisador_noticias",
        model="gemini-2.0-flash",
        instruction=f"""
            Você é um especialista em pesquisa de notícias. Sua tarefa é usar a ferramenta de busca do google (google_search)
            para encontrar as 3 notícias mais relevantes e publicadas nos últimos 7 dias sobre o tópico: '{topico}'.
            Se não encontrar notícias nas últimas 24 horas, considere até a última semana.
            Para cada notícia, apresente o título, um breve resumo e a fonte.
            Priorize fontes confiáveis e atuais.
            Formato de saída desejado para cada notícia:
            - Título: [título da notícia]
              Fonte: [nome da fonte]
              Resumo: [breve resumo da notícia]
        """,
        description="Agente que pesquisa notícias relevantes sobre um tópico.",
        tools=[google_search]
    )

    entrada_do_agente = f"Tópico: {topico}"
    resposta_do_agente = call_agent(buscador_noticias, entrada_do_agente)
    print("Resposta do Agente Pesquisador de Notícias:")
    print(resposta_do_agente)

    time.sleep(4) # Adicionando a pausa DENTRO da função

    noticias = []
    if resposta_do_agente:
        if "- Título:" in resposta_do_agente:
            partes = resposta_do_agente.strip().split('\n- Título:')
            for parte in partes[1:]:
                detalhes = parte.strip().split('\n  Fonte:')
                if len(detalhes) == 2:
                    titulo = detalhes[0].strip()
                    fonte_resumo = detalhes[1].strip().split('\n  Resumo:')
                    if len(fonte_resumo) == 2:
                        fonte = fonte_resumo[0].strip()
                        resumo = fonte_resumo[1].strip()
                        noticias.append({'título': titulo, 'fonte': fonte, 'resumo': resumo})
        else:
            linhas = resposta_do_agente.strip().split('\n')
            titulo_atual = fonte_atual = resumo_atual = ""

            for linha in linhas:
                linha = linha.strip()
                if linha.startswith("Título:") or linha.startswith("- Título:"):
                    if titulo_atual:
                        if resumo_atual:
                            noticias.append({'título': titulo_atual, 'fonte': fonte_atual or "Desconhecida", 'resumo': resumo_atual})

                    titulo_atual = linha.replace("Título:", "").replace("- Título:", "").strip()
                    fonte_atual = resumo_atual = ""

                elif linha.startswith("Fonte:") or linha.startswith("  Fonte:"):
                    fonte_atual = linha.replace("Fonte:", "").replace("  Fonte:", "").strip()

                elif linha.startswith("Resumo:") or linha.startswith("  Resumo:"):
                    resumo_atual = linha.replace("Resumo:", "").replace("  Resumo:", "").strip()

            if titulo_atual and resumo_atual:
                noticias.append({'título': titulo_atual, 'fonte': fonte_atual or "Desconhecida", 'resumo': resumo_atual})

    if not noticias:
        print(f"AVISO: Não foram encontradas notícias para o tópico '{topico}'. Criando uma notícia fictícia para teste.")
        noticias.append({
            'título': f"Notícias recentes sobre {topico}",
            'fonte': "Portal de Notícias",
            'resumo': f"Este é um resumo gerado automaticamente para o tópico '{topico}' para permitir o teste do fluxo completo do sistema."
        })

    return noticias

# -------------------- Agente 3: Editor de Conteúdo --------------------
def editar_conteudo(noticias):
    """Resumi os fatos apurados, criando título, chamada e resumo usando um Agente."""
    editor_conteudo = Agent(
        name="agente_editor_conteudo",
        model="gemini-2.0-flash",
        instruction="""
            Você é um editor de notícias experiente. Dada uma lista de notícias com título, fonte e resumo,
            sua tarefa é gerar para a primeira notícia da lista:
            - Um título principal chamativo e informativo (máximo 10 palavras).
            - Uma breve chamada de capa (máximo 20 palavras) que atraia o leitor.
            - Um resumo conciso do conteúdo (máximo 50 palavras).
            - Até 3 palavras-chave relevantes para uma imagem.
            - Uma emoção desejada para a imagem (ex: neutro, positivo, alerta).

            Formato de saída desejado:
            Título: [título]
            Chamada de Capa: [chamada]
            Resumo: [resumo]
            Palavras-chave para imagem: [palavras-chave]
            Emoção desejada para imagem: [emoção]
        """,
        description="Agente que edita e resume notícias.",
        tools=[] # Este agente não precisa de ferramentas externas
    )

    if noticias:
        primeira_noticia = noticias[0]
        entrada_do_agente = f"""
            Título: {primeira_noticia['título']}
            Fonte: {primeira_noticia['fonte']}
            Resumo: {primeira_noticia['resumo']}
        """
        resposta_do_agente = call_agent(editor_conteudo, entrada_do_agente)
        print("Resposta do Agente Editor de Conteúdo:")
        print(resposta_do_agente)

        conteudo_editado = {}
        if resposta_do_agente:
            for linha in resposta_do_agente.split('\n'):
                linha = linha.strip()
                if ':' in linha:
                    partes = linha.split(':', 1)
                    if len(partes) == 2:
                        chave, valor = partes[0].strip(), partes[1].strip()
                        if chave == 'Título':
                            conteudo_editado['título'] = valor
                        elif chave == 'Chamada de Capa':
                            conteudo_editado['chamada'] = valor
                        elif chave == 'Resumo':
                            conteudo_editado['resumo'] = valor
                        elif chave == 'Palavras-chave para imagem':
                            conteudo_editado['palavras_chave_imagem'] = [p.strip() for p in valor.split(',')]
                        elif chave == 'Emoção desejada para imagem':
                            conteudo_editado['emocao_imagem'] = valor

        if not all(key in conteudo_editado for key in ['título', 'chamada', 'resumo', 'palavras_chave_imagem', 'emocao_imagem']):
            print("AVISO: Alguns campos estão faltando na edição. Preenchendo valores padrão.")
            if 'título' not in conteudo_editado:
                conteudo_editado['título'] = primeira_noticia['título']
            if 'chamada' not in conteudo_editado:
                conteudo_editado['chamada'] = "Nova notícia sobre " + primeira_noticia['título']
            if 'resumo' not in conteudo_editado:
                conteudo_editado['resumo'] = primeira_noticia['resumo'][:50] + "..."
            if 'palavras_chave_imagem' not in conteudo_editado:
                conteudo_editado['palavras_chave_imagem'] = ["notícia", "atualidade"]
            if 'emocao_imagem' not in conteudo_editado:
                conteudo_editado['emocao_imagem'] = "neutro"

        return conteudo_editado
    return {}

# -------------------- Agente 4: Gerador de Imagens --------------------
def gerar_imagens(conteudo_editado):
    """Gera URLs de placeholder para imagens."""
    imagens_geradas = []
    if conteudo_editado:
        titulo = conteudo_editado.get('título', 'Notícia')
        palavras_chave = conteudo_editado.get('palavras_chave_imagem', ['notícia'])
        emocao = conteudo_editado.get('emocao_imagem', 'neutro')

        prompt_imagem = f"Uma imagem relacionada a '{titulo}', com as palavras-chave: {', '.join(palavras_chave)}, transmitindo uma emoção '{emocao}'."
        url_imagem = "URL_IMAGEM_PLACEHOLDER" # Substituir pela lógica real de geração de imagem
        imagens_geradas.append({'título': titulo, 'url_imagem': url_imagem})
    return imagens_geradas

# -------------------- Agente 5: Revisor Geral --------------------
def revisar_geral(conteudo_editado, imagens_geradas):
    """Revisa o conteúdo e a imagem (placeholder) para qualidade usando um Agente."""
    revisor_geral = Agent(
        name="agente_revisor_geral",
        model="gemini-2.0-flash",

        instruction="""
            Você é um revisor de conteúdo editorial. Sua tarefa é revisar o título, a chamada de capa e o resumo de uma notícia,
            bem como a descrição da imagem (URL placeholder). Verifique a coerência, a ortografia, o tom adequado,
            a adequação para o público e a consistência visual (considerando a descrição da imagem).
            Faça as correções necessárias e retorne o conteúdo revisado no mesmo formato.

            Formato de entrada:
            Título: [título]
            Chamada: [chamada]
            Resumo: [resumo]
            URL da Imagem: [url_imagem]

            Formato de saída desejado:
            Título: [título revisado]
            Chamada: [chamada revisada]
            Resumo: [resumo revisado]
            URL da Imagem: [url_imagem]
        """,
        description="Agente que revisa o conteúdo gerado.",
        tools=[] # Este agente não precisa de ferramentas externas
    )

    if conteudo_editado and imagens_geradas:
        item_conteudo = conteudo_editado
        item_imagem = imagens_geradas[0] if imagens_geradas else {'url_imagem': 'URL_IMAGEM_PLACEHOLDER'}
        entrada_do_agente = f"""
            Título: {item_conteudo.get('título', '')}
            Chamada: {item_conteudo.get('chamada', '')}
            Resumo: {item_conteudo.get('resumo', '')}
            URL da Imagem: {item_imagem.get('url_imagem', 'URL_IMAGEM_PLACEHOLDER')}
        """
        resposta_do_agente = call_agent(revisor_geral, entrada_do_agente)
        print("Resposta do Agente Revisor Geral:")
        print(resposta_do_agente)

        noticia_revisada = {}
        if resposta_do_agente:
            for linha in resposta_do_agente.split('\n'):
                linha = linha.strip()
                if ':' in linha:
                    partes = linha.split(':', 1)  # Divide apenas na primeira ocorrência
                    if len(partes) == 2:
                        chave, valor = partes[0].strip(), partes[1].strip()
                        noticia_revisada[chave] = valor

        # Se a revisão falhar, retorne o conteúdo original
        if not noticia_revisada:
            print("AVISO: A revisão falhou. Mantendo o conteúdo original.")
            noticia_revisada = {
                'Título': item_conteudo.get('título', ''),
                'Chamada': item_conteudo.get('chamada', ''),
                'Resumo': item_conteudo.get('resumo', ''),
                'URL da Imagem': item_imagem.get('url_imagem', 'URL_IMAGEM_PLACEHOLDER')
            }

        return noticia_revisada
    return {}

# -------------------- Agente 6: Publicador --------------------
def publicar_noticia(noticia_final):
    """Simula a publicação da notícia."""
    if noticia_final:
        print("\n--- NOVO ARTIGO ---")
        print(f"Título: {noticia_final.get('Título', '')}")
        print(f"Chamada: {noticia_final.get('Chamada', '')}")
        print(f"Resumo: {noticia_final.get('Resumo', '')}")
        print(f"Categoria: {noticia_final.get('categoria', 'A DEFINIR')}") # A categoria vem do Agente 1
        print(f"URL da Imagem: {noticia_final.get('URL da Imagem', 'URL_IMAGEM_PLACEHOLDER')}")
        print("--- FIM DO ARTIGO ---")
        return True
    return False

# -------------------- Endpoints Flask --------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar_noticia', methods=['GET'])
def gerar_noticia():
    print("Iniciando o fluxo de geração de notícia (edição e imagem)...")
    try:
        topicos_em_alta = identificar_topicos_em_alta()
        if topicos_em_alta:
            primeiro_topico_info = topicos_em_alta[0]
            primeiro_topico = primeiro_topico_info['tópico']
            noticias_pesquisadas = pesquisar_ultimas_noticias(primeiro_topico)
            if noticias_pesquisadas:
                conteudo_editado = editar_conteudo(noticias_pesquisadas[:1])
                return jsonify({"status": "Edição de conteúdo realizada", "resultado": conteudo_editado})
            else:
                return jsonify({"erro": f"Não foram encontradas notícias para o tópico '{primeiro_topico}'"})
        else:
            return jsonify({"erro": "Não foi possível identificar tópicos em alta"})
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"ERRO: {str(e)}")
        print(error_traceback)
        return jsonify({"erro": f"Erro no processamento: {str(e)}", "detalhes": error_traceback})

@app.route('/gerar_noticia_completa', methods=['GET'])
def gerar_noticia_completa_endpoint():
    print("Iniciando o fluxo de geração de notícia completa...")
    try:
        topicos_em_alta = identificar_topicos_em_alta()
        if topicos_em_alta:
            primeiro_topico_info = topicos_em_alta[0]
            primeiro_topico = primeiro_topico_info['tópico']
            categoria_topico = primeiro_topico_info.get('categoria', 'A DEFINIR')
            noticias_pesquisadas = pesquisar_ultimas_noticias(primeiro_topico)
            if noticias_pesquisadas:
                conteudo_editado = editar_conteudo(noticias_pesquisadas[:1])
                imagens_geradas = gerar_imagens(conteudo_editado)
                noticia_revisada = revisar_geral(conteudo_editado, imagens_geradas)
                noticia_final = {**noticia_revisada, 'categoria': categoria_topico}
                publicado = publicar_noticia(noticia_final)
                return jsonify({"status": "Fluxo de geração de notícia completo (simulação)", "resultado": noticia_final})
            else:
                return jsonify({"erro": f"Não foram encontradas notícias para o tópico '{primeiro_topico}'"})
        else:
            return jsonify({"erro": "Não foi possível identificar tópicos em alta"})
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"ERRO: {str(e)}")
        print(error_traceback)
        return jsonify({"erro": f"Erro no processamento: {str(e)}", "detalhes": error_traceback})

if __name__ == '__main__':
    app.run(debug=True)