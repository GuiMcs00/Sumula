import requests
from utils import login, senha, blue_log, red_log

tipo_dou = "DO1 DO2 DO3"
dou_extra = "DO1E DO2E DO3E"


url_login = "https://inlabs.in.gov.br/logar.php"
url_download = "https://inlabs.in.gov.br/index.php?p="

payload = {"email": login, "password": senha}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# Sessão global
session = requests.Session()


def start_session():
    try:
        
        blue_log("----> Iniciando login no inlabs")
        response = session.request("POST", url_login, data=payload, headers=headers)
        response.raise_for_status()
        blue_log("----> Finalizado login no inlabs")
        cookie = session.cookies.get('inlabs_session_cookie')

        if not session.cookies.get('inlabs_session_cookie'):
            red_log("Falha ao obter cookie")
            exit(37)
    
    except requests.exceptions.SSLError as e:
        red_log("SSL Error: %s", e)
    except requests.exceptions.ConnectionError as e:
        red_log(f"Erro de conexão: {str(e)}")


def check_cookie():
    '''
    Verifica se 'inlabs_session_cookie' está presente na sessão.
    '''
    cookie = session.cookies.get('inlabs_session_cookie')

    if not cookie:
        return False
    return True


def get_inlabs_cookies():
    '''
    Retorna o cookie da sessão, se não houver tenta login novamente.
    '''
    if not check_cookie():
        red_log("Cookie não encontrado. Fazendo login novamente...")
        start_session()

    return session.cookies.get('inlabs_session_cookie')


def request_inlabs_file(data, dou_secao):
    cookie = get_inlabs_cookies()
    url_arquivo = f"{url_download}{data}&dl={data}-{dou_secao}.zip"
    cabecalho_arquivo = {'Cookie': f'inlabs_session_cookie={cookie}', 'origem': '736372697074'}
    response_arquivo = requests.get(url_arquivo, headers=cabecalho_arquivo, stream=True)

    return response_arquivo


