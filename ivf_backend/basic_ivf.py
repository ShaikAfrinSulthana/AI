"""
Basic IVF Knowledge Base - Fallback responses
Used when RAG engine is unavailable
"""

BASIC_IVF_KNOWLEDGE = {
    "ivf_process": {
        "question": "What is the IVF process?",
        "answer": "IVF (In Vitro Fertilization) is a multi-step process: 1) Ovarian stimulation with fertility drugs, 2) Egg retrieval procedure, 3) Fertilization in the lab, 4) Embryo culture, 5) Embryo transfer. The entire process typically takes 4-6 weeks.",
        "category": "Treatment Process"
    },
    "success_rates": {
        "question": "What are IVF success rates?",
        "answer": "IVF success rates vary by age: Under 35: 40-50%, 35-37: 30-40%, 38-40: 20-30%, Over 40: 10-20% per cycle. Success depends on many factors including egg quality, sperm quality, and clinic expertise.",
        "category": "Success Rates"
    },
    "medications": {
        "question": "What medications are used in IVF?",
        "answer": "Common IVF medications include: FSH (Follicle Stimulating Hormone), LH (Luteinizing Hormone), hCG trigger shot, GnRH agonists/antagonists, and progesterone for luteal phase support.",
        "category": "Medications"
    },
    "testing": {
        "question": "What tests are done before IVF?",
        "answer": "Pre-IVF testing typically includes: Blood tests (AMH, FSH, estradiol), semen analysis, uterine evaluation (HSG or sonohysterogram), infectious disease screening, and sometimes genetic carrier screening.",
        "category": "Testing"
    },
    "cost": {
        "question": "How much does IVF cost?",
        "answer": "IVF costs vary widely by location and clinic. In the US, one cycle typically costs $12,000-$15,000 plus medication costs of $3,000-$5,000. Many countries have different pricing structures and some insurance plans offer coverage.",
        "category": "Cost & Insurance"
    }
}

def get_basic_response(query: str) -> str:
    """Get basic IVF response for common questions"""
    query_lower = query.lower()
    
    # Simple keyword matching
    if any(word in query_lower for word in ['process', 'step', 'procedure']):
        return BASIC_IVF_KNOWLEDGE['ivf_process']['answer']
    elif any(word in query_lower for word in ['success', 'rate', 'chance']):
        return BASIC_IVF_KNOWLEDGE['success_rates']['answer']
    elif any(word in query_lower for word in ['medication', 'drug', 'injection']):
        return BASIC_IVF_KNOWLEDGE['medications']['answer']
    elif any(word in query_lower for word in ['test', 'blood', 'check']):
        return BASIC_IVF_KNOWLEDGE['testing']['answer']
    elif any(word in query_lower for word in ['cost', 'price', 'insurance']):
        return BASIC_IVF_KNOWLEDGE['cost']['answer']
    else:
        return "I understand you're asking about IVF. For detailed information about specific procedures, success rates, medications, or costs, please ask more specific questions. Remember to consult with healthcare providers for personalized medical advice."