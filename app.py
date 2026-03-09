import streamlit as st
import json
import random
import pandas as pd
from pathlib import Path

DATA_FILE = "en_termituring_RAG_v2.json"
MAIN_KEY = "corpus_linguistics_terminology_experiment"

st.set_page_config(page_title="Terminology Evaluation", layout="wide")

st.title("Terminological Definition Evaluation")

# ----------------------------
# LOAD DATA
# ----------------------------

@st.cache_data
def load_terms():

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    pairs = []

    for block in data[MAIN_KEY]:
        for item in block["terms"]:

            if item.get("status") == "done":

                ai = item.get("ai_definition","").strip()
                human = item.get("human_definition","").strip()

                if ai and human:

                    pair = [
                        ("A", ai, "AI"),
                        ("B", human, "Human")
                    ]

                    random.shuffle(pair)

                    pairs.append({
                        "term": item["term"],
                        "A": pair[0][1],
                        "B": pair[1][1],
                        "A_origin": pair[0][2],
                        "B_origin": pair[1][2]
                    })

    return pairs


terms = load_terms()

# ----------------------------
# SESSION STATE
# ----------------------------

if "index" not in st.session_state:
    st.session_state.index = 0

if "responses" not in st.session_state:
    st.session_state.responses = []

if "annotator" not in st.session_state:
    st.session_state.annotator = ""


# ----------------------------
# ANNOTATOR ID
# ----------------------------

if st.session_state.annotator == "":
    st.session_state.annotator = st.text_input("Annotator ID")

    st.stop()

annotator = st.session_state.annotator

# ----------------------------
# END CONDITION
# ----------------------------

if st.session_state.index >= len(terms):

    st.success("Evaluation finished!")

    df = pd.DataFrame(st.session_state.responses)

    csv = df.to_csv(index=False)

    st.download_button(
        "Download results CSV",
        csv,
        file_name=f"terminology_eval_{annotator}.csv",
        mime="text/csv"
    )

    st.write(df)

    st.stop()

# ----------------------------
# CURRENT TERM
# ----------------------------

item = terms[st.session_state.index]

st.header(f"Term: {item['term']}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Definition A")
    st.write(item["A"])

with col2:
    st.subheader("Definition B")
    st.write(item["B"])

st.divider()

# ----------------------------
# SCORING
# ----------------------------

st.subheader("Evaluate Definition A")

A_adequacy = st.slider("Conceptual adequacy (A)", 0, 2)
A_completeness = st.slider("Completeness (A)", 0, 2)
A_precision = st.slider("Terminological precision (A)", 0, 2)
A_clarity = st.slider("Clarity (A)", 0, 2)

st.subheader("Evaluate Definition B")

B_adequacy = st.slider("Conceptual adequacy (B)", 0, 2)
B_completeness = st.slider("Completeness (B)", 0, 2)
B_precision = st.slider("Terminological precision (B)", 0, 2)
B_clarity = st.slider("Clarity (B)", 0, 2)

preference = st.radio(
    "Which definition would you prefer in a glossary?",
    ["A", "B", "Equivalent"]
)

comment = st.text_area("Optional comment")

# ----------------------------
# SAVE
# ----------------------------

if st.button("Save & Next"):

    st.session_state.responses.append({

        "annotator": annotator,
        "term": item["term"],

        "A_adequacy": A_adequacy,
        "A_completeness": A_completeness,
        "A_precision": A_precision,
        "A_clarity": A_clarity,

        "B_adequacy": B_adequacy,
        "B_completeness": B_completeness,
        "B_precision": B_precision,
        "B_clarity": B_clarity,

        "preference": preference,
        "comment": comment,

        "A_origin": item["A_origin"],
        "B_origin": item["B_origin"]

    })

    st.session_state.index += 1
    st.rerun()
