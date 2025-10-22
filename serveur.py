
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
joueurs_liste = []
nbr = 0
etat = ""
nbr_questions = 0

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
    global nbr
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
    print("✅ " + str(mdp) + " / " + str(nbr), flush=True)
    if str(mdp) == str(nbr) :
        pseudo = data.get("pseudo")
        lst = [str(pseudo), 0]
        joueurs_liste.append(lst)
        print("✅ joueur " + str(pseudo) + "connecte", flush=True)
        return jsonify({"status": "connecte"})
    else :
        print("✅ non connecte", flush=True)
        return jsonify({"status": "non connecte"})

# envoie la liste des joueurs
@app.route('/joueurs', methods=['GET'])
def joueurs():
    return jsonify({"joueurs": joueurs_liste})

# recois l'etat du questionnaire
@app.route('/env_etat', methods=['POST'])
def env_etat() :
    global etat
    global nbr_questions
    data = request.get_json()
    etat = data.get("etat_qst")
    nbr_questions = data.get("nbr_qst")
    print("✅ etat questionnaire recu " + str(etat) + " : " + str(nbr_questions), flush=True)
    return jsonify({"status": "ok"})

# renvoi l'etat du questionnaire
@app.route('/rec_etat', methods=['GET'])
def rec_etat() :
    global etat
    global nbr_questions
    print("✅ etat questionnaire envoye " + str(etat) + " : " + str(nbr_questions), flush=True)
    return jsonify({"etat": etat, "nbr_qst": nbr_questions})

# met a jour le score du joueur
@app.route('/maj_score', methods=['POST'])
def maj_score() :
    global joueurs_liste
    point = 100
    data = request.get_json()
    pseudo = data.get("pseudo")
    print("✅ joueur " + str(pseudo) + " + " + str(point) + " points", flush=True)

    for joueur in joueurs_liste :
        if joueur[0] == pseudo :
            joueur[1] = joueur[1] + point
    return jsonify({"status": "ok"})
# ----------- Démarrage serveur -----------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
