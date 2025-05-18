from google.adk.agents import Agent
from google.adk.tools import google_search
from utils import call_agent

def agente_coletor_detalhado(topico: str, completo: bool, noticias: str, categoria: str):
    """Coleta notícias detalhadas sobre um tópico usando um Agente com busca do Google."""
    coletor = Agent(
        name="agente_coletor_detalhado",
        model="gemini-2.0-flash",
        instruction=f"""
            Você é um assistente de coleta de conteúdo jornalístico.
            Com base nas seguintes notícias resumidas sobre o tópico "{topico}" da categoria "{categoria}", sua tarefa é:
            - Compreender os fatos principais.
            - Gerar um texto completo e informativo da notícia, com no mínimo 4 parágrafos.
            - Indicar a fonte principal da informação.
            - Incluir a data mais precisa possível do fato relatado.

            Notícias resumidas disponíveis:
            {noticias}

            Formato de saída desejado:
            Notícia Completa: [texto completo]
            Fonte: [fonte confiável utilizada]
            Data: [data do evento ou da publicação]
        """,
        description="Agente que expande resumos em uma notícia completa com fonte e data.",
        tools=[google_search]
    )

    entrada = f"Tópico: {topico}\nCategoria: {categoria}"
    resposta = call_agent(coletor, entrada)
    print("Resposta do Agente Coletor Detalhado:")
    print(resposta)

    resultado = {'noticia_completa': '', 'fonte': '', 'data': ''}

    if resposta:
        for linha in resposta.split('\n'):
            linha = linha.strip()
            if linha.startswith("Notícia Completa:"):
                resultado['noticia_completa'] = linha.replace("Notícia Completa:", "").strip()
            elif linha.startswith("Fonte:"):
                resultado['fonte'] = linha.replace("Fonte:", "").strip()
            elif linha.startswith("Data:"):
                resultado['data'] = linha.replace("Data:", "").strip()

    return resultado
