import nbformat
import os

def fix_chatbot_notebook(directory):
    nb_path = os.path.join(directory, "10_Chatbot_RAG_Completo.ipynb")
    
    try:
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        modified = False
        for cell in nb.cells:
            if cell.cell_type == 'code':
                if 'from google.colab import files' in cell.source:
                    print(f"Fixing {os.path.basename(nb_path)}")
                    cell.source = """try:
    from google.colab import files

    print("Faça upload do seu PDF:")
    uploaded = files.upload()
    filename = next(iter(uploaded))
    print(f"Arquivo {filename} carregado.")
except ImportError:
    print("Google Colab not detected. Using local file.")
    # Fallback for local execution
    filename = input("Digite o caminho do arquivo PDF: ")"""
                    modified = True
                    
        if modified:
            with open(nb_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
            print("Successfully patched notebook.")
        else:
            print("No matching cell found to patch.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_chatbot_notebook('.')
