
BIO = [
    "full name",
    "concept",
    "ssplat",
    "ambition",
    "sire",
    "desire",
    "predator",
    "clan",
    "generation",
]


SPLATS = [
    "vampire",
    "ghoul",
    "mortal",
]

ATTRIBUTES = [
    "strength",
    "dexterity",
    "stamina",
    "charisma",
    "manipulation",
    "composure",
    "intelligence",
    "wits",
    "resolve"
]

MENTAL = [
    "intelligence",
    "wits",
    "resolve",
    "academics",
    "awareness",
    "finance",
    "investigation",
    "medicine",
    "occult",
    "politics",
    "science",
    "technology"
]

PHYSICAL = [
    "strength",
    "dexterity",
    "stamina",
    "athletics",
    "brawl",
    "craft",
    "drive",
    "firearms",
    "larceny",
    "melee",
    "stealth",
    "survival"
]

SOCIAL = [
    "charisma",
    "manipulation",
    "composure",
    "animal ken",
    "etiquette",
    "insight",
    "intimidation",
    "leadership",
    "performance",
    "persuasion",
    "streetwise",
    "subterfuge"
]

SKILLS = [
    "athletics",
    "brawl",
    "craft",
    "drive",
    "firearms",
    "larceny",
    "melee",
    "stealth",
    "survival",
    "animal ken",
    "etiquette",
    "insight",
    "intimidation",
    "leadership",
    "performance",
    "persuasion",
    "streetwise",
    "subterfuge",
    "academics",
    "awareness",
    "finance",
    "investigation",
    "medicine",
    "occult",
    "politics",
    "science",
    "technology"
]

DISCIPLINES = [
    "animalism"
]
MERITS = [
    "beautiful",
    "stunning",
    "high-functioning addict",
    "bond resistance",
    "short bond",
    "unbondable",
    "bloodhound",
    "iron gullet",
    "eat food"
]
FLAWS = [
    "illiterate",
    "repulsive",
    "vile",
    "hopeless addiction",
    "addiction",
    "archaic",
    "lving in the past",
    "bondslave",
    "bond junkie",
    "long bond",
    "farmer",
    "organovore",
    "methuselah's thirst",
    "prey exclusion",
    "stake bait",
    "bane",
    "folklore block",
    "stigmata"
]


POOLS = [
    "health",
    "willpower",
    "blood",
    "humanity",
    "morality",
    "blood potency",
    "hunger"
]


INSTANCED = []


BIO_GOOD_VALUES = {
    "default": {
        "values": [],
        "check": lambda x: True,
        "check_message": "Permission Denied",
        "instanced": False,
        "has_specialties": False,
        "specialties": {}

    },
    "clan": {
        "values": [
            "brujah",
            "gangrel",
            "malkavian",
            "nosferatu",
            "toreador",
            "tremere",
            "ventrue"
        ],
        "check": lambda x: x["splat"] in "vampire",
        "check_message": "Clan is only available to vampires."
    },
    "sire": {
        "values": [],
        "check": lambda x: x["splat"] in "vampire",
        "check_message": "Sire is only available to vampires."
    },
    "generation": {
        "values": [16, 15, 14, 13, 12, 11, 10],
        "check": lambda x: x["splat"] in "vampire",
        "check_message": "Generation is only available to vampires."
    },
    "predator": {
        "values": [
            "allycat",
            "bagger",
            "bloodleech",
            "cleaver",
            "consensualist",
            "farmer",
            "scenequeen",
            "shepherd",
            "siren",
            "whisperer"
        ],
        "check": lambda x: "vampire" in x["splat"],
        "check_message": "Predator is only available to vampires."
    },
}

ATTRIBUTES_GOOD_VALUES = {
    "default": {
        "values": range(1, 20),
        "check": lambda x: True,
        "check_message": "You must have at least one dot in each attribute.",
        "instanced": False,
        "instances": [],
        "has_specialties": False,
        "specialties": {}
    },
}

SKILLS_GOOD_VALUES = {
    "default": {
        "values": range(1, 5),
        "check": lambda x: True,
        "check_message": "Permission Denied",
        "instanced": False,
        "instances": [],
        "has_specialties": True,
        "specialties": {}
    }
}


MERITS_GOOD_VALUES = {
    "default": {
        "values": [],
        "check": lambda x: True,
        "check_message": "Permission Denied",
        "instanced": False,
        "instances": [],
        "has_specialties": False,
        "specialties": {}
    },
    "beautiful": {"values": [2]},
    "stunning": {"values": [4]},
    "high-functioning addict": {"values": [1]},
    "bond resistance": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Bond Resistance is only available to vampires."
    },
    "short bond": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Short Bond is only available to vampires."
    },
    "unbondable": {
        "values": [4],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Unbondable is only available to vampires."
    },
    "bloodhound": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Bloodhound is only available to vampires."
    },
    "iron gullet": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Iron Gullet is only available to vampires."
    },
    "eat food": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Eat Food is only available to vampires."
    }
}


