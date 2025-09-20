from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import random
import re
from typing import List, Optional

app = FastAPI(
    title="Random Address Generator API",
    description="Generates completely random but realistic-looking addresses worldwide with names and phone numbers",
    version="2.0.0"
)

# Data pools for generating random content
first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
               "David", "Susan", "Richard", "Jessica", "Joseph", "Sarah", "Thomas", "Karen", "Charles", "Nancy",
               "Christopher", "Lisa", "Daniel", "Betty", "Matthew", "Margaret", "Anthony", "Sandra", "Mark", "Ashley",
               "Donald", "Kimberly", "Steven", "Emily", "Paul", "Donna", "Andrew", "Michelle", "Joshua", "Carol",
               "Kevin", "Dorothy", "Brian", "Helen", "Edward", "Sharon", "Ronald", "Laura", "Timothy", "Cynthia"]

last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
              "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
              "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
              "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"]

street_suffixes = ["Street", "Avenue", "Road", "Boulevard", "Lane", "Plaza", "Circle", "Drive", "Court", "Way", "Terrace"]
street_prefixes = ["Maple", "Oak", "Pine", "Cedar", "Elm", "Birch", "Willow", "Magnolia", "Juniper", "Sycamore", "Aspen", 
                  "Sunset", "Sunrise", "Lakeview", "Hillside", "Riverside", "Mountain", "Valley", "Park", "Garden", "Highland",
                  "North", "South", "East", "West", "Central", "Liberty", "Union", "Washington", "Jefferson", "Lincoln",
                  "Main", "Broad", "Church", "School", "Railroad", "Station", "Airport", "Harbor", "Ocean", "River"]

vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"

# Real country data with telephone formats
countries = [
    {"name": "United States", "code": "US", "phone_format": "+1 (###) ###-####", "phone_mask": "\\+1 \\(\\d{3}\\) \\d{3}-\\d{4}"},
    {"name": "United Kingdom", "code": "GB", "phone_format": "+44 ## #### ####", "phone_mask": "\\+44 \\d{2} \\d{4} \\d{4}"},
    {"name": "Canada", "code": "CA", "phone_format": "+1 (###) ###-####", "phone_mask": "\\+1 \\(\\d{3}\\) \\d{3}-\\d{4}"},
    {"name": "Australia", "code": "AU", "phone_format": "+61 # #### ####", "phone_mask": "\\+61 \\d \\d{4} \\d{4}"},
    {"name": "Germany", "code": "DE", "phone_format": "+49 ### #######", "phone_mask": "\\+49 \\d{3} \\d{7}"},
    {"name": "France", "code": "FR", "phone_format": "+33 # ## ## ## ##", "phone_mask": "\\+33 \\d \\d{2} \\d{2} \\d{2} \\d{2}"},
    {"name": "Japan", "code": "JP", "phone_format": "+81 ##-####-####", "phone_mask": "\\+81 \\d{2}-\\d{4}-\\d{4}"},
    {"name": "Brazil", "code": "BR", "phone_format": "+55 (##) #####-####", "phone_mask": "\\+55 \\(\\d{2}\\) \\d{5}-\\d{4}"},
    {"name": "India", "code": "IN", "phone_format": "+91 ####-######", "phone_mask": "\\+91 \\d{4}-\\d{6}"},
    {"name": "China", "code": "CN", "phone_format": "+86 ### #### ####", "phone_mask": "\\+86 \\d{3} \\d{4} \\d{4}"},
    {"name": "Italy", "code": "IT", "phone_format": "+39 ### #######", "phone_mask": "\\+39 \\d{3} \\d{7}"},
    {"name": "Spain", "code": "ES", "phone_format": "+34 ### ### ###", "phone_mask": "\\+34 \\d{3} \\d{3} \\d{3}"},
    {"name": "Mexico", "code": "MX", "phone_format": "+52 ### ### ####", "phone_mask": "\\+52 \\d{3} \\d{3} \\d{4}"},
    {"name": "South Korea", "code": "KR", "phone_format": "+82 ##-###-####", "phone_mask": "\\+82 \\d{2}-\\d{3}-\\d{4}"},
    {"name": "Russia", "code": "RU", "phone_format": "+7 (###) ###-##-##", "phone_mask": "\\+7 \\(\\d{3}\\) \\d{3}-\\d{2}-\\d{2}"},
    {"name": "Netherlands", "code": "NL", "phone_format": "+31 ## ### ####", "phone_mask": "\\+31 \\d{2} \\d{3} \\d{4}"},
    {"name": "Switzerland", "code": "CH", "phone_format": "+41 ## ### ## ##", "phone_mask": "\\+41 \\d{2} \\d{3} \\d{2} \\d{2}"},
    {"name": "Sweden", "code": "SE", "phone_format": "+46 ## ### ####", "phone_mask": "\\+46 \\d{2} \\d{3} \\d{4}"},
    {"name": "Norway", "code": "NO", "phone_format": "+47 ### ## ###", "phone_mask": "\\+47 \\d{3} \\d{2} \\d{3}"},
    {"name": "South Africa", "code": "ZA", "phone_format": "+27 ## ### ####", "phone_mask": "\\+27 \\d{2} \\d{3} \\d{4}"},
    {"name": "Argentina", "code": "AR", "phone_format": "+54 (###) ####-####", "phone_mask": "\\+54 \\(\\d{3}\\) \\d{4}-\\d{4}"},
    {"name": "Turkey", "code": "TR", "phone_format": "+90 (###) ### ####", "phone_mask": "\\+90 \\(\\d{3}\\) \\d{3} \\d{4}"}
]

