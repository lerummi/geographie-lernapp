import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from io import BytesIO

from europas_rekorde import records
from openai_tools import fact_to_question, evaluate_answer, hint_to_answer

# ---- Session-State initialisieren ----
state = st.session_state
state.auth_status = state.get("auth_status", None)

if not state.get("authentication_status", False):
    st.error("Gib bitte deine Zugangsdaten ein!")
else:
    st.set_page_config(page_title="Interaktive Europakarte", layout="wide")
    st.title("🌍 Europas Rekorde")

    def get_points():
        points = pd.read_csv("data/Europas_Rekorde/punkte_europa.csv", delimiter=";", index_col=0)
        points = points.join(records, how="left")
        state.points = points

    # Session-State für den aktuellen Punkt
    if "current_sample" not in st.session_state:
        st.session_state.current_sample = None

    def load_next_sample():
        if not state.points.empty:
            sample_row = state.points.sample(n=1)
            st.session_state.current_sample = sample_row.iloc[0].to_dict()
            # sample_row aus points entfernen
            state.points.drop(index=sample_row.index, inplace=True)
            st.session_state.question = fact_to_question(st.session_state.current_sample["fact"])
        else:
            st.session_state.current_sample = -1

    # ---- Button zum Starten ----
    if st.button("Neues Spiel starten") or st.session_state.current_sample is None:
        get_points()
        state.total_points = 0
        state.total_samples = 0
        state.user_answer = ""
        st.session_state.submitted_facts = []
        load_next_sample()

    left_col, right_col = st.columns(2)

    # ---- Aktuellen Punkt anzeigen ----
    if st.session_state.current_sample:
        sample = st.session_state.current_sample

        with left_col:
            # Karte vorbereiten
            m = folium.Map(
                location=[sample["lat"], sample["lon"]], 
                zoom_start=4,
                tiles="CartoDB positron"
            )
            folium.Marker(
                location=[sample["lat"], sample["lon"]],
                tooltip=f"Lat={sample['lat']:.4f}, Lon={sample['lon']:.4f}",
                icon=folium.DivIcon(html=f"""
                    <div style="font-size: 14px; font-weight: bold; color: red;">
                        x
                    </div>
                """)
            ).add_to(m)

            st_folium(m, width=600, height=600)

        with right_col:

            st.info(f"Bisherige Gesamtpunkte: {st.session_state.get('total_points', 0)}, Bisherige Fragen: {st.session_state.get('total_samples', 0)}")

            # Fact anzeigen
            st.subheader("Frage")
            st.text(state.question)

            def clear_text():
                st.session_state["user_answer"] = ""  # Setzt das Feld im Callback zurück

            # Antwortfeld und Button
            answer = st.text_input("Deine Antwort:", key="user_answer")

            if st.button("Abschicken"):
                # Bewertung der Antwort
                evaluation = evaluate_answer(
                    fact=sample["fact"],
                    question=state.question,
                    user_answer=answer
                )

                # Feedback anzeigen
                if evaluation["score"] == 1:
                    st.balloons()
                    st.success(f"{evaluation['feedback']} | Punkte: {evaluation['score']}")
                elif evaluation["score"] == 0.5:
                    st.warning(f"{evaluation['feedback']} | Punkte: {evaluation['score']}")
                else:
                    st.error(f"{evaluation['feedback']} | Punkte: {evaluation['score']}")


                st.session_state.submitted_facts.append({
                    "question": state.question,
                    "user_answer": answer,
                    "fact": sample["fact"],
                    "feedback": evaluation["feedback"],
                    "points": evaluation["score"]
                })
                st.session_state.total_points += evaluation["score"]
                st.session_state.total_samples += 1

            if st.button("Tipp geben"):
                hint = hint_to_answer(sample["fact"], state.question)
                st.warning(hint)

            if st.button("Nächste Frage", on_click=clear_text):
                load_next_sample()
                st.rerun()

    else:
        st.success("Du hast alle Fragen beantwortet! Super gemacht! 🎉")
        st.info(f"Gesamtpunkte: {st.session_state.get('total_points', 0)}, Fragen: {st.session_state.get('total_samples', 0)}")

