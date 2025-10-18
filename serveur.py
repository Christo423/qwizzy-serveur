
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import hashlib
import os
import random

app = Flask(__name__)
CORS(app)

# ----------- Routes -----------
questions_liste = []
joueurs_liste = ["christo", "daniel", "blessing"]
nbr = 0
# recupere le questionnaire 
@app.route('/questionnaire', methods=['POST'])
def questionnaire():
    global questions_liste
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
    return jsonify({"questions": questions_liste})

# ajouter un joueur
@app.route('/ajouter_joueur', methods=['POST'])
def ajouter_joueur():
    global joueurs_liste
    data = request.get_json()
    mdp = data.get("clee")
    if str(mdp) == str(nbr) :
        pseudo = data.get("pseudo")
        joueurs_liste.append(str(pseudo))
        print("✅ joueur " + str(pseudo), flush=True)
    return jsonify({"status": "ok"})

# envoie la liste des joueurs
@app.route('/joueurs', methods=['GET'])
def joueurs():
    return jsonify({"joueurs": joueurs_liste})
# ----------- Démarrage serveur -----------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
