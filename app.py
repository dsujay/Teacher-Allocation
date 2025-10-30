import streamlit as st
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def allocate(df, faculty_cols):
    """
    Performs the student allocation based on CGPA and preferences.
    
    Args:
        df (pd.DataFrame): The complete DataFrame with student info and preferences.
        faculty_cols (list): The list of faculty column names to consider for allocation.
    """
    try:
        df_sorted = df.sort_values(by='CGPA', ascending=False)
        logging.info("Sorted students by CGPA in descending order.")

        n_faculty = len(faculty_cols)
        if n_faculty == 0:
            st.error("No faculty columns selected. Please check your input.")
            return None
            
        logging.info(f"Considering {n_faculty} faculty members for allocation.")

        allocation = {}
        allocated_students = set()
        faculty_counts = {fac: 0 for fac in faculty_cols}
        
        # Determine the base number of students per faculty
        students_per_faculty = len(df_sorted) // n_faculty
        # Determine how many faculties will get one extra student
        extra_students = len(df_sorted) % n_faculty

        faculty_max_load = {fac: students_per_faculty for fac in faculty_cols}
        
        # Distribute the extra students to the first 'extra_students' faculties
        # (This is just one way to do it; could be randomized or based on fac pref)
        # For simplicity, we just assign them. The round-robin will fill them.
        fac_index = 0
        for _ in range(extra_students):
            faculty_max_load[faculty_cols[fac_index]] += 1
            fac_index = (fac_index + 1) % n_faculty

        logging.info(f"Calculated faculty load: Base={students_per_faculty}, Extra={extra_students}")

        # First pass allocation: Iterate by preference number
        # We iterate from preference 1 up to the number of faculties
        for pref_num in range(1, n_faculty + 1):
            for _, student_row in df_sorted.iterrows():
                student_roll = student_row['Roll']
                
                # If student is already allocated, skip
                if student_roll in allocated_students:
                    continue

                # Get the student's preferences for the *considered* faculties
                student_prefs = student_row[faculty_cols]
                
                # Find which faculty (if any) this student ranked with the current pref_num
                preferred_fac_series = student_prefs[student_prefs == pref_num]
                
                if not preferred_fac_series.empty:
                    # Student did rank a faculty with this preference number
                    preferred_fac = preferred_fac_series.index[0]

                    # Check if that faculty is full
                    if faculty_counts.get(preferred_fac, 0) < faculty_max_load[preferred_fac]:
                        # Allocate student
                        allocation[student_roll] = {
                            'Name': student_row['Name'],
                            'Email': student_row['Email'],
                            'CGPA': student_row['CGPA'],
                            'Allocated': preferred_fac
                        }
                        allocated_students.add(student_roll)
                        faculty_counts[preferred_fac] += 1
        
        # Second pass: Allocate any remaining students (who didn't get any choice)
        # These students are allocated via simple round-robin to the least loaded faculties.
        remaining_students_df = df_sorted[~df_sorted['Roll'].isin(allocated_students)]
        
        if not remaining_students_df.empty:
            logging.warning(f"Allocating {len(remaining_students_df)} students who did not get any of their preferences.")
            for _, student_row in remaining_students_df.iterrows():
                student_roll = student_row['Roll']
                
                # Find the faculty with the minimum current count
                min_load_fac = min(faculty_counts, key=faculty_counts.get)
                
                # Allocate to this faculty
                allocation[student_roll] = {
                    'Name': student_row['Name'],
                    'Email': student_row['Email'],
                    'CGPA': student_row['CGPA'],
                    'Allocated': min_load_fac
                }
                allocated_students.add(student_roll)
                faculty_counts[min_load_fac] += 1

        df_allocation = pd.DataFrame.from_dict(allocation, orient='index')
        df_allocation.index.name = 'Roll'
        df_allocation.reset_index(inplace=True)
        logging.info("Created the allocation DataFrame.")
        return df_allocation

    except KeyError as e:
        logging.error(f"A required column is missing: {e}. Check your input file format.")
        st.error(f"A required column is missing: {e}. Please ensure your file has 'Roll', 'Name', 'Email', and 'CGPA' columns.")
        return None
    except Exception as e:
        logging.error(f"An error occurred during allocation: {e}")
        st.error(f"An error occurred during allocation: {e}")
        return None

