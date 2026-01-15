import nbformat
import glob
import os

def fix_notebooks(directory):
    notebooks = glob.glob(os.path.join(directory, "*.ipynb"))
    for nb_path in notebooks:
        modified = False
        try:
            with open(nb_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
        except Exception as e:
            print(f"Skipping {os.path.basename(nb_path)} due to read error: {e}")
            continue
        
        for cell in nb.cells:
            if cell.cell_type == 'code':
                if 'from google.colab import userdata' in cell.source:
                    # Check if it's not already fixed
                    if 'try:' not in cell.source or 'except ImportError:' not in cell.source:
                        print(f"Fixing {os.path.basename(nb_path)}")
                        cell.source = cell.source.replace(
                            "from google.colab import userdata", 
                            "try:\n    from google.colab import userdata\nexcept ImportError:\n    userdata = None"
                        )
                        modified = True
                    
        if modified:
            with open(nb_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
            print(f"Saved {os.path.basename(nb_path)}")

if __name__ == "__main__":
    fix_notebooks('.')
