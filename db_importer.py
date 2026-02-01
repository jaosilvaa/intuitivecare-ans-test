import pandas as pd
import os

BASE_DIR = "data"
RAW_DIR = os.path.join(BASE_DIR, "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")

FILE_CADOP = os.path.join(RAW_DIR, "Relatorio_Cadop.csv")
FILE_CONSOLIDADO = os.path.join(PROCESSED_DIR, "consolidado_despesas.csv")
FILE_AGREGADO = os.path.join(PROCESSED_DIR, "despesas_agregadas.csv")
OUTPUT_SQL = "inserts.sql"


def clean_decimal(val):
    if pd.isna(val) or str(val).strip() == '':
        return 'NULL'
    return str(val).replace('.', '').replace(',', '.')


def clean_str(text):
    if pd.isna(text) or str(text).strip() == '':
        return 'NULL'
    return "'" + str(text).replace("'", "''").strip() + "'"


def clean_uf(val):
    """Trata UF: Se for maior que 2 caracteres (ex: 'Indefinido'), retorna NULL"""
    if pd.isna(val) or str(val).strip() == '':
        return 'NULL'
    clean_val = str(val).strip()
    if len(clean_val) > 2:
        return 'NULL'
    return "'" + clean_val + "'"


def run():
    print(">>> Gerando script de carga SQL <<<")
    
    registered_ops = set()

    with open(OUTPUT_SQL, 'w', encoding='utf-8') as f:
        f.write("-- Script de Carga de Dados\n")

        print("[INFO] Processando Operadoras...")
        try:
            cadop = pd.read_csv(FILE_CADOP, sep=';', encoding='utf-8', dtype=str, on_bad_lines='skip')
        except:
            cadop = pd.read_csv(FILE_CADOP, sep=';', encoding='latin1', dtype=str, on_bad_lines='skip')

        for _, row in cadop.iterrows():
            reg = row.get('REGISTRO_OPERADORA', '0')
            registered_ops.add(str(reg))

            cnpj = row.get('CNPJ', '')
            razao = clean_str(row.get('Razao_Social'))
            mod = clean_str(row.get('Modalidade'))
            uf = clean_uf(row.get('UF'))
            
            f.write(f"INSERT INTO operadoras (registro_ans, cnpj, razao_social, modalidade, uf) VALUES ({reg}, '{cnpj}', {razao}, {mod}, {uf}) ON CONFLICT (registro_ans) DO NOTHING;\n")

        print("[INFO] Processando Demonstrações Contábeis...")
        consol = pd.read_csv(FILE_CONSOLIDADO, sep=';', encoding='utf-8', dtype=str)
        
        for _, row in consol.iterrows():
            try:
                reg_ans = str(row['RazaoSocial']).split(' ')[-1]
            except:
                continue

            if reg_ans not in registered_ops:
                dummy_razao = f"'Operadora Histórica {reg_ans}'"
                f.write(f"INSERT INTO operadoras (registro_ans, cnpj, razao_social, modalidade, uf) VALUES ({reg_ans}, NULL, {dummy_razao}, 'Desconhecida', NULL) ON CONFLICT (registro_ans) DO NOTHING;\n")
                registered_ops.add(reg_ans)

            ano = row['Ano']
            trim = row['Trimestre']
            val = clean_decimal(row['ValorDespesas'])
            
            if val != 'NULL':
                f.write(f"INSERT INTO demonstracoes_contabeis (registro_ans, ano, trimestre, valor_despesa) VALUES ({reg_ans}, {ano}, {trim}, {val});\n")

        print("[INFO] Processando Dados Agregados...")
        agreg = pd.read_csv(FILE_AGREGADO, sep=';', encoding='utf-8', dtype=str)
        
        for _, row in agreg.iterrows():
            reg = row['RegistroANS']

            if str(reg) not in registered_ops:
                dummy_razao = f"'Operadora Agregada {reg}'"
                f.write(f"INSERT INTO operadoras (registro_ans, cnpj, razao_social, modalidade, uf) VALUES ({reg}, NULL, {dummy_razao}, 'Desconhecida', NULL) ON CONFLICT (registro_ans) DO NOTHING;\n")
                registered_ops.add(str(reg))

            razao = clean_str(row['RazaoSocial'])
            uf = clean_uf(row['UF'])
            total = clean_decimal(row['Total_Despesas'])
            media = clean_decimal(row['Media_Trimestral'])
            std = clean_decimal(row['Desvio_Padrao'])
            
            f.write(f"INSERT INTO despesas_agregadas (registro_ans, razao_social, uf, total_despesas, media_trimestral, desvio_padrao) VALUES ({reg}, {razao}, {uf}, {total}, {media}, {std}) ON CONFLICT (registro_ans) DO NOTHING;\n")

    print(f"[SUCESSO] Arquivo {OUTPUT_SQL} gerado com sucesso.")
    print(">>> Processo finalizado <<<")

if __name__ == "__main__":
    run()