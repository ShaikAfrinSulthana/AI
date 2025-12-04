# run_frontend.py
import sys
from pathlib import Path

# Absolute path to the project root (folder that contains ivf_frontend and ivf_backend)
PROJECT_ROOT = Path(__file__).resolve().parent

# Add to Python path
sys.path.insert(0, str(PROJECT_ROOT))

print(">>> USING PROJECT ROOT:", PROJECT_ROOT)

# Import Streamlit app
from ivf_frontend.app import main

if __name__ == "__main__":
    main()
