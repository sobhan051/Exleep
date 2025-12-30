import collections.abc

# ==========================================
# 0. COMPATIBILITY PATCH (For Python 3.10+)
# ==========================================
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'Sequence'):
    collections.Sequence = collections.abc.Sequence

from experta import *

# ==========================================
# 1. INPUT HELPER FUNCTIONS
# ==========================================
def ask_scale_1_5(question, label_low="Never / Not at all", label_high="Always / Very Much"):
    """
    Standardizes all frequency/intensity questions to a 1-5 scale.
    """
    print(f"\n[?] {question}")
    print(f"    1: {label_low}")
    print("    2: Rarely / A little / Poor")
    print("    3: Sometimes / Somewhat / Average")
    print("    4: Often / Much / Good")
    print(f"    5: {label_high}")
    
    while True:
        try:
            val = int(input("    Enter 1-5: "))
            if 1 <= val <= 5: return val
        except ValueError: pass
        print("    Please enter a number between 1 and 5.")

def ask_choice(question, choices):
    """
    Handles categorical data (Gender, Age, Time Ranges).
    """
    print(f"\n[?] {question}")
    for i, c in enumerate(choices, 1):
        print(f"    {i}. {c}")
    while True:
        try:
            val = int(input("    Select option number: "))
            if 1 <= val <= len(choices):
                return choices[val-1]
        except ValueError: pass
        print("    Invalid selection.")

def ask_yes_no(question):
    """
    Handles strict binary facts (Medical History).
    """
    print(f"\n[?] {question} (yes/no)")
    while True:
        val = input("    > ").lower().strip()
        if val in ['yes', 'y']: return True
        if val in ['no', 'n']: return False
        print("    Please type 'yes' or 'no'.")

# ==========================================
# 2. DEFINE FACTS
# ==========================================
class Person(Fact):
    pass

class Diagnosis(Fact):
    pass

class Advice(Fact):
    pass

