# # ui_flask.py

import os
import threading
import time
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from werkzeug.utils import secure_filename

# Import ingestion and RAG logic
from ingest import ingest_all
from rag import answer_question

# ===========================
# APP CONFIGURATION
# ===========================
app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "docs"
Session(app)


# ===========================
# ROUTES
# ===========================

@app.route("/")
def index():
    """Render main chat UI."""
    if "memory" not in session:
        session["memory"] = {"history": [], "current_patient": None}
    return render_template("index_main.html")


# ===== Check Ollama Availability =====
@app.route("/check_ollama")
def check_ollama():
    try:
        import subprocess
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "llama3.1" in result.stdout:
            return jsonify({
                "status": "ok",
                "message": "✅ Ollama is running and 'llama3.1' model is available."
            })
        else:
            return jsonify({
                "status": "error",
                "message": "⚠️ Ollama is running, but 'llama3.1' model not found."
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"❌ Ollama not available: {e}"
        })


# ===== Ingest All Documents =====
@app.route("/ingest", methods=["POST"])
def run_ingestion():
    """Trigger full ingestion of all PDFs in docs/."""
    try:
        ingest_all()
        return jsonify({"message": "✅ Ingestion completed successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== Upload and Ingest New Patient Record =====
@app.route("/upload", methods=["POST"])
def upload_file():
    """Upload a new patient record and re-run ingestion."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded."}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename."}), 400

        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(save_path)

        # Run ingestion after upload
        ingest_all()
        return jsonify({"message": f"✅ File '{filename}' uploaded and ingested successfully."})

    except Exception as e:
        return jsonify({"error": f"Upload failed: {e}"}), 500


# ===== Chat Endpoint =====
@app.route("/ask", methods=["POST"])
def ask_question():
    """Handles user questions and returns answers."""
    try:
        question = request.form.get("question", "").strip()
        if not question:
            return jsonify({"error": "Question cannot be empty."}), 400

        # Load conversation memory
        memory = session.get("memory", {"history": [], "current_patient": None})

        # Generate answer
        answer, docs, metas, memory = answer_question(question, memory)

        # Update memory
        session["memory"] = memory
        current_patient = memory.get("current_patient")

        # Extract document titles / sources for explainability
        sources = []
        for meta in metas:
            if "source" in meta:
                sources.append(meta["source"])
            else:
                sources.append(str(meta))

        return jsonify({
            "answer": answer,
            "sources": sources,
            "current_patient": current_patient
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== Clear Memory =====
@app.route("/clear_memory", methods=["POST"])
def clear_memory():
    """Clears conversation memory."""
    session["memory"] = {"history": [], "current_patient": None}
    return jsonify({"message": "🧹 Conversation memory cleared."})


# ===== Exit Application =====
@app.route("/exit", methods=["POST"])
def exit_app():
    """Gracefully shuts down the Flask app and closes the browser tab."""
    try:
        shutdown_func = request.environ.get("werkzeug.server.shutdown")
        if shutdown_func:
            threading.Thread(target=lambda: (time.sleep(0.5), shutdown_func()), daemon=True).start()
            return jsonify({"message": "🛑 Server shutting down (graceful)..."}), 200
        else:
            # Fallback: force exit
            threading.Thread(target=lambda: (time.sleep(0.5), os._exit(0)), daemon=True).start()
            return jsonify({"message": "🛑 Server shutting down (forceful fallback)."}), 200
    except Exception as e:
        return jsonify({"error": f"Shutdown failed: {e}"}), 500


# ===========================
# MAIN ENTRY POINT
# ===========================
if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)
    print("🚀 Starting Medical RAG Dashboard at http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
