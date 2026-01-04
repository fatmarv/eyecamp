# app.py
import streamlit as st
import pandas as pd

# -------------------------
# File Upload
# -------------------------
st.title("👁️ Eye Camp Data Explorer")

uploaded_file = st.file_uploader("Upload Eye Camp CSV", type=["csv", "xlsx"])
if uploaded_file:
    # Detect file type
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("File uploaded successfully!")
    st.write("### Raw Data Preview", df.head(5))

    # -------------------------
    # Attendance Summary
    # -------------------------
    st.header("📊 Attendance Summary")
    attendance_summary = df.groupby([df.columns[2], df.columns[1]]).size().unstack(fill_value=0).reset_index()
    attendance_summary["Total"] = attendance_summary.sum(axis=1, numeric_only=True)
    st.dataframe(attendance_summary)

    # -------------------------
    # Agewise Report
    # -------------------------
    st.header("👶 Age Group Report")
    Agewise = df.groupby(['Age group ', 'Gender']).size().reset_index(name='Total')
    pivot_agereport = Agewise.pivot_table(index='Age group ', columns='Gender', values='Total', fill_value=0)
    pivot_agereport["Total"] = pivot_agereport.sum(axis=1, numeric_only=True)
    st.dataframe(pivot_agereport)

    # -------------------------
    # Medicines
    # -------------------------
    st.header("💊 Medicine Usage")
    if "Medicine\nGutt - Drops , occ- ointment, e/d -eyedrops" in df.columns:
        df_medicine = df[["Gender", "Age group ", "Medicine\nGutt - Drops , occ- ointment, e/d -eyedrops"]].copy()
        df_medicine = df_medicine.dropna()
        df_medicine = df_medicine[df_medicine.iloc[:,2].str.strip().str.upper() != "N/A"]
        df_medicine["Medicine_List"] = df_medicine.iloc[:,2].str.split(",")
        df_medicine = df_medicine.explode("Medicine_List")
        df_medicine["Medicine_List"] = df_medicine["Medicine_List"].str.strip()

        medicine_counts = (
            df_medicine.groupby(["Gender", "Age group ", "Medicine_List"])
            .size()
            .reset_index(name="Count")
            .sort_values(by="Count", ascending=False)
        )
        st.dataframe(medicine_counts)

    # -------------------------
    # Glasses Positive
    # -------------------------
    if "Glasses +" in df.columns:
        st.header("👓 Glasses Positive Cases")
        df_positive = df[["Gender", "Age group ", "Glasses +"]].dropna()
        df_positive["Glasses_List"] = df_positive["Glasses +"].str.split(",")
        df_positive = df_positive.explode("Glasses_List")
        glasses_positive_counts = (
            df_positive.groupby(["Gender", "Age group ", "Glasses_List"])
            .size()
            .reset_index(name="Count")
            .sort_values(by="Count", ascending=False)
        )
        st.dataframe(glasses_positive_counts)

    # -------------------------
    # Diagnosis
    # -------------------------
    if "Diagnosis" in df.columns:
        st.header("🩺 Diagnosis Report")
        df_d = df[["Age group ", "Gender", "Diagnosis"]].dropna()
        df_d["Diagnosis List"] = df_d["Diagnosis"].str.split(",")
        df_d_explode = df_d.explode("Diagnosis List")
        df_d_explode["Diagnosis List"] = df_d_explode["Diagnosis List"].str.strip()

        top_10_diagnosis = (
            df_d_explode.groupby(['Age group ', 'Gender', 'Diagnosis List'])
            .size()
            .reset_index(name='Count')
            .sort_values(by='Count', ascending=False)
            .groupby(['Age group ', 'Gender'])
            .head(10)
        )
        st.dataframe(top_10_diagnosis)

