import os
from collections import OrderedDict
from dataclasses import dataclass

from pyexcel_ods3 import save_data, get_data

from selenium import webdriver

# SET HERE THE URL OF TO SALARIES
glassdoorUrl = r"https://www.glassdoor.COM/Salaries/index.htm"

# MOZILLA PROFILE DIRECTORY
profileDir = r"/home/user/.mozilla/firefox/xxxxxxx.default-release"

# OUTPUT ODS FILENAME
outputOds = "result.ods"

jobTitles = [
    "Researcher",
    "Developer",
    "Engineer",
]

jobModifiers = [
    "",
    "Java",
    "Backend",
    "Software",
]

jobSeniority = [
    "",
    "Junior",
    "Middle",
    "Senior"
]

jobs = []

for title in jobTitles:
    for mod in jobModifiers:
        for sen in jobSeniority:
            result = " ".join(x for x in [sen, mod, title] if x)
            if result:
                jobs.append(result)

# Country names to search in you language
countries = [
    "United Kingdom",
    "United States of America",
]

# Currencies as they appear when you search a job
# Include all currencies you are interested in
currencies = {
    "€",
    "£",
    "USD"
}

# Your currency symbol
myCurrency = "€"

# Set here the conversion factor FROM the listed currency TO your currency
toYourCurrencyConversion = {
    myCurrency: 1,
    "€": 1,
    "£": 1.19,
    "USD": 0.95
}

# Set here the conversion to Year when "year" or "month" or other time units
# are encountered by the bot. Here you should add "year" and "month" in you language
toYearConversion = {
    "year": 1,
    "month": 12
}
