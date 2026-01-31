import pandas as pd
import os
import zipfile
import re


PROCESSED_DIR = os.path.join("data", "processed")
RAW_DIR = os.path.join("data", "raw")

INPUT_CSV = os.path.join(PROCESSED_DIR, "consolidado_despesas.csv")
CADOP_CSV = os.path.join(RAW_DIR, "Relatorio_Cadop.csv")

OUTPUT_CSV = os.path.join(PROCESSED_DIR, "despesas_agregadas.csv")
OUTPUT_ZIP = os.path.join(PROCESSED_DIR, "Teste_Joao_Vitor.zip")


def format_cnpj(value: str) -> str:
    """
    Formata o CNPJ no padrão XX.XXX.XXX/0001-XX apenas para visualização.
    Caso o valor não possua 14 dígitos, retorna o valor original.
    """
    digits = re.sub(r"\D", "", str(value))

    if len(digits) != 14:
        return str(value)

    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def run() -> None:
    """
    Executa a etapa de enriquecimento e agregação dos dados,
    realizando o cruzamento com o CADOP, validações e geração do CSV final.
    """
    print(">>> Iniciando Etapa 2: Enriquecimento e Agregação <<<")

    if not os.path.exists(INPUT_CSV):
        print(f"[ERRO] Arquivo de entrada não encontrado: {INPUT_CSV}")
        return

    if not os.path.exists(CADOP_CSV):
        print(f"[ERRO] Arquivo do CADOP não encontrado: {CADOP_CSV}")
        return

    print("[INFO] Lendo arquivos CSV...")

    try:
        expenses_df = pd.read_csv(
            INPUT_CSV, sep=";", decimal=",", encoding="utf-8", dtype=str
        )
    except:
        expenses_df = pd.read_csv(
            INPUT_CSV, sep=";", decimal=",", encoding="latin1", dtype=str
        )

    try:
        cadop_df = pd.read_csv(
            CADOP_CSV, sep=";", encoding="utf-8", dtype=str
        )
    except:
        try:
            cadop_df = pd.read_csv(
                CADOP_CSV, sep=";", encoding="latin1", dtype=str
            )
        except:
            cadop_df = pd.read_csv(
                CADOP_CSV, sep=",", encoding="latin1", dtype=str
            )

    print("[INFO] Preparando chaves...")

    expenses_df["REG_ANS"] = expenses_df["RazaoSocial"].apply(
        lambda x: str(x).split(" ")[-1]
    )

    cadop_df = cadop_df.rename(
        columns={
            "REGISTRO_OPERADORA": "REG_ANS",
            "CNPJ": "CNPJ_NEW",
            "Razao_Social": "RAZAO_SOCIAL_NEW",
            "UF": "UF_NEW",
        }
    )

    if "REG_ANS" not in cadop_df.columns:
        print("[ERRO FATAL] Coluna REG_ANS não encontrada no CADOP.")
        return

    print("[INFO] Realizando o cruzamento...")

    final_df = pd.merge(expenses_df, cadop_df, on="REG_ANS", how="left")

    final_df["CNPJ"] = final_df["CNPJ_NEW"].fillna("")
    final_df["RazaoSocial"] = final_df["RAZAO_SOCIAL_NEW"].fillna(
        final_df["RazaoSocial"]
    )
    final_df["UF"] = final_df["UF_NEW"].fillna("Indefinido")

    print("[INFO] Validando e formatando dados...")

    final_df["CNPJ"] = final_df["CNPJ"].apply(format_cnpj)

    final_df["ValorDespesas"] = final_df["ValorDespesas"].apply(
        lambda x: float(str(x).replace(",", "."))
    )

    final_df["CNPJ_Valido"] = final_df["CNPJ"].apply(
        lambda x: len(re.sub(r"\D", "", str(x))) == 14
    )

    invalid_count = len(final_df[~final_df["CNPJ_Valido"]])
    if invalid_count > 0:
        print(f"[AVISO] {invalid_count} registros com CNPJ incompleto ou ausente.")

    print("[INFO] Calculando estatísticas...")

    aggregated_df = (
        final_df.groupby(["RazaoSocial", "CNPJ", "UF"])["ValorDespesas"]
        .agg(
            Total_Despesas="sum",
            Media_Trimestral="mean",
            Desvio_Padrao="std",
        )
        .reset_index()
    )

    aggregated_df = aggregated_df.sort_values(
        by="Total_Despesas", ascending=False
    )

    aggregated_df["Total_Despesas"] = aggregated_df["Total_Despesas"].round(2)
    aggregated_df["Media_Trimestral"] = aggregated_df["Media_Trimestral"].round(2)
    aggregated_df["Desvio_Padrao"] = (
        aggregated_df["Desvio_Padrao"].fillna(0).round(2)
    )

    aggregated_df = aggregated_df[
        [
            "RazaoSocial",
            "CNPJ",
            "UF",
            "Total_Despesas",
            "Media_Trimestral",
            "Desvio_Padrao",
        ]
    ]

    print(f"[INFO] Salvando CSV final em: {OUTPUT_CSV}")

    aggregated_df.to_csv(
        OUTPUT_CSV,
        index=False,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
    )

    print(f"[INFO] Gerando ZIP: {OUTPUT_ZIP}")

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(OUTPUT_CSV, arcname="despesas_agregadas.csv")

    print(">>> Processo finalizado com sucesso! <<<")


if __name__ == "__main__":
    run()
