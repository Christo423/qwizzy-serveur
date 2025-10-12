from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import hashlib
import os

app = Flask(__name__)
CORS(app)


# ----------- Initialisation BDD si elle n'existe pas -----------

def get_db_connection():
    return psycopg2.connect("postgresql://neondb_owner:npg_IOF0fzBHolK1@ep-muddy-dust-a2csyic0-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # utilisateurs
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE,
            username TEXT,
            password_hash TEXT,
            moogems INTEGER DEFAULT 100,
            mooshes JSON DEFAULT '[]'
        )
    ''')
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS age INTEGER")
    # mooshes du store
    cur.execute('''
        CREATE TABLE IF NOT EXISTS mooshes (
            id SERIAL PRIMARY KEY,
            rarete TEXT,
            nom TEXT,
            prix INTEGER,
            en_vente BOOLEAN DEFAULT TRUE,
            proprio_id INTEGER,
            date_creation TIMESTAMP DEFAULT Now(),
            visu JSON
        )
    ''')
    cur.execute("ALTER TABLE mooshes ADD COLUMN IF NOT EXISTS serie INTEGER")
    cur.execute("ALTER TABLE mooshes ADD COLUMN IF NOT EXISTS etat TEXT")
    conn.commit()
    conn.close()
init_db()

# ----------- Utilitaires -----------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_email(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = c.fetchone()
    conn.close()
    return user

# ----------- Routes -----------

# enregistrements de l'utilisateur
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if data is None :
        return jsonify({"error": "aucune donnée reçue"}), 400
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    age = data.get("age")

    if not email or not username or not password:
        return jsonify({"error": "Champs manquants"}), 400

    if get_user_by_email(email):
        return jsonify({"error": "Email déjà utilisé"}), 409

    password_hash = hash_password(password)

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (email, username, password_hash, age) VALUES (%s, %s, %s, %s)",
              (email, username, password_hash, age))
    conn.commit()
    conn.close()

    return jsonify({"message": "Compte créé avec succès"}), 201

# connexion de l'utilisateur 
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data is None :
        return jsonify({"error": "aucune donnée reçue"}), 400
    email = data.get("email")
    password = data.get("password")
    user = get_user_by_email(email)

    if not user or hash_password(password) != user[3]:
        return jsonify({"error": "Identifiants invalides"}), 401

    return jsonify({
        "id": user[0],
        "username": user[2],
        "moogems": user[4],
        "mooshes": user[5],
        "age": user[6]
    })
    
# interface administrateur (utilisateurs)
@app.route('/admin/users', methods=['GET'])
def show_all_users():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, email, username, moogems, mooshes, age FROM users")
    users = c.fetchall()
    conn.close()
    
    result = []
    for u in users:
        result.append({
            "id": u[0],
            "email": u[1],
            "username": u[2],
            "moogems": u[3],
            "mooshes": u[4],
            "age": u[5]
        })
    
    return jsonify(result)
    
# interfaces administrateur (store)
@app.route('/admin/ajouter_moosh', methods=['POST'])
def modif_store():
    data = request.get_json()
    if data is None :
        return jsonify({"error": "aucune donnée reçue"}), 400
    nom = data.get("nom")
    rarete = data.get("rarete")
    prix = data.get("prix")
    proprio_id = data.get("proprio_id")
    en_vente = data.get("en_vente")
    visu = data.get("visu")
    serie = data.get("serie")
    etat = data.get("etat")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO mooshes (nom, rarete, prix, proprio_id, en_vente, visu, serie, etat) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
              (nom, rarete, prix, proprio_id, en_vente, visu, serie, etat))
    conn.commit()
    conn.close()

    return jsonify({"message": "moosh créé avec succès"}), 201
    
# store
@app.route('/store', methods=['GET'])
def get_store_mooshes():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, nom, rarete, prix, proprio_id, visu, serie, en_vente, etat FROM mooshes")
    rows = c.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "nom": row[1],
            "rarete": row[2],
            "prix": row[3],
            "proprio_id" : row[4],
            "visu": row[5],
            "serie": row[6],
            "en_vente" : row[7],
            "etat" : row[8]
        })

    return jsonify(result)
    
# acheter les mooshes 
@app.route('/moosh/acheter', methods=['POST'])
def acheter_moosh():
    data = request.json
    moosh_id = data.get('id')
    proprio_id = data.get('proprio_id')
    en_vente = data.get('en_vente')
    etat = data.get('etat')

    if not moosh_id or not proprio_id:
        return jsonify({'success': False, 'error': 'id ou acheteur_id manquant'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Met à jour en_vente et le propriétaire
        cur.execute("""
            UPDATE mooshes
            SET en_vente = %s, proprio_id = %s, etat = %s
            WHERE id = %s
        """, (en_vente, proprio_id, etat, moosh_id))

        conn.commit()
        cur.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
        
# route temporaire pour effacer les mooshes
@app.route('/supp', methods=['POST'])
def reset_mooshes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM mooshes;")
    conn.commit()
    return {"message": "Tous les mooshes ont été supprimés."}, 200
    
# ping pong avec le client 
@app.route('/ping', methods=['POST'])
def ping():
    data = request.get_json()
    
    return jsonify({"message" : "pong"})
    
# ----------- Démarrage serveur -----------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0
