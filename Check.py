
import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------
# Setup
# --------------------------
st.set_page_config(page_title="Internal Audit QA Tool", layout="wide")

DATA_FILE = "audit_qa_data.csv"

# Load existing data
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Audit_ID", "Auditor", "Reviewer",
            "Completeness", "Documentation", "Compliance",
            "Overall_Score", "Findings", "Date"
        ])

# Save data
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# --------------------------
# Sidebar Navigation
# --------------------------
menu = st.sidebar.radio("Navigation", ["New QA Review", "Dashboard", "Records"])

st.title("🛡️ Internal Audit Quality Assurance Tool")

# --------------------------
# 1. New QA Review
# --------------------------
if menu == "New QA Review":

    st.header("📋 Audit QA Review Form")

    with st.form("qa_form"):
        col1, col2 = st.columns(2)

        with col1:
            audit_id = st.text_input("Audit ID")
            auditor = st.text_input("Auditor Name")

        with col2:
            reviewer = st.text_input("Reviewer Name")
            review_date = datetime.today().strftime('%Y-%m-%d')

        st.subheader("✅ Quality Checklist (Score 1-5)")

        completeness = st.slider("Completeness of Workpapers", 1, 5, 3)
        documentation = st.slider("Documentation Quality", 1, 5, 3)
        compliance = st.slider("Compliance with Standards", 1, 5, 3)

        findings = st.text_area("Key Findings / Observations")

        submitted = st.form_submit_button("Submit Review")

        if submitted:
            overall_score = round((completeness + documentation + compliance) / 3, 2)

            new_record = pd.DataFrame([{
                "Audit_ID": audit_id,
                "Auditor": auditor,
                "Reviewer": reviewer,
                "Completeness": completeness,
                "Documentation": documentation,
                "Compliance": compliance,
                "Overall_Score": overall_score,
                "Findings": findings,
                "Date": review_date
            }])

            df = pd.concat([df, new_record], ignore_index=True)
            save_data(df)

            st.success(f"✅ Review submitted! Overall Score: {overall_score}")

# --------------------------
# 2. Dashboard
# --------------------------
elif menu == "Dashboard":

    st.header("📊 QA Dashboard")

    if df.empty:
        st.warning("No data available")
    else:
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Reviews", len(df))
        col2.metric("Average Score", round(df["Overall_Score"].mean(), 2))
        col3.metric("Low Quality Reviews (<3)",
                    len(df[df["Overall_Score"] < 3]))

        st.subheader("📈 Trend of Scores")
        df["Date"] = pd.to_datetime(df["Date"])
        trend = df.groupby("Date")["Overall_Score"].mean()

        st.line_chart(trend)

        st.subheader("📊 Score Distribution")
        st.bar_chart(df["Overall_Score"])

# --------------------------
# 3. Records View
# --------------------------
elif menu == "Records":

    st.header("📁 QA Review Records")

    if df.empty:
        st.warning("No records available")
    else:
        search = st.text_input("Search by Audit ID / Auditor")

        filtered_df = df[
            df["Audit_ID"].str.contains(search, case=False, na=False) |
            df["Auditor"].str.contains(search, case=False, na=False)
        ]

        st.dataframe(filtered_df, use_container_width=True)

        st.download_button(
            "⬇️ Download Data",
            filtered_df.to_csv(index=False),
            "audit_qa_records.csv",
            "text/csv"
        )
