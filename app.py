import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(
    page_title="Panchamahabhuta Self-Assessment",
    page_icon="🕉️",
    layout="wide"
)
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open("responses.xlsx").sheet2
# ---------- HEADER ----------
col1, col2 = st.columns([1, 5])

with col1:
    if os.path.exists("assets/shc_logo.png"):
        st.image("assets/shc_logo.png", width=100)

with col2:
    st.title("Panchamahabhuta Self-Assessment Questionnaire")
    st.write("**An IKS-Based Personality Profiling Tool**")
    st.write("Sacred Heart College (Autonomous), Thevara, Kochi")
    st.write("Department of Management Studies")

st.divider()

# ---------- INTRODUCTION ----------
st.subheader("Welcome")

st.write("""
The Panchamahabhuta framework describes five fundamental elements:
Earth (Prithvi), Water (Jala), Fire (Agni), Air (Vayu), and Space (Akasha).

This assessment helps you understand your personality profile through an
Indian Knowledge Systems (IKS) perspective.
""")

# ---------- STUDENT DETAILS ----------
st.header("Student Information")

assessment_id = f"SHC-IKS-{datetime.now().year}-{datetime.now().strftime('%H%M%S')}"

name = st.text_input("Name")
register_no = st.text_input("Register Number")
programme = st.text_input("Programme")
semester = st.text_input("Semester")
section = st.text_input("Section")

gender = st.selectbox(
    "Gender",
    ["Male", "Female", "Other"]
)

age = st.number_input(
    "Age",
    min_value=15,
    max_value=100,
    value=18
)

email = st.text_input("Email")
mobile = st.text_input("Mobile Number")

st.write("Assessment ID:", assessment_id)

# ---------- QUESTIONS ----------
questions = {
    "Earth (Prithvi)": [
        "I prefer a structured routine.",
        "Others consider me reliable and dependable.",
        "I remain calm during challenging situations.",
        "I complete my responsibilities patiently."
    ],
    "Water (Jala)": [
        "I adapt easily when circumstances change.",
        "I understand and respect others’ feelings.",
        "I enjoy helping people.",
        "I work well with different kinds of people."
    ],
    "Fire (Agni)": [
        "I enjoy taking initiative.",
        "I am motivated to achieve my goals.",
        "I enjoy challenges and competition.",
        "I stay focused until a task is completed."
    ],
    "Air (Vayu)": [
        "I enjoy learning new things.",
        "I often generate creative ideas.",
        "I like exploring different possibilities.",
        "I express my thoughts confidently."
    ],
    "Space (Akasha)": [
        "I enjoy spending time in reflection.",
        "I listen attentively when others speak.",
        "I think deeply about experiences and ideas.",
        "I feel connected to nature and my surroundings."
    ]
}

st.header("Assessment")

responses = {}
scores = {}
q_no = 1

for element, items in questions.items():

    st.subheader(element)

    total = 0

    for item in items:

        response = st.radio(
            f"{q_no}. {item}",
            [1, 2, 3, 4, 5],
            horizontal=True,
            key=f"q{q_no}"
        )

        responses[f"Q{q_no}"] = response
        total += response
        q_no += 1

    scores[element] = total

# ---------- SUBMIT ----------
if st.button("Generate My Profile"):

    dominant = max(scores, key=scores.get)

    sorted_scores = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    secondary = sorted_scores[1][0]

    personality_map = {
        "Earth (Prithvi)": "The Stabilizer",
        "Water (Jala)": "The Harmonizer",
        "Fire (Agni)": "The Achiever",
        "Air (Vayu)": "The Innovator",
        "Space (Akasha)": "The Sage"
    }

    personality = personality_map[dominant]

    st.success(f"Dominant Element: {dominant}")
    st.info(f"Personality Type: {personality}")

    # Scores Table
    score_df = pd.DataFrame({
        "Element": list(scores.keys()),
        "Score": list(scores.values())
    })

    st.dataframe(score_df)

    # Radar Chart
    categories = list(scores.keys())
    values = list(scores.values())

    categories += [categories[0]]
    values += [values[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself'
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0,20]
            )
        ),
        showlegend=False
    )

    st.plotly_chart(fig)

    # Save Data
    record = {
        "Assessment_ID": assessment_id,
        "Name": name,
        "Register_No": register_no,
        "Programme": programme,
        "Semester": semester,
        "Section": section,
        "Gender": gender,
        "Age": age,
        "Email": email,
        "Mobile": mobile,
        "Dominant_Element": dominant,
        "Secondary_Element": secondary,
        "Personality_Type": personality
    }
    record.update(scores)

    df = pd.DataFrame([record])

    sheet.append_row([
        assessment_id,
        name,
        register_no,
        programme,
        semester,
        section,
        gender,
        age,
        email,
        mobile,
        scores["Earth (Prithvi)"],
        scores["Water (Jala)"],
        scores["Fire (Agni)"],
        scores["Air (Vayu)"],
        scores["Space (Akasha)"],
        dominant,
        secondary,
        personality,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

    st.success("Response Saved Successfully!")
