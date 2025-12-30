import json
import operator
import os

class JSONCoachingEngine:
    def __init__(self, rules_file="src/data/rules.json"):
        # Load rules from JSON file
        self.rules = self._load_rules(rules_file)
        
        # Map string operators to Python functions
        self.ops = {
            "==": operator.eq,
            "!=": operator.ne,
            ">": operator.gt,
            ">=": operator.ge,
            "<": operator.lt,
            "<=": operator.le,
        }

    def _load_rules(self, filepath):
        """Safely loads the JSON file."""
        try:
            # Construct absolute path to ensure it finds the file
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            full_path = os.path.join(base_path, filepath)
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Could not find rules file at {filepath}")
            return []

    def evaluate(self, person_data, diagnoses):
        """
        person_data: Dictionary of user answers (e.g., {'caffeine_pm': 3})
        diagnoses: List of diagnosis strings (e.g., ['Insomnia'])
        """
        advice_list = []

        for rule in self.rules:
            # 1. Check Condition (e.g., "caffeine_pm >= 3")
            condition_met = self._check_condition(rule, person_data)
            
            # 2. Check Context (Diagnosis requirements)
            context_met = self._check_context(rule, diagnoses)

            if condition_met and context_met:
                advice_list.append(rule['advice'])

        return advice_list

    def _check_condition(self, rule, person_data):
        """Parses the 'condition' string (e.g., 'age >= 3')"""
        if 'condition' not in rule:
            return True # Always run if no condition

        # Split string: "variable operator value"
        # Example: "caffeine_pm >= 3"
        try:
            parts = rule['condition'].split()
            var_name = parts[0]
            op_str = parts[1]
            
            # Handle string values (e.g. sleep_hrs == '< 4')
            if "'" in rule['condition'] or '"' in rule['condition']:
                target_val = rule['condition'].split(op_str)[1].strip().strip("'").strip('"')
            else:
                target_val = float(parts[2]) # Assume number

            # Get user's actual value
            user_val = person_data.get(var_name)
            
            # Skip if user didn't answer this question
            if user_val is None:
                return False

            # Compare
            if op_str in self.ops:
                return self.ops[op_str](user_val, target_val)
            
        except Exception as e:
            print(f"Error parsing rule {rule.get('id')}: {e}")
            return False
        
        return False

    def _check_context(self, rule, diagnoses):
        """Checks 'required_diagnosis' and 'block_if_diagnosis'"""
        
        # Requirement Check
        if 'required_diagnosis' in rule:
            if rule['required_diagnosis'] not in diagnoses:
                return False # Diagnosis missing, don't show advice

        # Blocking Check (Prevent duplicate/conflicting advice)
        if 'block_if_diagnosis' in rule:
            if rule['block_if_diagnosis'] in diagnoses:
                return False # Diagnosis present, block this generic advice

        return True