# Real states/provinces for some countries
states_by_country = {
    "US": ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", 
           "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", 
           "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", 
           "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
           "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", 
           "West Virginia", "Wisconsin", "Wyoming"],
    "CA": ["Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador", "Nova Scotia", 
           "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan", "Northwest Territories", "Nunavut", "Yukon"],
    "GB": ["England", "Scotland", "Wales", "Northern Ireland"],
    "AU": ["New South Wales", "Queensland", "South Australia", "Tasmania", "Victoria", "Western Australia", 
           "Australian Capital Territory", "Northern Territory"],
    "DE": ["Baden-Württemberg", "Bavaria", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hesse", "Lower Saxony", 
           "Mecklenburg-Vorpommern", "North Rhine-Westphalia", "Rhineland-Palatinate", "Saarland", "Saxony", 
           "Saxony-Anhalt", "Schleswig-Holstein", "Thuringia"],
    "FR": ["Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", "Brittany", "Centre-Val de Loire", "Corsica", "Grand Est", 
           "Hauts-de-France", "Île-de-France", "Normandy", "Nouvelle-Aquitaine", "Occitanie", "Pays de la Loire", "Provence-Alpes-Côte d'Azur"],
    "JP": ["Hokkaido", "Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima", "Ibaraki", "Tochigi", "Gunma", 
           "Saitama", "Chiba", "Tokyo", "Kanagawa", "Niigata", "Toyama", "Ishikawa", "Fukui", "Yamanashi", "Nagano", 
           "Gifu", "Shizuoka", "Aichi", "Mie", "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama", "Tottori", 
           "Shimane", "Okayama", "Hiroshima", "Yamaguchi", "Tokushima", "Kagawa", "Ehime", "Kochi", "Fukuoka", "Saga", 
           "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima", "Okinawa"]
}

class Address(BaseModel):
    name: str
    surname: str
    house_no: int
    street: str
    city: str
    state: str
    country: str
    country_code: str
    postal_code: str
    phone: str
    latitude: float
    longitude: float

def generate_name(min_len: int, max_len: int) -> str:
    """Generate a random name with alternating consonants and vowels"""
    length = random.randint(min_len, max_len)
    name = []
    starts_with_vowel = random.choice([True, False])
    
    for i in range(length):
        if (starts_with_vowel and i % 2 == 0) or (not starts_with_vowel and i % 2 == 1):
            name.append(random.choice(vowels))
        else:
            name.append(random.choice(consonants))
    
    # Capitalize the first letter
    return ''.join(name).capitalize()

