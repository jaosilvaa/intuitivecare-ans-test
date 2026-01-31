from ingestion.downloader import run as run_ingestion
from processing.data_processor import run as run_processing
from processing.data_enrichment import run as run_enrichment

if __name__ == "__main__":
    try:
        run_ingestion()
        print("\n" + "="*30 + "\n")
       
        run_processing()
        print("\n" + "="*30 + "\n")
        
        run_enrichment()
        
        print("\n--- PROCESSO FINALIZADO ---")
        
    except KeyboardInterrupt:
        print("\n[!] Processo interrompido pelo usuário.")