# ==========================================
# 3. KNOWLEDGE ENGINE
# ==========================================
class SleepEngine(KnowledgeEngine):
    
    # ==========================================================
    # PART A: DIAGNOSTIC RULES
    # ==========================================================

    # --- 1. INSOMNIA ---
    @Rule(
        OR(
            Person(insomnia_fall=P(lambda x: x >= 4)),
            Person(insomnia_stay=P(lambda x: x >= 4)),
            Person(insomnia_early=P(lambda x: x >= 4))
        ),
        Person(insomnia_tired=P(lambda x: x >= 3))
    )
    def diagnose_insomnia(self):
        self.declare(Diagnosis(name="Insomnia"))

    # --- 2. SLEEP APNEA ---
    @Rule(
        OR(
            Person(apnea_snore=P(lambda x: x >= 4)),
            Person(apnea_choke=P(lambda x: x >= 2))
        ),
        OR(
            Person(apnea_sleepy=P(lambda x: x >= 4)),
            Person(apnea_headache=P(lambda x: x >= 3))
        )
    )
    def diagnose_apnea(self):
        self.declare(Diagnosis(name="Obstructive Sleep Apnea"))

    # --- 3. RLS ---
    @Rule(
        Person(rls_urge=P(lambda x: x >= 4)),
        Person(rls_worse_night=P(lambda x: x >= 4)),
        Person(rls_move_help=P(lambda x: x >= 4))
    )
    def diagnose_rls(self):
        self.declare(Diagnosis(name="Restless Legs Syndrome (RLS)"))

    # --- 4. NARCOLEPSY ---
    @Rule(
        Person(narco_attack=P(lambda x: x >= 3)),
        OR(
            Person(narco_cata=P(lambda x: x >= 2)),
            Person(narco_hallu=P(lambda x: x >= 4)),
            Person(narco_paralysis=P(lambda x: x >= 4))
        )
    )
    def diagnose_narcolepsy(self):
        self.declare(Diagnosis(name="Narcolepsy"))

    # --- 5. CRSD ---
    @Rule(
        Person(crsd_timing=P(lambda x: x >= 4)),
        Person(crsd_social=P(lambda x: x >= 4)),
        Person(crsd_alert_night=P(lambda x: x >= 4))
    )
    def diagnose_crsd(self):
        self.declare(Diagnosis(name="Circadian Rhythm Sleep Disorder"))

    # --- 6. PARASOMNIA ---
    @Rule(
        OR(
            Person(para_act=P(lambda x: x >= 2)),
            Person(para_nightmare=P(lambda x: x >= 4)),
            Person(para_acting_out=P(lambda x: x >= 2))
        )
    )
    def diagnose_parasomnia(self):
        self.declare(Diagnosis(name="Parasomnia"))


    # ==========================================================
    # PART B: COACHING RULES
    # ==========================================================

    # --- MEDICAL ---
    @Rule(Person(diagnosed_neuro_resp=True))
    def medical_history_check(self):
        self.declare(Advice(text="⚠️ MEDICAL: You indicated a history of neurological/respiratory disorders. Ensure your doctor monitors your sleep."))

    @Rule(Person(medication_sleep=True))
    def med_check(self):
        self.declare(Advice(text="💊 MEDS: Review your medications. Some antidepressants or stimulants directly cause insomnia as a side effect."))

    @Rule(Person(chronic_pain=True))
    def pain_check(self):
        self.declare(Advice(text="🩺 PAIN: Chronic pain is disrupting your sleep architecture. Pain management is the priority here."))

    # --- LIFESTYLE ---
    
    # FIXED: Replaced MATCH("< 4") with simple equality check
    @Rule(Person(sleep_hrs="< 4"))
    def sleep_duration_critical(self):
        self.declare(Advice(text="🔴 DURATION: Sleeping <4 hours is dangerous. It severely impacts cognitive function and immunity."))

    @Rule(Person(work_shift=P(lambda x: x >= 3)))
    def shift_work_advice(self):
        self.declare(Advice(text="⏰ SHIFT WORK: Use 'Darkness Anchors'. Wear sunglasses on your commute home after a night shift to prevent waking your body clock."))

    @Rule(Person(physical_activity=P(lambda x: x <= 2)))
    def exercise_advice(self):
        self.declare(Advice(text="🏃 ACTIVITY: You are sedentary. 20 mins of daily exercise increases 'adenosine' (sleep pressure)."))

    # --- SLEEP QUALITY ---
    
    # FIXED: Replaced MATCH("60+") with simple equality check
    @Rule(Person(fall_time="60+"))
    def latency_high(self):
        self.declare(Advice(text="⏳ LATENCY: Taking >1 hour to fall asleep suggests hyperarousal. Try 'Paradoxical Intention' (try to keep your eyes open instead of forcing sleep)."))

    @Rule(Person(refreshed=P(lambda x: x <= 2)))
    def inertia_advice(self):
        self.declare(Advice(text="🔋 ENERGY: Significant Sleep Inertia detected. Hydrate immediately upon waking and seek bright sunlight within 15 minutes."))

    # --- MENTAL HEALTH ---
    @Rule(Person(mental_stress=P(lambda x: x >= 4)))
    def stress_advice(self):
        self.declare(Advice(text="🧠 STRESS: High bedtime stress. Try 'Box Breathing' (4s in, 4s hold, 4s out, 4s hold) or write a 'Worry List' 2 hours before bed."))

    @Rule(Person(mood_change=P(lambda x: x >= 4)))
    def mood_advice(self):
        self.declare(Advice(text="🧠 MOOD: Your mood is tightly linked to your sleep. This suggests a bidirectional relationship. Consider CBT-I (Cognitive Behavioral Therapy for Insomnia)."))

    # --- ENVIRONMENT ---
    @Rule(Person(room_quality=P(lambda x: x <= 2)))
    def room_advice(self):
        self.declare(Advice(text="🛏️ ENVIRONMENT: Your bedroom is not sleep-ready. It needs to be Pitch Black, Quiet, and Cool (around 18°C/65°F)."))

    @Rule(Person(noise_light=P(lambda x: x >= 4)))
    def disturbance_advice(self):
        self.declare(Advice(text="🔇 ENVIRONMENT: External disturbances are waking you. Invest in silicone earplugs and a high-quality eye mask."))

    # --- DIET ---
    @Rule(Person(heavy_meal=P(lambda x: x >= 4)))
    def diet_heavy_advice(self):
        self.declare(Advice(text="🥗 DIET: Heavy meals require high energy for digestion, raising body temp. Eat lighter dinners at least 3 hours before bed."))

    @Rule(Person(caffeine_pm=P(lambda x: x >= 3)))
    def caffeine_advice(self):
        self.declare(Advice(text="☕ CAFFEINE: Caffeine has a 6-hour half-life. Drinking it after 6 PM chemically blocks sleep. Switch to herbal tea."))

    @Rule(Person(alcohol_bed=P(lambda x: x >= 3)))
    def alcohol_advice(self):
        self.declare(Advice(text="🍷 ALCOHOL: Alcohol helps you fall asleep but fragments REM sleep later. Avoid it within 3 hours of bed."))

    # --- TECHNOLOGY ---
    @Rule(Person(tech_interferes=P(lambda x: x >= 4)))
    def tech_addiction(self):
        self.declare(Advice(text="📱 TECH: You admitted tech interferes with sleep. Remove the phone from the bedroom entirely. Use an old-school alarm clock."))

    @Rule(Person(avoid_scr=P(lambda x: x <= 2)))
    def blue_light_advice(self):
        self.declare(Advice(text="💡 LIGHT: Blue light suppresses melatonin. Use 'Night Shift' mode or blue-light blocking glasses starting 90 mins before sleep."))

    # --- CHRONOBIOLOGY ---
    @Rule(Person(chrono_type="Night owl"), Person(work_shift="Never"))
    def owl_advice(self):
        self.declare(Advice(text="🦉 TYPE: You are a 'Night Owl'. Avoid bright light in the evening and seek immediate sunlight upon waking to shift your clock earlier."))

    @Rule(Person(consistent=P(lambda x: x <= 2)))
    def consistency_advice(self):
        self.declare(Advice(text="⏰ RHYTHM: Social Jetlag detected. You need to wake up at the same time every day (even weekends) to anchor your circadian rhythm."))

    # --- HYGIENE ---
    @Rule(Person(naps=P(lambda x: x >= 3)))
    def nap_advice(self):
        self.declare(Advice(text="💤 HABIT: Long naps (>30 mins) steal 'sleep pressure' from the night. Limit naps to 20 mins max."))

    @Rule(Person(bed_usage=False))
    def bed_association(self):
        self.declare(Advice(text="🛏️ HABIT: Stop working or eating in bed. Your brain needs to associate the bed ONLY with sleep and intimacy."))

    # --- SOCIAL ---
    @Rule(Person(social_lonely=P(lambda x: x >= 4)))
    def social_advice(self):
        self.declare(Advice(text="❤️ SOCIAL: Loneliness keeps the brain in 'alert mode'. Scheduling a call with a friend in the evening can lower cortisol."))

