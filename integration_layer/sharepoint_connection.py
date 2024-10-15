import requests
import json
import re

from utils import *


def generate_access_token():
    header_token = {'Content-Type': 'application/x-www-form-urlencoded'}
    playload_token = {
        'grant_type': 'client_credentials',
        'client_id': f'{client_id}@{tenant_id}',
        'client_secret': f'{client_secret}',
        'resource': f'00000003-0000-0ff1-ce00-000000000000/bacen.sharepoint.com@{tenant_id}'
    }
    url_token = "https://accounts.accesscontrol.windows.net/" + tenant_id + "/tokens/OAuth/2"
    request_token = requests.post(url_token, data=playload_token, headers=header_token, verify=False)
    access_token = request_token.json()['access_token']

    return access_token


def generate_sharepoint_headers(access_token):
    headers = {'Authorization': f'Bearer {access_token}',
               'Accept': 'application/json;odata=verbose',
               'Content-Type': 'application/json;odata=verbose'}

    return headers


def salva_zip_biblioteca(data, dou_secao, caminho_arquivo):
    access_token = generate_access_token()
    headers = generate_sharepoint_headers(access_token)
    
    #Verifica se a pasta existe:
    url_pasta = f"https://bacen.sharepoint.com/sites/sumula/_api/web/GetFolderByServerRelativeUrl('Arquivos do inlabs/{data}')"
    request_get = requests.get(url_pasta, headers=headers)
    if request_get.status_code == 404:
        #Cria a pasta caso não exista:
        dados = '''{ "__metadata": {"type": "SP.Folder"},
                    "ServerRelativeUrl": "%s"
                }''' % (data)

        url_nova_pasta = "https://bacen.sharepoint.com/sites/sumula/_api/web/GetFolderByServerRelativeUrl('Arquivos do inlabs')/folders"
        request_post = requests.post(url_nova_pasta, headers=headers, data=dados.encode('utf-8', 'ignore'))

    nome_arquivo = f"{data}-{dou_secao}.zip"
    print(f"Salvando arquivo {nome_arquivo} na pasta em 'Arquivos do inlabs'...")
    #Salva o arquivo zip dentro da pasta:
    if request_get.status_code == 200 or request_post.status_code == 201:
        arquivo = open(caminho_arquivo, "rb")
        url_salva_zip = f"https://bacen.sharepoint.com/sites/sumula/_api/web/GetFolderByServerRelativeUrl('Arquivos do inlabs/{data}')/Files/add(url='{nome_arquivo}',overwrite=false)"
        response_post = requests.post(url_salva_zip, headers=headers, data=arquivo)

        if response_post.status_code == 200:
            green_log(f"Arquivo salvo com sucesso na lista 'Arquivos do inlabs': {nome_arquivo}")
        else:
            print(f"Arquivo {nome_arquivo} já existe na lista 'Arquivos do inlabs': status code: {response_post.status_code}")
            
            # URL para baixar o arquivo
            url_download_zip = f"https://bacen.sharepoint.com/sites/sumula/_layouts/15/download.aspx?SourceUrl=/sites/sumula/Arquivos%20do%20inlabs/{data}/{nome_arquivo}"
            
            # Fazer a solicitação GET para baixar o arquivo
            response_get = requests.get(url_download_zip, headers=headers)
            
            if response_get.status_code == 200:
                with open("xmls/" + nome_arquivo, "wb") as arquivo_baixado:
                    arquivo_baixado.write(response_get.content)
                green_log(f"Arquivo baixado da lista 'Arquivos do inlabs': {nome_arquivo}")
            else:
                red_log(f"Falha ao baixar o arquivo. Status code: {response_get.status_code}")


def send_to_sharepoint(dados_formatados, lista_sharepoint):
    access_token = generate_access_token()
    headers = generate_sharepoint_headers(access_token)
    artigo_existente = check_article_existence(dados_formatados['Title'], dados_formatados['Texto'], lista_sharepoint, headers)

    if artigo_existente:
        update_article(artigo_existente['ID'], dados_formatados, lista_sharepoint, headers)

    else:
        api_url = f"https://bacen.sharepoint.com/sites/sumula/_api/lists/getbytitle('{lista_sharepoint}')/items"
        

        response = requests.post(api_url, headers=headers, data=json.dumps(dados_formatados), verify=False)
        if response.status_code == 201:
            green_log(f"Artigo '{dados_formatados['Title']}' enviado com sucesso!")
        else:
            red_log(f"Falha ao enviar artigo '{dados_formatados['Title']}': {response.text}")


def check_article_existence(titulo, texto, lista_sharepoint, headers):
    titulo_encode = requests.utils.quote(titulo)
    api_url = f"https://bacen.sharepoint.com/sites/sumula/_api/lists/getbytitle('{lista_sharepoint}')/items?$filter=Title eq '{titulo_encode}'"

    response = requests.get(api_url, headers=headers, verify=False)

    if response.status_code != 200:
        return None

    resultados = response.json().get('d', {}).get('results', [])

    if not resultados:
        return None
    
    regex_titulos_especiais = re.compile(r"Despacho|Retificação|Retificações", re.IGNORECASE)

    for item_lista in resultados:
        titulo_lista = item_lista.get('Title', '')

        if regex_titulos_especiais.search(titulo_lista):
            if texto == str(item_lista.get('Texto', '')):
                return item_lista
        else:
            return item_lista
        
    return None


