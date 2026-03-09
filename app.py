import streamlit as st
import json
import random
import pandas as pd

DATA_FILE = "data.json"
MAIN_KEY = "corpus_linguistics_terminology_experiment"

st.set_page_config(page_title="Terminology Evaluation", layout="wide")

# ----------------------------
# CUSTOM STYLES
# ----------------------------

st.markdown(
    """
    <style>
    :root {
        --purple-main: #7c3aed;
        --purple-soft: #f3e8ff;
        --pink-soft: #fdf2f8;
        --pink-border: #f9a8d4;
        --text-dark: #2d1b3d;
        --muted: #6b7280;
    }

    /* Scroll to top on rerun */
    html {
        scroll-behavior: auto;
    }

    /* General accents */
    .stProgress > div > div > div > div {
        background-color: var(--purple-main);
    }

    /* Buttons */
    .stButton > button, .stDownloadButton > button, div[data-testid="stFormSubmitButton"] button {
        background-color: var(--purple-main);
        color: white;
        border-radius: 0.6rem;
        border: none;
        font-weight: 600;
    }

    .stButton > button:hover, .stDownloadButton > button:hover, div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #6d28d9;
        color: white;
    }

    /* Radio */
    div[role="radiogroup"] label {
        color: var(--text-dark);
        font-weight: 500;
    }

    /* Captions / muted text */
    .custom-muted {
        color: var(--muted);
        font-size: 0.95rem;
    }

    /* Term box */
    .term-box {
        padding: 1rem 1.2rem;
        border: 1px solid #d8b4fe;
        border-radius: 0.9rem;
        background-color: var(--purple-soft);
        margin-bottom: 1rem;
    }

    .term-item {
        color: var(--muted);
        font-size: 0.9rem;
        margin-bottom: 0.2rem;
    }

    .term-title {
        color: var(--text-dark);
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
    }

    /* Definition boxes */
    .def-box {
        padding: 1rem 1rem 0.8rem 1rem;
        border: 1px solid var(--pink-border);
        border-radius: 0.9rem;
        background-color: var(--pink-soft);
        margin-bottom: 0.8rem;
        min-height: 180px;
    }

    .def-title {
        color: var(--text-dark);
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }

    .scale-box {
        padding: 0.8rem 1rem;
        border-left: 4px solid var(--purple-main);
        background-color: #faf5ff;
        border-radius: 0.5rem;
        margin-top: 0.6rem;
        margin-bottom: 0.8rem;
    }

    .welcome-box {
        padding: 1rem 1.2rem;
        border: 1px solid #d8b4fe;
        border-radius: 0.9rem;
        background-color: #faf5ff;
    }
    </style>

    <script>
        window.scrollTo(0, 0);
    </script>
    """,
    unsafe_allow_html=True
)

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
                ai = item.get("ai_definition", "").strip()
                human = item.get("human_definition", "").strip()

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

if not terms:
    st.error("No valid definition pairs were found in the JSON file.")
    st.stop()

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
# WELCOME SCREEN
# ----------------------------

if st.session_state.annotator == "":

    st.header("Welcome!")

    st.markdown(
        """
        <div class="welcome-box">
        Thank you very much for taking part in this study! This experiment focuses on the evaluation of specialised definitions in <b>Corpus Linguistics</b>.<br><br>

        You will be shown a series of <b>terms</b> together with <b>two alternative definitions</b> for each term.
        Your task is to assess each definition independently according to several criteria.<br><br>

        <b>📝 For each term:</b><br>
        - Read both definitions carefully.<br>
        - Evaluate <b>Definition A</b> and <b>Definition B</b> separately.<br>
        - Indicate which definition you would include in a specialised glossary.<br>
        - You may optionally add a brief comment.<br><br>

        <b>🔎 Evaluation criteria:</b><br>
        <b>Conceptual adequacy</b>: Does the definition correctly capture the concept?<br>
        <b>Completeness</b>: Does the definition include the main conceptual properties?<br>
        <b>Terminological precision</b>: Is the formulation technically precise and appropriate for a specialised context?<br>
        <b>Clarity</b>: Is the definition clearly written and easy to understand?<br><br>

        <b>📊 Scoring system:</b><br>
        - <b>0</b> = poor<br>
        - <b>1</b> = acceptable<br>
        - <b>2</b> = good<br><br>

        The evaluation contains multiple terms and usually takes around <b>5–10 minutes</b>.<br><br>

        Thank you again for your participation 🌿<br>
        Please enter your identifier below to begin. You may include your name or an alias. Don't worry, it will be properly anonymised.
        </div>
        """,
        unsafe_allow_html=True
    )

    annotator_input = st.text_input("Annotator ID")

    if st.button("Start evaluation"):
        if annotator_input.strip():
            st.session_state.annotator = annotator_input.strip()
            st.rerun()
        else:
            st.warning("Please enter an Annotator ID.")

    st.stop()