FLAWS_GOOD_VALUES = {
    "default": {
        "values": [],
        "check": lambda x: True,
        "check_message": "Permission Denied",
        "instanced": False,
        "instances": [],
        "has_specialties": False,
        "specialties": {}
    },
    "illiterate": {"values": [1]},
    "repulsive": {"values": [2]},
    "vile": {"values": [4]},
    "hopeless addiction": {"values": [2]},
    "addiction": {"values": [1]},
    "archaic": {
        "values": [1], "check": lambda x: x["splat"] == "vampire",
        "check_message": "Archaic is only available to vampires."
    },
    "living in the past": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Living in the Past is only available to vampires."
    },
    "bondslave": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Bondslave is only available to vampires."
    },
    "bond junkie": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Bond Junkie is only available to vampires."
    },
    "long bond": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Long Bond is only available to vampires."
    },
    "farmer": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Farmer is only available to vampires."
    },
    "organavore": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Organavore is only available to vampires."
    },
    "methuselah's thirst": {
        "values": [3], "check": lambda x: x["splat"] == "vampire",
        "check_message": "Methuselah's Thirst is only available to vampires."
    },
    "prey exclusion": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Prey Exclusion is only available to vampires.",
        "instanced": True
    },
    "stake bait": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Stake Bait is only available to vampires."
    },
    "folklore bane": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Folklore Bane is only available to vampires."
    },
    "folklore block": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Folklore Block is only available to vampires."
    },
}


DISCIPLINES_GOOD_VALUES = {
    "animalism": {
        "values": range(1, 6),
        "check": lambda x: x["splat"] in "vampire",
        "check_message": "Animalism is only available to vampires.",
        "instanced": False,
        "instances": [],
        "has_specialties": True,
        "specialties": {
            "bond famulus": {
                "values": [1],
                "check": lambda x: x.disciplines["animalism"] >= 1,
                "check_message": "Animalism 1 is required."
            },
            "sense the beast": {
                "values": [1],
                "check": lambda x: x.disciplines["animalism"] >= 1,
                "check_message": "Animalism 1 is required."
            },
            "feral whispers": {
                "values": [2],
                "check": lambda x: x.disciplines["animalism"] >= 2,
                "check_message": "Animalism 2 is required."
            },
            "animal succulence": {
                "values": [3],
                "check": lambda x: x.disciplines["animalism"] >= 3,
                "check_message": "Animalism 3 is required."
            },
            "quell the beast": {
                "values": [3],
                "check": lambda x: x.disciplines["animalism"] >= 3,
                "check_message": "Animalism 3 is required."
            },
            "living hive": {
                "values": [3],
                "check": lambda x: x.disciplines["obfuscate"] >= 2 and x.disciplines["animalism"] >= 3,
                "check_message": "Obfuscate 2 and Animalism 3 are required."
            },
            "subsume the spirit": {
                "values": [4],
                "check": lambda x: x.disciplines["animalism"] >= 4,
                "check_message": "Animalism 4 is required."
            },
            "animal dominion": {
                "values": [5],
                "check": lambda x: x.disciplines["animalism"] >= 5,
                "check_message": "Animalism 5 is required."
            },
            "draw out the beast": {
                "values": [5],
                "check": lambda x: x.disciplines["animalism"] >= 5,
                "check_message": "Animalism 5 is required."
            }
        },
    },

    "default": {
        "values": [],
        "check": lambda x: x["splat"] in "vampire",
        "check_message": "Permission Denied",
        "instanced": False,
        "instances": [],
        "has_specialties": False,
        "specialties": {}
    }
}

