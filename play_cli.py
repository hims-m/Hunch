from engine import Game, load_data

KEYS = {"y": "yes", "n": "no", "p": "probably", "pn": "probably_not", "d": "dont_know"}

game = Game(load_data())
print("Think of a character! Answer with y / n / p / pn / d\n")

while not game.should_guess():
    qid = game.next_question()
    reply = ""
    while reply not in KEYS:
        reply = input(f"{game.data['questions'][qid]} ").strip().lower()
    game.answer(qid, KEYS[reply])

name, prob = game.top_guess()
if input(f"\nIs it {name}? ({prob:.0%} sure) y/n: ").strip().lower() == "y":
    game.learn(name)
    print("Got it!")
else:
    real = input("Who was it? ").strip()
    if real:
        game.learn(real)
        print(f"Thanks, I'll remember {real}.")