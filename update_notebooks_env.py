import nbformat
import glob
import os

def update_notebooks_env(directory):
    notebooks = glob.glob(os.path.join(directory, "*.ipynb"))
    for nb_path in notebooks:
        modified = False
        try:
            with open(nb_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
        except Exception as e:
            print(f"Skipping {os.path.basename(nb_path)}: {e}")
            continue
        
        # Check if dotenv is already used
        has_dotenv = False
        for cell in nb.cells:
            if cell.cell_type == 'code' and 'load_dotenv' in cell.source:
                has_dotenv = True
                break
        
        if not has_dotenv:
            # Inject at the top, or after imports
            # Strategy: Find the first code cell. Inject import and load.
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    # Prepend to the first code cell
                    print(f"Injecting dotenv into {os.path.basename(nb_path)}")
                    cell.source = "import os\nfrom dotenv import load_dotenv\nload_dotenv()\n\n" + cell.source
                    modified = True
                    break # Only inject once
        
        if modified:
            with open(nb_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
            print(f"Updated {os.path.basename(nb_path)}")

if __name__ == "__main__":
    update_notebooks_env('.')
