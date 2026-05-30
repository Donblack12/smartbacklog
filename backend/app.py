from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import uuid
import sqlite3
import json
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "smartbacklog.db")

MAX_LEN = {"name": 100, "email": 200, "password": 200, "title": 200, "description": 2000}
VALID_STATUS = ("todo", "inprogress", "done")
VALID_PRIORITY = ("urgent", "bloquant", "normal")


# ===== BASE DE DONNÉES =====

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       TEXT PRIMARY KEY,
            name     TEXT NOT NULL,
            email    TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token   TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS tickets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT DEFAULT '',
            status      TEXT DEFAULT 'todo',
            priority    TEXT DEFAULT NULL,
            points      INTEGER DEFAULT NULL,
            due_date    TEXT DEFAULT NULL,
            created_by  TEXT DEFAULT 'Anonyme',
            criteria    TEXT DEFAULT '[]',
            created_at  TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


init_db()


# ===== UTILITAIRES =====

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def row_to_ticket(row):
    t = dict(row)
    t["criteria"] = json.loads(t.get("criteria") or "[]")
    return t


def get_token():
    return request.headers.get("Authorization", "").replace("Bearer ", "").strip()


def get_current_user():
    token = get_token()
    if not token:
        return None
    conn = get_db()
    row = conn.execute(
        "SELECT u.* FROM users u JOIN sessions s ON u.id = s.user_id WHERE s.token = ?",
        (token,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ===== AUTH =====

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.json or {}
    name     = str(data.get("name",     "")).strip()[:MAX_LEN["name"]]
    email    = str(data.get("email",    "")).strip().lower()[:MAX_LEN["email"]]
    password = str(data.get("password", "")).strip()[:MAX_LEN["password"]]

    if not name or not email or not password:
        return jsonify({"error": "Tous les champs sont requis"}), 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "Email invalide"}), 400
    if len(password) < 6:
        return jsonify({"error": "Mot de passe trop court (minimum 6 caractères)"}), 400

    conn = get_db()
    if conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
        conn.close()
        return jsonify({"error": "Un compte avec cet email existe déjà"}), 409

    user_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO users (id, name, email, password) VALUES (?, ?, ?, ?)",
        (user_id, name, email, hash_password(password))
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Compte créé avec succès"}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    data     = request.json or {}
    email    = str(data.get("email",    "")).strip().lower()
    password = str(data.get("password", "")).strip()

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user or user["password"] != hash_password(password):
        conn.close()
        return jsonify({"error": "Email ou mot de passe incorrect"}), 401

    token = str(uuid.uuid4())
    conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user["id"]))
    conn.commit()
    conn.close()
    return jsonify({
        "message": "Connexion réussie",
        "token": token,
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]}
    }), 200


@app.route("/auth/logout", methods=["POST"])
def logout():
    token = get_token()
    if token:
        conn = get_db()
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
    return jsonify({"message": "Déconnecté"}), 200


# ===== TICKETS =====

@app.route("/tickets", methods=["GET"])
def get_tickets():
    search   = request.args.get("q",        "").strip()
    status   = request.args.get("status",   "").strip()
    priority = request.args.get("priority", "").strip()

    conn   = get_db()
    query  = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if search:
        query  += " AND (title LIKE ? OR description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if status and status in VALID_STATUS:
        query  += " AND status = ?"
        params.append(status)
    if priority and priority in VALID_PRIORITY:
        query  += " AND priority = ?"
        params.append(priority)

    query += " ORDER BY id DESC"
    rows   = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([row_to_ticket(r) for r in rows])


@app.route("/tickets", methods=["POST"])
def add_ticket():
    data        = request.json or {}
    title       = str(data.get("title",       "")).strip()[:MAX_LEN["title"]]
    description = str(data.get("description", "")).strip()[:MAX_LEN["description"]]
    created_by  = str(data.get("created_by",  "Anonyme")).strip()[:100]
    priority    = data.get("priority")  if data.get("priority")  in VALID_PRIORITY else None
    due_date    = data.get("due_date",  None)

    if not title:
        return jsonify({"error": "Le titre est requis"}), 400

    conn = get_db()
    cur  = conn.execute(
        "INSERT INTO tickets (title, description, status, priority, due_date, created_by, criteria) "
        "VALUES (?, ?, 'todo', ?, ?, ?, '[]')",
        (title, description, priority, due_date, created_by)
    )
    ticket_id = cur.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    conn.close()
    return jsonify(row_to_ticket(row)), 201


