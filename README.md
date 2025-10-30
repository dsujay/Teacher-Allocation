# 🎓 BTP/MTP Allocation System

A **Streamlit-based intelligent allocation system** that automates the distribution of students to faculty members for BTP/MTP (Bachelor/Master Thesis Projects) based on **CGPA**, **faculty preferences**, and optional **faculty override files**.

---

## 🧩 Features

✅ Sorts students dynamically by **CGPA (Descending)** — higher CGPA gets priority.
✅ Distributes students evenly among faculties while respecting **preference rankings**.
✅ Supports **faculty preference overrides** — where faculty choices can take precedence.
✅ Automatically calculates **load balance** so no faculty is overloaded.
✅ Generates detailed reports for:

* Student Allocations
* Faculty Preference Statistics
  ✅ Built with **Streamlit** for a clean, interactive interface.

---

## 🧠 Allocation Logic

### Step-by-Step Overview

1. **Input Upload**

   * Upload a CSV file containing student data:

     ```
     Roll, Name, Email, CGPA, Faculty_1, Faculty_2, Faculty_3, ...
     ```

     Each faculty column should contain numeric values representing **preference order** (1 = highest preference).

2. **Sorting**

   * Students are sorted in **descending order of CGPA**.

3. **Faculty Identification**

   * Faculties are automatically detected from all columns after the 4th one.

4. **Load Balancing**

   * The number of students per faculty is computed as:

     ```
     students_per_faculty = total_students // total_faculties
     extra_students = total_students % total_faculties
     ```

     Extra students are distributed to the first few faculties.

5. **Preference-Based Allocation**

   * For each student (in sorted order), the system checks their 1st, 2nd, … preference.
   * If the preferred faculty still has capacity, the student is allocated there.

6. **Faculty Preference Override**

   * If a **faculty preference override file** is uploaded, the system respects that.
     Example:

     ```
     Faculty, Roll
     Prof_A, S101
     Prof_B, S104
     ```

     These pairs are locked-in allocations that override CGPA-based logic.

7. **Fallback Allocation**

   * Remaining students are allocated in a **round-robin** manner to the least-loaded faculties.

8. **Output**

   * The system generates:

     * `output_btp_mtp_allocation.csv`
     * `fac_preference_count.csv`

---

## 📂 Input File Format

### 🎓 Student File

| Roll | Name | Email | CGPA | Faculty_1 | Faculty_2 | Faculty_3 | ... |
|------|------|--------|------|------------|------------|------------|
| S101 | Alice | [alice@abc.com](mailto:alice@abc.com) | 9.1 | 1 | 2 | 3 |
| S102 | Bob | [bob@abc.com](mailto:bob@abc.com) | 8.9 | 2 | 1 | 3 |
| ... | ... | ... | ... | ... | ... | ... |

### 👩‍🏫 Faculty Override File (Optional)

| Faculty   | Roll |
| --------- | ---- |
| Faculty_1 | S101 |
| Faculty_3 | S107 |

---

## 🚀 How to Run

### 1️⃣ Install Dependencies

```bash
pip install streamlit pandas
```

### 2️⃣ Run the App

```bash
streamlit run app.py
```

### 3️⃣ Upload Files

* **Step 1:** Upload your **student CSV file**
* **Step 2 (Optional):** Upload the **faculty override file**
* **Step 3:** Click **Run Allocation**

---

## 🗂️ Output Files

| File                            | Description                               |
| ------------------------------- | ----------------------------------------- |
| `output_btp_mtp_allocation.csv` | Final allocation of students to faculties |
| `fac_preference_count.csv`      | Preference distribution statistics        |

---

## 🧾 Example Output

### Allocation Table

| Roll | Name  | Email                                 | CGPA | Allocated |
| ---- | ----- | ------------------------------------- | ---- | --------- |
| S101 | Alice | [alice@abc.com](mailto:alice@abc.com) | 9.1  | Faculty_1 |
| S102 | Bob   | [bob@abc.com](mailto:bob@abc.com)     | 8.9  | Faculty_2 |

### Faculty Preference Summary

| Fac       | Count Pref 1 | Count Pref 2 | Count Pref 3 |
| --------- | ------------ | ------------ | ------------ |
| Faculty_1 | 10           | 5            | 3            |
| Faculty_2 | 8            | 7            | 2            |

---

## 🧑‍💻 File Structure

```
btp_mtp_allocation/
│
├── app.py                        # Main Streamlit app
├── README.md                     # Documentation
├── sample_students.csv            # Example input
├── sample_faculty_override.csv    # Example faculty preference input
└── outputs/
    ├── output_btp_mtp_allocation.csv
    └── fac_preference_count.csv
```

---

## 🧮 Tech Stack

* **Python 3.8+**
* **Streamlit** for frontend
* **Pandas** for data processing
* **Logging** for debug and traceability

---

## 🧩 Future Enhancements

* Faculty dashboard for manual adjustments
* Email notification to students after allocation
* Weighting logic for CGPA × preference hybrid scoring
* Support for multiple departments in a single run

---
