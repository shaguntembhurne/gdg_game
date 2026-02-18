from flask import Flask, request, jsonify, send_from_directory, send_file
import os
import sqlite3

app = Flask(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR  = os.path.join(BASE_DIR, 'static')
GAME_DIR    = os.path.join(STATIC_DIR, 'game')
DB_PATH     = os.path.join(BASE_DIR, 'scores.db')


# ── Database ────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            score      INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ── Pages ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_file(os.path.join(STATIC_DIR, 'index.html'))


@app.route('/game')
def game():
    return send_file(os.path.join(GAME_DIR, 'index.html'))


# ── API ─────────────────────────────────────────────────────────────────────
@app.route('/leaderboard')
def leaderboard():
    conn = get_db()
    rows = conn.execute(
        'SELECT name, score FROM scores ORDER BY score DESC LIMIT 3'
    ).fetchall()
    conn.close()
    return jsonify([{'name': r['name'], 'score': r['score']} for r in rows])


@app.route('/submit-score', methods=['POST'])
def submit_score():
    data = request.get_json(force=True, silent=True)
    if not data or not str(data.get('name', '')).strip():
        return jsonify({'error': 'name is required'}), 400
    if not str(data.get('phone', '')).strip():
        return jsonify({'error': 'phone is required'}), 400
    name  = str(data['name']).strip()
    phone = str(data['phone']).strip()
    score = int(data.get('score', 0))
    conn  = get_db()
    conn.execute(
        'INSERT INTO scores (name, phone, score) VALUES (?, ?, ?)',
        (name, phone, score)
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})


# ── Game assets (requested at root level by duckhunt.js) ────────────────────
@app.route('/sprites.json')
def sprites_json():
    return send_from_directory(GAME_DIR, 'sprites.json')


@app.route('/sprites.png')
def sprites_png():
    return send_from_directory(GAME_DIR, 'sprites.png')


@app.route('/audio.json')
def audio_json():
    return send_from_directory(GAME_DIR, 'audio.json')


@app.route('/audio.mp3')
def audio_mp3():
    return send_from_directory(GAME_DIR, 'audio.mp3')


@app.route('/audio.ogg')
def audio_ogg():
    return send_from_directory(GAME_DIR, 'audio.ogg')


# ── Static files (/static/**) ────────────────────────────────────────────────
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


if __name__ == '__main__':
    app.run(debug=True)
