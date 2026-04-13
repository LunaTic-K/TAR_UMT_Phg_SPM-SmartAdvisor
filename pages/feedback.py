import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime

def show():
    try:
        with open("style/feedback.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
            st.error("CSS file not found. Please ensure 'feedback.css' is in the same folder.")

    #in submission state
    if "feedback_submitted" not in st.session_state:
        st.session_state.feedback_submitted = False

    st.markdown(
        """
        <div class="main-header">
            Feedback and Suggestions
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.write("")

    #get user data
    user_data = st.session_state.get('user_data', {})
    has_input_form = user_data.get('eligible', False)
    user_name = user_data.get('name', 'Friend')

# thanks msg
    if st.session_state.feedback_submitted:
        if has_input_form:
            thanks_msgs = [
                f"Thanks {user_name}! Your input is a huge help.",
                f"Feedback received, {user_name}! You're helping us build a smarter advisor.",
                f"Success! We've noted your suggestions, {user_name}. Have a great day!"
            ]
        else:
            thanks_msgs = [
                f"Thanks for the feedback, {user_name}! We appreciate the support.",
                f"Got it, {user_name}! Thanks for helping us improve.",
                f"Thank you {user_name}! Your suggestions are officially noted."
            ]
        
        with st.container():
            st.markdown(f"""
                <div class="success-box">
                    <h2 style="color: white !important; border: none;">Thank You!</h2>
                    <p style="font-size: 1.2rem; color: white;">{random.choice(thanks_msgs)}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("")
    
            if st.button(":material/add_comment: Submit Another Response", use_container_width=True):
                    st.session_state.feedback_submitted = False
                    st.rerun()
        return
    #form view
    st.markdown('<div class="sub-text">Help us make <b>TAR UMT Pahang SPM SmartAdvisor</b> even better.</div>', unsafe_allow_html=True)

    st.divider()

    left, center, right = st.columns([1, 4, 1])
    with center:
        with st.container(border=True):
            st.markdown("### :material/reviews: Share Your Experience")
            
            rating = None
            recommend = "N/A"

            #CASE 1:show all 3 questions if did the course finder form
            if has_input_form:
                st.markdown('<p class="section-header">How satisfied are you with your results?</p>', unsafe_allow_html=True)
                rating = st.feedback("stars")
                
                st.write("")
                st.markdown('<p class="section-header">Would you recommend this tool to others?</p>', unsafe_allow_html=True)
                recommend = st.segmented_control(
                    label="Rec", options=["Yes", "Maybe", "No"], label_visibility="collapsed"
                )
                st.write("")

            #CASE 2:show only 1 question if not do course finder form
            st.markdown('<p class="section-header">What could we improve?</p>', unsafe_allow_html=True)
            comment = st.text_area("Comment", label_visibility="collapsed", placeholder="Share your thoughts...", height=120)

            if st.button(":material/send: Submit Feedback", type="primary", use_container_width=True):
                if has_input_form and rating is None:
                    st.error("Please provide a star rating!")
                elif not comment.strip():
                    st.error("Please enter a comment before submitting!")
                else:
                    try:
                        feedback_file = "feedback_logs.csv"
                        feedback_data = {
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Student_Name": user_name if user_name != 'Friend' else 'Anonymous',
                            "Rating": rating + 1 if rating is not None else "N/A",
                            "Comment": comment.strip(),
                            "Recommend": recommend if recommend else "N/A"
                        }
                        
                        file_exists = os.path.exists(feedback_file)
                        pd.DataFrame([feedback_data]).to_csv(feedback_file, mode='a', index=False, header=not file_exists, encoding='utf-8')
                        
                        st.session_state.feedback_submitted = True 
                        st.balloons()
                        st.rerun() 
                        
                    except Exception as e:
                        st.error(f"Error: {e}")

show()