# # main.py
import os
import webbrowser
import threading
from ui_flask_main import app

def open_browser(port):
    """Open the web app in the default browser after Flask starts."""
    webbrowser.open_new(f"http://127.0.0.1:{port}")

if __name__ == "__main__":
    # Ensure docs directory exists
    os.makedirs("docs", exist_ok=True)
    port = int(os.environ.get("PORT", "5000"))

    print("🚀 Launching Medical RAG Dashboard...")
    print("📂 Docs folder:", os.path.abspath("docs"))
    print(f"🌐 Opening web browser at http://127.0.0.1:{port}")

    # Run Flask in a thread, and open browser automatically
    threading.Timer(1.0, open_browser, args=(port,)).start()
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
