import json
import math
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data.json"

# How each button maps to a "yes-ness" value. None = skip (no update).
ANSWER_VALUES = {
    "yes": 1.0,
    "probably": 0.75,
    "dont_know": None,
    "probably_not": 0.25,
    "no": 0.0,
}

MIN_P, MAX_P = 0.05, 0.95   # never fully certain, so one wrong answer can't kill the right character
GUESS_THRESHOLD = 0.8       # guess when top character reaches 80%
MAX_QUESTIONS = 20
LEARNING_RATE = 0.1         # how far to nudge stored probabilities after each game


def clamp(p):
    return max(MIN_P, min(MAX_P, p))


def load_data():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def likelihood(p_yes, value):
    """Probability of this answer for a character whose P(yes) is p_yes.
    value=1 -> p_yes, value=0 -> 1-p_yes, value=0.75 -> a soft mix."""
    return value * p_yes + (1 - value) * (1 - p_yes)


def entropy(probs):
    """Shannon entropy in bits: higher = more uncertain."""
    return -sum(p * math.log2(p) for p in probs if p > 0)


class Game:
    def __init__(self, data, scores=None, asked=None, answers=None):
        self.data = data
        self.characters = list(data["characters"].keys())
        n = len(self.characters)
        self.scores = scores if scores else {c: 1 / n for c in self.characters}
        # Characters added to data.json since this game started get a tiny score
        for c in self.characters:
            self.scores.setdefault(c, 1e-6)
        self.asked = asked if asked else []
        self.answers = answers if answers else {}

    # ---------- core probability helpers ----------

    def p_yes(self, character, qid):
        return clamp(self.data["characters"][character].get(qid, 0.5))

    def _normalize(self):
        total = sum(self.scores.values())
        if total == 0:
            n = len(self.scores)
            self.scores = {c: 1 / n for c in self.scores}
            return
        for c in self.scores:
            self.scores[c] /= total

    # ---------- Bayesian update ----------

    def answer(self, qid, response):
        self.asked.append(qid)
        value = ANSWER_VALUES[response]
        if value is None:          # "Don't know" -> no information
            return
        self.answers[qid] = value
        for c in self.characters:
            # posterior ∝ prior × likelihood
            self.scores[c] *= likelihood(self.p_yes(c, qid), value)
        self._normalize()

    # ---------- choosing the next question ----------

    def expected_entropy(self, qid):
        """Average uncertainty left AFTER asking qid, weighted over yes/no outcomes."""
        p_yes_total = sum(self.scores[c] * self.p_yes(c, qid) for c in self.characters)
        result = 0.0
        for outcome_prob, is_yes in ((p_yes_total, True), (1 - p_yes_total, False)):
            if outcome_prob <= 0:
                continue
            posterior = []
            for c in self.characters:
                p = self.p_yes(c, qid)
                l = p if is_yes else 1 - p
                posterior.append(self.scores[c] * l / outcome_prob)
            result += outcome_prob * entropy(posterior)
        return result

    def next_question(self):
        remaining = [q for q in self.data["questions"] if q not in self.asked]
        if not remaining:
            return None
        # Lowest expected entropy = highest information gain
        return min(remaining, key=self.expected_entropy)

    # ---------- guessing ----------

    def top_guess(self):
        best = max(self.scores, key=self.scores.get)
        return best, self.scores[best]

    def should_guess(self):
        _, prob = self.top_guess()
        return (
            prob >= GUESS_THRESHOLD
            or len(self.asked) >= MAX_QUESTIONS
            or self.next_question() is None
        )

    # ---------- learning from feedback ----------

    def learn(self, character):
        chars = self.data["characters"]
        # Case-insensitive match, so "virat kohli" finds "Virat Kohli"
        match = next((c for c in chars if c.lower() == character.lower()), None)

        if match is None:
            # New character: start from this player's answers
            chars[character] = {qid: clamp(v) for qid, v in self.answers.items()}
        else:
            # Existing character: nudge each probability toward this player's answer
            for qid, value in self.answers.items():
                old = chars[match].get(qid, 0.5)
                chars[match][qid] = round(old + LEARNING_RATE * (value - old), 3)

        save_data(self.data)

    # ---------- save/restore (for Flask sessions) ----------

    def to_dict(self):
        return {"scores": self.scores, "asked": self.asked, "answers": self.answers}

    @classmethod
    def from_dict(cls, data, state):
        return cls(data, state["scores"], state["asked"], state["answers"])