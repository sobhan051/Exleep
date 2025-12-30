# src/logic/scoring.py

class ScoringEngine:
    """
    Calculates weighted confidence scores (0-100%) for sleep disorders.
    """
    
    @staticmethod
    def normalize(val):
        """Converts 1-5 input scale to 0-4 math scale."""
        return val - 1

    @staticmethod
    def calculate_confidence(data):
        results = {}
        
        # --- 1. INSOMNIA ---
        score = (ScoringEngine.normalize(data['insomnia_fall']) * 2.0 +
                 ScoringEngine.normalize(data['insomnia_stay']) * 2.0 +
                 ScoringEngine.normalize(data['insomnia_early']) * 2.0 +
                 ScoringEngine.normalize(data['insomnia_tired']) * 1.5)
        max_score = (4*2 + 4*2 + 4*2 + 4*1.5) # 30
        results['Insomnia'] = (score / max_score) * 100

        # --- 2. SLEEP APNEA ---
        score = (ScoringEngine.normalize(data['apnea_snore']) * 2.0 +
                 ScoringEngine.normalize(data['apnea_choke']) * 3.0 +
                 ScoringEngine.normalize(data['apnea_headache']) * 1.0 +
                 ScoringEngine.normalize(data['apnea_sleepy']) * 2.0)
        max_score = (4*2 + 4*3 + 4*1 + 4*2) # 32
        results['Obstructive Sleep Apnea'] = (score / max_score) * 100

        # --- 3. RLS ---
        score = (ScoringEngine.normalize(data['rls_urge']) * 3.0 +
                 ScoringEngine.normalize(data['rls_worse_night']) * 2.0 +
                 ScoringEngine.normalize(data['rls_move_help']) * 2.0)
        max_score = (4*3 + 4*2 + 4*2) # 28
        results['Restless Legs Syndrome'] = (score / max_score) * 100

        # --- 4. NARCOLEPSY ---
        score = (ScoringEngine.normalize(data['narco_attack']) * 3.0 +
                 ScoringEngine.normalize(data['narco_cata']) * 3.0 +
                 ScoringEngine.normalize(data['narco_hallu']) * 1.5 +
                 ScoringEngine.normalize(data['narco_paralysis']) * 1.5)
        max_score = (4*3 + 4*3 + 4*1.5 + 4*1.5) # 36
        results['Narcolepsy'] = (score / max_score) * 100

        # --- 5. CRSD ---
        score = (ScoringEngine.normalize(data['crsd_timing']) * 2.0 +
                 ScoringEngine.normalize(data['crsd_social']) * 2.0 +
                 ScoringEngine.normalize(data['crsd_alert_night']) * 2.0)
        max_score = (4*2 + 4*2 + 4*2) # 24
        results['Circadian Rhythm Disorder'] = (score / max_score) * 100

        # --- 6. PARASOMNIA ---
        score = (ScoringEngine.normalize(data['para_act']) * 3.0 +
                 ScoringEngine.normalize(data['para_nightmare']) * 1.5 +
                 ScoringEngine.normalize(data['para_dream']) * 1.0)
        max_score = (4*3 + 4*1.5 + 4*1) # 22
        results['Parasomnia'] = (score / max_score) * 100

        return results