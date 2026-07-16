"""Vedic astrology constants used by the birth chart generator."""

SIGN_NAMES = [
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
]

SIGN_SYMBOLS = [
    "Ari",
    "Tau",
    "Gem",
    "Can",
    "Leo",
    "Vir",
    "Lib",
    "Sco",
    "Sag",
    "Cap",
    "Aqu",
    "Pis",
]

SIGN_ELEMENTS = {
    "Aries": "fire",
    "Taurus": "earth",
    "Gemini": "air",
    "Cancer": "water",
    "Leo": "fire",
    "Virgo": "earth",
    "Libra": "air",
    "Scorpio": "water",
    "Sagittarius": "fire",
    "Capricorn": "earth",
    "Aquarius": "air",
    "Pisces": "water",
}

SIGN_QUALITIES = {
    "Aries": "movable",
    "Taurus": "fixed",
    "Gemini": "dual",
    "Cancer": "movable",
    "Leo": "fixed",
    "Virgo": "dual",
    "Libra": "movable",
    "Scorpio": "fixed",
    "Sagittarius": "dual",
    "Capricorn": "movable",
    "Aquarius": "fixed",
    "Pisces": "dual",
}

SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

HOUSE_MEANINGS = {
    1: "Personality, body, appearance, self",
    2: "Wealth, speech, family, early education",
    3: "Siblings, courage, communication, short travels",
    4: "Home, mother, vehicles, happiness, land",
    5: "Children, intelligence, education, speculation",
    6: "Disease, enemies, debts, service, obstacles",
    7: "Marriage, partnerships, business, foreign lands",
    8: "Longevity, transformations, occult, inheritance",
    9: "Fortune, father, higher learning, religion",
    10: "Career, status, government, reputation",
    11: "Gains, friends, elder siblings, aspirations",
    12: "Losses, expenses, liberation, foreign residence",
}

HOUSE_TRINITY = {
    1: "dharma",
    5: "dharma",
    9: "dharma",
    2: "artha",
    6: "artha",
    10: "artha",
    3: "kama",
    7: "kama",
    11: "kama",
    4: "moksha",
    8: "moksha",
    12: "moksha",
}

HOUSE_KENDRA = {1, 4, 7, 10}
HOUSE_UPACHAYA = {3, 6, 10, 11}
HOUSE_MALEFIC = {6, 8, 12}
HOUSE_BENEFIC = {1, 5, 9}

NAKSHATRAS = [
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

NAKSHATRA_LORDS = [
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
]

NAKSHATRA_PADA_LORDS = [
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
]

PLANETS = [
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
]

PLANET_GENDERS = {
    "Sun": "male",
    "Moon": "female",
    "Mars": "male",
    "Mercury": "neutral",
    "Jupiter": "male",
    "Venus": "female",
    "Saturn": "neutral",
    "Rahu": "female",
    "Ketu": "neutral",
}

PLANET_ELEMENTS = {
    "Sun": "fire",
    "Moon": "water",
    "Mars": "fire",
    "Mercury": "earth",
    "Jupiter": "ether",
    "Venus": "water",
    "Saturn": "air",
    "Rahu": "air",
    "Ketu": "fire",
}

PLANET_COLORS = {
    "Sun": "#f97316",  # orange
    "Moon": "#94a3b8",  # silver
    "Mars": "#ef4444",  # red
    "Mercury": "#10b981",  # green
    "Jupiter": "#facc15",  # yellow
    "Venus": "#ec4899",  # pink
    "Saturn": "#1f2937",  # dark
    "Rahu": "#6366f1",  # indigo
    "Ketu": "#64748b",  # grey
}

PLANET_SYMBOLS = {
    "Sun": "Su",
    "Moon": "Mo",
    "Mars": "Ma",
    "Mercury": "Me",
    "Jupiter": "Ju",
    "Venus": "Ve",
    "Saturn": "Sa",
    "Rahu": "Ra",
    "Ketu": "Ke",
}

PLANET_SWISS_IDS = {
    "Sun": 0,
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 5,
    "Saturn": 6,
    "Rahu": 10,  # mean node
    "Ketu": -1,  # computed as opposite of Rahu
}

PLANET_DIGNITY_SCORES = {
    "exalted": 5,
    "moolatrikona": 4,
    "own": 3,
    "friendly": 2,
    "neutral": 1,
    "enemy": 0,
    "debilitated": -2,
}

PLANET_EXALTATION = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra",
    "Rahu": "Taurus",
    "Ketu": "Scorpio",
}

