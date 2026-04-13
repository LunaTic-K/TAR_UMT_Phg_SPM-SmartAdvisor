import streamlit as st
from data.courses import PAHANG_COURSES, FACULTY_NAMES
from fuzzywuzzy import process
import re
import os
import pandas as pd
from datetime import datetime

if "user_data" not in st.session_state:
    st.warning("No data found. Please go back and complete the form.")
    st.stop()

def show():

    # --- 辅助函数：扁平化课程列表 ---
    def flatten_courses(courses_dict):
        """将嵌套的课程字典转换为扁平列表"""
        all_courses = []
        for dept_code, dept_data in courses_dict.items():
            faculty_name = FACULTY_NAMES.get(dept_code, dept_code)
            for course in dept_data.get("DIPLOMA", []):
                course_with_faculty = course.copy()
                course_with_faculty["faculty"] = faculty_name
                course_with_faculty["dept_code"] = dept_code
                all_courses.append(course_with_faculty)
            for course in dept_data.get("DEGREE", []):
                course_with_faculty = course.copy()
                course_with_faculty["faculty"] = faculty_name
                course_with_faculty["dept_code"] = dept_code
                all_courses.append(course_with_faculty)
        return all_courses

    # --- 类别映射 ---
    def get_course_category(course):
        """根据课程的 category 字段判断类别 - Updated for consistency"""
        metadata = course.get('metadata', {})
        course_category = metadata.get('category', '')
        if course_category:
            if "Information Technology" in course_category:
                return "Information Technology"
            elif "Accounting, Finance & Business" in course_category:
                return "Accounting, Finance & Business"
            elif "Social Science" in course_category:
                return "Social Science & Humanities"
        
        faculty = course.get('faculty', '')
        if "Computing" in faculty:
            return "Information Technology"
        elif "Accountancy" in faculty or "Business" in faculty:
            return "Accounting, Finance & Business"
        elif "Social Science" in faculty or "Humanities" in faculty:
            return "Social Science & Humanities"
        return "Others"

    # --- FuzzyWuzzy 推荐算法 ---
    def calculate_course_match(user_interest, course_tags, user_grades, course_requirements, user_category=None, course_category=None):
        interest_score = 0
        is_valid_interest = user_interest and user_interest.strip() and user_interest != user_category
        
        if is_valid_interest and course_tags:
            keywords = re.split(r'[,\s]+', user_interest.lower())
            keywords = [k.strip() for k in keywords if k.strip() and len(k.strip()) > 1]
            if not keywords:
                keywords = [user_interest.lower()]
            weighted_scores = []
            for keyword in keywords:
                matches = process.extract(keyword, course_tags, limit=1)
                if matches:
                    score = matches[0][1]
                    if score < 40:
                        score = score * 0.3
                    weighted_scores.append(score)
            if weighted_scores:
                interest_score = sum(weighted_scores) / len(weighted_scores)
            else:
                interest_score = 0
            interest_score = min(interest_score, 100)
        elif user_category and course_category:
            if user_category == course_category:
                interest_score = 70
            else:
                interest_score = 30
        else:
            interest_score = 50
        
        if interest_score < 30:
            return round(interest_score * 0.3, 1)
        
        academic_rank = (user_grades.get('total_credits', 0) / 6) * 100
        academic_rank = min(academic_rank, 100)
        grade_score = 0
        grade_weight = 0
        
        specific_reqs = course_requirements.get('specific', {})
        math_req = specific_reqs.get('Mathematics', None)
        if math_req is not None:
            grade_weight += 1
            if user_grades.get('math', 0) >= math_req:
                grade_score += 1
        
        eng_req = specific_reqs.get('English Language', 2)
        if eng_req is not None:
            grade_weight += 1
            if user_grades.get('eng', 0) >= eng_req:
                grade_score += 1

        eligibility_status = 100 if (grade_weight == 0 or grade_score == grade_weight) else 0
        total_score = (academic_rank * 0.5) + (interest_score * 0.3) + (eligibility_status * 0.2)
        return round(total_score, 1)

    def get_course_recommendations(user_interest, user_category, user_grades, courses_data, top_n=5):
        all_courses = flatten_courses(courses_data)
        recommendations = []
        category_map = {
            "Information Technology": "Information Technology",
            "Business & Accounting": "Accounting, Finance & Business",
            "Education & Social Science": "Social Science & Humanities"
        }
        target_category = category_map.get(user_category, user_category)
        has_interest_text = user_interest and user_interest.strip() and user_interest != user_category
        
        for course in all_courses:
            course_category = get_course_category(course)
            if user_category != "Others" and course_category != target_category:
                continue
            
            metadata = course.get('metadata', {})
            course_tags = metadata.get('tags', [])
            course_requirements = course.get('requirements', {})
            
            if 'study_modes' in course:
                fee = course['study_modes']['Full-Time']['fees']
                duration = course['study_modes']['Full-Time']['duration']
            else:
                fee = course.get('estimated_fees', 0)
                duration = course.get('duration', '2 Years')
            
            career_paths = metadata.get('career_paths', [])
            career = ", ".join(career_paths) if career_paths else 'Various career opportunities'
            
            match_score = calculate_course_match(
                user_interest if has_interest_text else "", 
                course_tags,
                user_grades,
                course_requirements,
                user_category,
                course_category
            )
            
            if match_score > 0:
                recommendations.append({
                    'course_name': course.get('name', ''),
                    'score': round(match_score, 1),
                    'fee': fee,
                    'description': metadata.get('description', 'No description available.'),
                    'link': metadata.get('link', '#'),
                    'career': career,
                    'tags': course_tags,
                    'progression': metadata.get('progression', ''),
                    'category': course_category,
                    'faculty': course.get('faculty', ''),
                    'duration': duration,
                    'study_modes': course.get('study_modes', None),
                    'is_preferred': True
                })
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:top_n]

    # --- 主页面逻辑 ---
    user = st.session_state.get('user_data', {})
    if not user or not user.get('eligible', False):
        st.warning(":material/warning: Please complete the Course Finder first!")
        if st.button(":material/arrow_back: Go to Course Finder", use_container_width=True):
            st.session_state['current_page'] = 'course_finder'
            st.rerun()
        st.stop()
        
    st.markdown("""
    <style>
        .main-header {
            font-size: 32px;
            font-weight: 700;
            color: #1f3a93;
            margin-bottom: 1px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="main-header">Recommended Courses for {user["name"]}</div>', unsafe_allow_html=True)
    st.caption(f"Personalized results matching **{user['interest']}** in the **{user.get('interest_category')}** faculty.")
    st.divider()

    user_grades = {
        'math': user.get('math_val', 0),
        'eng': user.get('eng_val', 0),
        'bm': user.get('bm_val', 0),
        'total_credits': user.get('total_credits', 0)
    }

    is_eligible = user.get('eligible', False)

    if not is_eligible:
        st.error(":material/error: **You do not meet the minimum requirements** (BM and Sejarah must be at least a pass AND at least 3 credits) for Diploma programs at TAR UMT Pahang.")
        if st.button(":material/arrow_back: Back to Course Finder", key="btn_ineligible_back", use_container_width=True):
            st.session_state['current_page'] = 'course_finder'
            st.rerun()
    else:
        results = get_course_recommendations(user['interest'], user.get('interest_category', 'Others'), user_grades, PAHANG_COURSES, top_n=3)
        
        if not results:
            st.warning(f":material/search: No courses found in **{user.get('interest_category', 'Others')}** category.")
        else:
            st.subheader(f":material/recommend: Top 3 Courses Recommendations in {user.get('interest_category', 'Others')}")
            
            for item in results:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {item['course_name']}")
                        
                        if item.get('study_modes'):
                            modes = item['study_modes']
                            
                            st.write("**Estimated fee:**")
                            for mode_name, data in modes.items():
                                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;🔹 {mode_name}: RM {data['fees']:,}")
                            
                            st.write("**Progression:**")
                            for mode_name, data in modes.items():
                                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;🔹 {mode_name}: {data['duration']}")
                        else:
                            fee = item['fee']
                            if fee and fee > 0:
                                st.write(f"**Estimated Fee:** RM {fee:,}")
                            else:
                                st.write("**Estimated Fee:** Please check official website")
                            
                            duration = item.get('duration', '2 Years')
                            st.write(f"**Progression:** {duration}")
                        # --- END CUSTOM DISPLAY ---
                        
                        st.write(item['description'])

                        button_html = f"""
                        <a href="{item['link']}" target="_blank" style="
                            text-decoration: none; 
                            color: white; 
                            background-color: #003366;
                            padding: 8px 16px; 
                            border-radius: 5px; 
                            font-weight: bold; 
                            display: inline-block;
                            margin-top: 10px;
                            font-size: 14px;
                        ">
                            View Course Details →
                        </a>
                        """
                        st.markdown(button_html, unsafe_allow_html=True)
                        
                    with col2:
                        score = item['score']
                        if score >= 80:
                            st.metric("Match Score", f"{score}%", delta="Excellent Match!", delta_color="normal")
                            st.success(":material/star: Highly Recommended")
                        elif score >= 60:
                            st.metric("Match Score", f"{score}%", delta="Good Match", delta_color="normal")
                            st.info(":material/thumb_up: Good Option")
                        elif score >= 40:
                            st.metric("Match Score", f"{score}%", delta="Fair Match", delta_color="inverse")
                            st.warning(":material/more_horiz: Consider Alternatives")
                        else:
                            st.metric("Match Score", f"{score}%", delta="Low Match", delta_color="inverse")
                            st.error(":material/warning: Check Requirements")
                        st.write(f"**Career:** {item['career']}")

show()