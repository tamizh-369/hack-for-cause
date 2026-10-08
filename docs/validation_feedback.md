# Peer Review & Design Feedback Log (Phase 4)

**Project:** Public Health Claim Watchdog  
**Date:** October 2026  
**Session Type:** Informal Peer & Mentor Review Session  
**Participants:** Project Developer & Peer Reviewer (Student Fact-Checking / Open Data Enthusiast)

---

## 1. Prototype Walkthrough Conducted
During this review session, we walked through the initial prototype:
1. Running claim verification on provisional data (`release_1.csv`) vs audited data (`release_2.csv`) for Tamil Nadu districts.
2. The automatic trigger of a **Revision Drift Alert** when figures changed between releases.
3. The arithmetic breakdown in the evidence table (baseline, outcome, delta).
4. Explanations rendered in English, Hindi (हिंदी), and Tamil (தமிழ்).
5. The reviewer console (Approve / Reject buttons) and the session audit trail.

---

## 2. Direct Feedback Received & Adjustments

### Point 1: Don't label missing data as "debunked"
- **Reviewer Comment:**  
  *"If a district is missing data or has a spelling typo, calling the claim 'False' or 'Unsupported' is unfair. That's a data gap, not necessarily a false claim."*
- **What was adjusted:**  
  We ensured the engine strictly routes any data validation failure (missing cells, unmapped indicators, missing periods) to **`Needs review`**, explicitly preventing it from being flagged as Unsupported.

### Point 2: Keep the tone neutral and non-accusatory
- **Reviewer Comment:**  
  *"Saying 'Governments quietly change numbers and no one catches it' sounds accusatory. Routine audits and reconciliations happen all the time in state health surveys. Keep the phrasing objective."*
- **What was adjusted:**  
  Reworded explanations and pitch script to: *"Published figures are sometimes revised upon routine data auditing, and claims quoted earlier may no longer match."*

### Point 3: Need transparent math, not a black-box verdict
- **Reviewer Comment:**  
  *"I want to see the exact numbers: what was the old percentage, what was the new percentage, and what was the delta. If that's clear, people can trust the verdict."*
- **What was adjusted:**  
  Kept the Verifiable Evidence Table front and center, displaying baseline number, outcome number, net difference, and threshold criteria.

### Point 4: Regional Language Focus for Tamil Nadu
- **Reviewer Comment:**  
  *"Since the state focus is Tamil Nadu, Tamil explanations must feel natural and accurate, not like broken Google Translate. Hindi is also good for broader national reach."*
- **What was adjusted:**  
  Refined pre-written templates in Tamil (தமிழ்) and Hindi (हिंदी) with natural phrasing for public health metrics. Removed unbuilt language mentions.

---

## 3. Honest Prototype Status
- All sample datasets are currently simulated releases structured around official MoHFW HMIS reporting formats for Tamil Nadu districts.
- The pipeline processes CSV files deterministically with zero paid API dependencies.