@app.route("/tickets/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id):
    data = request.json or {}
    conn = get_db()
    row  = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Ticket non trouvé"}), 404

    t = dict(row)
    if "title"       in data: t["title"]       = str(data["title"]).strip()[:MAX_LEN["title"]]
    if "description" in data: t["description"] = str(data["description"]).strip()[:MAX_LEN["description"]]
    if "status"      in data and data["status"] in VALID_STATUS:   t["status"]   = data["status"]
    if "priority"    in data: t["priority"]    = data["priority"] if data["priority"] in VALID_PRIORITY else None
    if "due_date"    in data: t["due_date"]    = data["due_date"]
    if "points"      in data: t["points"]      = data["points"]
    if "criteria"    in data: t["criteria"]    = json.dumps(data["criteria"]) if isinstance(data["criteria"], list) else "[]"

    conn.execute(
        "UPDATE tickets SET title=?, description=?, status=?, priority=?, due_date=?, criteria=?, points=? WHERE id=?",
        (t["title"], t["description"], t["status"], t["priority"], t["due_date"], t["criteria"], t["points"], ticket_id)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    conn.close()
    return jsonify(row_to_ticket(row))


@app.route("/tickets/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    conn = get_db()
    conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ===== STATS =====

@app.route("/stats", methods=["GET"])
def get_stats():
    conn  = get_db()
    total = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    todo  = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='todo'").fetchone()[0]
    inp   = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='inprogress'").fetchone()[0]
    done  = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='done'").fetchone()[0]
    ai    = conn.execute("SELECT COUNT(*) FROM tickets WHERE criteria != '[]'").fetchone()[0]
    conn.close()
    return jsonify({"total": total, "todo": todo, "inprogress": inp, "done": done, "ai_analyzed": ai})


# ===== IA — Sprint 2 =====

SYSTEM_PROMPT = """Tu es un Coach Agile expert spécialisé dans la gestion de produits et la méthodologie Scrum.
Quand on te donne le titre et la description d'un ticket (User Story), retourne UNIQUEMENT un objet JSON valide avec ces 3 champs :

- "criteria" : liste de 3 à 5 critères d'acceptation précis et testables
- "points" : entier parmi [1, 2, 3, 5, 8, 13] estimant la complexité (suite de Fibonacci)
- "priority" : exactement "urgent", "bloquant" ou "normal" selon l'impact métier

Règles story points : 1-2=simple(<2h), 3=moyen(demi-journée), 5=complexe(journée), 8=très complexe(plusieurs jours), 13=massif(à découper)
Règles priorité : urgent=impacte utilisateur/revenu directement, bloquant=d'autres tâches en dépendent, normal=important mais ne bloque rien

Réponds UNIQUEMENT avec le JSON brut, sans markdown ni texte autour."""


@app.route("/ai/analyze", methods=["POST"])
def analyze():
    import os
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return jsonify({"error": "Clé API OpenAI manquante — définir OPENAI_API_KEY"}), 500

    data        = request.json or {}
    title       = str(data.get("title",       "")).strip()[:200]
    description = str(data.get("description", "")).strip()[:1000]

    if not title:
        return jsonify({"error": "Le titre est requis"}), 400

    user_message = f"Titre du ticket : {title}"
    if description:
        user_message += f"\nDescription : {description}"

    try:
        client   = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message}
            ],
            temperature=0.4,
            max_tokens=600
        )

        result   = json.loads(response.choices[0].message.content)

        criteria = result.get("criteria", [])
        if not isinstance(criteria, list):
            criteria = []
        criteria = [str(c) for c in criteria[:5]]

        points = result.get("points", 3)
        if points not in [1, 2, 3, 5, 8, 13]:
            points = 3

        priority = result.get("priority", "normal")
        if priority not in ["urgent", "bloquant", "normal"]:
            priority = "normal"

        return jsonify({"criteria": criteria, "points": points, "priority": priority})

    except json.JSONDecodeError:
        return jsonify({"error": "Réponse IA invalide"}), 500
    except Exception as e:
        return jsonify({"error": f"Erreur OpenAI : {str(e)}"}), 500
