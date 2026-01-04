# 🌙 Sleep Disorder Expert System & Coach

A robust, modular **Expert System** built in Python that analyzes sleep patterns, calculates the probability of specific sleep disorders using weighted scoring, and provides context-aware coaching advice based on a customizable knowledge base.

> **Note:** This project demonstrates the implementation of a Rule-Based Expert System combined with Weighted Confidence Scoring.

---

## 🚀 Features

*   **📊 Weighted Diagnostic Engine:** Unlike simple "Yes/No" classifiers, this system calculates a **Confidence Score (0-100%)** for 6 major sleep disorders:
    *   Insomnia
    *   Obstructive Sleep Apnea (OSA)
    *   Restless Legs Syndrome (RLS)
    *   Narcolepsy
    *   Circadian Rhythm Sleep Disorder (CRSD)
    *   Parasomnia
*   **🧠 Context-Aware Coaching:** The logic engine links diagnoses with habits.
    *   *Example:* If a user drinks coffee at 7 PM, the advice changes depending on whether they have *Insomnia* (Critical Stop) or just *Poor Hygiene* (General Advice).
*   **📂 Data-Driven Knowledge Base:** Coaching rules are stored in an external `.json` file, allowing medical logic to be updated without touching the source code.
*   **🧩 Modular Architecture:** Clean separation between Data, Logic (Math/Rules), and Interface.
*   **🐍 Python 3.10+ Compatible:** Includes patches for compatibility with older expert system libraries.

---


## 🛠️ Installation & Usage

### Prerequisites
*   Python 3.8 or higher

### Steps
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/sleep-expert-system.git
    cd sleep-expert-system
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
---

## 📝 To-Do List / Roadmap
### 🎨 User Interface
- [x] **Migrate to Streamlit:** Build a web-based UI to replace the Command Line Interface (CLI).