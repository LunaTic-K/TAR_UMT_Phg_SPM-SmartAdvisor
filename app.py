import streamlit as st
import time

st.set_page_config(page_title="TAR UMT Pahang SPM Advisor", layout="wide")

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# 1. Check eligibility
user_is_eligible = st.session_state.get('user_data', {}).get('eligible', False)

# 2. Define Page List
if user_is_eligible:
    pages = [
        st.Page("pages/home.py", title="Home", default=True),
        st.Page("pages/Course_Finder.py", title="Course Finder"),
        st.Page("pages/recommendations.py", title="Recommendations"),
        st.Page("pages/feedback.py", title="Feedback")
    ]
else:
    pages = [
        st.Page("pages/home.py", title="Home", default=True),
        st.Page("pages/Course_Finder.py", title="Course Finder"),
        st.Page("pages/feedback.py", title="Feedback")
    ]

# 3. Initialize Navigation
pg = st.navigation(pages, position="top")

# 4. Handle Redirection (This is the tricky part)
if user_is_eligible and not st.session_state.get('has_redirected'):
    st.session_state['has_redirected'] = True
    st.switch_page("pages/recommendations.py")

# 5. Run Styles and Navigation
local_css("style/naviBar.css")
local_css("style/footer.css")

pg.run()

# 6. Footer
footer_html = """
<div class="footer">
    <p>© 2026 Developed by Dini</p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
