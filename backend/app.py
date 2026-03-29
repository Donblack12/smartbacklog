from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import uuid

app = Flask(__name__)
CORS(app)

# ===== BASE DE DONNÉES EN MÉMOIRE =====
users = []
tickets = []
next_ticket_id = 1

# ===== UTILITAIRES =====
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def find_user_by_email(email):
    for u in users:
        if u["email"] == email:
            return u
    return None

# ===== ROUTES AUTH =====

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not name or not email or not password:
        return jsonify({"error": "Tous les champs sont requis"}), 400

    if len(password) < 6:
        return jsonify({"error": "Mot de passe trop court"}), 400

    if find_user_by_email(email):
        return jsonify({"error": "Un compte avec cet email existe déjà"}), 409

    user = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "password": hash_password(password)
    }
    users.append(user)
    return jsonify({"message": "Compte créé avec succès"}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    user = find_user_by_email(email)
    if not user or user["password"] != hash_password(password):
        return jsonify({"error": "Email ou mot de passe incorrect"}), 401

    return jsonify({
        "message": "Connexion réussie",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }), 200


# ===== ROUTES TICKETS =====

@app.route("/tickets", methods=["GET"])
def get_tickets():
    return jsonify(tickets)


@app.route("/tickets", methods=["POST"])
def add_ticket():
    global next_ticket_id
    data = request.json
    ticket = {
        "id": next_ticket_id,
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "status": "todo",
        "created_by": data.get("created_by", "Anonyme"),
        "criteria": [],
        "points": None,
        "priority": None
    }
    tickets.append(ticket)
    next_ticket_id += 1
    return jsonify(ticket), 201


@app.route("/tickets/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id):
    data = request.json
    for t in tickets:
        if t["id"] == ticket_id:
            t.update(data)
            return jsonify(t)
    return jsonify({"error": "Ticket non trouvé"}), 404


@app.route("/tickets/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    global tickets
    tickets = [t for t in tickets if t["id"] != ticket_id]
    return jsonify({"success": True})


# ===== ROUTE IA — sera complétée par HK au Sprint 2 =====

@app.route("/ai/analyze", methods=["POST"])
def analyze():
    return jsonify({"error": "IA non encore configurée — Sprint 2"}), 501


if __name__ == "__main__":
    app.run(debug=True, port=5000)