#import libraries
import streamlit as st
import pandas as pd


st.title("👁️ Eye Camp Data Explorer")
st.caption("Upload CSV / Excel or use Google Sheet URL")

uploaded_file = st.file_uploader("Upload Eye Camp File URL", type=["csv", "xlsx"])

sheet_url = st.text_input("Or enter Google Sheet CSV URL", "")

df = None

# -------------------------
# File Upload and Reading
# -------------------------
if uploaded_file is not None:
    # read uploaded file
    try:
        uploaded_file.seek(0) # Ensure we're at the start of the file

        if uploaded_file.name.lower().endswith(".csv"):
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            except:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="utf-16", sep=";")

        else:
            df = pd.read_excel(uploaded_file)

        if df is None or df.empty or df.shape[1] == 1:
            st.error("❌ CSV loaded but columns could not be parsed.")
            st.stop()

        st.success("✅ File loaded successfully")
        # st.write("Detected columns:", list(df.columns))

    except Exception as e:
        st.error(f"❌ Failed to read file: {e}")
        st.stop()


elif sheet_url:
    #reding google sheet url
    df = pd.read_csv(sheet_url)


# -------------------------
# Merging Male and Female columns
# -------------------------
def clean_data(df):
    mask = df.iloc[:, 1] == "Female"  # Column B is index 1
    # Move L–T (index 11–19) into C–K (index 2–10) for Female
    df.loc[mask, df.columns[2:11]] = df.loc[mask, df.columns[11:20]].values
    # Clear original L–T columns for Female
    df.loc[mask, df.columns[11:20]] = ""
    # Keep only first 11 columns (cleaned)
    df = df.iloc[:, :11]
    return df


# -------------------------
# Field to but csv url
# -------------------------


if uploaded_file or sheet_url:
   
    if df is not None:
        clean_df = clean_data(df)
        st.write("Data Cleaned ")
        df = clean_df
    else:
        st.error("❌ No data loaded.")
        st.stop()


    # -------------------------
    # Attendance Summary

    st.header("📊 Attendance Summary")
    # Column D = Date (index 3), Column B = Gender (index 1)

    attendance_summary = df.groupby([df.columns[3], df.columns[1]]).size().unstack(fill_value=0).reset_index() 
    attendance_summary["Total"] = attendance_summary.sum(axis=1, numeric_only=True)

    # Calculate grand total
    grand_total = attendance_summary.sum(numeric_only=True)
    grand_total[df.columns[3]] = "Grand Total"

    # Append grand total row to the summary
    attendance_summary = pd.concat(
        [attendance_summary, pd.DataFrame([grand_total])],
        ignore_index=True
    )
    attendance_summary.index = range(1, len(attendance_summary) + 1)

    st.dataframe(attendance_summary)

    #-------------------------
    # Agewise Report
    #-------------------------
    st.header ("Agewise Report")
    Agewise = df.groupby(['M_AgeGroup ', 'Gender']).size().reset_index(name='Total')

    # Create a pivot table to display the data in a more readable format
    pivot_agereport = Agewise.pivot_table(index='M_AgeGroup ', columns='Gender', values='Total', fill_value=0)
    #total age wise
    pivot_agereport["Total"] =pivot_agereport.sum(axis=1,numeric_only= True)

    # Add a 'Grand Total' row at the end
    pivot_agereport.loc['Grand Total'] = pivot_agereport.sum(numeric_only=True)

    st.dataframe(pivot_agereport)
    # -------------------------
    # Diagnosis Report 
    # -------------------------

    st.header("Diagnosis Report")
    df_d= df[["M_AgeGroup ", "Gender", "M_Diagnosis"]].copy()
    # Drop rows where Diagnosis is NA
    df_d = df_d.dropna(subset=["M_Diagnosis"])

    df_d["Diagnosis List"] = df_d["M_Diagnosis"].str.split(",")
    #top 10 diagnosis, in each age group, group by gender
    df_d_explode = df_d.explode("Diagnosis List")
    top_10_diagnosis = df_d_explode.groupby(['M_AgeGroup ', 'Gender', 'Diagnosis List']).size().reset_index(name='Count')
    top_10_diagnosis = top_10_diagnosis.sort_values(by='Count', ascending=False).groupby(['M_AgeGroup ', 'Gender']).head(30)
    # Pivot the top_10_diagnosis table
    pivot_top10_diagnosis_gender = top_10_diagnosis.pivot_table(
        index="Diagnosis List",           # Rows are age groups
        columns=["M_AgeGroup ", "Gender"],  # Multi-level columns: Diagnosis and then Gender
        values="Count",              # The values in the table are the counts
        fill_value=0                 # Replace any missing values with 0
    )

    # 2️⃣ Add TOTAL column (after all age groups)
    pivot_top10_diagnosis_gender[('All Age Groups', 'Total')] = (
        pivot_top10_diagnosis_gender.sum(axis=1)
    )


    # Display the pivoted table
    st.dataframe(pivot_top10_diagnosis_gender)

    # -------------------------
    # Medicine Report
    # -------------------------
    st.header("Medicine Report")
    df_medicine = df[["Gender", "M_AgeGroup ", "M_Medicine \nGutt -Drops,occ- ointment,e/d -eyedrops"]].copy()
    df_medicine = df_medicine.dropna(subset=["M_Medicine \nGutt -Drops,occ- ointment,e/d -eyedrops"])
    df_medicine = df_medicine[df_medicine["M_Medicine \nGutt -Drops,occ- ointment,e/d -eyedrops"].str.strip().str.upper() != "N/A"]
    df_medicine["Medicine_List"] = df_medicine["M_Medicine \nGutt -Drops,occ- ointment,e/d -eyedrops"].str.split(",")
    df_medicine = df_medicine.explode("Medicine_List")
    # Clean medicine names
    df_medicine["Medicine_List"] = df_medicine["Medicine_List"].str.strip()

    medicine_counts = (
    #df_medicine.groupby(["Gender", "Age group ", "Medicine_List"])
    df_medicine.groupby(["Gender", "Medicine_List"])
    .size()
    .reset_index(name="Count")
    .sort_values(by="Count", ascending=False))
    
    pivot_df = medicine_counts.pivot_table(
   # index="Age group ",
    index="Medicine_List",
    #columns=["Medicine_List", "Gender"],
    columns=["Gender"],
    values="Count",
    aggfunc="sum",      # Ensures both male+female counts are summed for the same age group
    fill_value=0)

    st.dataframe(pivot_df)

else:
    st.info("Please upload a file  to proceed.")
    st.stop()