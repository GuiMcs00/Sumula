import os
import sys
import re
import requests
import time
import json
from bs4 import BeautifulSoup

from utils import blue_log, green_log, yellow_log, red_log

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)



    
 
def obter_link_diario(titulo, escopo, texto, data_pub, secao, pubOrder, qtd_excecoes=0, max_tentativas=3):
    # Busca os links das matérias no sistema do Diário Oficial:
    blue_log(f'Buscando link para o artigo {titulo}')
 
    header_link = {"Accept": "application/json"}
    url = f"https://www.in.gov.br/leiturajornal?data={data_pub}&secao={secao}"
    
    texto_full = titulo + " " + texto

    escopo_splitado = escopo.split("/")
    primeiro_escopo = escopo_splitado[0]
 
    while qtd_excecoes < max_tentativas:
        try:
            blue_log('Tentando conexão com o Diário Oficial...')
            
            lista = extrair_dados(url, header_link)
 
            link_base = "https://www.in.gov.br/web/dou/-/"
            # Verifica o conteúdo da lista para encontrar o link correto
            for dado in lista:
                
                # Aplicação das regras de busca
                if primeiro_escopo in dado['hierarchyStr'] and re.search(str(dado['title']).replace('*', ''), str(titulo).replace('*', ''), re.IGNORECASE) \
                        and not re.search("Despacho", titulo, re.IGNORECASE) \
                        and not re.search("(Portarias de(.*?[0-9](.*?de [0-9]{4})))", titulo, re.IGNORECASE) \
                        and not re.search("(Decretos de(.*?[0-9](.*?de [0-9]{4})))", titulo, re.IGNORECASE) \
                        and  pubOrder in dado['pubOrder']:                    
                    link_completo = link_base + dado['urlTitle']
                    green_log(f'Conexão efetuada com sucesso! Link encontrado: {link_completo}')

                    return link_completo
                
                elif re.search("Despacho", titulo, re.IGNORECASE) and primeiro_escopo in dado['hierarchyStr'] \
                        and re.search(dado['title'], titulo, re.IGNORECASE) \
                        and texto_match(texto_full=texto_full, texto_partial=dado['content']) \
                        and  pubOrder in dado['pubOrder']:                                            
                    link_completo = link_base + dado['urlTitle']
                    green_log(f'Conexão efetuada com sucesso! Link encontrado: {link_completo}')

                    return link_completo
                
                elif primeiro_escopo in dado['hierarchyStr'] and re.search(str(dado['title']).replace('*', '\*'), titulo, re.IGNORECASE) \
                    and not re.search("Despacho", titulo, re.IGNORECASE) \
                    and (re.search("(Portarias de(.*?[0-9](.*?de [0-9]{4})))", titulo, re.IGNORECASE) or
                            re.search("(Decretos de(.*?[0-9](.*?de [0-9]{4})))", titulo, re.IGNORECASE)) \
                        and texto_match(texto_full=texto_full, texto_partial=dado['content']) \
                        and  pubOrder in dado['pubOrder']:                                            
                    link_completo = link_base + dado['urlTitle']
                    green_log(f'Conexão efetuada com sucesso! Link encontrado: {link_completo}')

                    return link_completo
                
                else:
                    if re.search("Despacho", titulo, re.IGNORECASE) and 'Despacho' in dado['artType'] \
                                and texto_match(texto_full=texto_full, texto_partial=dado['content']) \
                                and  pubOrder in dado['pubOrder']:                                                    
                        link_completo = link_base + dado['urlTitle']
                        green_log(f'Conexão efetuada com sucesso! Link encontrado: {link_completo}')

                        return link_completo                
 
            yellow_log(f'Artigo {titulo} não encontrado nos parâmetros fornecidos.')
            return ""
 
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            qtd_excecoes += 1
            red_log(f'Erro de conexão: {e}. Tentativa {qtd_excecoes} de {max_tentativas}')
            time.sleep(5)  # Aguardar antes de tentar novamente
 
        except Exception as e:
            red_log(f'Erro inesperado: {e}')
            return ""
 
    red_log(f'Falha ao obter o link do artigo {titulo} após {max_tentativas} tentativas.')
    return ""


def extrair_dados(url, headers):

    r_link = requests.get(url=url, headers=headers, timeout=5)
    r_link.raise_for_status()

    html_base = BeautifulSoup(r_link.text, 'html.parser')

    script = html_base.find('script', {'id': 'params'})
    if script is None:
        return None
    
    script_string = script.string
    lista = json.loads(script_string)
    
    return lista.get('jsonArray', [])


def texto_match(texto_full, texto_partial) -> bool:
    texto_full = normalize(texto_full)
    texto_partial = normalize(texto_partial)

    # return True if texto_full_ajustado in texto_partial else False

    if texto_partial.endswith('...'):
        texto_partial_clean = texto_partial[:-3].strip()
        return texto_full.startswith(texto_partial_clean)
    
    return texto_partial in texto_full


def normalize(texto):
    return (texto
            .replace(' ', '')
            .replace('(', '')
            .replace(')', '')
            .replace('"', '')
            .replace('$', '')
            .replace('*', r'\*')
            .replace(u'\xa0', u'')
            )