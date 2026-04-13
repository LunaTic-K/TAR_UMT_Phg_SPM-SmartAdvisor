import streamlit as st
import pandas as pd
import os
import easyocr
import numpy as np
from PIL import Image
import re
import time
from data.courses import PAHANG_COURSES
from datetime import datetime

@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['en', 'ms'])

@st.dialog("Missing Information")
def show_name_error():
    st.warning(":material/person_off: **Full Name Required**")
    st.write("Please enter your name to proceed with the course finder analysis.")
    if st.button("OK", use_container_width=True,type="primary"):
        st.rerun()

def extract_spm_grades(image):
    try:
        reader = get_ocr_reader()
        img_array = np.array(image.convert('L'))
        results = reader.readtext(img_array, paragraph=False)

        full_text = " ".join([res[1].upper() for res in results]).replace("€", "C")
        all_text_found = [res[1].upper().replace("€", "C") for res in results]

        found_grades = {}
        core_patterns = {
            'bm': r'BAHASA MELAYU|BM',
            'math': r'MATEMATIK|MATHEMATICS|MATH|MATHS',
            'eng': r'BAHASA INGGERIS|ENGLISH|BI',
            'hist': r'SEJARAH|HISTORY'
        }

        for key, patterns in core_patterns.items():
            found_grade = None
            pattern_list = patterns.split('|')
            
            for pattern in pattern_list:
                match = re.search(rf"{pattern}[\s\W]*?([A-G][+-]?)", full_text, re.IGNORECASE)
                if match and match.group(1):
                    found_grade = match.group(1).upper()
                    break
                
                match = re.search(rf'([A-G][+-]?)[\s\W]*?{pattern}', full_text, re.IGNORECASE)
                if match and match.group(1):
                    found_grade = match.group(1).upper()
                    break
            
            if not found_grade:
                for pattern in pattern_list:
                    subject_pos = full_text.find(pattern)
                    if subject_pos != -1:
                        start = max(0, subject_pos - 50)
                        end = min(len(full_text), subject_pos + 100)
                        surrounding = full_text[start:end]
                        grade_match = re.search(r'([A-G][+-]?)', surrounding)
                        if grade_match and grade_match.group(1):
                            found_grade = grade_match.group(1).upper()
                            break
            
            if found_grade:
                found_grades[key] = found_grade

        all_possible_grades = []
        for text in all_text_found:
            grade_match = re.search(r'\b(A\+|A-|A|B\+|B|C\+|C|D|E|G|€)\b', text)
            if grade_match and grade_match.group(1):
                clean_grade = grade_match.group(1).replace("€", "C")
                all_possible_grades.append(clean_grade)

        used_core_grades = list(found_grades.values())
        electives = []
        for g in all_possible_grades:
            if g in used_core_grades:
                used_core_grades.remove(g)
            else:
                electives.append(g)

        grade_order = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G"]
        electives.sort(key=lambda x: grade_order.index(x) if x in grade_order else 999)

        if len(electives) >= 1: 
            found_grades['e1'] = electives[0]
        if len(electives) >= 2: 
            found_grades['e2'] = electives[1]
            
        return found_grades if found_grades else None
        
    except Exception as e:
        st.error(f":material/error: Scan failed: {e}")
        return None


#int session state
if 'inputs' not in st.session_state:
    st.session_state['inputs'] = {
        "user_name": "",
        "interest_text": "",
        "interest_category": "Information Technology",
        "year_idx": 1,
        "bm_idx": 6,
        "math_idx": 6,
        "eng_idx": 6,
        "hist_idx": 6,
        "e1_idx": 6,
        "e2_idx": 6
    }
if 'go_to_rec' not in st.session_state:
    st.session_state['go_to_rec'] = False