def generate_postal_code(country_code: str) -> str:
    """Generate a random postal code appropriate for the country"""
    if country_code in ["US", "CA"]:
        # US/Canada format: ##### or #####-####
        if random.random() < 0.7:
            return ''.join(random.choices("0123456789", k=5))
        else:
            return ''.join(random.choices("0123456789", k=5)) + "-" + ''.join(random.choices("0123456789", k=4))
    elif country_code == "GB":
        # UK format: AA## #AA or similar
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return ''.join(random.choices(letters, k=2)) + ''.join(random.choices("0123456789", k=2)) + " " + \
               ''.join(random.choices("0123456789", k=1)) + ''.join(random.choices(letters, k=2))
    elif country_code in ["AU", "DE", "FR", "ES", "IT", "NL", "SE", "NO"]:
        # European format: #####
        return ''.join(random.choices("0123456789", k=5))
    elif country_code in ["JP", "KR"]:
        # Japan/Korea format: ###-####
        return ''.join(random.choices("0123456789", k=3)) + "-" + ''.join(random.choices("0123456789", k=4))
    elif country_code == "BR":
        # Brazil format: #####-###
        return ''.join(random.choices("0123456789", k=5)) + "-" + ''.join(random.choices("0123456789", k=3))
    elif country_code == "IN":
        # India format: ######
        return ''.join(random.choices("0123456789", k=6))
    elif country_code == "CN":
        # China format: ######
        return ''.join(random.choices("0123456789", k=6))
    elif country_code == "MX":
        # Mexico format: #####
        return ''.join(random.choices("0123456789", k=5))
    elif country_code == "RU":
        # Russia format: ######
        return ''.join(random.choices("0123456789", k=6))
    elif country_code == "ZA":
        # South Africa format: ####
        return ''.join(random.choices("0123456789", k=4))
    elif country_code == "AR":
        # Argentina format: ####
        return ''.join(random.choices("0123456789", k=4))
    elif country_code == "TR":
        # Turkey format: #####
        return ''.join(random.choices("0123456789", k=5))
    else:
        # Default format: alphanumeric 6-8 chars
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        length = random.randint(6, 8)
        return ''.join(random.choices(chars, k=length))

def generate_phone_number(country: dict) -> str:
    """Generate a random phone number following the country's format"""
    phone_format = country["phone_format"]
    phone_number = ""
    
    for char in phone_format:
        if char == "#":
            phone_number += random.choice("0123456789")
        else:
            phone_number += char
            
    return phone_number

