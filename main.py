from ingestion.downloader import run as run_ingestion
from processing.data_processor import run as run_processing

if __name__ == "__main__":
    try:
        run_ingestion()
        print("\n" + "="*30 + "\n")
        run_processing()
        
    except KeyboardInterrupt:
        print("\n[!] Processo interrompido pelo usuário.")