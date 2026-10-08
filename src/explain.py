"""Bilingual explanation generator module for Public Health Claim Watchdog.

Generates transparent, human-readable explanations in English and draft translations
in Hindi and Tamil (human review in progress) for each verdict and drift alert.
"""

from typing import Any, Dict, Optional

TEMPLATES_EN = {
    "Supported": (
        "✅ **VERIFIED / SUPPORTED**: The claim regarding {indicator_name} in {district} "
        "is consistent with data published in `{release_file}`.\n\n"
        "**Key Findings:**\n"
        "- Baseline value ({period_from}): **{old_value}%**\n"
        "- Comparison value ({period_to}): **{new_value}%**\n"
        "- Net observed change: **{change:+g}%**\n"
        "- Claimed direction: **{direction}** (claimed target: ~{claimed_magnitude}% ± {tolerance}%)\n\n"
        "Official health records confirm that the trend matches the public statement."
    ),
    "Unsupported": (
        "❌ **UNSUPPORTED**: The claim regarding {indicator_name} in {district} "
        "is **not substantiated** by data published in `{release_file}`.\n\n"
        "**Discrepancy Details:**\n"
        "- Baseline in release ({period_from}): **{old_value}%**\n"
        "- Outcome in release ({period_to}): **{new_value}%**\n"
        "- Actual observed change: **{change:+g}%**\n"
        "- Claimed assertion: **{direction}** by ~{claimed_magnitude}% ± {tolerance}%\n\n"
        "**Reason:** {reason}\n\n"
        "*Published figures are sometimes revised upon routine data auditing, and claims quoted earlier may no longer match current official records.*"
    ),
    "Needs review": (
        "⚠️ **NEEDS REVIEW**: The claim regarding {indicator_name} in {district} "
        "cannot be verified at this stage due to data quality or schema constraints.\n\n"
        "**Review Diagnostics:**\n"
        "- Dataset checked: `{release_file}`\n"
        "- Issue encountered: **{reason}**\n\n"
        "*Per public health verification standards, missing or unverified data generates a 'Needs review' status rather than marking it unsupported.*"
    ),
    "Drift_Alert": (
        "🚨 **OFFICIAL REVISION DRIFT ALERT**:\n\n"
        "This claim matched provisional release data (`{file_r1}`) as **{verdict_r1}**,\n"
        "but subsequent audited data (`{file_r2}`) adjusted the indicators, shifting the verdict to **{verdict_r2}**.\n\n"
        "**Comparison Summary:**\n"
        "- Provisional reported change: **{change_r1:+g}%**\n"
        "- Audited reconciled change: **{change_r2:+g}%**\n\n"
        "*Published figures are sometimes revised upon routine data auditing, and claims quoted earlier may no longer match. Reviewers should record this revision in the audit trail.*"
    ),
}