# ==========================================
# 4. MAIN PROGRAM EXECUTION
# ==========================================
def run_system():
    engine = SleepEngine()
    engine.reset()

    print("\n=======================================================")
    print("      COMPREHENSIVE SLEEP DISORDER EXPERT SYSTEM       ")
    print("=======================================================")
    print("Please answer the following assessment.")
    print("For questions with a 1-5 scale, use the guide provided.")

    # --- SECTION 1: DEMOGRAPHICS ---
    gender = ask_choice("Gender?", ["Male", "Female"])
    age = ask_choice("Age Group?", ["Child", "Adolescent", "Adult", "Elderly"])

    # --- SECTION 2: LIFESTYLE ---
    print("\n--- LIFESTYLE ---")
    sleep_hrs = ask_choice("Average sleep hours per night?", ["< 4", "4-6", "6-8", "8-10", "10 <"])
    irregular = ask_scale_1_5("Do you have an irregular sleep schedule?")
    shifts = ask_scale_1_5("Do you work in rotating or night shifts?")
    phys_act = ask_scale_1_5("Physical activity level during the day?", label_low="Sedentary", label_high="Very Active")

    # --- SECTION 3: SLEEP QUALITY ---
    print("\n--- SLEEP QUALITY ---")
    fall_time = ask_choice("How long does it take you to fall asleep?", ["<15 min", "15-30", "30-45", "45-60", "60+"])
    wake_night = ask_scale_1_5("How often do you wake up during the night?")
    refreshed = ask_scale_1_5("Do you feel refreshed upon waking up?", label_low="Not at all", label_high="Fully refreshed")

    # --- SECTION 4: MENTAL HEALTH ---
    print("\n--- MENTAL HEALTH ---")
    stress = ask_scale_1_5("Do you experience stress/racing thoughts at bedtime?")
    diag_mh = ask_yes_no("Have you been diagnosed with depression or anxiety?")
    worry = ask_scale_1_5("Do you worry excessively about not sleeping enough?")
    mood = ask_scale_1_5("Do mood changes affect your sleep quality?")

    # --- SECTION 5: ENVIRONMENT ---
    print("\n--- ENVIRONMENT ---")
    room_qual = ask_scale_1_5("Is your bedroom quiet, dark, and comfortable?", label_low="Not at all", label_high="Perfect")
    noise = ask_scale_1_5("Are you disturbed by noise or light at night?")

    # --- SECTION 6: DIET ---
    print("\n--- DIET ---")
    heavy_meal = ask_scale_1_5("Do you eat heavy meals close to bedtime?")
    caff_pm = ask_scale_1_5("Do you drink caffeine after 6 PM?")
    alc_bed = ask_scale_1_5("Do you consume alcohol before sleep?")
    diet_bal = ask_scale_1_5("Do you follow a balanced diet?", label_low="Very Poor", label_high="Excellent")

    # --- SECTION 7: TECHNOLOGY ---
    print("\n--- TECHNOLOGY ---")
    tech_hr = ask_scale_1_5("Do you use phone/TV within an hour before sleep?")
    scroll = ask_scale_1_5("Do you scroll social media while in bed?")
    tech_int = ask_scale_1_5("Do you feel technology interferes with your sleep?")

    # --- SECTION 8: CHRONOBIOLOGY ---
    print("\n--- CHRONOBIOLOGY ---")
    chronotype = ask_choice("Are you a morning person or night owl?", ["Morning", "Neutral", "Night owl"])
    consistent = ask_scale_1_5("Do you wake up at consistent times (even weekends)?")
    adjust = ask_scale_1_5("Is it difficult to adjust sleep times after changes?")
    alert_morn = ask_scale_1_5("How alert do you feel in the morning?", label_low="Groggy", label_high="Very Alert")

    # --- SECTION 9: SLEEP HYGIENE ---
    print("\n--- SLEEP HYGIENE ---")
    routine = ask_scale_1_5("Do you maintain a consistent bedtime routine?")
    bed_use = ask_yes_no("Do you use your bed mainly for sleep (not for working/eating)?")
    avoid_scr = ask_scale_1_5("Do you avoid screens/bright light before sleep?", label_low="Never (Use screens)", label_high="Always (Avoid)")
    naps = ask_scale_1_5("Do you nap for more than 30 minutes during the day?")

    # --- SECTION 10: SOCIAL FACTORS ---
    print("\n--- SOCIAL FACTORS ---")
    soc_stress = ask_scale_1_5("Are you experiencing personal/work stress?")
    fam_prob = ask_scale_1_5("Do relationship/family problems affect your sleep?")
    lonely = ask_scale_1_5("Do you feel lonely or lack emotional support?")
    soc_sat = ask_scale_1_5("How satisfied are you with your social life?", label_low="Dissatisfied", label_high="Satisfied")

    # --- SECTION 11: MEDICAL HISTORY ---
    print("\n--- MEDICAL HISTORY ---")
    pain = ask_yes_no("Do you suffer from chronic pain that disturbs sleep?")
    meds = ask_yes_no("Do you take medication that might affect sleep?")
    neuro = ask_yes_no("Diagnosed with neurological or respiratory disorder?")

    # --- SECTION 12: SYMPTOM CHECKER ---
    print("\n--- SYMPTOM CHECKER ---")
    # Insomnia
    ins_fall = ask_scale_1_5("[1/6] Difficulty falling asleep?")
    ins_stay = ask_scale_1_5("[1/6] Wake up frequently during the night?")
    ins_early = ask_scale_1_5("[1/6] Wake up too early and can't fall back?")
    ins_tired = ask_scale_1_5("[1/6] Feel tired even after sleeping?")
    
    # RLS
    rls_urge = ask_scale_1_5("[2/6] Uncontrollable urge to move legs while resting?")
    rls_worse = ask_scale_1_5("[2/6] Sensations worse in the evening/night?")
    rls_help = ask_scale_1_5("[2/6] Does movement relieve the discomfort?")
    
    # Apnea
    ap_snore = ask_scale_1_5("[3/6] Snore loudly or stop breathing?")
    ap_choke = ask_scale_1_5("[3/6] Wake up choking or gasping?")
    ap_head = ask_scale_1_5("[3/6] Morning headaches or dry mouth?")
    ap_sleepy = ask_scale_1_5("[3/6] Excessive daytime sleepiness?")
    
    # Narcolepsy
    na_att = ask_scale_1_5("[4/6] Sudden sleep attacks during daytime?")
    na_cata = ask_scale_1_5("[4/6] Muscle weakness during strong emotions?")
    na_hall = ask_scale_1_5("[4/6] Vivid hallucinations when falling asleep?")
    na_para = ask_scale_1_5("[4/6] Sleep paralysis?")
    
    # CRSD
    cr_time = ask_scale_1_5("[5/6] Sleep times much later/earlier than desired?")
    cr_soc = ask_scale_1_5("[5/6] Struggle to sleep at normal hours?")
    cr_alert = ask_scale_1_5("[5/6] Alert at night but sleepy in morning?")
    
    # Parasomnia
    pa_act = ask_scale_1_5("[6/6] Sleepwalk, talk, or perform actions?")
    pa_night = ask_scale_1_5("[6/6] Frequent nightmares?")
    pa_dream = ask_scale_1_5("[6/6] Act out dreams (move/shout)?")

    # --- DECLARE FACTS INTO ENGINE ---
    print("\n[Thinking...] Analyzing patterns and cross-referencing habits...")
    
    engine.declare(Person(
        # Demographics
        gender=gender, age=age,
        # Lifestyle
        sleep_hrs=sleep_hrs, irregular=irregular, work_shift=shifts, physical_activity=phys_act,
        # Quality
        fall_time=fall_time, wake_night=wake_night, refreshed=refreshed,
        # Mental
        mental_stress=stress, diagnosed_dep_anx=diag_mh, worry_sleep=worry, mood_change=mood,
        # Env
        room_quality=room_qual, noise_light=noise,
        # Diet
        heavy_meal=heavy_meal, caffeine_pm=caff_pm, alcohol_bed=alc_bed, diet_bal=diet_bal,
        # Tech
        tech_hr=tech_hr, scroll_bed=scroll, tech_interferes=tech_int,
        # Chrono
        chrono_type=chronotype, consistent=consistent, adjust_diff=adjust, alert_morning=alert_morn,
        # Hygiene
        routine=routine, bed_usage=bed_use, avoid_scr=avoid_scr, naps=naps,
        # Social
        social_stress=soc_stress, fam_prob=fam_prob, social_lonely=lonely, social_sat=soc_sat,
        # Medical
        chronic_pain=pain, medication_sleep=meds, diagnosed_neuro_resp=neuro,
        # Symptoms
        insomnia_fall=ins_fall, insomnia_stay=ins_stay, insomnia_early=ins_early, insomnia_tired=ins_tired,
        rls_urge=rls_urge, rls_worse_night=rls_worse, rls_move_help=rls_help,
        apnea_snore=ap_snore, apnea_choke=ap_choke, apnea_headache=ap_head, apnea_sleepy=ap_sleepy,
        narco_attack=na_att, narco_cata=na_cata, narco_hallu=na_hall, narco_paralysis=na_para,
        crsd_timing=cr_time, crsd_social=cr_soc, crsd_alert_night=cr_alert,
        para_act=pa_act, para_nightmare=pa_night, para_acting_out=pa_dream
    ))

    # --- FIRE RULES ---
    engine.run()

    # --- EXTRACT RESULTS ---
    diagnoses = [f['name'] for f in engine.facts.values() if isinstance(f, Diagnosis)]
    advice_list = [f['text'] for f in engine.facts.values() if isinstance(f, Advice)]

    # --- DISPLAY FINAL REPORT ---
    print("\n\n#################################################")
    print("              FINAL ASSESSMENT REPORT            ")
    print("#################################################")
    
    print("\n🔍 DIAGNOSTIC FINDINGS:")
    if diagnoses:
        for d in set(diagnoses): 
            print(f"   🔴 POSITIVE FOR: {d}")
    else:
        print("   🟢 NO CLINICAL DISORDER DETECTED.")
        print("   (Symptoms do not meet the threshold for a specific disorder)")

    print("\n📋 EXPERT COACHING & RECOMMENDATIONS:")
    if advice_list:
        # Sort and remove duplicates
        unique_advice = sorted(list(set(advice_list)))
        for a in unique_advice:
            print(f"   {a}")
    else:
        print("   ✅ You seem to have excellent sleep habits! Keep it up.")
    
    print("\n#################################################")
    print("DISCLAIMER: This system is for educational purposes only.")
    print("It is NOT a substitute for professional medical diagnosis.")
    print("#################################################")

if __name__ == "__main__":
    run_system()