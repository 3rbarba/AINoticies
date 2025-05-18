from .topic_finder import identificar_topicos_em_alta
from .news_searcher import pesquisar_noticias  # Alterado aqui
from .content_editor import editar_conteudo
from .content_collector import agente_coletor_detalhado
from .content_reviewer import revisar_geral
from .publisher import publicar_noticia

__all__ = [
    'identificar_topicos_em_alta',
    'pesquisar_noticias',  # Alterado aqui
    'editar_conteudo',
    'agente_coletor_detalhado',
    'revisar_geral',
    'publicar_noticia'
]