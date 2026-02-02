import os
import glob
import nbformat
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv
import time

# Load key from scripts/.env
env_path = os.path.abspath(os.path.join("scripts", ".env"))
load_dotenv(env_path)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Target directory
KIDS_DIR = "kids_course"
os.makedirs(KIDS_DIR, exist_ok=True)

class KidsContent(BaseModel):
    title: str = Field(description="Um título divertido para a aula")
    explanation: str = Field(description="Explicação simples estilo ELI5 em Markdown")
    code: str = Field(description="Código Python simples usando LangChain e Gemini 2.0")

def generate_kids_content(name, preview):
    """Generates a child-friendly explanation and a simple code example."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_template(
        """Você é um professor de escola primária muito gentil.
        Explique o conceito técnico abaixo para uma criança de 8 anos, usando metáforas (robôs, brinquedos, escola).
        
        NOME DO ASSUNTO: {name}
        CONTEXTO TÉCNICO: {preview}
        
        Sua resposta deve ter:
        1. Um título divertido.
        2. Uma explicação simples (ELI5) em Português.
        3. Um pequeno código Python (LangChain) QUE FUNCIONE e seja MUITO simples. Use ChatGoogleGenerativeAI(model="gemini-2.0-flash").
        
        Não use muitas bibliotecas extras. Foco no LangChain básico.
        """
    )
    
    chain = prompt | llm.with_structured_output(KidsContent)
    return chain.invoke({"name": name, "preview": preview})

def create_kids_notebook(original_path):
    print(f"[*] Processando: {original_path}")
    basename = os.path.basename(original_path)
    
    try:
        with open(original_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        preview = ""
        for cell in nb.cells[:8]:
            if cell.cell_type in ['markdown', 'code']:
                preview += f"\n{cell.source[:200]}"

        data = generate_kids_content(basename, preview)
        
        new_nb = nbformat.v4.new_notebook()
        header = f"# 🌈 {data.title}\n\n{data.explanation}"
        new_nb.cells.append(nbformat.v4.new_markdown_cell(header))
        
        # Setup cell with ABSOLUTE path to env
        abs_env = os.path.abspath(os.path.join("scripts", ".env"))
        setup_code = f"""# Configuração Inicial
import os
from dotenv import load_dotenv

# Carregando chaves do arquivo central de scripts
load_dotenv(r'{abs_env}')
"""
        new_nb.cells.append(nbformat.v4.new_code_cell(setup_code))
        
        new_nb.cells.append(nbformat.v4.new_code_cell(data.code))
        
        new_path = os.path.join(KIDS_DIR, f"CRIANCAS_{basename}")
        with open(new_path, 'w', encoding='utf-8') as f:
            nbformat.write(new_nb, f)
            
        print(f"  [+] Gerado: CRIANCAS_{basename}")
        return new_path
    except Exception as e:
        print(f"  [!] Erro: {e}")
        return None

def main():
    if not GOOGLE_API_KEY:
        print("GOOGLE_API_KEY not found.")
        return

    notebooks = sorted([f for f in glob.glob("*.ipynb") if "checkpoint" not in f])
    print(f"Regerando versão infantil com paths absolutos...")
    
    for nb in notebooks:
        create_kids_notebook(nb)
        
    print(f"\nConcluído!")

if __name__ == "__main__":
    main()
