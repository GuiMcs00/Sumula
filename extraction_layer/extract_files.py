import os
import shutil
import zipfile
import time
from requests.exceptions import ChunkedEncodingError, ConnectionError


from integration_layer import *
from calendar_layer import data_completa, data_anterior_util, data_anterior_feriado
from utils import green_log, yellow_log, red_log




def extract_files(data=data_completa):
    data_anterior = data_anterior_util()
    possivel_feriado = data_anterior_feriado()

    arquivos_xml = manage_xml_extraction(data, tipo_dou)
    arquivos_xml += manage_xml_extraction(data_anterior, dou_extra)

    if possivel_feriado != data_anterior:
        arquivos_xml += manage_xml_extraction(possivel_feriado, dou_extra)

    green_log(f"Total de arquivos XML extraídos: {len(arquivos_xml)}")

    return arquivos_xml


def manage_xml_extraction(data, tipo_dou):
    arquivos_xml = []
    for dou_secao in tipo_dou.split(' '):
        caminho_arquivo = download_zip_file(data, dou_secao)
        if caminho_arquivo:
            arquivos_xml += extract_zip_file(caminho_arquivo)
    return arquivos_xml


def download_zip_file(data, dou_secao, tentativas=5, intervalo=5):
    tentativa_atual = 0
    caminho_arquivo = f"xmls/{data}-{dou_secao}.zip"

    while tentativa_atual < tentativas:
        try:
            response_arquivo = request_inlabs_file(data, dou_secao)
            if response_arquivo.status_code == 200:
                if not os.path.isdir('./xmls'):
                    os.mkdir("./xmls")
                with open(caminho_arquivo, "wb") as arquivo:
                    arquivo.write(response_arquivo.content)
                    green_log(f"Arquivo {caminho_arquivo} salvo na máquina local.")
                    salva_zip_biblioteca(data, dou_secao, caminho_arquivo)
                return caminho_arquivo
            elif response_arquivo.status_code == 404:
                yellow_log(f"Arquivo não encontrado: {data}-{dou_secao}.zip")
                # baixar de Arquivos Inlabs sharepoint
                break
            else:
                red_log(f"Erro ao baixar o arquivo {data}-{dou_secao}.zip: {response_arquivo.status_code}")
                break
        
        except (ChunkedEncodingError, ConnectionError) as e:
            tentativa_atual += 1
            red_log(f"Erro na conexão na tentativa {tentativa_atual}/{tentativas}: {e}. Tentando novamente em {intervalo} segundos...")
            time.sleep(intervalo)

        except Exception as e:
            red_log(f"Erro inesperado: {e}") 

    red_log(f"Falha ao baixar o arquivo{data}-{dou_secao}.zip após {tentativa_atual} tentativas.")
    return None
    


def extract_zip_file(caminho_arquivo):
    arquivos_xml = []
    if os.path.isfile(caminho_arquivo):
        try:
            if zipfile.is_zipfile(caminho_arquivo):
                with zipfile.ZipFile(caminho_arquivo, 'r') as zip_ref:
                    pasta_extracao = os.path.dirname(caminho_arquivo)
                    for arq in zip_ref.namelist():
                        try:
                            zip_ref.extract(arq, pasta_extracao)
                            extensao = os.path.splitext(arq)
                            if extensao[1] == '.xml':
                                arquivos_xml.append(os.path.join(pasta_extracao, arq))
                        except Exception as e:
                            red_log(f"Erro ao extrair '{arq}': {e} Continuando com os próximos arquivos.")
            else:
                red_log(f"O arquivo '{caminho_arquivo}' não é um arquivo zip válido")

        except zipfile.BadZipFile:
            red_log(f"Erro: o arquivo '{caminho_arquivo}' está corrompido ou não é um arquivo zip válido")
        except Exception as e:
            red_log(f"Erro inesperado: {e}")
    else:
        red_log(f"O arquivo '{caminho_arquivo}' não existe ou não é um arquivo válido.")
        
    return arquivos_xml


def apagar_xmls():
    if os.path.isdir('./xmls'):
        shutil.rmtree('./xmls')