import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

try:
    import app.main
    print("ALL_SYSTEMS_GO: app.main imported successfully!")
except Exception as e:
    import traceback
    print("FAILED_TO_IMPORT:")
    traceback.print_exc()
