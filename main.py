from ingestion.downloader import run

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n[!] Processo interrompido pelo usuário.")