def update_article(item_id, dados_formatados, lista_sharepoint, headers):
    api_url = f"https://bacen.sharepoint.com/sites/sumula/_api/lists/getbytitle('{lista_sharepoint}')/items({item_id})"
    headers.update({'IF-MATCH': '*', 'X-HTTP-METHOD': 'MERGE'})

    response = requests.post(api_url, headers=headers,  data=json.dumps(dados_formatados), verify=False)
    if response.status_code == 204:
        green_log(f"Artigo '{dados_formatados['Title']}' atualizado com sucesso!")
    else:
        red_log(f"Falha ao atualizar o artigo '{dados_formatados['Title']}': {response.text}")


def link_arquivo_biblioteca(nome_arquivo, header=generate_sharepoint_headers(generate_access_token())):
    # URL para a biblioteca de documentos onde o arquivo será salvo
    url_library = f"https://bacen.sharepoint.com/sites/sumula/_api/web/GetFolderByServerRelativeUrl('Arquivos do inlabs')/Files/add(url='{nome_arquivo}',overwrite=true)"
 
    try:
        # Abrir o arquivo e fazer o upload
        with open(f"xmls/{nome_arquivo}", "rb") as arquivo:
            response = requests.post(url_library, headers=header, data=arquivo)
 
        # Verificar se o arquivo foi inserido com sucesso
        if response.status_code == 201:
            blue_log(f"Arquivo {nome_arquivo} inserido com sucesso na biblioteca de documentos!")

        # Requisição para obter o id de cada arquivo na biblioteca:
        url_titulo = f"https://bacen.sharepoint.com/sites/sumula/_api/web/Lists/getByTitle('Arquivos do inlabs')/items?$filter=Title eq '{nome_arquivo}'"
        response1 = requests.get(url_titulo, headers=header)
        resposta = response1.json()['d']['results']
        id_arquivo = resposta[0]['ID']

        # Requisição para obter o link de cada arquivo na biblioteca:
        url_link = f"https://bacen.sharepoint.com/sites/sumula/_api/web/Lists/getByTitle('Arquivos do inlabs')/items?$select=EncodedAbsUrl&$filter=Id eq {id_arquivo}"
        response2 = requests.get(url_link, headers=header)
        resposta_link = response2.json()['d']['results']
        link = resposta_link[0]['EncodedAbsUrl']
        return link

 
    except FileNotFoundError:
        red_log(f"Arquivo '{nome_arquivo}' não encontrado no diretório 'xmls/'.")
    except Exception as e:
        red_log(f"Ocorreu um erro: {str(e)}")
 
    return None


def despacho_mensagem(lista_sharepoint, data_payload, header=generate_sharepoint_headers(generate_access_token())):
    for paragrafo_ementa in data_payload['Ementa']:
        #Primeiro pega o id se já existir na lista:
        data_inicial = data_payload['DataTriagem'] + "T00:00:00Z"
        data_final = data_payload['DataTriagem'] + "T23:59:59Z"
        try:
            r1 = requests.get(f"https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('{lista_sharepoint}')/items?$filter=(Title eq '{data_payload['Title']}')and(DataPublica_x00e7__x00e3_o ge '{data_inicial}')and(DataPublica_x00e7__x00e3_o le '{data_final}')", headers=header)
            dado_item = r1.json()['d']['results']
            tamanho = len(dado_item)
        except requests.exceptions.RequestException as e:
            print("Ocorreu um erro ao verificar se o artigo " + data_payload['Title'] + " já existe na lista " + lista_sharepoint + ".")
            print(e)
        id = 0
        if len(dado_item) > 0:
            for v in range(0, tamanho):
                lista_item = dado_item[v]
                if re.search("Despacho", lista_item['Title'], re.IGNORECASE) and data_payload['Texto'] == str(lista_item['Texto']).replace('"', '\\"') and paragrafo_ementa == str(lista_item['Ementa']).replace('"', '\\"'):
                    id = lista_item['ID']

        if id == 0:  # não encontrou nenhum item na data de hoje com o título do arquivo encontrado
            #Requisição para inserir itens na lista do Sharepoint:
            request_post = requests.post(f"https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('{lista_sharepoint}')/items",
                        headers=header, data=data_payload.encode('utf-8', 'ignore'))
            blue_log(request_post.status_code)
            green_log(f"Artigo inserido na lista do sharepoint {lista_sharepoint}!")
            if request_post.status_code != 201:
                red_log(f"Erro ao subir o artigo para lista do sharepoint {lista_sharepoint}! ({request_post.text})")
                blue_log(request_post.text)
        else:
            update_article(id, data_payload, lista_sharepoint, header)
