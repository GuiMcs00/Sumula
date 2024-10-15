import os
import sys
import traceback
import urllib3
from datetime import datetime
import socket
import re

from integration_layer import *
from extraction_layer import extract_files, apagar_xmls
from utils import green_log, yellow_log, red_log, properties
from search_layer import search_article
from formatting_layer import montar_ementa, obter_link_diario


lista_sharepoint = properties.get('default', 'lista_sharepoint')

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#pega valor do proxy, se estiver configurado na máquina
env_vars = {key.upper(): value for key, value in os.environ.items()}
http_proxy_key = 'HTTP_PROXY'
https_proxy_key = 'HTTPS_PROXY'
http_proxy_value = os.environ[http_proxy_key] if http_proxy_key in env_vars else ''
https_proxy_value = os.environ[https_proxy_key] if https_proxy_key in env_vars else ''

def atualizaVariavelAmbienteProxy(valor_http, valor_https):
    # se estiver rodando no servidor sbcdf420, não precisa alterar essa variável.
    if not ('sbcdf420' in socket.gethostname().lower()):
        if http_proxy_key in env_vars: os.environ[http_proxy_key] = valor_http 
        if https_proxy_key in env_vars: os.environ[https_proxy_key] = valor_https 

    print(f"---{http_proxy_key}: {os.environ[http_proxy_key] if http_proxy_key in env_vars else ''}----")
    print(f"---{https_proxy_key}: {os.environ[https_proxy_key] if https_proxy_key in env_vars else ''}----")


def format_data(artigos_validados, lista_sharepoint):

    for artigo in artigos_validados:

        data_triagem = datetime.now().isoformat()

        atualizaVariavelAmbienteProxy('', '')

        linkArtigo = obter_link_diario(titulo= artigo.get('Título'),
                                       escopo= artigo.get('Escopo'),
                                       texto= artigo.get('Texto'), 
                                       data_pub= artigo.get('DataPub'),
                                       secao= artigo.get('Seção'),
                                       pubOrder= artigo.get('PubOrder'))

        # linkArtigo = dev_obter_link_diario(titulo= artigo.get('Título'),
        #                                escopo= artigo.get('Escopo'),
        #                                texto= artigo.get('Texto'), 
        #                                data_pub= artigo.get('DataPub'),
        #                                secao= artigo.get('Seção'),
        #                                pubOrder= artigo.get('PubOrder'))
        
        atualizaVariavelAmbienteProxy(http_proxy_value, https_proxy_value)

        link_arquivo = link_arquivo_biblioteca(artigo.get('LinkArquivo', ''))
        payload = {
            "__metadata": {
                "type": f"SP.Data.{lista_sharepoint}ListItem"
            },
            "Title": artigo.get('Título', ''),
            "Escopo": artigo.get('Escopo', ''),
            "Ementa": artigo.get('Ementa', ''),
            "Texto": artigo.get('Texto', ''),
            "Assinatura": artigo.get('Assinatura', ''),
            "Se_x00e7__x00e3_o": artigo.get('Seção', ''),
            "Edi_x00e7__x00e3_o": artigo.get('Edição', ''),
            "DataTriagem": data_triagem,
            "DataPublica_x00e7__x00e3_o": datetime.strptime(artigo.get('DataPub', ''), "%d-%m-%Y").date().isoformat(),
            "Ok": True,
            "IsUpdate": False,
            "NomeArquivoLink": {
                    "Description": artigo.get('LinkArquivo', ''),
                    "Url": link_arquivo if link_arquivo else ''},
            "Inclu_x00ed_doNaS_x00fa_mula": True,
            "TermosEncontrados": "\n".join(artigo.get('Termos Encontrados', [])),
            "LinkArtigo": {
                    "Description": artigo.get('Título', ''),
                    "Url": linkArtigo if linkArtigo else ''},
            "LinkArtigoAlternativo": {
                    "Description": artigo.get('pdfPage', ''),
                    "Url": artigo.get('pdfPage', '')},
        }

        if payload.get('Ementa', '') == 'None':
            blue_log(f"Iniciando montagem de ementa para {payload['Title']}")
            payload['Ementa'] = montar_ementa(titulo= artigo.get('Título', ''), 
                                              subtitulo= artigo.get('SubTítulo', ''), 
                                              escopo= artigo.get('Escopo'),
                                              texto_conteudo= artigo.get('Texto', ''),
                                              puNameSecao=artigo.get('Seção', ''), 
                                              artType= artigo.get('artType', ''),
                                              idOficio= artigo.get('idOficio', ''),
                                              artigos_encontrados= artigos_validados)
            green_log("Montagem de ementa finalizada.")

        if re.search('Despacho', artigo.get('Título', ''), re.IGNORECASE) \
            and re.search(r"(Presidência da República)|(Presidente da República)", artigo.get('Escopo', ''), re.IGNORECASE) \
                and re.search("Banco Central do Brasil", artigo.get('Texto', ''), re.IGNORECASE) \
                    and re.search("Mensagem", artigo.get('artType', ''), re.IGNORECASE):
            blue_log(f"Iniciando Despacho Mensagem para {payload['Title']}")
            despacho_mensagem(lista_sharepoint, payload)

        send_to_sharepoint(payload, lista_sharepoint)



artigos_validados = []
if __name__ == "__main__":
    try:
        green_log("----")
        green_log("----> Iniciada nova execução")
        green_log("----")

        start_session()

        arquivos_xml = extract_files()

        if arquivos_xml:
            artigos_validados = search_article(arquivos_xml)
        else:
            yellow_log("Nenhum arquivo XML foi encontrado para processar.")

        green_log(f"Busca Encerrada!\nEnviando artigos para a lista: {lista_sharepoint}...")

        format_data(artigos_validados, lista_sharepoint)
        
        apagar_xmls()

        green_log("----> Finalizada execução com sucesso!")

    except:
        red_log(traceback.format_exc())