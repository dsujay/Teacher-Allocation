import streamlit as st
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def allocate(df):
    """
    Performs the student allocation based on CGPA and preferences.
    """
    try:
        df_sorted = df.sort_values(by='CGPA', ascending=False)
        logging.info("Sorted students by CGPA in descending order.")

        faculty_cols = df.columns[4:]
        n_faculty = len(faculty_cols)
        logging.info(f"Dynamically identified {n_faculty} faculty members.")

        allocation = {}
        allocated_students = set()
        faculty_counts = {fac: 0 for fac in faculty_cols}
        
        # Determine the number of students per faculty
        students_per_faculty = len(df_sorted) // n_faculty
        extra_students = len(df_sorted) % n_faculty

        # First pass allocation based on preferences
        for pref_num in range(1, n_faculty + 2): # Iterate through all preferences
            for _, student_row in df_sorted.iterrows():
                student_roll = student_row['Roll']
                if student_roll not in allocated_students:
                    student_prefs = student_row[faculty_cols]
                    
                    # Find faculty for the current preference number
                    preferred_fac_series = student_prefs[student_prefs == pref_num]
                    if not preferred_fac_series.empty:
                        preferred_fac = preferred_fac_series.index[0]

                        # Check faculty load
                        max_load = students_per_faculty + (1 if extra_students > 0 else 0)
                        if faculty_counts.get(preferred_fac, 0) < max_load:
                            allocation[student_roll] = {
                                'Name': student_row['Name'],
                                'Email': student_row['Email'],
                                'CGPA': student_row['CGPA'],
                                'Allocated': preferred_fac
                            }
                            allocated_students.add(student_roll)
                            faculty_counts[preferred_fac] = faculty_counts.get(preferred_fac, 0) + 1
                            if faculty_counts[preferred_fac] == max_load:
                                extra_students = max(0, extra_students -1)
        
        # Allocate any remaining students using round-robin to least loaded faculty
        remaining_students = df_sorted[~df_sorted['Roll'].isin(allocated_students)]
        for _, student_row in remaining_students.iterrows():
            student_roll = student_row['Roll']
            min_load_fac = min(faculty_counts, key=faculty_counts.get)
            allocation[student_roll] = {
                'Name': student_row['Name'],
                'Email': student_row['Email'],
                'CGPA': student_row['CGPA'],
                'Allocated': min_load_fac
            }
            faculty_counts[min_load_fac] += 1

        df_allocation = pd.DataFrame.from_dict(allocation, orient='index')
        df_allocation.index.name = 'Roll'
        df_allocation.reset_index(inplace=True)
        logging.info("Created the allocation DataFrame.")
        return df_allocation

    except Exception as e:
        logging.error(f"An error occurred during allocation: {e}")
        st.error(f"An error occurred during allocation: {e}")
        return None

def generate_faculty_preference_stats(df):
    """
    Generates statistics on faculty preferences.
    """
    try:
        faculty_cols = df.columns[4:]
        pref_counts = {f'Count Pref {i}': {fac: 0 for fac in faculty_cols} for i in range(1, 19)}

        for fac in faculty_cols:
            for pref_num in range(1, 19):
                count = (df[fac] == pref_num).sum()
                pref_counts[f'Count Pref {pref_num}'][fac] = count

        df_fac_pref = pd.DataFrame(pref_counts)
        df_fac_pref.index.name = 'Fac'
        df_fac_pref.reset_index(inplace=True)
        logging.info("Created the faculty preference statistics DataFrame.")
        return df_fac_pref
        
    except Exception as e:
        logging.error(f"An error occurred during preference stats generation: {e}")
        st.error(f"An error occurred during preference stats generation: {e}")
        return None


# Streamlit App
st.title('BTP/MTP Allocation System')

uploaded_file = st.file_uploader("Upload your input CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")

        st.subheader("Input Data")
        st.dataframe(df)

        if st.button('Run Allocation'):
            df_allocation = allocate(df.copy())
            df_fac_pref = generate_faculty_preference_stats(df.copy())

            if df_allocation is not None and df_fac_pref is not None:
                st.subheader("Allocation Results")
                st.dataframe(df_allocation)
                st.download_button(
                    label="Download Allocation CSV",
                    data=df_allocation.to_csv(index=False).encode('utf-8'),
                    file_name='output_btp_mtp_allocation.csv',
                    mime='text/csv',
                )

                st.subheader("Faculty Preference Statistics")
                st.dataframe(df_fac_pref)
                st.download_button(
                    label="Download Faculty Preference CSV",
                    data=df_fac_pref.to_csv(index=False).encode('utf-8'),
                    file_name='fac_preference_count.csv',
                    mime='text/csv',
                )

    except Exception as e:
        st.error(f"An error occurred: {e}")
        logging.error(f"An error occurred in the Streamlit app: {e}")