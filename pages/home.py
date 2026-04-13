import streamlit as st

st.set_page_config(page_title="SPM SmartAdvisor | Home", layout="wide")

# load css file
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">', unsafe_allow_html=True)

local_css("style/home.css") 

#HERO HEADER
st.markdown("""
<div style='display: flex; flex-direction: column; align-items: center; text-align: center; padding: 10px 0px; '>
<img src="https://en.your-uni.com/assets/images/university/tunku-abdul-rahman-university-of-management-and-technology-tar-umt.png" style='width: 350px; height:100px; max-width: 95%; height: auto; margin-bottom: 1px; margin-top: -50px;'>
<h1 style='color: #1e3c72; font-size: 3.2rem; font-weight: 800; margin-top: 0; margin-bottom: 0; line-height: 1.1;'>
TAR UMT PAHANG SPM SmartAdvisor
</h1>
<p style='color: #6c757d; font-size: 1.3rem; margin-top: 5px;'>Your Intelligent Gateway to TAR UMT Pahang</p>
</div>
""", unsafe_allow_html=True)

#ABOUT SECTION
st.markdown("""
    <div class="blue-hero-container">
        <i class="material-icons hero-icon">info</i>
        <div class="hero-content">
            <h3>About the App</h3>
            <p>
                <strong>TAR UMT Pahang SPM SmartAdvisor</strong> is an advanced educational tool designed to help SPM graduates 
                navigate their future in TAR UMT Pahang. By using smart document scanning and intelligent matching, 
                we remove the guesswork from university applications, ensuring students find 
                the perfect course that fits their grades and passions.
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)
st.write(" ")

#MISSION & VISION
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="card">
            <h3 style="color: white;"><i class="material-icons icon-style">track_changes</i> Our Mission</h3>
            <p>To simplify TAR UMT Pahang university admissions through automation and provide accurate, data-driven guidance to every student.</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="card">
            <h3 style="color: white;"><i class="material-icons icon-style">visibility</i> Our Vision</h3>
            <p>To become the leading digital advisor for tertiary education placement in Malaysia through innovative AI solutions.</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# TEAM SECTION
st.markdown("<h2 style='text-align: center; color: #1e3c72; margin-bottom: 30px;'>The Development Team</h2>", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3)

with t1:
    st.markdown("""
        <div class="team-card">
            <div class="center-icon"><i class="material-icons" style="font-size: 50px; color: white;">account_circle</i></div>
            <h4>Lee Hui Yin</h4>
            <span class="role-badge">Software Lead</span>
        </div>
    """, unsafe_allow_html=True)

with t2:
    st.markdown("""
        <div class="team-card">
            <div class="center-icon"><i class="material-icons" style="font-size: 50px; color: white;">analytics</i></div>
            <h4>Yap Hui Xin</h4>
            <span class="role-badge">System Analyst</span>
        </div>
    """, unsafe_allow_html=True)

with t3:
    st.markdown("""
        <div class="team-card">
            <div class="center-icon"><i class="material-icons" style="font-size: 50px; color: white;">palette</i></div>
            <h4>Nur Dini Kay</h4>
            <span class="role-badge">UI/UX Designer</span>
        </div>
    """, unsafe_allow_html=True)
