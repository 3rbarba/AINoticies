from datetime import date
from google.adk.agents import Agent
from google.adk.tools import google_search
from utils import call_agent

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
            Para cada tópico, tente identificar sua categoria principal
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
                    categoria = partes_topico[2].strip() if len(partes_topico) > 2 else "A DEFINIR"
                    categoria = categoria.split('\n')
                    for categoria in categoria:
                        inicio = categoria.find('(')
                        fim = categoria.find(')')
                        if inicio != -1 and fim != -1 and inicio < fim:
                            texto_entre_parenteses = categoria[inicio:fim+1].strip()
                            categoria = texto_entre_parenteses
                    topicos_com_categoria.append({'tópico': topico, 'categoria': categoria})
    print("Tópicos identificados:", topicos_com_categoria)
  
    return topicos_com_categoria[:50]
