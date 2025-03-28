import sqlite3
import random
from flask import Flask, render_template, request, jsonify
from Games.blackjack import Deck, Player

app = Flask(__name__)

# Initialize game state
deck = None
player = None
dealer = None

# Database setup
def init_db():
    conn = sqlite3.connect("leaderboard.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            score INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT
        )
    """)
    # Add 30,000 fake players if the table is empty
    cursor.execute("SELECT COUNT(*) FROM leaderboard")
    if cursor.fetchone()[0] == 0:
        fake_players = [(f"Player{i}", random.randint(0, 1000)) for i in range(1, 30001)]
        cursor.executemany("INSERT INTO leaderboard (name, score) VALUES (?, ?)", fake_players)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_game():
    global deck, player, dealer
    deck = Deck()
    player = Player("Player")
    dealer = Player("Dealer")

    # Initial deal
    for _ in range(2):
        player.add_card(deck.draw())
        dealer.add_card(deck.draw())

    return jsonify({
        "player_hand": [str(card) for card in player.hand],
        "dealer_hand": [str(dealer.hand[0])],  # Show only one dealer card
        "player_value": player.hand_value()
    })

@app.route("/hit", methods=["POST"])
def hit():
    global player
    player.add_card(deck.draw())
    if player.hand_value() > 21:
        update_leaderboard(-1)  # Player loses
        return jsonify({
            "player_hand": [str(card) for card in player.hand],
            "player_value": player.hand_value(),
            "result": "Bust! You lose."
        })
    return jsonify({
        "player_hand": [str(card) for card in player.hand],
        "player_value": player.hand_value()
    })

@app.route("/stand", methods=["POST"])
def stand():
    global dealer
    while dealer.hand_value() < 17:
        dealer.add_card(deck.draw())

    dealer_value = dealer.hand_value()
    player_value = player.hand_value()

    if dealer_value > 21 or player_value > dealer_value:
        result = "You win!"
        update_leaderboard(1)  # Player wins
    elif player_value < dealer_value:
        result = "You lose!"
        update_leaderboard(-1)  # Player loses
    else:
        result = "It's a tie!"

    return jsonify({
        "dealer_hand": [str(card) for card in dealer.hand],
        "dealer_value": dealer_value,
        "result": result
    })

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    conn = sqlite3.connect("leaderboard.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM leaderboard ORDER BY score DESC LIMIT 10")
    top_players = cursor.fetchall()
    conn.close()
    return jsonify(top_players)

@app.route("/set_username", methods=["POST"])
def set_username():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Username cannot be empty"}), 400

    conn = sqlite3.connect("leaderboard.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM player_user")  # Ensure only one username exists
    cursor.execute("INSERT INTO player_user (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Username set successfully"})

@app.route("/get_username", methods=["GET"])
def get_username():
    conn = sqlite3.connect("leaderboard.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM player_user LIMIT 1")
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({"username": user[0]})
    return jsonify({"username": None})

def update_leaderboard(result):
    conn = sqlite3.connect("leaderboard.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM player_user LIMIT 1")
    user = cursor.fetchone()
    username = user[0] if user else "Player"

    cursor.execute("SELECT id, score FROM leaderboard WHERE name = ?", (username,))
    player = cursor.fetchone()
    if player:
        new_score = player[1] + (10 if result == 1 else -10)
        cursor.execute("UPDATE leaderboard SET score = ? WHERE id = ?", (new_score, player[0]))
    else:
        cursor.execute("INSERT INTO leaderboard (name, score) VALUES (?, ?)", (username, 10 if result == 1 else 0))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
