import streamlit as st
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.logic.scoring import ScoringEngine
from src.logic.coaching import JSONCoachingEngine

# ============================================
# 1. PAGE CONFIGURATION & STYLING
# ============================================
st.set_page_config(
    page_title="Sleep Expert AI",
    layout="centered",  # wide 
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #FAFAFA;
    }
    h1 {
        color: #2C3E50;
        text-align: center;
        font-family: 'Helvetica', sans-serif;
    }
    .stButton>button {
        width: 100%;
        background-color: #4F8BF9;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 3em;
    }
    /* Style the containers to look like cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# 2. HELPER FUNCTIONS
# ============================================
def get_scale_input(label, key, help_text=None):
    return st.slider(
        label,
        min_value=1,
        max_value=5,
        value=3,
        key=key,
        help=help_text
    )

def display_confidence_bar(disorder_name, score):
    # Determine Status
    if score >= 75:
        color_bar = ":red" # Streamlit color notation
        status = "HIGH PROBABILITY"
    elif score >= 50:
        color_bar = ":orange"
        status = "MODERATE RISK"
    else:
        color_bar = ":green"
        status = "LOW RISK"

    st.markdown(f"**{disorder_name}**")
    st.progress(int(score))
    st.caption(f"Confidence: **{score:.1f}%** — {status}")

# ============================================
# 3. SIDEBAR
# ============================================
with st.sidebar:
    st.title("Sleep Expert")
    st.info(
        """
        **How it works:**
        1. Answer questions about your habits.
        2. Exleep calculates risk probabilities.
        3. Receive context-aware coaching.
        """
    )
    st.write("---")

# ============================================
# 4. MAIN ASSESSMENT FORM
# ============================================
st.title("Comprehensive Sleep Assessment")
st.markdown("### 📝 Patient Intake Form")

with st.form("sleep_assessment_form"):

    # --- TABS FOR CLEANER UI ---
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "☕ Habits", "🧠 Health", "🩺 Symptoms"])

    # TAB 1: DEMOGRAPHICS
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gender", ["Male", "Female"])
            age = st.selectbox("Age Group", ["Child", "Adolescent", "Adult", "Elderly"])
            phys_act = get_scale_input("Physical Activity Level", "act", "1=Sedentary, 5=Athlete")
        with col2:
            sleep_hrs = st.selectbox("Average Sleep Duration", ["< 4", "4-6", "6-8", "8-10", "10 <"])
            shifts = get_scale_input("Work in rotating/night shifts?", "shift")
            irregular = get_scale_input("Irregular sleep schedule?", "irreg")

    # TAB 2: HABITS
    with tab2:
        col3, col4 = st.columns(2)
        with col3:
            room_qual = get_scale_input("Room Quality (Dark/Quiet/Cool)", "room", "1=Poor, 5=Perfect")
            caff_pm = get_scale_input("Caffeine after 6 PM?", "caff")
            alc_bed = get_scale_input("Alcohol before bed?", "alc")
        with col4:
            heavy_meal = get_scale_input("Heavy meals near bedtime?", "meal")
            tech_int = get_scale_input("Does tech interfere with sleep?", "tech")
            avoid_scr = get_scale_input("Do you avoid screens before bed?", "scr", "1=Never, 5=Always")
        
        st.divider()
        c5, c6 = st.columns(2)
        with c5:
            naps = get_scale_input("Nap >30 mins during the day?", "naps")
        with c6:
            bed_usage = st.radio("Do you use your bed ONLY for sleep?", ["Yes", "No"], horizontal=True)
            bed_usage_bool = True if bed_usage == "Yes" else False

    # TAB 3: HEALTH
    with tab3:
        st.subheader("Mental & Social")
        col5, col6 = st.columns(2)
        with col5:
            stress = get_scale_input("Stress/Racing thoughts at night?", "stress")
            social_lonely = get_scale_input("Feeling lonely/lack support?", "lonely")
        with col6:
            mood = get_scale_input("Mood changes affect sleep?", "mood")
        
        st.subheader("Medical History")
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            pain = st.radio("Chronic Pain?", ["No", "Yes"])
        with m_col2:
            meds = st.radio("Sleep-altering Meds?", ["No", "Yes"])
        with m_col3:
            neuro = st.radio("Neuro/Resp Disorder?", ["No", "Yes"])

        # Boolean conversion
        pain_bool = True if pain == "Yes" else False
        meds_bool = True if meds == "Yes" else False
        neuro_bool = True if neuro == "Yes" else False

    # TAB 4: SYMPTOMS
    with tab4:
        st.info("Rate symptom frequency: **1 (Never)** to **5 (Always)**")
        symptoms = {}
        
        with st.expander("Insomnia Symptoms", expanded=True):
            cols = st.columns(2)
            symptoms['insomnia_fall'] = cols[0].slider("Difficulty falling asleep", 1, 5, 1, key="i1")
            symptoms['insomnia_stay'] = cols[1].slider("Wake up frequently", 1, 5, 1, key="i2")
            symptoms['insomnia_early'] = cols[0].slider("Wake up too early", 1, 5, 1, key="i3")
            symptoms['insomnia_tired'] = cols[1].slider("Tired after sleep", 1, 5, 1, key="i4")

        with st.expander("Sleep Apnea Symptoms"):
            cols = st.columns(2)
            symptoms['apnea_snore'] = cols[0].slider("Loud Snoring", 1, 5, 1, key="a1")
            symptoms['apnea_choke'] = cols[1].slider("Wake up choking", 1, 5, 1, key="a2")
            symptoms['apnea_headache'] = cols[0].slider("Morning Headache", 1, 5, 1, key="a3")
            symptoms['apnea_sleepy'] = cols[1].slider("Daytime Sleepiness", 1, 5, 1, key="a4")

        with st.expander("Movement (RLS) Symptoms"):
            cols = st.columns(2)
            symptoms['rls_urge'] = cols[0].slider("Urge to move legs", 1, 5, 1, key="r1")
            symptoms['rls_worse_night'] = cols[1].slider("Worse at night", 1, 5, 1, key="r2")
            symptoms['rls_move_help'] = cols[0].slider("Movement helps", 1, 5, 1, key="r3")

        with st.expander("Narcolepsy Symptoms"):
            cols = st.columns(2)
            symptoms['narco_attack'] = cols[0].slider("Sleep Attacks", 1, 5, 1, key="n1")
            symptoms['narco_cata'] = cols[1].slider("Muscle Weakness", 1, 5, 1, key="n2")
            symptoms['narco_hallu'] = cols[0].slider("Hallucinations", 1, 5, 1, key="n3")
            symptoms['narco_paralysis'] = cols[1].slider("Sleep Paralysis", 1, 5, 1, key="n4")

        with st.expander("Circadian Rhythm (CRSD)"):
            cols = st.columns(2)
            symptoms['crsd_timing'] = cols[0].slider("Sleep times off-schedule", 1, 5, 1, key="c1")
            symptoms['crsd_social'] = cols[1].slider("Struggle with social hours", 1, 5, 1, key="c2")
            symptoms['crsd_alert_night'] = cols[0].slider("Alert at night", 1, 5, 1, key="c3")

        with st.expander("Parasomnia"):
            cols = st.columns(2)
            symptoms['para_act'] = cols[0].slider("Sleepwalking", 1, 5, 1, key="p1")
            symptoms['para_nightmare'] = cols[1].slider("Nightmares", 1, 5, 1, key="p2")
            symptoms['para_dream'] = cols[0].slider("Act out dreams", 1, 5, 1, key="p3")

    # --- SUBMIT ---
    st.write("")
    submit_button = st.form_submit_button("Generate Analysis", type="primary")

# ============================================
# 5. LOGIC PROCESSING & OUTPUT
# ============================================
if submit_button:
    with st.spinner("Analyzing sleep architecture..."):
        time.sleep(0.8)

        # 1. Base User Data
        user_data = {
            "gender": gender, "age": age,
            "sleep_hrs": sleep_hrs, "irregular": irregular,
            "work_shift": shifts, "physical_activity": phys_act,
            "room_quality": room_qual, "heavy_meal": heavy_meal,
            "caffeine_pm": caff_pm, "alcohol_bed": alc_bed,
            "tech_interferes": tech_int, "avoid_scr": avoid_scr,
            "naps": naps, "bed_usage": bed_usage_bool,
            "social_lonely": social_lonely, "mental_stress": stress,
            "mood_change": mood,
            "chronic_pain": pain_bool, 
            "medication_sleep": meds_bool, 
            "diagnosed_neuro_resp": neuro_bool
        }

        # 2. Logic Engines
        scores = ScoringEngine.calculate_confidence(symptoms)
        
        # --- NEW STEP: Merge symptom scores into user_data ---
        # This allows rules to check specific symptoms if needed
        # e.g., if you wanted a rule "If snoring >= 5"
        user_data.update(symptoms) 
        # ---------------------------------------------------

        active_diagnoses = [d for d, s in scores.items() if s >= 50.0]
        
        coach = JSONCoachingEngine()
        advice_list = coach.evaluate(user_data, active_diagnoses)

    # --- DISPLAY RESULTS ---
    st.divider()
    st.title("Analysis Report")

    # Use 2 columns for results (Works better with layout="wide")
    res_col1, res_col2 = st.columns([1, 1.2])

    with res_col1:
        with st.container(border=True): # Use native Streamlit container instead of HTML
            st.subheader("Diagnostic Risk Profile")
            st.caption("Weighted probabilities based on symptom severity.")
            st.write("")
            for disorder, score in scores.items():
                display_confidence_bar(disorder, score)

    with res_col2:
        with st.container(border=True):
            st.subheader("📋 Coach Recommendations")
            
            if active_diagnoses:
                st.error(f"⚠️ Potential Clinical Flags: {', '.join(active_diagnoses)}")
            else:
                st.success("✅ No major clinical disorders detected.")

            st.write("---")
            
            if advice_list:
                unique_advice = sorted(list(set(advice_list)))
                for item in unique_advice:
                    if "MEDICAL" in item or "CRITICAL" in item:
                        st.error(item)
                    elif "FIX" in item:
                        st.warning(item)
                    else:
                        st.info(item)
            else:
                st.success("Your sleep habits are optimized! No specific corrections needed.")