TEMPLATES_HI = {
    "Supported": (
        "✅ **सत्यापित (समर्थित)**: {district} में {indicator_name} से संबंधित दावा `{release_file}` "
        "के आधिकारिक आंकड़ों के अनुरूप है।\n\n"
        "**मुख्य आंकड़े:**\n"
        "- आधारभूत मान ({period_from}): **{old_value}%**\n"
        "- तुलनात्मक मान ({period_to}): **{new_value}%**\n"
        "- शुद्ध वास्तविक बदलाव: **{change:+g}%**\n"
        "- दावा की गई दिशा: **{direction}** (लक्षित मान: ~{claimed_magnitude}% ± {tolerance}%)\n\n"
        "स्वास्थ्य रिकॉर्ड पुष्टि करते हैं कि सरकारी आंकड़ों में यह प्रगति दर्ज है।"
    ),
    "Unsupported": (
        "❌ **असमर्थित**: {district} में {indicator_name} के संबंध में किया गया दावा `{release_file}` "
        "के आंकड़ों द्वारा प्रमाणित नहीं होता है।\n\n"
        "**विसंगति विवरण:**\n"
        "- आधारभूत वर्ष ({period_from}): **{old_value}%**\n"
        "- परिणाम वर्ष ({period_to}): **{new_value}%**\n"
        "- दर्ज वास्तविक परिवर्तन: **{change:+g}%**\n"
        "- किया गया दावा: **{direction}** (~{claimed_magnitude}% ± {tolerance}%)\n\n"
        "**कारण:** {reason}\n\n"
        "*प्रकाशित सरकारी आंकड़ों में नियमित संशोधन होते रहते हैं, इसलिए पहले उद्धृत किए गए दावे बाद के आंकड़ों से भिन्न हो सकते हैं।*"
    ),
    "Needs review": (
        "⚠️ **समीक्षा आवश्यक**: {district} में {indicator_name} संबंधी दावे को डेटा गुणवत्ता "
        "या अपूर्ण प्रविष्टि के कारण अभी सत्यापित नहीं किया जा सकता।\n\n"
        "**जांच विवरण:**\n"
        "- जांची गई फाइल: `{release_file}`\n"
        "- चिन्हित समस्या: **{reason}**\n\n"
        "*सार्वजनिक स्वास्थ्य सुरक्षा मानकों के अनुसार, अपूर्ण डेटा पर स्थिति 'समीक्षा आवश्यक' रखी जाती है।*"
    ),
    "Drift_Alert": (
        "🚨 **डेटा संशोधन सूचना (डेटा ड्रिफ्ट)**:\n\n"
        "यह दावा प्रारंभिक अनंतिम रिपोर्ट (`{file_r1}`) में **{verdict_r1}** था,\n"
        "परंतु ऑडिटेड रिपोर्ट (`{file_r2}`) जारी होने के बाद इसकी स्थिति बदलकर **{verdict_r2}** हो गई है।\n\n"
        "**तुलनात्मक विवरण:**\n"
        "- अनंतिम बदलाव: **{change_r1:+g}%**\n"
        "- ऑडिट किया गया बदलाव: **{change_r2:+g}%**\n\n"
        "*सरकारी आंकड़ों में नियमित ऑडिट के बाद संशोधन होना सामान्य है; इसलिए पहले किए गए दावों की अद्यतन आंकड़ों से पुनः पुष्टि आवश्यक है।*"
    ),
}

TEMPLATES_TA = {
    "Supported": (
        "✅ **உறுதிப்படுத்தப்பட்டது (ஆதரிக்கப்பட்டது)**: {district} மாவட்டத்தில் {indicator_name} குறித்த கூற்று "
        "`{release_file}` இல் உள்ள அதிகாரப்பூர்வ புள்ளிவிவரங்களுடன் ஒத்துப்போகிறது.\n\n"
        "**முக்கிய புள்ளிவிவரங்கள்:**\n"
        "- ஆரம்ப நிலை ({period_from}): **{old_value}%**\n"
        "- பிந்தைய நிலை ({period_to}): **{new_value}%**\n"
        "- நிகர மாற்றம்: **{change:+g}%**\n"
        "- கோரப்பட்ட அளவு: **{direction}** (~{claimed_magnitude}% ± {tolerance}%)\n\n"
        "சுகாதாரத் துறைப் பதிவேடுகள் இக்கூற்றை உறுதிப்படுத்துகின்றன."
    ),
    "Unsupported": (
        "❌ **ஆதரிக்கப்படவில்லை**: {district} மாவட்டத்தில் {indicator_name} பற்றிய அறிக்கை "
        "`{release_file}` இல் உள்ள புள்ளிவிவரங்களுடன் பொருந்தவில்லை.\n\n"
        "**விவரங்கள்:**\n"
        "- ஆரம்ப நிலை ({period_from}): **{old_value}%**\n"
        "- இறுதி நிலை ({period_to}): **{new_value}%**\n"
        "- உண்மையான மாற்றம்: **{change:+g}%**\n"
        "- கோரப்பட்ட அளவு: **{direction}** (~{claimed_magnitude}% ± {tolerance}%)\n\n"
        "**காரணம்:** {reason}\n\n"
        "*அரசு தரவுகள் தணிக்கைக்குப் பின் மாற்றியமைக்கப்படுவது வழக்கமான நடைமுறை என்பதால், முன்னதாக தெரிவிக்கப்பட்ட கூற்றுகள் பிந்தைய புள்ளிவிவரங்களுடன் மாறுபடக்கூடும்.*"
    ),
    "Needs review": (
        "⚠️ **மறுபரிசீலனை தேவை**: {district} மாவட்டத்தில் {indicator_name} பற்றிய கூற்றை தரவு பற்றாக்குறை "
        "அல்லது விடுபட்ட தகவல் காரணமாக தற்போது உறுதிப்படுத்த இயலவில்லை.\n\n"
        "**கண்டறியப்பட்ட காரணம்:** **{reason}**\n\n"
        "*பொது சுகாதார நெறிமுறைகளின்படி, போதுமான தரவு இல்லாதபோது அது 'மறுபரிசீலனை தேவை' என்றே வகைப்படுத்தப்படும்.*"
    ),
    "Drift_Alert": (
        "🚨 **தரவு மாற்ற எச்சரிக்கை (டிரிஃப்ட்)**:\n\n"
        "இக்கூற்று தற்காலிக அறிக்கையில் (`{file_r1}`) **{verdict_r1}** என இருந்தது; "
        "ஆனால் தணிக்கை செய்யப்பட்ட இறுதி அறிக்கையில் (`{file_r2}`) இதன் நிலை **{verdict_r2}** என மாறியுள்ளது.\n\n"
        "**மாற்ற விவரங்கள்:**\n"
        "- தற்காலிக அறிக்கையின் மாற்றம்: **{change_r1:+g}%**\n"
        "- தணிக்கை அறிக்கையின் மாற்றம்: **{change_r2:+g}%**\n\n"
        "*அரசு தரவுகள் அவ்வப்போது தணிக்கை செய்யப்பட்டு புதுப்பிக்கப்படுவதால், பழைய புள்ளிவிவரங்களை அடிப்படையாகக் கொண்ட கூற்றுகள் மாறுபடலாம்.*"
    ),
}

