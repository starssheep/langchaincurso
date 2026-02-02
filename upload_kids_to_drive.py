import os
import sys
import glob
from dotenv import load_dotenv

# Adiciona o diretório base para importar scripts/upload_to_drive.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.upload_to_drive import authenticate_drive, create_or_get_folder, upload_file, make_file_public

# Load env from scripts/.env
env_path = os.path.join("scripts", ".env")
load_dotenv(env_path)

KIDS_DIR = "kids_course"
KIDS_FOLDER_NAME = "LangChain para Crianças"

def main():
    service = authenticate_drive()
    if not service:
        print("Falha na autenticação.")
        return
        
    print(f"--- Iniciando Upload de Notebooks Infantis ---")
    
    # Cria pasta no drive
    folder_id = create_or_get_folder(service, KIDS_FOLDER_NAME)
    
    # Lista arquivos IPYNB
    files = glob.glob(os.path.join(KIDS_DIR, "*.ipynb"))
    print(f"Encontrados {len(files)} notebooks infantis.")
    
    links = []
    for f in sorted(files):
        try:
            file_id = upload_file(service, f, folder_id)
            make_file_public(service, file_id)
            
            name = os.path.basename(f)
            colab_link = f"https://colab.research.google.com/drive/{file_id}"
            links.append(f"| {name} | [🚀 Abrir]({colab_link}) |")
            print(f"  [+] Pronto: {name}")
        except Exception as e:
            print(f"  [!] Erro em {f}: {e}")

    # Salva arquivo local com links
    links_file = "links_kids.md"
    with open(links_file, "w") as lf:
        lf.write("# 🌈 Links para Notebooks Infantis (ELI5)\n\n")
        lf.write("| Aula | Link Colab |\n")
        lf.write("| :--- | :--- |\n")
        lf.write("\n".join(links))
    
    print(f"\nUpload concluído! Verifique '{links_file}'.")

if __name__ == "__main__":
    main()
