# knowledge_base.py - Fully Comprehensive Knowledge Base for Barauni Refinery
# Updated: January 2026

IOCL_DATA = {
    "company_info": {
        "name": "Indian Oil Corporation Limited (IOCL)",
        "status": "Maharatna PSU",
        "leadership": "Shri Shrikant Madhav Vaidya (Chairman)",
        "vision": "The Energy of India",
        "values": "Care, Innovation, Passion, Trust"
    },
    
    "barauni_refinery": {
        "location": "Begusarai, Bihar - 851114",
        "established": "1964 (Collaboration with USSR)",
        "capacity": "Current: 6.0 MMTPA | Expanding to: 9.0 MMTPA",
        "google_maps": "https://maps.app.goo.gl/0 (Barauni Refinery Main Gate)",
        "working_hours": "Monday to Friday: 10:00 AM - 5:00 PM",
        "official_contacts": "L&D Centre: 06243-275279 / 275272",
        "township": "Indradhanush Township"
    },

    "internship_details": {
        "mentor": "Mr. Sudhanshu Pandey (Information Systems Officer)",
        "mentor_contact": "Email: kumarsunit3@indianoil.in | Mob: 9452168944",
        "reporting_flow": "1. CISF Pass Section -> 2. L&D Centre",
        "mandatory_docs": [
            "Character & Antecedent Certificate (signed by HOD)",
            "Personal Accidental Insurance (Min Rs. 1 Lakh cover)",
            "College ID Card & Training Letter",
            "Project Report (for completion certificate)"
        ],
        "dress_code": {
            "Admin_Area": "Full Sleeve Shirt (Coloured), Formal Black Pants",
            "Plant_Area": "Mandatory PPE: Helmet, Safety Shoes, Dangri"
        },
        "prohibited_items": "Mobile phones, Laptops, and Pen Drives are STRICTLY PROHIBITED inside the plant area."
    },

    "fuel_prices_jan_2026": {
        "petrol_begusarai": "Rs. 105.16 per Litre (Current as of Jan 3, 2026)",
        "diesel_begusarai": "Rs. 91.85 per Litre",
        "lpg_indane": "Approx Rs. 900-1000 (Check IndianOil One app for daily dynamic pricing)",
        "booking_whatsapp": "7588888824",
        "booking_call": "7718955555"
    },

    "safety_helmet_codes": {
        "White": "Officers, Managers, Engineers, and Supervisors",
        "Yellow": "General Workers, Laborers, and Technical Staff",
        "Blue": "Electricians and Technical Maintenance",
        "Red": "Fire & Safety Personnel",
        "Green": "Safety Officers and Environmental Team",
        "Grey": "Site Visitors and Trainees/Interns"
    },

    "safety_hazards": [
        "Major Accident Explosions",
        "Vapor Cloud Explosions (VCE)",
        "Toxic Releases (H2S, SO2)",
        "Boiling Liquid Expanding Vapor Explosion (BLEVE)"
    ],

    "career_guide_cse": {
        "recruitment_path": "Through GATE Exam (Graduate Aptitude Test in Engineering)",
        "selection_process": "GATE Score -> Group Discussion (GD) -> Personal Interview (PI)",
        "eligible_branches": [
            "Computer Science (CS)", "Information Technology (IT)", 
            "Mechanical", "Electrical", "Chemical", "Civil", "Instrumentation"
        ],
        "cse_roles": [
            "Information Systems (IS) Officer",
            "Cybersecurity & Network Management",
            "SAP/ERP System Administration",
            "Digital Refinery (Industry 4.0) Projects"
        ],
        "eligibility": "B.E/B.Tech with min 65% (General/OBC) or 55% (SC/ST). Age limit: Max 26 years."
    }
}

FAQ_PATTERNS = [
    {
        "intent": "greeting", 
        "patterns": ["hi", "hello", "namaste", "hey"], 
        "responses": ["Namaste! I am your Barauni Refinery Assistant. How can I help you today?"]
    },
    {
        "intent": "fuel_rates",
        "patterns": ["petrol price", "diesel rate", "fuel cost", "lpg price"],
        "responses": [f"Today in Begusarai: Petrol is {IOCL_DATA['fuel_prices_jan_2026']['petrol_begusarai']} and Diesel is {IOCL_DATA['fuel_prices_jan_2026']['diesel_begusarai']}."]
    },
    {
        "intent": "helmet_colors",
        "patterns": ["helmet color", "cap color", "white cap", "red helmet"],
        "responses": ["Helmet Codes: White=Officers/Engineers, Yellow=Workers, Blue=Electricians, Red=Fire & Safety, Grey=Visitors."]
    },
    {
        "intent": "job_process",
        "patterns": ["job kaise paye", "how to join iocl", "recruitment", "cse job"],
        "responses": ["Engineers join via GATE score followed by GD/PI. CSE students work in the Information Systems (IS) department."]
    },
    {
        "intent": "safety_rules",
        "patterns": ["safety rules", "hazards", "phone allowed", "laptop allowed"],
        "responses": ["Refinery hazards include explosions and toxic releases. Mobile phones and laptops are NOT allowed inside."]
    },
    {
        "intent": "internship_mentor",
        "patterns": ["who is mentor", "sudhanshu pandey", "officer name", "internship"],
        "responses": [f"Your mentor is {IOCL_DATA['internship_details']['mentor']}. Contact: {IOCL_DATA['internship_details']['mentor_contact']}."]
    }
]