PLANET_DEBILITATION = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
    "Rahu": "Scorpio",
    "Ketu": "Taurus",
}

PLANET_MOOLATRIKONA = {
    "Sun": ("Leo", "Leo"),
    "Moon": ("Taurus", "Cancer"),
    "Mars": ("Aries", "Aries"),
    "Mercury": ("Virgo", "Virgo"),
    "Jupiter": ("Sagittarius", "Sagittarius"),
    "Venus": ("Libra", "Pisces"),
    "Saturn": ("Aquarius", "Capricorn"),
    "Rahu": ("Virgo", "Gemini"),
    "Ketu": ("Pisces", "Sagittarius"),
}

VALID_PLANETS = list(PLANET_SWISS_IDS.keys())

PLANET_OWN_SIGNS = {
    "Sun": {"Leo"},
    "Moon": {"Cancer"},
    "Mars": {"Aries", "Scorpio"},
    "Mercury": {"Gemini", "Virgo"},
    "Jupiter": {"Sagittarius", "Pisces"},
    "Venus": {"Taurus", "Libra"},
    "Saturn": {"Capricorn", "Aquarius"},
    "Rahu": {"Virgo", "Gemini"},
    "Ketu": {"Pisces", "Sagittarius"},
}

PLANET_FRIEND_SIGNS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
    "Rahu": {"Mercury", "Saturn", "Venus"},
    "Ketu": {"Mercury", "Mars", "Jupiter"},
}

PLANET_ENEMY_SIGNS = {
    "Sun": {"Saturn", "Venus"},
    "Moon": {"Rahu", "Ketu"},
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
    "Rahu": {"Sun", "Moon"},
    "Ketu": {"Sun", "Venus"},
}

DIGNITY_FRIENDLY = {
    "Sun": {"Aries", "Leo", "Scorpio", "Sagittarius"},
    "Moon": {"Taurus", "Cancer", "Libra", "Pisces"},
    "Mars": {"Aries", "Leo", "Scorpio", "Sagittarius"},
    "Mercury": {"Gemini", "Virgo", "Libra", "Aquarius"},
    "Jupiter": {"Aries", "Cancer", "Leo", "Scorpio", "Sagittarius", "Pisces"},
    "Venus": {"Taurus", "Gemini", "Virgo", "Libra", "Capricorn", "Aquarius"},
    "Saturn": {"Taurus", "Virgo", "Libra", "Capricorn", "Aquarius"},
    "Rahu": {"Taurus", "Gemini", "Virgo", "Libra", "Capricorn", "Aquarius"},
    "Ketu": {"Aries", "Cancer", "Leo", "Scorpio", "Sagittarius", "Pisces"},
}

COMBUST_ORBS = {
    "Sun": 0.0,
    "Moon": 12.0,
    "Mars": 17.0,
    "Mercury": 14.0,
    "Jupiter": 11.0,
    "Venus": 10.0,
    "Saturn": 16.0,
    "Rahu": 0.0,
    "Ketu": 0.0,
}

# Vimshottari dasha sequence and years
DASHA_SEQUENCE = [
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
]

DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

DASHA_TOTAL_YEARS = 120

HOUSE_LORD_NATURAL = {
    1: "Mars",
    2: "Venus",
    3: "Mercury",
    4: "Moon",
    5: "Sun",
    6: "Mercury",
    7: "Venus",
    8: "Mars",
    9: "Jupiter",
    10: "Saturn",
    11: "Saturn",
    12: "Jupiter",
}

# Aspects: planet -> list of houses aspected (relative to planet's own house)
# 7th is universal. Mars aspects 4,7,8. Saturn aspects 3,7,10. Jupiter aspects 5,9,12.
ASPECT_HOUSES = {
    "Sun": {7},
    "Moon": {7},
    "Mars": {4, 7, 8},
    "Mercury": {7},
    "Jupiter": {5, 7, 9, 12},
    "Venus": {7},
    "Saturn": {3, 7, 10},
    "Rahu": {7},
    "Ketu": {7},
}

ASPECT_NAMES = {
    "Sun": "full",
    "Moon": "full",
    "Mars": "special",
    "Mercury": "full",
    "Jupiter": "special",
    "Venus": "full",
    "Saturn": "special",
    "Rahu": "full",
    "Ketu": "full",
}

# Varga chart types (divisional). Supported: D1, D9. Others extendable.
VARGA_DIVISIONS = {
    "rashi": 1,
    "navamsa": 9,
    "dasamsa": 10,
    "saptamsa": 7,
    "shashtiamsa": 60,
    "moon": 1,
    "transit": 1,
}


