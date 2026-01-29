import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
OUTPUT_DIR = os.path.join("data", "raw")

def get_soup(url):
    """
    Faz a requisição HTTP e retorna o HTML parseado.
    Retorna None em caso de erro de acesso.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"[ERRO] Falha ao acessar {url}: {e}")
        return None

def get_available_years():
    """
    Retorna os anos disponíveis no diretório da ANS,
    ordenados do mais recente para o mais antigo.
    """
    soup = get_soup(BASE_URL)
    if not soup:
        return []
    
    years = []
    for link in soup.find_all('a'):
        href = link.get('href', '').strip('/')
        if href.isdigit() and len(href) == 4:
            years.append(href)
    
    return sorted(years, reverse=True)

def get_zips_from_year(year):
    """
    Retorna todos os arquivos .zip disponíveis para um ano específico.
    """
    year_url = urljoin(BASE_URL, f"{year}/")
    soup = get_soup(year_url)
    if not soup:
        return []

    zip_links = []
    for link in soup.find_all('a'):
        href = link.get('href', '')
        if href.lower().endswith('.zip'):
            full_url = urljoin(year_url, href)
            zip_links.append(full_url)
    
    return sorted(zip_links, reverse=True)

def download_file(url):
    """
    Baixa um arquivo ZIP em partes para evitar uso excessivo de memória.
    """
    filename = url.split('/')[-1]
    filepath = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(filepath):
        print(f"[INFO] Arquivo já existe, pulando: {filename}")
        return True

    print(f"[BAIXANDO] {filename}...")
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"[SUCESSO] Download concluído: {filename}")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao baixar {filename}: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False

def run():
    """
    Executa o processo de ingestão,
    baixando os 3 arquivos mais recentes disponíveis.
    """

    print(">>> Iniciando ingestão de dados ANS")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    years = get_available_years()
    downloads_count = 0
    target = 3

    for year in years:
        if downloads_count >= target:
            break
        
        print(f"[INFO] Verificando arquivos de {year}...")
        zips = get_zips_from_year(year)

        for zip_url in zips:
            if downloads_count >= target:
                break
            if download_file(zip_url):
                downloads_count += 1

    if downloads_count == 0:
        print("[AVISO] Nenhum arquivo foi baixado. Verifique a conexão ou o site.")
    else:
        print(f">>> Processo finalizado. {downloads_count} arquivos salvos em {OUTPUT_DIR}")