import sys
import time

def slow_print(text, delay=0.01):
    """Print text slowly to make interaction feel more human."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

CONDITIONS = {
    "Common Cold": {
        "symptoms": {
            "cough": 1.0,
            "sore throat": 1.0,
            "runny nose": 1.0,
            "sneezing": 0.8,
            "mild fever": 0.5,
            "fatigue": 0.6
        },
        "advice": "Self-care: rest, fluids, OTC medicines. See doctor if symptoms worsen or persist beyond 7-10 days."
    },
    "Influenza (Flu)": {
        "symptoms": {
            "high fever": 1.5,
            "body aches": 1.2,
            "chills": 1.0,
            "cough": 1.0,
            "fatigue": 1.0,
            "headache": 0.9
        },
        "advice": "See a doctor for possible antiviral treatment, especially if high-risk (elderly, pregnant, immunocompromised)."
    },
    "COVID-19": {
        "symptoms": {
            "fever": 1.2,
            "dry cough": 1.2,
            "loss of taste or smell": 2.0,
            "fatigue": 0.9,
            "shortness of breath": 1.8,
            "sore throat": 0.8
        },
        "advice": "Get tested for COVID-19 and isolate. See healthcare if breathing difficulty or severe symptoms."
    },
    "Strep Throat": {
        "symptoms": {
            "severe sore throat": 2.0,
            "fever": 1.0,
            "swollen lymph nodes": 1.0,
            "difficulty swallowing": 1.2,
            "no cough": 0.5
        },
        "advice": "See a doctor — strep often needs antibiotic treatment."
    },
    "Migraine": {
        "symptoms": {
            "severe headache": 2.0,
            "nausea": 0.9,
            "sensitivity to light": 1.0,
            "visual disturbances": 1.3
        },
        "advice": "Rest in a quiet, dark room; see neurologist if headaches are frequent or disabling."
    },
    "Gastroenteritis (Stomach Flu/Food Poisoning)": {
        "symptoms": {
            "nausea": 1.0,
            "vomiting": 1.3,
            "diarrhea": 1.4,
            "abdominal pain": 1.0,
            "fever": 0.8
        },
        "advice": "Hydrate (oral rehydration), rest. See doctor if unable to retain fluids or if symptoms severe."
    },
    "Urinary Tract Infection (UTI)": {
        "symptoms": {
            "burning urination": 2.0,
            "frequent urination": 1.2,
            "urinary urgency": 1.1,
            "lower abdominal pain": 0.9,
            "fever": 0.7
        },
        "advice": "See a doctor for urine test and likely antibiotic treatment."
    },
    "Pneumonia": {
        "symptoms": {
            "high fever": 1.5,
            "productive cough": 1.3,
            "shortness of breath": 2.0,
            "chest pain": 1.5,
            "fatigue": 1.0
        },
        "advice": "Seek prompt medical evaluation — pneumonia can be serious and may require antibiotics or hospitalization."
    }
}


def normalize_symptom(s: str) -> str:
    """Normalize a user-entered symptom (lowercase, strip)."""
    return s.strip().lower()

def ask_yes_no(prompt: str) -> bool:
    """Ask the user a yes/no question; return True for yes, False for no."""
    while True:
        ans = input(prompt + " (y/n): ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")

def collect_basic_info():
    """Collects age and any urgent red-flag symptoms."""
    print("\n--- Patient Info ---")
    while True:
        try:
            age = int(input("Enter patient's age (years): ").strip())
            break
        except ValueError:
            print("Please enter a valid integer for age.")
    # Check red flags
    print("\nQuick emergency check — answer honestly. These suggest immediate medical attention.")
    red_flags = []
    rf_questions = [
        ("severe chest pain", "Are you experiencing severe chest pain right now?"),
        ("severe difficulty breathing", "Are you having severe difficulty breathing or shortness of breath?"),
        ("loss of consciousness", "Have you fainted or lost consciousness?"),
        ("severe bleeding", "Is there uncontrolled/severe bleeding?"),
        ("sudden weakness or slurred speech", "Do you have sudden weakness, drooping face, or slurred speech?")
    ]
    for key, q in rf_questions:
        if ask_yes_no(q):
            red_flags.append(key)
    return age, red_flags

def symptom_input_loop():
    """Interactively collect symptoms from the user until they say 'done'."""
    print("\nEnter symptoms one at a time. Type 'done' when finished.")
    print("Examples: 'fever', 'cough', 'shortness of breath', 'nausea', 'sore throat', 'loss of taste or smell'")
    symptoms = []
    while True:
        s = input("Symptom: ").strip()
        if s.lower() == "done":
            break
        s = normalize_symptom(s)
        if s:
            symptoms.append(s)
    return symptoms

def match_conditions(user_symptoms):
    """Score each condition using the symptom weights and return ranked results."""
    scores = {}
    for cond, info in CONDITIONS.items():
        score = 0.0
        for usym in user_symptoms:
            if usym in info["symptoms"]:
                score += info["symptoms"][usym]
            else:
                for known_sym, w in info["symptoms"].items():
                    if usym in known_sym or known_sym in usym:
                        score += w * 0.9
        scores[cond] = score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked

def interpret_scores(ranked_scores, user_symptoms, age, red_flags):
    """Create a human-readable interpretation, thresholds chosen heuristically."""
    if red_flags:
        return {
            "level": "Emergency",
            "message": "You reported one or more emergency symptoms: {}. Seek immediate medical attention or call emergency services.".format(", ".join(red_flags)),
            "recommendation": "Emergency — seek immediate care"
        }

    top_condition, top_score = ranked_scores[0]
    second_score = ranked_scores[1][1] if len(ranked_scores) > 1 else 0.0

    if top_score == 0:
        level = "Unclear"
        message = "Your symptoms did not clearly match the knowledge base. Consider seeing a doctor for a full evaluation."
        recommendation = "See a doctor if symptoms persist or worsen."
    elif top_score >= 2.5 and (top_score - second_score) >= 0.7:
        level = "Likely"
        message = f"Most likely: {top_condition} (score {top_score:.1f}). Matched symptoms: {', '.join(user_symptoms)}"
        recommendation = CONDITIONS[top_condition]["advice"]
    elif top_score >= 1.2:
        level = "Possible"
        message = f"Possible: {top_condition} (score {top_score:.1f}). Also consider: {', '.join([c for c,s in ranked_scores[1:4]])}"
        recommendation = CONDITIONS[top_condition]["advice"]
    else:
        level = "Unclear"
        message = "Symptoms are vague or mild. Monitor and seek medical advice if symptoms worsen."
        recommendation = "Self-care or see a doctor if concerned."

    if age >= 65 and level != "Emergency":
        recommendation += " Note: Because of your age (65+), seek medical advice sooner."

    return {
        "level": level,
        "message": message,
        "recommendation": recommendation
    }

def main():
    slow_print("Welcome to the Medical Symptom Checker (Interactive).", 0.005)
    age, red_flags = collect_basic_info()
    user_symptoms = symptom_input_loop()
    if not user_symptoms and not red_flags:
        slow_print("No symptoms entered. If this is an error, please run the tool again and enter symptoms.", 0.01)
        return

    ranked = match_conditions(user_symptoms)
    result = interpret_scores(ranked, user_symptoms, age, red_flags)

    print("\n--- Results ---")
    print("Severity level :", result["level"])
    print("Interpretation  :", result["message"])
    print("Recommendation  :", result["recommendation"])

    print("\nTop matches (condition : score)")
    for cond, score in ranked[:6]:
        print(f" - {cond:30s} : {score:.2f}")

    print("\nDisclaimer: This symptom checker is educational and rule-based. It is NOT a substitute for professional medical advice, diagnosis, or treatment. If you are in doubt, seek professional care.")

if __name__ == "__main__":
    main()
