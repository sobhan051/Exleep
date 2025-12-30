# src/interface.py

from src.utils import ask_choice, ask_scale_1_5, ask_yes_no
from src.logic.scoring import ScoringEngine
from src.logic.coaching import JSONCoachingEngine

def run_app():
    # ==========================================
    # 1. INITIALIZATION & HEADER
    # ==========================================
    print("\n=======================================================")
    print("      SLEEP EXPERT SYSTEM (Modular & Data-Driven)      ")
    print("=======================================================")
    print("Please answer the following assessment questions.")
    print("For 1-5 scales: 1=Never/Poor, 5=Always/Excellent.")

    # ==========================================
    # 2. DATA COLLECTION (Inputs)
    # ==========================================
    
    # --- A. Demographics ---
    print("\n[ Section 1: Demographics ]")
    gender = ask_choice("Gender?", ["Male", "Female"])
    age = ask_choice("Age Group?", ["Child", "Adolescent", "Adult", "Elderly"])

    # --- B. Lifestyle ---
    print("\n[ Section 2: Lifestyle ]")
    sleep_hrs = ask_choice("Average sleep hours per night?", ["< 4", "4-6", "6-8", "8-10", "10 <"])
    irregular = ask_scale_1_5("Do you have an irregular sleep schedule?")
    shifts = ask_scale_1_5("Do you work in rotating or night shifts?")
    phys_act = ask_scale_1_5("Physical activity level?", label_low="Sedentary", label_high="Very Active")

    # --- C. Habits & Environment ---
    print("\n[ Section 3: Habits & Environment ]")
    room_qual = ask_scale_1_5("Is your bedroom quiet, dark, and cool?", label_low="Poor", label_high="Perfect")
    heavy_meal = ask_scale_1_5("Do you eat heavy meals close to bedtime?")
    caff_pm = ask_scale_1_5("Do you drink caffeine after 6 PM?")
    alc_bed = ask_scale_1_5("Do you consume alcohol before sleep?")
    
    print("\n--- Technology ---")
    tech_int = ask_scale_1_5("Do you feel technology interferes with your sleep?")
    avoid_scr = ask_scale_1_5("Do you avoid screens (blue light) before bed?", label_low="Never (Use screens)", label_high="Always (Avoid)")
    
    print("\n--- Routine ---")
    naps = ask_scale_1_5("Do you nap for more than 30 minutes during the day?")
    bed_usage = ask_yes_no("Do you use your bed mainly for sleep (not working/eating)?")

    # --- D. Social & Mental ---
    print("\n[ Section 4: Social & Mental Health ]")
    social_lonely = ask_scale_1_5("Do you feel lonely or lack emotional support?")
    stress = ask_scale_1_5("Do you experience stress or racing thoughts at bedtime?")
    mood = ask_scale_1_5("Do mood changes affect your sleep quality?")

    # --- E. Medical History ---
    print("\n[ Section 5: Medical History ]")
    pain = ask_yes_no("Do you suffer from chronic pain that disturbs sleep?")
    meds = ask_yes_no("Do you take medication that might affect sleep?")
    neuro = ask_yes_no("Have you been diagnosed with a neurological or respiratory disorder?")

    # --- F. Symptom Assessment (For Diagnostic Scoring) ---
    print("\n[ Section 6: Symptom Checker ]")
    symptoms = {}

    print(">> Insomnia Check")
    symptoms['insomnia_fall'] = ask_scale_1_5("Difficulty falling asleep?")
    symptoms['insomnia_stay'] = ask_scale_1_5("Wake up frequently during the night?")
    symptoms['insomnia_early'] = ask_scale_1_5("Wake up too early and can't fall back?")
    symptoms['insomnia_tired'] = ask_scale_1_5("Feel tired even after sleeping?")

    print(">> Apnea Check")
    symptoms['apnea_snore'] = ask_scale_1_5("Snore loudly?")
    symptoms['apnea_choke'] = ask_scale_1_5("Wake up choking or gasping?")
    symptoms['apnea_headache'] = ask_scale_1_5("Morning headaches or dry mouth?")
    symptoms['apnea_sleepy'] = ask_scale_1_5("Excessive daytime sleepiness?")

    print(">> Restless Legs (RLS) Check")
    symptoms['rls_urge'] = ask_scale_1_5("Uncontrollable urge to move legs while resting?")
    symptoms['rls_worse_night'] = ask_scale_1_5("Sensations worse in the evening/night?")
    symptoms['rls_move_help'] = ask_scale_1_5("Does movement relieve the discomfort?")

    print(">> Narcolepsy Check")
    symptoms['narco_attack'] = ask_scale_1_5("Sudden sleep attacks during daytime?")
    symptoms['narco_cata'] = ask_scale_1_5("Muscle weakness during strong emotions?")
    symptoms['narco_hallu'] = ask_scale_1_5("Vivid hallucinations when falling asleep?")
    symptoms['narco_paralysis'] = ask_scale_1_5("Sleep paralysis?")

    print(">> Circadian Rhythm (CRSD) Check")
    symptoms['crsd_timing'] = ask_scale_1_5("Sleep times much later/earlier than desired?")
    symptoms['crsd_social'] = ask_scale_1_5("Struggle to sleep at normal social hours?")
    symptoms['crsd_alert_night'] = ask_scale_1_5("Alert at night but sleepy in the morning?")

    print(">> Parasomnia Check")
    symptoms['para_act'] = ask_scale_1_5("Sleepwalking, talking, or performing actions?")
    symptoms['para_nightmare'] = ask_scale_1_5("Frequent nightmares?")
    symptoms['para_dream'] = ask_scale_1_5("Act out dreams (move/shout)?")

    # ==========================================
    # 3. AGGREGATION
    # ==========================================
    # We pack user answers into a dictionary to pass to the JSON Rules Engine.
    # The keys here must match the variable names used in 'rules.json'.
    user_data = {
        "gender": gender,
        "age": age,
        "sleep_hrs": sleep_hrs,
        "irregular": irregular,
        "work_shift": shifts,
        "physical_activity": phys_act,
        "room_quality": room_qual,
        "heavy_meal": heavy_meal,
        "caffeine_pm": caff_pm,
        "alcohol_bed": alc_bed,
        "tech_interferes": tech_int,
        "avoid_scr": avoid_scr,
        "naps": naps,
        "bed_usage": bed_usage, # Boolean
        "social_lonely": social_lonely,
        "mental_stress": stress,
        "mood_change": mood,
        "chronic_pain": pain,
        "medication_sleep": meds,
        "diagnosed_neuro_resp": neuro
    }

    # ==========================================
    # 4. LOGIC EXECUTION
    # ==========================================
    
    print("\n[Thinking...] Analyzing patterns and calculating probabilities...")
    
    # STEP A: Calculate Diagnostic Scores (Python Math)
    diagnostic_scores = ScoringEngine.calculate_confidence(symptoms)

    # STEP B: Determine Active Diagnoses (Thresholding)
    threshold = 50.0  # Confidence % required to flag a disorder
    active_diagnoses = []
    
    for disorder, confidence in diagnostic_scores.items():
        if confidence >= threshold:
            active_diagnoses.append(disorder)

    # STEP C: Generate Coaching Advice (JSON Rules)
    # We initialize the engine (loads rules.json)
    coach = JSONCoachingEngine() 
    # We evaluate the user data + the context of their diagnoses
    advice_list = coach.evaluate(user_data, active_diagnoses)

    # ==========================================
    # 5. FINAL REPORT
    # ==========================================
    print("\n\n")
    print("#################################################")
    print("              FINAL ASSESSMENT REPORT            ")
    print("#################################################")

    # --- Part 1: Diagnosis ---
    print(f"\n📊 CLINICAL CONFIDENCE SCORES (Threshold: {threshold}%)")
    print("-" * 60)
    for disorder, confidence in diagnostic_scores.items():
        # Create a visual bar chart
        bar_len = int(confidence / 5) # 100% = 20 chars
        bar = "█" * bar_len + "░" * (20 - bar_len)
        
        # Status Label
        if confidence >= 75: 
            status = "🔴 HIGH PROBABILITY"
        elif confidence >= 50: 
            status = "🟠 MODERATE RISK"
        else: 
            status = "🟢 LOW RISK"
        
        print(f"{disorder.ljust(25)} | {bar} {confidence:.1f}%  {status}")

    # --- Part 2: Coaching ---
    print("\n📋 EXPERT COACHING & RECOMMENDATIONS:")
    print("-" * 60)
    
    if advice_list:
        # Sort to make it tidy and remove duplicates
        unique_advice = sorted(list(set(advice_list)))
        for advice in unique_advice:
            print(f"   • {advice}")
    else:
        print("   ✅ Your habits look great! No specific corrective advice generated.")
        
    print("-" * 60) 
    print("#################################################")