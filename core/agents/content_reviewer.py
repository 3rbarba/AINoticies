from google.adk.agents import Agent
from utils import call_agent

def revisar_geral(conteudo_editado):
    """Revisa o conteúdo para qualidade usando um Agente."""
    revisor_geral = Agent(
        name="agente_revisor_geral",
        model="gemini-2.0-flash",
        instruction="""
            Você é um revisor de conteúdo editorial. Sua tarefa é revisar o título, a chamada de capa, o resumo e a notícia completa.
            Verifique a coerência, a ortografia, o tom adequado e a adequação para o público.
            Faça as correções necessárias e retorne o conteúdo revisado no mesmo formato.

            Formato de entrada:
            Título: [título]
            Chamada: [chamada]
            Resumo: [resumo]
            Notícia Completa: [texto completo]
            Data: [data]

            Formato de saída desejado:
            Título: [título revisado]
            Chamada: [chamada revisada]
            Resumo: [resumo revisado]
            Notícia Completa: [texto completo revisado]
            Data: [data revisada]
        """,
        description="Agente que revisa o conteúdo gerado.",
        tools=[]
    )

    if conteudo_editado:
        entrada_do_agente = f"""
            Título: {conteudo_editado.get('título', '')}
            Chamada: {conteudo_editado.get('chamada', '')}
            Resumo: {conteudo_editado.get('resumo', '')}
            Notícia Completa: {conteudo_editado.get('noticia_completa', '')}
            Data: {conteudo_editado.get('data', '')}
        """
        resposta_do_agente = call_agent(revisor_geral, entrada_do_agente)
        print("Resposta do Agente Revisor Geral:")
        print(resposta_do_agente)

        noticia_revisada = {}
        if resposta_do_agente:
            for linha in resposta_do_agente.split('\n'):
                linha = linha.strip()
                if ':' in linha:
                    partes = linha.split(':', 1)
                    if len(partes) == 2:
                        chave, valor = partes[0].strip(), partes[1].strip()
                        noticia_revisada[chave] = valor

        if not noticia_revisada:
            print("AVISO: A revisão falhou. Mantendo o conteúdo original.")
            noticia_revisada = {
                'Título': conteudo_editado.get('título', ''),
                'Chamada': conteudo_editado.get('chamada', ''),
                'Resumo': conteudo_editado.get('resumo', ''),
                'Notícia Completa': conteudo_editado.get('noticia_completa', ''),
                'Data': conteudo_editado.get('data', '')
            }

        return noticia_revisada
    return {}
