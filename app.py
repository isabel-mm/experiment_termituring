import streamlit as st
import json
import random
import pandas as pd

DATA_FILE = "data.json"
MAIN_KEY = "corpus_linguistics_terminology_experiment"

st.set_page_config(page_title="Terminology Evaluation", layout="wide")

# ----------------------------
# FORCE SCROLL TO TOP
# ----------------------------

st.markdown(
    """
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

    st.header("👋 Welcome")

    st.markdown("""
Thank you very much for taking part in this study.

This experiment focuses on the evaluation of specialised definitions in **Corpus Linguistics**.

You will be shown a series of **terms** together with **two alternative definitions** for each term.  
Your task is to assess each definition independently according to several criteria.

### 📝 For each term:
- Read both definitions carefully.
- Evaluate **Definition A** and **Definition B** separately.
- Indicate which definition you would include in a specialised glossary.
- You may optionally add a brief comment.

### 🔎 Evaluation criteria:
**Conceptual adequacy**  
Does the definition correctly capture the concept?

**Completeness**  
Does the definition include the main conceptual properties?

**Terminological precision**  
Is the formulation technically precise and appropriate for a specialised context?

**Clarity**  
Is the definition clearly written and easy to understand?

### 📊 Scoring system:
- **0** = poor
- **1** = acceptable
- **2** = good

The evaluation contains multiple terms and usually takes around **5–10 minutes**.

Thank you again for your participation! 🌿  
Please enter your identifier below to begin. You may include your name or an alias. Don't, worry, it will be properly anonymised.
""")

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
Please send your results to **isabel.moyano@uca.es**  
with the subject line:

**TERMITURING RESULTS**
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

st.write(f"**Annotator:** {annotator}")
st.write(f"**Completed:** {completed} / {total_terms}")
st.write(f"**Remaining:** {remaining}")
st.progress(progress_value)

# ----------------------------
# CURRENT TERM
# ----------------------------

item = terms[current_index]

st.header(f"Term: {item['term']}")
st.caption(f"Item {current_index + 1} of {total_terms}")

# ----------------------------
# FORM
# ----------------------------

with st.form(key=f"evaluation_form_{current_index}"):

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Definition A")
        st.write(item["A"])

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
        st.subheader("Definition B")
        st.write(item["B"])

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

        st.markdown(
            """
**Scale guide**
- **0** = poor / inadequate
- **1** = acceptable / partially adequate
- **2** = good / fully adequate
"""
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
