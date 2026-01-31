import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

class ANSScraper:
    """
    Serviço responsável por identificar e baixar arquivos trimestrais do Portal de Dados Abertos da ANS.
    """

    # Headers para simular um navegador e evitar bloqueios
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    @classmethod
    def _get_soup(cls, url):
        """
        Retorna um objeto BeautifulSoup para a URL fornecida.
        """
        try:
            response = requests.get(url, headers=cls.HEADERS, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão ao aceder a {url}: {e}")
            raise

    @classmethod
    def identificar_arquivos_trimestrais(cls, base_url):
        """
        Identifica os arquivos trimestrais mais recentes disponíveis no portal da ANS.
        """
        print(f"📂 Scraper: Explorando portal ANS em: {base_url}")
        try:
            soup = cls._get_soup(base_url)

            # 1. Identificar anos (Ex: 2025, 2024...)
            links_raiz = [a['href'] for a in soup.find_all('a', href=True)]
            anos = sorted([l for l in links_raiz if l.strip(
                '/').isdigit() and len(l.strip('/')) == 4], reverse=True)

            arquivos_para_baixar = []

            for ano in anos:
                if len(arquivos_para_baixar) >= 3:
                    break

                url_ano = urljoin(base_url, ano)
                if not url_ano.endswith('/'):
                    url_ano += '/'

                print(f"  📂 Acedendo ano: {ano.strip('/')}")

                try:
                    soup_ano = cls._get_soup(url_ano)
                    links_ano = soup_ano.find_all('a', href=True)

                    # Procura ZIPs que contenham 'T' (ex: 1T2025.zip) diretamente no ano
                    zips = sorted([
                        urljoin(url_ano, l['href'])
                        for l in links_ano if l['href'].lower().endswith('.zip') and 'T' in l['href'].upper()
                    ], reverse=True)

                    for z in zips:
                        if len(arquivos_para_baixar) >= 3:
                            break
                        arquivos_para_baixar.append(z)
                        print(
                            f"    ✅ Arquivo identificado: {z.split('/')[-1]}")

                    # Se não achou 3, tenta subpastas (Resiliência)
                    if len(arquivos_para_baixar) < 3:
                        subpastas = [l['href'] for l in links_ano if l['href'].endswith(
                            '/') and not l['href'].startswith('.')]
                        for sub in sorted(subpastas, reverse=True):
                            if len(arquivos_para_baixar) >= 3:
                                break

                            url_sub = urljoin(url_ano, sub)
                            print(
                                f"    🔍 Explorando subpasta: {sub.strip('/')}")
                            try:
                                soup_sub = cls._get_soup(url_sub)
                                zips_sub = [urljoin(url_sub, z['href']) for z in soup_sub.find_all(
                                    'a', href=True) if z['href'].lower().endswith('.zip')]
                                for zs in zips_sub:
                                    if len(arquivos_para_baixar) >= 3:
                                        break
                                    arquivos_para_baixar.append(zs)
                                    print(
                                        f"      ✅ Arquivo encontrado: {zs.split('/')[-1]}")
                            except Exception as e:
                                print(
                                    f"      ⚠️ Falha ao explorar subpasta {sub}: {e}")

                except Exception as e:
                    print(f"    ⚠️ Falha ao processar o ano {ano}: {e}")
                    continue

            return arquivos_para_baixar[:3]

        except Exception as e:
            print(f"💥 Erro crítico na identificação dos trimestres: {e}")
            return []

    @classmethod
    def baixar_arquivos(cls, urls, data_dir):
        """
        Realiza o download dos arquivos identificados para a pasta data/.
        """
        if not urls:
            print("⚠️ Nenhuma URL encontrada para download.")
            return []

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        baixados = []
        for url in urls:
            nome_arquivo = url.split("/")[-1]
            caminho_local = os.path.join(data_dir, nome_arquivo)

            try:
                print(f"📥 Baixando: {nome_arquivo}...")
                # Stream=True para lidar com ficheiros grandes sem estourar a RAM
                with requests.get(url, stream=True, headers=cls.HEADERS, timeout=30) as r:
                    r.raise_for_status()
                    with open(caminho_local, 'wb') as f:
                        # 1MB chunks
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
                baixados.append(caminho_local)
                print(f"    💾 Guardado em: {data_dir}/{nome_arquivo}")
            except Exception as e:
                print(f"❌ Falha ao baixar {nome_arquivo}: {e}")

        print(
            f"\n✨ Processo finalizado: {len(baixados)} ficheiros na pasta {data_dir}.")
        return baixados
