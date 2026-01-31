import os
import zipfile
import glob
import pandas as pd
import re

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
EXTRACT_DIR = os.path.join(PROCESSED_DIR, "extracted")

FINAL_CSV = os.path.join(PROCESSED_DIR, "consolidado_despesas.csv")
FINAL_ZIP = os.path.join(PROCESSED_DIR, "consolidado_despesas.zip")

COLUMN_MAP = {
    "CD_OPERADORA": "REG_ANS",
    "RegistroANS": "REG_ANS",
    "REG_ANS": "REG_ANS",
    "DATA": "DATA",
    "DT_CMPTC": "DATA",
    "VL_SALDO_FINAL": "VL_SALDO_FINAL",
    "DESCRICAO": "DESCRICAO",
    "DS_CONTA": "DESCRICAO"
}


def extract_zips():
    """Extrai todos os arquivos ZIP para o diretório de trabalho."""
    print("[INFO] Extraindo arquivos ZIP...")
    os.makedirs(EXTRACT_DIR, exist_ok=True)

    for f in glob.glob(os.path.join(EXTRACT_DIR, "*")):
        try:
            os.remove(f)
        except:
            pass

    zip_files = glob.glob(os.path.join(RAW_DIR, "*.zip"))
    if not zip_files:
        print("[AVISO] Nenhum ZIP encontrado em data/raw.")
        return

    for zip_path in zip_files:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(EXTRACT_DIR)
            print(f"[OK] Extraído: {os.path.basename(zip_path)}")
        except zipfile.BadZipFile:
            print(f"[ERRO] ZIP inválido: {zip_path}")


def clean_currency(valor):
    """Normaliza valores monetários para float."""
    if pd.isna(valor):
        return 0.0
    try:
        return float(str(valor).replace('.', '').replace(',', '.'))
    except:
        return 0.0


def get_periodo_from_filename(filename):
    """Obtém ano e trimestre a partir do nome do arquivo."""
    nome = filename.upper()

    ano_match = re.search(r'20\d{2}', nome)
    ano = int(ano_match.group()) if ano_match else 2025

    if "1T" in nome:
        trimestre = 1
    elif "2T" in nome:
        trimestre = 2
    elif "3T" in nome:
        trimestre = 3
    elif "4T" in nome:
        trimestre = 4
    else:
        trimestre = 1

    return ano, trimestre


def process_file(filepath):
    """Filtra e normaliza registros de despesas com eventos/sinistros."""
    filename = os.path.basename(filepath)

    try:
        try:
            df = pd.read_csv(filepath, sep=';', encoding='utf-8', dtype=str)
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, sep=';', encoding='latin1', dtype=str)

        df.rename(columns=COLUMN_MAP, inplace=True)

        required = {'REG_ANS', 'VL_SALDO_FINAL', 'DESCRICAO'}
        if not required.issubset(df.columns):
            return None

        filtro = (
            df['DESCRICAO']
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r'\s+', ' ', regex=True)
            .str.replace(' / ', '/', regex=False)
        ) == 'despesas com eventos/sinistros'

        df = df[filtro].copy()
        if df.empty:
            return None

        df['VL_SALDO_FINAL'] = df['VL_SALDO_FINAL'].apply(clean_currency)
        df = df[df['VL_SALDO_FINAL'] > 0]

        ano, trimestre = get_periodo_from_filename(filename)
        df['Ano'] = ano
        df['Trimestre'] = trimestre

        return df[['REG_ANS', 'Ano', 'Trimestre', 'VL_SALDO_FINAL']]

    except Exception as e:
        print(f"[ERRO] Falha ao processar {filename}: {e}")
        return None


def run():
    print(">>> Iniciando consolidação de despesas <<<")

    extract_zips()

    csv_files = glob.glob(os.path.join(EXTRACT_DIR, "**", "*.csv"), recursive=True)
    if not csv_files:
        csv_files = glob.glob(os.path.join(EXTRACT_DIR, "*.csv"))

    print(f"[INFO] {len(csv_files)} arquivos encontrados.")

    dfs = []
    for f in csv_files:
        df_temp = process_file(f)
        if df_temp is not None:
            dfs.append(df_temp)

    if not dfs:
        print("[AVISO] Nenhum dado válido encontrado.")
        return

    full_df = pd.concat(dfs, ignore_index=True)

    df_consolidado = (
        full_df
        .groupby(['REG_ANS', 'Ano', 'Trimestre'], as_index=False)['VL_SALDO_FINAL']
        .sum()
    )

    df_consolidado['VL_SALDO_FINAL'] = df_consolidado['VL_SALDO_FINAL'].round(2)
    df_consolidado['RazaoSocial'] = 'Operadora ANS ' + df_consolidado['REG_ANS'].astype(str)
    df_consolidado['CNPJ'] = ''

    df_consolidado.rename(columns={'VL_SALDO_FINAL': 'ValorDespesas'}, inplace=True)
    df_consolidado.sort_values(by=['Ano', 'Trimestre', 'RazaoSocial'], inplace=True)

    df_final = df_consolidado[['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'ValorDespesas']]

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    df_final.to_csv(
        FINAL_CSV,
        index=False,
        sep=';',
        decimal=',',
        encoding='latin1'
    )

    with zipfile.ZipFile(FINAL_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(FINAL_CSV, arcname="consolidado_despesas.csv")

    print(f"[SUCESSO] Arquivos gerados em {PROCESSED_DIR}")
    print(">>> Processo finalizado <<<")

if __name__ == "__main__":
    run()