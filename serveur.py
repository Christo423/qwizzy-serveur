
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import hashlib
import os

app = Flask(__name__)
CORS(app)

# ----------- Routes -----------

rp = ""

@app.route('/reponse', methods=['POST'])
def reponse():
    global rp
    data = request.get_json()
    if data is None :
        return jsonify({"error": "aucune donnée reçue"}), 400
    rp = data.get("reponse")
    return jsonify({"message": "oui"}), 201

@app.route('/rec', methods=['GET'])
def rec():
    return jsonify({"reponse": rp})
     
# ----------- Démarrage serveur -----------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
