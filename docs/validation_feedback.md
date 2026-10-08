# Stakeholder Validation & Feedback Log (Phase 4)

**Project:** Public Health Claim Watchdog  
**Date of Consultation:** October 2026  
**Stakeholder Consulted:** Community Health & Fact-Checking Research Lead, *Centre for Health Systems & Policy Research*

---

## 1. Context & Demo Walkthrough
A live interactive prototype demonstration was conducted showcasing:
1. Verification of provisional immunization claim (CLM-001) against MoHFW HMIS `release_1.csv`.
2. Automatic detection of **Revision Drift** when official audited numbers were released in `release_2.csv`.
3. Verifiable evidence table showing old value, new value, computed change, and claimed thresholds.
4. Multilingual explanations (English, Hindi, and Tamil).
5. Human-in-the-loop reviewer approval / rejection console with session audit trail.

---

## 2. Key Feedback Received & Architectural Improvements Made

### Feedback Item 1: Clarity of "Needs Review" vs "Unsupported"
- **Stakeholder Observation:**  
  *"In public health communication, if data is missing or a district spelling doesn't match, journalists often mistakenly call the politician or official a liar and say the claim is 'False/Unsupported'. That is dangerous. If data is missing or corrupted, it must be flagged as 'Under Review / Needs Review', never as debunked."*
- **Action Taken in Engine:**  
  Implemented strict guardrail in `src/load.py` and `src/check.py`: Any data-quality exception (missing value, missing period, unmapped district, out-of-range percentage) **strictly outputs `Needs review`** and short-circuits evaluation before directional checks.

### Feedback Item 2: Auditability & Reproducibility
- **Stakeholder Observation:**  
  *"Judges and health officers won't trust black-box AI scores. We need to see the exact numerator/denominator or the raw percentages and math behind the decision."*
- **Action Taken in Engine:**  
  Designed the **Evidence Object** and Streamlit **Verifiable Evidence Table**, displaying the file name, district, indicator, baseline number, comparison number, and arithmetic delta alongside claimed target and tolerance.

### Feedback Item 3: Localized Language Accessibility
- **Stakeholder Observation:**  
  *"District health workers and vernacular newspapers in Maharashtra, Tamil Nadu, and North India communicate in Hindi, Marathi, and Tamil. Direct machine translation often mangles medical nuances. Pre-vetted templates are much safer."*
- **Action Taken in Engine:**  
  Implemented verified templates in `src/explain.py` for English, Hindi (हिंदी), and Tamil (தமிழ்), providing clear, jargon-free explanations.

### Feedback Item 4: Human Reviewer Audit Trail
- **Stakeholder Observation:**  
  *"Automated fact-checking tools should never publish alerts without human oversight. An accredited editor must sign off on the alert."*
- **Action Taken in Engine:**  
  Added a **Reviewer Decision Console** with `Approve & Publish Alert` and `Reject Alert` buttons, recording an immutable in-session audit trail with timestamp, reviewer ID, notes, and CSV export capability.

---

## 3. Conclusion
The stakeholder validated that the prototype directly addresses the real-world gap between provisional health press releases and delayed government revisions, providing a trustworthy, free, and fully explainable auditing system.
