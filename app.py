from pathlib import Path

import streamlit as st

from reviewer.core import review_diff

ROOT = Path(__file__).resolve().parent
SAMPLE_DIR = ROOT / "data" / "sample_diffs"
SEVERITY_ICON = {"critical": "🔴", "major": "🟠", "minor": "🟡", "nit": "⚪"}

st.set_page_config(page_title="PR Review Assistant", layout="wide")
st.title("AI PR Review Assistant")

if "run_id" not in st.session_state:
    st.session_state["run_id"] = 0
    st.session_state["result"] = None



samples = sorted(p.name for p in SAMPLE_DIR.glob("*.diff"))
choice = st.selectbox("Load a sample PR diff (or choose none and paste your own)", ["-- none --"] + samples)

default_text = ""
if choice != "-- none --":
    default_text = (SAMPLE_DIR / choice).read_text(encoding="utf-8")

diff_text = st.text_area("PR diff", value=default_text, height=300, key=f"diff_{choice}")

if st.button("Review PR", type="primary", disabled=not diff_text.strip()):
    with st.spinner("Reviewing the pull request..."):
        try:
            st.session_state["result"] = review_diff(diff_text)
            st.session_state["run_id"] += 1
        except Exception as error:
            st.session_state["result"] = None
            st.error(f"Review failed: {error}")




result = st.session_state["result"]
if result:
    st.subheader("Summary")
    st.write(result.summary)

    st.subheader("Rubric scores")
    cols = st.columns(4)
    scores = result.scores
    for col, (label, value) in zip(
        cols,
        [
            ("Correctness", scores.correctness),
            ("Tests", scores.tests),
            ("Security", scores.security),
            ("Readability", scores.readability),
        ],
    ):
        col.metric(label, f"{value}/5")

    st.subheader(f"Issues found: {len(result.issues)}")
    if not result.issues:
        st.success("No issues found.")
    for issue in result.issues:
        location = f"{issue.file}:{issue.line}" if issue.line else issue.file
        title = f"{SEVERITY_ICON[issue.severity]} [{issue.severity}] {issue.title} ({location})"
        with st.expander(title, expanded=issue.severity in ("critical", "major")):
            st.markdown(f"**Category:** {issue.category}")
            st.markdown(f"**Why it matters:** {issue.explanation}")
            st.markdown(f"**Suggested fix:** {issue.suggested_fix}")

    st.subheader("mentor comment")
    st.text_area(
        "Edit before sending to the student",
        value=result.mentor_comment,
        height=150,
        key=f"comment_{st.session_state['run_id']}",
    )