st.markdown("""
    <style>
    .stSelectbox label { font-weight: 600; color: #1f3a93; }
    .main-header { font-size: 32px; font-weight: 700; color: #1f3a93; margin-bottom: 5px; }
    .sub-text { color: #666; margin-bottom: 20px; }
    [data-testid="stMetricValue"] { color: #1f3a93; font-size: 24px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">TAR UMT Pahang SPM SmartAdvisor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Academic Path Recommendation System for TAR UMT Pahang</div>', unsafe_allow_html=True)


def get_grade_point(grade):
    grade_map = {"A+": 4, "A": 4, "A-": 4, "B+": 3, "B": 3, "C+": 2, "C": 2, "D": 1, "E": 1, "G": 0}
    return grade_map.get(grade, 0)


st.divider()

st.subheader(":material/photo_camera: Optional: Auto-fill via Result Slip")
uploaded_file = st.file_uploader("Upload your SPM result image", type=['jpg', 'jpeg', 'png'])

spm_grades = ["A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G"]


if uploaded_file:
    MAX_SIZE_MB = 3
    if uploaded_file.size > MAX_SIZE_MB * 1024 * 1024:
        st.error(":material/file_upload_off: File too large! Maximum size is 3MB. Your file is {:.1f}MB.".format(uploaded_file.size / 1024 / 1024))
        uploaded_file = None
    
    if uploaded_file:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"

        if st.session_state.get('last_file_id') != file_id:
            st.session_state['last_file_id'] = file_id
            progress_placeholder = st.empty()

            with progress_placeholder.container():
                st.markdown(":material/search_activity: *Just a moment, please. We are carefully scanning your file...*")
                bar = st.progress(0)
                status_text = st.status(":material/sync: Initializing EasyOCR Engine...")

                for i in range(1, 40):
                    bar.progress(i)
                    time.sleep(0.05)

                status_text.update(label=":material/database_search: Analyzing Text Patterns...", state="running")

                img = Image.open(uploaded_file)
                extracted = extract_spm_grades(img)

                for i in range(40, 101):
                    bar.progress(i)
                    time.sleep(0.02)

                status_text.update(label=":material/check_circle: Scan Complete! Updating your form...", state="complete")
                time.sleep(0.5)

            if extracted:
                progress_placeholder.success(":material/task_alt: **Success!** We have identified your grades and updated the form below.")
                
                for sub, grade in extracted.items():
                    if grade in spm_grades:
                        st.session_state['inputs'][f"{sub}_idx"] = spm_grades.index(grade)

                time.sleep(2.5)
                progress_placeholder.empty()
                st.rerun()


user_name = st.text_input(
    "Full Name",
    value=st.session_state['inputs']['user_name'],
    placeholder="Enter your name (e.g., Dini)"
)

interest_categories = ["Information Technology", "Business & Accounting", "Education & Social Science", "Others"]
interest_category = st.selectbox(
    "Select your main area of interest",
    options=interest_categories,
    index=interest_categories.index(st.session_state['inputs']['interest_category'])
)

interest_text = st.text_area(
    "Tell us more about your interests (optional)",
    value=st.session_state['inputs']['interest_text'],
    placeholder="Example: I want to learn about cybersecurity..."
)

exam_years = list(range(2026, 2016, -1))
exam_year = st.selectbox(
    "Select your SPM Year",
    options=exam_years,
    index=st.session_state['inputs']['year_idx']
)

c1, c2 = st.columns(2)
with c1:
    bm = st.selectbox("Bahasa Melayu", spm_grades, index=st.session_state['inputs']['bm_idx'])
    if get_grade_point(bm) == 0:
        st.error(":material/cancel: Must Pass BM!")

    math = st.selectbox("Mathematics", spm_grades, index=st.session_state['inputs']['math_idx'])

with c2:
    eng = st.selectbox("English", spm_grades, index=st.session_state['inputs']['eng_idx'])

    hist = st.selectbox("Sejarah", spm_grades, index=st.session_state['inputs']['hist_idx'])
    if get_grade_point(hist) == 0:
        st.error(":material/cancel: Must Pass Sejarah!")

st.subheader("2. Best Electives")
e1 = st.selectbox("Elective 1", spm_grades, index=st.session_state['inputs']['e1_idx'])
e2 = st.selectbox("Elective 2", spm_grades, index=st.session_state['inputs']['e2_idx'])

all_subjects = [bm, math, eng, hist, e1, e2]
total_credits = sum(1 for g in all_subjects if get_grade_point(g) >= 2)
is_pass_bm_sj = get_grade_point(bm) >= 1 and get_grade_point(hist) >= 1

st.divider()
st.metric(label="Total Credits Found", value=f"{total_credits} Credits")


@st.dialog("Processing Results")
def show_results_popup(is_pass_bm_sj, total_credits):
    st.write("### Analysis Complete")
    if not is_pass_bm_sj:
        st.error(":material/block: Requirement Not Met: Must Pass BM & Sejarah.")
    elif total_credits < 3:
        st.warning(f":material/warning: Low Credit Count: You have {total_credits} credits.")
    else:
        st.success(":material/check_circle: Eligible! Go to Recommendations.")
        if st.button(":material/analytics: View Recommendations", use_container_width=True,type="primary"):
            if 'user_data' in st.session_state:
                st.session_state['user_data']['eligible'] = True
            st.session_state['go_to_rec'] = True
            st.rerun()


if st.button("Process My Path", use_container_width=True,type="primary"):
    # check if name is empty
    if not user_name.strip():
        show_name_error() # Triggers the centered popup
    else:
        # 2.if name exists, proceed
        faculty_map = {
            "Information Technology": "FOCS_DEPT",
            "Business & Accounting": "AFB_DEPT",
            "Education & Social Science": "FSSH_DEPT",
            "Others": "Others"
        }
        selected_faculty_key = faculty_map.get(interest_category, "Others")
        #save inputs to session state
        st.session_state['inputs'].update({
            "user_name": user_name,
            "interest_text": interest_text,
            "interest_category": interest_category,
            "year_idx": exam_years.index(exam_year),
            "bm_idx": spm_grades.index(bm),
            "math_idx": spm_grades.index(math),
            "eng_idx": spm_grades.index(eng),
            "hist_idx": spm_grades.index(hist),
            "e1_idx": spm_grades.index(e1),
            "e2_idx": spm_grades.index(e2)
        })

        user_data = {
            "name": user_name,
            "interest": interest_text if interest_text else interest_category,
            "interest_category": interest_category,
            "math_val": get_grade_point(math),
            "eng_val": get_grade_point(eng),
            "total_credits": total_credits,
            "eligible": is_pass_bm_sj and total_credits >= 3
        }
        st.session_state['user_data'] = user_data

        #course matching logic
        top_course = "No Eligible Courses"
        faculty_courses = PAHANG_COURSES.get(selected_faculty_key, {}).get("DIPLOMA", [])
        for course in faculty_courses:
            req = course.get('requirements', {})
            spec = req.get('specific', {})
            if (total_credits >= req.get('min_credits', 3) and
                user_data['math_val'] >= spec.get('Mathematics', 0) and
                user_data['eng_val'] >= spec.get('English Language', 0)):
                top_course = course['name']
                break

        #store and show the success/results popup
        try:
            log_file = "consultation_logs.csv"
            new_record = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Student_Name": user_name,
                "Interest_Category": interest_category,
                "Credits": total_credits,
                "Eligible": "Yes" if user_data['eligible'] else "No",
                "Top_Match": top_course
            }
            pd.DataFrame([new_record]).to_csv(log_file, mode='a', index=False, header=not os.path.exists(log_file))
            
            show_results_popup(is_pass_bm_sj, total_credits)
            
        except PermissionError:
            st.error(":material/lock: Close 'consultation_logs.csv' first!")


if st.session_state.get('go_to_rec'):
    st.session_state['go_to_rec'] = False
    st.switch_page("pages/recommendations.py")
