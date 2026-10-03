import json
from pathlib import Path

YES, NO = 0.95, 0.05
OUTPUT = Path(__file__).parent / "data.json"

QUESTIONS = {
    "demigod": "Is your character a demigod?",
    "male": "Is your character male?",
    "god": "Is your character a god or goddess?",
    "creature": "Is your character a monster or magical creature?",
    "mortal": "Is your character an ordinary mortal?",
    "big_three": "Is your character a child of Zeus, Poseidon, or Hades?",
    "sea": "Is your character connected to the sea?",
    "underworld": "Is your character connected to the Underworld?",
    "sky": "Is your character connected to the sky or lightning?",
    "villain": "Is your character an enemy of Percy at some point?",
    "kronos": "Did your character serve or help Kronos?",
    "dies": "Does your character die in the series?",
    "hunter": "Is your character a Hunter of Artemis?",
    "main_trio": "Is your character part of the main trio?",
    "camp": "Does your character spend a lot of time at Camp Half-Blood?",
    "smart": "Is your character known for wisdom or strategy?",
    "fighter": "Is your character known as a fierce fighter?",
    "parent": "Is your character a parent of a main character?",
    "crafting": "Is your character good at building or metalwork?",
    "prophecy": "Is your character connected to prophecies or the Oracle?",
    "love": "Is your character connected to love or beauty?",
    "titan": "Is your character a Titan?",
    "camp_staff": "Does your character run or teach at Camp Half-Blood?",
    "one_eye": "Does your character have only one working eye?",
    "hooves": "Does your character have hooves?",
    "pet": "Is your character someone's pet?",
}

# name: ("space-separated YES traits", {trait: in-between probability})
CHARACTERS = {
    "Percy Jackson":        ("demigod male big_three sea main_trio fighter", {"camp": 0.8, "prophecy": 0.4}),
    "Annabeth Chase":       ("demigod main_trio camp smart", {"crafting": 0.5, "fighter": 0.6}),
    "Grover Underwood":     ("male creature main_trio hooves", {"camp": 0.7}),
    "Luke Castellan":       ("demigod male villain kronos dies fighter", {"camp": 0.5, "prophecy": 0.3}),
    "Thalia Grace":         ("demigod big_three sky hunter fighter", {"camp": 0.3}),
    "Nico di Angelo":       ("demigod male big_three underworld", {"camp": 0.4}),
    "Bianca di Angelo":     ("demigod big_three underworld hunter dies", {}),
    "Clarisse La Rue":      ("demigod camp fighter", {"villain": 0.2}),
    "Chiron":               ("male creature camp camp_staff hooves", {"smart": 0.7}),
    "Tyson":                ("male creature sea crafting one_eye", {"camp": 0.4, "fighter": 0.5}),
    "Rachel Elizabeth Dare": ("mortal prophecy", {"camp": 0.3}),
    "Kronos":               ("male titan villain kronos fighter", {"dies": 0.6}),
    "Poseidon":             ("male god sea parent", {}),
    "Zeus":                 ("male god sky parent", {}),
    "Hades":                ("male god underworld parent", {"villain": 0.3}),
    "Artemis":              ("god hunter", {"sky": 0.2}),
    "Dionysus":             ("male god camp camp_staff", {"parent": 0.3}),
    "Sally Jackson":        ("mortal parent", {}),
    "Silena Beauregard":    ("demigod camp kronos dies love", {"villain": 0.3}),
    "Charles Beckendorf":   ("demigod male camp crafting dies", {}),
    "Medusa":               ("creature villain", {"dies": 0.8, "kronos": 0.3}),
    "Mrs. O'Leary":         ("creature underworld pet", {"camp": 0.7}),
    "Ethan Nakamura":       ("demigod male villain kronos dies one_eye", {}),
}


def build():
    characters = {}
    for name, (yes_traits, partial) in CHARACTERS.items():
        yes_set = set(yes_traits.split())
        unknown = (yes_set | set(partial)) - set(QUESTIONS)
        if unknown:
            raise ValueError(f"{name}: unknown trait(s) {unknown}, check for typos")
        characters[name] = {
            q: partial.get(q, YES if q in yes_set else NO) for q in QUESTIONS
        }

    data = {"questions": QUESTIONS, "characters": characters}
    OUTPUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(characters)} characters and {len(QUESTIONS)} questions to {OUTPUT.name}")


if __name__ == "__main__":
    build()