import os
import glob
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

KIDS_DIR = "kids_course"

def run_notebook(path):
    print(f"[*] Executando: {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': KIDS_DIR}})
        
        with open(path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        print("  [+] Executado.")
        return True
    except Exception as e:
        print(f"  [!] Falha na execução: {e}")
        return False

def main():
    notebooks = sorted(glob.glob(os.path.join(KIDS_DIR, "*.ipynb")))
    print(f"Iniciando execução de {len(notebooks)} notebooks...")
    
    for nb in notebooks:
        run_notebook(nb)
        
    print("\nExecução concluída!")

if __name__ == "__main__":
    main()