# "auspex": {
#     "heightened senses": {"value": 1, "check": lambda x: x["auspex"] >= 1},
#     "sense the unseen": {"value": 1, "check": lambda x: x["auspex"] >= 1},
#     "premonition": {"value": 2, "check": lambda x: x["auspex"] >= 2},
#     "scry the soul": {"value": 3, "check": lambda x: x["auspex"] >= 3},
#     "shared senses": {"value": 3, "check": lambda x: x["auspex"] >= 3},
#     "spirits touch": {"value": 4, "check": lambda x: x["auspex"] >= 4},
#     "clairvoyance": {"value": 5, "check": lambda x: x["auspex"] >= 5},
#     "possession": {"value": 5, "check": lambda x: x["auspex"] >= 5 and x["dominate"] >= 3},
#     "telepathy": {"value": 5, "check": lambda x: x["auspex"] >= 5}
# },
# "celerity": {
#     "cats grace": {"value": 1, "check": lambda x: x["celerity"] >= 1},
#     "fleetness": {"value": 2, "check": lambda x: x["celerity"] >= 2},
#     "blink": {"value": 3, "check": lambda x: x["celerity"] >= 3},
#     "traversal": {"value": 3, "check": lambda x: x["celerity"] >= 3},
#     "draught of elegance": {"value": 4, "check": lambda x: x["celerity"] >= 4},
#     "unerring aim": {"value": 4, "check": lambda x: x["celerity"] >= 4 and x["auspex"] >= 2},
#     "lightning strike": {"value": 5, "check": lambda x: x["celerity"] >= 5},
#     "split second": {"value": 5, "check": lambda x: x["celerity"] >= 5},
# },
# "dominate": {
#     "cloud memory": {"value": 1, "check": lambda x: x["dominate"] >= 1},
#     "compel": {"value": 1, "check": lambda x: x["dominate"] >= 1},
#     "mesmerize": {"value": 2, "check": lambda x: x["dominate"] >= 2},
#     "dementation": {"value": 2, "check": lambda x: x["dominate"] >= 2 and x["obfuscate"] >= 2},
#     "the forgetful mind": {"value": 3, "check": lambda x: x["dominate"] >= 3},
#     "submerged directive": {"value": 3, "check": lambda x: x["dominate"] >= 3},
#     "rationalize": {"value": 4, "check": lambda x: x["dominate"] >= 4},
#     "mass manipulation": {"value": 5, "check": lambda x: x["dominate"] >= 5},
#     "terminal decree": {"value": 5, "check": lambda x: x["dominate"] >= 5},
# },
# "fortitude": {},
# "obfuscate": {},
# "obtenebration": {},
# "potence": {},
# "presence": {},
# "protean": {},
# "blood sorcery": {},
# "thin-blood rituals": {}


POOLS_GOOD_VALUES = {
    "default": {"values": [], "check": lambda x: True, "check_message": "Permission Denied", "specialties": False, "specialties": {}},
    "humanity": {"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "check": lambda x: x["splat"] == "vampire"},
    "willpower": {"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
    "blood potency": {"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "check": lambda x: x["splat"] == "vampire"},
    "health": {"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
    "hunger": {"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "check": lambda x: x["splat"] == "vampire"},
}


TOTAL_TRAITS = [
    ("bio", BIO, BIO_GOOD_VALUES),
    ("attributes", ATTRIBUTES, ATTRIBUTES_GOOD_VALUES),
    ("skills", SKILLS, SKILLS_GOOD_VALUES),
    ("merits", MERITS, MERITS_GOOD_VALUES),
    ("flaws", FLAWS, FLAWS_GOOD_VALUES),
    ("disciplines", DISCIPLINES, DISCIPLINES_GOOD_VALUES),
    ("pools", POOLS, POOLS_GOOD_VALUES),
]


def get_trait_list(string):
    for list in TOTAL_TRAITS:
        for trait in list[1]:
            if string in trait:

                # create an object and add the values to it to return
                # TODO: This is a nightmare driven hell machine. Fix it.
                # The dark magics of python are at work here.
                output = {}
                output["trait"] = trait
                output["category"] = list[0]
                output["values"] = list[2][trait]["values"] if trait in list[2] else list[2]["default"]["values"]
                try:
                    output["check"] = list[2][trait]["check"] if trait in list[2] else list[
                        2]["default"]["check"] if "default" in list[2] else lambda x: True
                except KeyError:
                    output["check"] = lambda x: True
                try:
                    output["check_message"] = list[2][trait]["check_message"] if trait in list[2] else list[
                        2]["default"]["check_message"] if "default" in list[2] else "Permission denied."
                except KeyError:
                    output["check_message"] = "Permission denied."

                try:
                    output["has_specialties"] = list[2][trait]["has_specialties"] if trait in list[
                        2] else list[2]["default"]["has_specialties"] if "default" in list[2] else False
                    output["specialties"] = list[2][trait]["specialties"] if trait in list[
                        2] else list[2]["default"]["specialties"] if "default" in list[2] else {}
                except:
                    output["has_specialties"] = False
                    output["specialties"] = {}

                return output

# get the category of a trait


def get_trait_category(string):
    for list in TOTAL_TRAITS:
        for trait in list[1]:
            if string in trait:
                return list[0]