annotator = st.session_state.annotator

# ----------------------------
# END CONDITION
# ----------------------------

total_terms = len(terms)
current_index = st.session_state.index
remaining = total_terms - current_index

if current_index >= total_terms:
    st.success("Evaluation finished!")

    df = pd.DataFrame(st.session_state.responses)
    csv = df.to_csv(index=False)

    st.markdown("## 🎉 Thank you for taking part in this experiment.")

    st.markdown(
        """
Your participation is greatly appreciated.

**Did you know?**  
Some of the definitions you evaluated were automatically generated by a **large language model (LLM)**, while others were written by human experts.

The purpose of this study is to investigate how automatically generated terminological definitions compare to human-written ones in the domain of **Corpus Linguistics**.
"""
    )

    st.markdown(
        """
Please download your results and send them to: **isabel.moyano@uca.es** with the subject line: **TERMITURING RESULTS**
"""
    )

    st.write(f"**Annotator:** {annotator}")
    st.write(f"**Completed items:** {len(df)}")

    st.download_button(
        "Download results CSV",
        csv,
        file_name=f"terminology_eval_{annotator}.csv",
        mime="text/csv"
    )

    st.dataframe(df, use_container_width=True)
    st.stop()

# ----------------------------
# PROGRESS INFO
# ----------------------------

completed = current_index
progress_value = completed / total_terms if total_terms > 0 else 0

progress_col1, progress_col2, progress_col3 = st.columns([1, 1, 2])

with progress_col1:
    st.write(f"**Annotator:** {annotator}")

with progress_col2:
    st.write(f"**Completed:** {completed} / {total_terms}")

with progress_col3:
    st.write(f"**Remaining:** {remaining}")

st.progress(progress_value)

# ----------------------------
# CURRENT TERM
# ----------------------------

item = terms[current_index]

# ----------------------------
# FORM
# ----------------------------

with st.form(key=f"evaluation_form_{current_index}"):

    st.markdown(
        f"""
        <div class="term-box">
            <div class="term-item">Item {current_index + 1} of {total_terms}</div>
            <div class="term-title">Term: {item['term']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="def-box">
                <div class="def-title">Definition A</div>
                <div>{item['A']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("**Evaluate Definition A**")
        st.caption("Use the scale 0–2, where 0 = poor, 1 = acceptable, and 2 = good.")

        A_adequacy = st.slider(
            "To what extent does Definition A correctly capture the concept?",
            0, 2, 1, key=f"A_adequacy_{current_index}"
        )
        A_completeness = st.slider(
            "To what extent does Definition A include the main conceptual properties?",
            0, 2, 1, key=f"A_completeness_{current_index}"
        )
        A_precision = st.slider(
            "How terminologically precise is Definition A for a specialised context?",
            0, 2, 1, key=f"A_precision_{current_index}"
        )
        A_clarity = st.slider(
            "How clear and well formulated is Definition A?",
            0, 2, 1, key=f"A_clarity_{current_index}"
        )

    with col2:
        st.markdown(
            f"""
            <div class="def-box">
                <div class="def-title">Definition B</div>
                <div>{item['B']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("**Evaluate Definition B**")
        st.caption("Use the scale 0–2, where 0 = poor, 1 = acceptable, and 2 = good.")

        B_adequacy = st.slider(
            "To what extent does Definition B correctly capture the concept?",
            0, 2, 1, key=f"B_adequacy_{current_index}"
        )
        B_completeness = st.slider(
            "To what extent does Definition B include the main conceptual properties?",
            0, 2, 1, key=f"B_completeness_{current_index}"
        )
        B_precision = st.slider(
            "How terminologically precise is Definition B for a specialised context?",
            0, 2, 1, key=f"B_precision_{current_index}"
        )
        B_clarity = st.slider(
            "How clear and well formulated is Definition B?",
            0, 2, 1, key=f"B_clarity_{current_index}"
        )

    st.divider()

    preference = st.radio(
        "Which definition would you include in a specialised glossary?",
        ["A", "B"],
        key=f"preference_{current_index}"
    )

    comment = st.text_area("Optional comment", key=f"comment_{current_index}")

    submitted = st.form_submit_button("Save & Next")

# ----------------------------
# SAVE
# ----------------------------

if submitted:
    already_saved_terms = {r["term"] for r in st.session_state.responses}

    if item["term"] not in already_saved_terms:
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
