"""Shared constants for the Vedic astrology knowledge base."""

VALID_PLANETS = {
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
}

VALID_HOUSES = set(range(1, 13))

VALID_SIGNS = {
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
}

VALID_NAKSHATRAS = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

VALID_DASHAS = [
    "Vimshottari",
    "Ashtottari",
    "Yogini",
    "Kalachakra",
]

VALID_YOGAS = [
    "Raja Yoga",
    "Dhana Yoga",
    "Viparita Raja Yoga",
    "Kala Sarpa Yoga",
    "Gaja Kesari Yoga",
    "Pancha Mahapurusha Yoga",
    "Budha Aditya Yoga",
    "Chandra Mangala Yoga",
]

VALID_DOSHAS = [
    "Mangal Dosha",
    "Kaal Sarp Dosha",
    "Pitru Dosha",
    "Nadi Dosha",
    "Guru Chandal Dosha",
    "Shani Sade Sati",
]

VALID_BOOKS = {
    "BPHS": "Brihat Parashara Hora Shastra",
    "Brihat_Jataka": "Brihat Jataka",
    "Phaladeepika": "Phaladeepika",
    "Saravali": "Saravali",
    "Jataka_Parijata": "Jataka Parijata",
    "Laghu_Parashari": "Laghu Parashari",
    "Hora_Sara": "Hora Sara",
    "Uttara_Kalamrita": "Uttara Kalamrita",
    "Jaimini_Sutras": "Jaimini Sutras",
}

DEFAULT_RULE_CATEGORIES = {
    "houses",
    "planets",
    "nakshatras",
    "dashas",
    "transits",
    "yogas",
    "doshas",
    "career",
    "marriage",
    "finance",
    "health",
    "relationships",
    "spirituality",
    "classical-texts",
}
