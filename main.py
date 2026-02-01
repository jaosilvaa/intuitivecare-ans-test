from ingestion.downloader import run as run_ingestion
from processing.data_processor import run as run_processing
from processing.data_enrichment import run as run_enrichment
from db_importer import run as run_sql_generation

if __name__ == "__main__":
    try:
        run_ingestion()
        print("\n" + "="*30 + "\n")
       
        run_processing()
        print("\n" + "="*30 + "\n")
        
        run_enrichment()
        print("\n" + "="*30 + "\n")

        run_sql_generation()
        
        print("\n--- PROCESSO FINALIZADO COM SUCESSO ---")
        
    except KeyboardInterrupt:
        print("\n[!] Processo interrompido pelo usuário.")
    except Exception as e:
        print(f"\n[ERRO FATAL] Ocorreu um erro inesperado: {e}")