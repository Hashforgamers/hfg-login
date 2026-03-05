# run.py

from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(__import__("os").getenv("PORT", "5055"))
    debug_mode = __import__("os").getenv("DEBUG_MODE", "false").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
