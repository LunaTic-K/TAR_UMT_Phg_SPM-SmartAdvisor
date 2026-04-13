import streamlit as st

sst.set_page_config(page_title="TAR UMT Pahang SPM Advisor", layout="wide")
def local_css(file_name):
    try:
        with open(file_name) as f:
           st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

#Check if user has data and is eligible
user_is_eligible = st.session_state.get('user_data', {}).get('eligible', False)

if user_is_eligible :
    #Show all 3 pages if they ligible
    pages = [
        st.Page("pages/home.py", title="Home", default=True),
        st.Page("pages/Course_Finder.py", title="Course Finder",),
        st.Page("pages/recommendations.py", title="Recommendations"),
        st.Page("pages/feedback.py", title="Feedback")
    ]
else:
    #Hide the recommendation page if they aren't eligible yet
    pages = [
        st.Page("pages/home.py", title="Home", default=True),
        st.Page("pages/Course_Finder.py", title="Course Finder"),
        st.Page("pages/feedback.py", title="Feedback")
    ]
if user_is_eligible and st.session_state.get('has_redirected') is not True:
    st.session_state['has_redirected'] = True
    st.switch_page("pages/recommendations.py")
    
pg = st.navigation(pages, position="top")
local_css("style/naviBar.css")
local_css("style/footer.css")
# 3.Run the navi
pg.run()

footer_html = """
<div class="footer">
    <p>© 2026 Developed by DHY</p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