LANGUAGES = {
    "en": {"name": "English", "templates": TEMPLATES_EN},
    "hi": {"name": "हिंदी (Hindi)", "templates": TEMPLATES_HI},
    "ta": {"name": "தமிழ் (Tamil)", "templates": TEMPLATES_TA},
}


def explain_verdict(
    claim: Dict[str, Any],
    eval_result: Dict[str, Any],
    lang: str = "en",
) -> str:
    """Generate localized natural language explanation for a claim evaluation."""
    lang_data = LANGUAGES.get(lang, LANGUAGES["en"])
    templates = lang_data["templates"]

    verdict = eval_result.get("verdict", "Needs review")
    template = templates.get(verdict, templates["Needs review"])

    evidence = eval_result.get("evidence", {})
    indicator = claim.get("indicator", "")
    indicator_name = indicator.replace("_", " ").title()

    return template.format(
        indicator_name=indicator_name,
        district=evidence.get("district") or claim.get("district", "N/A"),
        release_file=evidence.get("file_name", "official_data.csv"),
        period_from=evidence.get("period_from", claim.get("period_from", "N/A")),
        period_to=evidence.get("period_to", claim.get("period_to", "N/A")),
        old_value=evidence.get("old_value", "N/A"),
        new_value=evidence.get("new_value", "N/A"),
        change=evidence.get("computed_change", 0.0),
        direction=evidence.get("claimed_direction", claim.get("direction", "N/A")),
        claimed_magnitude=evidence.get("claimed_magnitude", claim.get("magnitude", "N/A")),
        tolerance=evidence.get("tolerance", claim.get("tolerance", 0.0)),
        reason=eval_result.get("reason", "N/A"),
    )


def explain_drift(
    drift_result: Dict[str, Any],
    lang: str = "en",
) -> str:
    """Generate localized natural language explanation for a drift alert."""
    lang_data = LANGUAGES.get(lang, LANGUAGES["en"])
    template = lang_data["templates"]["Drift_Alert"]

    ev1 = drift_result.get("evidence_release_1", {})
    ev2 = drift_result.get("evidence_release_2", {})

    return template.format(
        verdict_r1=drift_result.get("verdict_release_1", "Unknown"),
        verdict_r2=drift_result.get("verdict_release_2", "Unknown"),
        file_r1=ev1.get("file_name", "release_1.csv"),
        file_r2=ev2.get("file_name", "release_2.csv"),
        change_r1=ev1.get("computed_change", 0.0),
        change_r2=ev2.get("computed_change", 0.0),
    )