def generate_faculty_preference_stats(df, faculty_cols):
    """
    Generates statistics on faculty preferences.
    
    Args:
        df (pd.DataFrame): The complete DataFrame with student info and preferences.
        faculty_cols (list): The list of faculty column names to consider for stats.
    """
    try:
        n_faculty = len(faculty_cols)
        if n_faculty == 0:
            st.error("No faculty columns selected for stats.")
            return None
            
        # Create a dictionary to hold counts. The number of preferences to count
        # is equal to the number of faculties being considered.
        pref_counts = {f'Count Pref {i}': {fac: 0 for fac in faculty_cols} for i in range(1, n_faculty + 1)}

        for fac in faculty_cols:
            # Check if faculty column exists in df
            if fac not in df.columns:
                logging.warning(f"Faculty column {fac} not found in DataFrame. Skipping.")
                continue
                
            for pref_num in range(1, n_faculty + 1):
                # Count how many times this faculty (fac) was ranked as this pref_num
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


# =============================================================================
# Streamlit App
# =============================================================================
st.title('BTP/MTP Allocation System')

uploaded_file = st.file_uploader("Upload your input CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")

        st.subheader("Input Data")
        st.dataframe(df.head())

        # --- New UI elements ---
        st.markdown("---")
        st.subheader("Faculty Selection")
        
        auto_detect = st.checkbox(
            "Auto-detect all faculties (default)", 
            value=True,
            help="This will use all columns after 'CGPA' as faculty columns."
        )
        
        num_faculties = st.number_input(
            "Or, specify number of faculties to consider:", 
            min_value=1, 
            value=18, 
            disabled=auto_detect,
            help="This will select the first N columns after 'CGPA'."
        )
        st.markdown("---")
        # --- End of new UI elements ---


        if st.button('Run Allocation'):
            # Determine which faculty columns to use based on user input
            try:
                base_df_cols = ['Roll', 'Name', 'Email', 'CGPA']
                # Find the index of the CGPA column
                cgpa_index = df.columns.get_loc('CGPA')
                all_faculty_cols = df.columns[cgpa_index + 1:]
                
                if not all_faculty_cols.any():
                     st.error("Could not find 'CGPA' column or any faculty columns after it. Please check your file.")
                     raise ValueError("No faculty columns found after 'CGPA'.")

                faculty_cols_to_use = []
                
                if auto_detect:
                    faculty_cols_to_use = list(all_faculty_cols)
                    st.info(f"Auto-detected {len(faculty_cols_to_use)} faculties.")
                else:
                    if num_faculties > len(all_faculty_cols):
                        st.warning(f"You requested {num_faculties} faculties, but only {len(all_faculty_cols)} were found. Using all {len(all_faculty_cols)}.")
                        faculty_cols_to_use = list(all_faculty_cols)
                    else:
                        faculty_cols_to_use = list(all_faculty_cols[:num_faculties])
                        st.info(f"Using the first {num_faculties} faculties: {', '.join(faculty_cols_to_use)}")
                
                # Run the allocation and stats generation
                df_allocation = allocate(df.copy(), faculty_cols_to_use)
                df_fac_pref = generate_faculty_preference_stats(df.copy(), faculty_cols_to_use)

                # Display results if successful
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
            
            except ValueError as e:
                # This catches the "No faculty columns found" error
                logging.error(f"Configuration error: {e}")
            except Exception as e:
                st.error(f"An error occurred during the main process: {e}")
                logging.error(f"An error occurred in the Streamlit app's main block: {e}")

    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        logging.error(f"An error occurred while reading the file: {e}")