def generate_city_name(country_code: str) -> str:
    """Generate a random city name that fits the country's naming pattern"""
    if country_code in ["US", "CA", "GB", "AU"]:
        # English-style names
        prefixes = ["New", "North", "South", "East", "West", "Lake", "Port", "Fort", "Mount"]
        suffixes = ["ville", "town", "burg", "field", "wood", "haven", "shore", "view", "dale", "brook"]
        roots = ["York", "London", "Oxford", "Cambridge", "Spring", "River", "Hill", "Forest", "Rock", "Green"]
        
        if random.random() < 0.4:
            return random.choice(prefixes) + random.choice(roots)
        elif random.random() < 0.7:
            return random.choice(roots) + random.choice(suffixes)
        else:
            return generate_name(5, 10)
    
    elif country_code in ["DE", "AT", "CH"]:
        # German-style names
        prefixes = ["Bad", "Berg", "Burg", "Frank", "Hamb", "Heidel", "Mun", "Stutt", "Wolfs"]
        suffixes = ["burg", "dorf", "feld", "hausen", "heim", "stadt", "berg", "bach", "see"]
        
        return random.choice(prefixes) + random.choice(suffixes)
    
    elif country_code in ["FR", "BE", "CH"]:
        # French-style names
        prefixes = ["Saint", "Mont", "Val", "Bois", "Château", "Ville", "Font", "Beau", "Grand"]
        suffixes = ["ville", "court", "fort", "bourg", "neur", "lieu", "mont", "mar", "cy"]
        
        if random.random() < 0.5:
            return random.choice(prefixes) + "-" + generate_name(3, 6).capitalize()
        else:
            return generate_name(4, 8).capitalize() + random.choice(suffixes)
    
    elif country_code in ["ES", "MX", "AR"]:
        # Spanish-style names
        prefixes = ["San", "Santa", "Los", "Las", "El", "La", "Villa", "Puerto", "Ciudad"]
        suffixes = ["a", "o", "ia", "io", "ales", "anos", "illa", "illo"]
        
        if random.random() < 0.5:
            return random.choice(prefixes) + " " + generate_name(3, 6).capitalize()
        else:
            return generate_name(4, 8).capitalize() + random.choice(suffixes)
    
    elif country_code in ["IT"]:
        # Italian-style names
        prefixes = ["San", "Santa", "Monte", "Castel", "Villa", "Porto", "Citta"]
        suffixes = ["a", "o", "ia", "io", "ano", "ina", "etta", "ello"]
        
        if random.random() < 0.5:
            return random.choice(prefixes) + " " + generate_name(3, 6).capitalize()
        else:
            return generate_name(4, 8).capitalize() + random.choice(suffixes)
    
    elif country_code in ["JP", "KR", "CN"]:
        # Asian-style names (shorter, more consonant-vowel patterns)
        name = ""
        syllables = random.randint(2, 3)
        
        for _ in range(syllables):
            name += random.choice(consonants) + random.choice(vowels)
            
        return name.capitalize()
    
    else:
        # Default style
        return generate_name(5, 10)

def generate_address() -> Address:
    """Generate a single random address"""
    # Select a random country
    country = random.choice(countries)
    country_code = country["code"]
    
    # Generate name and surname
    name = random.choice(first_names)
    surname = random.choice(last_names)
    
    # Generate address components
    house_no = random.randint(1, 9999)
    street_name = random.choice(street_prefixes) + " " + random.choice(street_suffixes)
    city = generate_city_name(country_code)
    
    # Select state based on country
    if country_code in states_by_country:
        state = random.choice(states_by_country[country_code])
    else:
        state = generate_name(6, 15)
    
    # Generate country-specific postal code and phone number
    postal_code = generate_postal_code(country_code)
    phone = generate_phone_number(country)
    
    # Generate coordinates (weighted toward populated areas)
    if random.random() < 0.7:  # 70% chance for coordinates in populated areas
        latitude = round(random.uniform(-60, 70), 6)
        longitude = round(random.uniform(-180, 180), 6)
    else:  # 30% chance for coordinates anywhere
        latitude = round(random.uniform(-90, 90), 6)
        longitude = round(random.uniform(-180, 180), 6)
    
    return Address(
        name=name,
        surname=surname,
        house_no=house_no,
        street=street_name,
        city=city,
        state=state,
        country=country["name"],
        country_code=country_code,
        postal_code=postal_code,
        phone=phone,
        latitude=latitude,
        longitude=longitude
    )

@app.get("/", response_model=dict)
async def root():
    return {
        "message": "Random Address Generator API",
        "version": "2.0.0",
        "endpoints": {
            "/address": "Generate a single random address",
            "/addresses": "Generate multiple random addresses (use count parameter)",
            "/countries": "Get list of supported countries"
        }
    }

@app.get("/address", response_model=dict)
async def get_single_address():
    """Return a single random address"""
    return {"address": generate_address()}

@app.get("/addresses", response_model=dict)
async def get_multiple_addresses(count: int = Query(1, ge=1, le=100)):
    """Return multiple random addresses based on the count parameter"""
    addresses = [generate_address() for _ in range(count)]
    return {"addresses": addresses}

@app.get("/countries", response_model=dict)
async def get_countries():
    """Return the list of supported countries"""
    return {"countries": [{"name": c["name"], "code": c["code"]} for c in countries]}

# For debugging and testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
