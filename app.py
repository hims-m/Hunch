from flask import Flask, render_template, request, redirect, url_for, session
from engine import Game, load_data, ANSWER_VALUES
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-key")

def get_game():
    data = load_data()
    state = session.get("game")
    return Game.from_dict(data, state) if state else Game(data)


def save_game(game):
    session["game"] = game.to_dict()


@app.route("/")
def index():
    session.pop("game", None)
    return render_template("index.html", stage="start")


@app.route("/play")
def play():
    game = get_game()
    if game.should_guess():
        save_game(game)
        return redirect(url_for("guess"))
    qid = game.next_question()
    save_game(game)
    return render_template(
        "index.html",
        stage="question",
        qid=qid,
        question=game.data["questions"][qid],
        number=len(game.asked) + 1,
    )


@app.route("/answer", methods=["POST"])
def answer():
    game = get_game()
    qid = request.form.get("qid")
    response = request.form.get("response")
    if qid in game.data["questions"] and qid not in game.asked and response in ANSWER_VALUES:
        game.answer(qid, response)
        save_game(game)
    return redirect(url_for("play"))


@app.route("/guess")
def guess():
    game = get_game()
    name, prob = game.top_guess()
    return render_template("index.html", stage="guess", name=name, confidence=round(prob * 100))


@app.route("/result", methods=["POST"])
def result():
    game = get_game()
    if request.form.get("correct") == "yes":
        game.learn(game.top_guess()[0])
        session.pop("game", None)
        return render_template("index.html", stage="win")
    return render_template("index.html", stage="teach")


@app.route("/teach", methods=["POST"])
def teach():
    game = get_game()
    name = request.form.get("name", "").strip()
    if name:
        game.learn(name)
    session.pop("game", None)
    return render_template("index.html", stage="learned", name=name)


if __name__ == "__main__":
    app.run(debug=True)