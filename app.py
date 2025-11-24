import os
import uuid
from flask import Flask, request, jsonify, render_template
from azure.cosmos import CosmosClient

app = Flask(__name__)

# Configuración (Las tomará de Azure cuando lo subamos)
COSMOS_URI = os.getenv("COSMOS_URI")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = "notasdb"
CONTAINER_NAME = "notas"

# Conexión segura (Manejo de errores si faltan claves)
try:
    if COSMOS_URI and COSMOS_KEY:
        client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
        database = client.get_database_client(DATABASE_NAME)
        container = database.get_container_client(CONTAINER_NAME)
    else:
        container = None
except Exception as e:
    container = None
    print(f"Error conectando a DB: {e}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/notas", methods=["GET"])
def get_notas():
    if not container: return jsonify([])
    query = "SELECT * FROM c"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    return jsonify(items)

@app.route("/api/notas", methods=["POST"])
def create_nota():
    if not container: return jsonify({"error": "No DB connection"}), 500
    data = request.json
    item = {
        "id": str(uuid.uuid4()),
        "titulo": data.get("titulo", "Sin título"),
        "contenido": data.get("contenido", "")
    }
    container.create_item(item)
    return jsonify(item)

@app.route("/api/notas/<id>", methods=["DELETE"])
def delete_nota(id):
    if not container: return jsonify({"error": "No DB connection"}), 500
    container.delete_item(item=id, partition_key=id)
    return jsonify({"status": "deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)