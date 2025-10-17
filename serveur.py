
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import hashlib
import os
import random

app = Flask(__name__)
CORS(app)

# ----------- Routes -----------
global questions_liste

# recupere le questionnaire 
@app.route('/questionnaire', methods=['POST'])
def questionnaire():
    data = request.get_json()
    if data :
        questions_liste = data.get("questions")
        print("✅ donnes " + str(questions_liste), flush=True)
    return jsonify({"status": "ok"})

# genere la clee a 4 chiffres
def genererClee() :
    nombres = ""
    for _ in range(4) :
        a = random.randint(0, 9)
        nombres = nombres + str(a)
        
    return nombres
    
#envoie la clee a 4 chiffres
@app.route('/clee', methods=['GET'])
def clee():
    nbr = genererClee()
    print("✅ clee" + str(nbr), flush=True)
    return jsonify({"reponse": nbr})
     
#envoie les questions 
@app.route('/recupQuestions', methods=['GET'])
def recupQuestions():
    if questions_liste :
        return jsonify({"questions": questions_liste})
    else :
        return jsonify({"questions": "aucune donnes"})
# ----------- Démarrage serveur -----------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
