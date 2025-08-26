import os
import json
from openai import OpenAI


# Client initialisieren
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def fact_to_question(fact: str) -> str:
    prompt = f"""
    Formuliere aus dem folgenden Fakt eine kurze, präzise Frage, deren Antwort ausschließlich im Fakt enthalten ist.
    Eine Frage die nicht aus dem Fakt hervorgeht, ist nicht erlaubt.
    Die Frage muss zwingend so gestellt werden, dass nur ein Wort bzw. Term als Antwort erwartet wird (z.B. ein Ort, ein Name, eine Zahl). 
    
    Fakt: {fact}
    
    Frage:
    """
    response = client.chat.completions.create(
        model=os.environ["OPENAI_MODEL"],
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=100
    )
    
    question = response.choices[0].message.content.strip()
    return question


def evaluate_answer(fact: str, question: str, user_answer: str) -> dict:
    """
    Evaluiert die gegebene Antwort gegen den Fact/Frage unter Verwendung von Structured Outputs.
    
    Regeln:
    1. Antwort korrekt inkl. Rechtschreibung -> 1 Punkt
    2. Antwort prinzipiell richtig, aber grobe Rechtschreibfehler -> 0.5 Punkte
    3. Antwort falsch -> 0 Punkte
    """

    prompt = f"""
    Bewerte folgende Antwort strikt nach Schema. Nutze dabei folgende Regeln:
    Regeln:
    1. Antwort stimmt mit dem Fakt überein inkl. Rechtschreibung -> score=1
    2. Antwort stimmt fast mit dem Fakt überein, aber es gibt grobe Rechtschreibfehler. Kleine typos with ein falscher Buchstabe darf hier toleriert werden -> score=0.5
    3. Antwort stimmt unzureichend oder nicht mit dem Fakt überein -> score=0

    In den Fällen 2. und 3. gib die richtige Antwort im Feedback an. Im Fall 1. gib ein positives Feedback.
    Eine Antwort als Wort oder Term ist korrekt, es muss nicht der ganze Satz aus dem Fact wiedergegeben werden.

        Fakt: {fact}
        Frage: {question}
        Antwort: {user_answer}
    """

    resp = client.chat.completions.create(
        model=os.environ["OPENAI_MODEL"],  # oder dein lokales Modell
        messages=[
            {"role": "system", "content": "Du bist ein Bewertungs-LLM."},
            {"role": "user", "content": prompt}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "answer_evaluation",
                "schema": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number", "enum": [0, 0.5, 1]},
                        "feedback": {"type": "string"},
                    },
                    "required": ["score","feedback"]
                }
            }
        }
    )

    return json.loads(resp.choices[0].message.content)
