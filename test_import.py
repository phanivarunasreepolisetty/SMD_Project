try:
    from app import app
    print("App imported successfully")
except Exception as e:
    import traceback
    print(f"Failed to import app: {e}")
    traceback.print_exc()
