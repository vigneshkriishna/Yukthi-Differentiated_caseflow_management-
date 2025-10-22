"""
BNS Training Data - Comprehensive Dataset for Bharatiya Nyaya Sanhita Section Classification
This creates a realistic training dataset for BNS section prediction
"""

BNS_TRAINING_DATA = [
    # VIOLENT CRIMES
    {
        "section": "103", "title": "Murder",
        "description": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
        "examples": [
            "The accused intentionally killed the victim by stabbing with a knife during a fight",
            "Premeditated murder of shopkeeper during robbery using firearm",
            "Death caused by poisoning with intent to kill the victim",
            "Accused shot the victim multiple times leading to death on the spot",
            "Murder committed during domestic violence incident using blunt weapon"
        ]
    },
    {
        "section": "105", "title": "Culpable homicide not amounting to murder",
        "description": "Culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.",
        "examples": [
            "Death caused during sudden fight without premeditation",
            "Accidental death during scuffle between two parties",
            "Death caused by rash or negligent act without criminal intent",
            "Manslaughter during heat of passion provoked by victim",
            "Unintentional killing during commission of another crime"
        ]
    },
    {
        "section": "322", "title": "Voluntarily causing grievous hurt",
        "description": "Whoever voluntarily causes grievous hurt shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "examples": [
            "Causing permanent disability by acid attack on victim",
            "Severe assault resulting in broken bones and internal injuries",
            "Grievous hurt causing permanent disfigurement of face",
            "Attack with iron rod causing fractures and permanent damage",
            "Assault leading to loss of eye or limb of the victim"
        ]
    },
    {
        "section": "316", "title": "Voluntarily causing hurt",
        "description": "Whoever voluntarily causes hurt shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both.",
        "examples": [
            "Simple assault causing minor injuries and bruises",
            "Slapping and pushing causing temporary pain",
            "Minor fight resulting in cuts and scratches",
            "Physical altercation causing swelling and minor wounds",
            "Assault with hands causing temporary bodily harm"
        ]
    },
    {
        "section": "63", "title": "Rape",
        "description": "Whoever commits rape shall be punished with rigorous imprisonment of either description for a term which shall not be less than ten years, but which may extend to imprisonment for life, and shall also be liable to fine.",
        "examples": [
            "Sexual assault on woman against her consent using force",
            "Rape committed by person in position of authority",
            "Gang rape involving multiple accused persons",
            "Sexual violence against minor girl child",
            "Marital rape causing physical and mental trauma"
        ]
    },

    # PROPERTY CRIMES
    {
        "section": "64", "title": "Theft",
        "description": "Whoever intends to take dishonestly any moveable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft.",
        "examples": [
            "Stealing mobile phone from person's pocket in crowded area",
            "Theft of bicycle parked outside residence",
            "Shoplifting goods from retail store without payment",
            "Stealing cash from employer's office drawer",
            "Theft of gold ornaments from house during absence"
        ]
    },
    {
        "section": "69", "title": "Robbery",
        "description": "In all robbery there is either theft or extortion. When theft is robbery, and when extortion is robbery.",
        "examples": [
            "Armed robbery of bank using weapons and threats",
            "Highway robbery of travelers by gang of criminals",
            "Snatching purse from woman using force and violence",
            "Robbery of jewelry shop with guns and intimidation",
            "Daylight robbery of cash from businessman using threats"
        ]
    },
    {
        "section": "303", "title": "Burglary",
        "description": "Whoever commits lurking house-trespass or house-breaking, having made preparation for causing hurt to any person or for assaulting any person, or for wrongfully restraining any person, or for putting any person in fear of hurt, or of assault, or of wrongful restraint, commits burglary.",
        "examples": [
            "Breaking into house at night to steal valuables",
            "Burglary of office premises during weekend",
            "House breaking with intent to commit theft",
            "Breaking locks and entering residence for robbery",
            "Night time burglary of shop after breaking security"
        ]
    },
    {
        "section": "318", "title": "Cheating",
        "description": "Whoever cheats shall be punished with imprisonment of either description for a term which may extend to one year, or with fine, or with both.",
        "examples": [
            "Online fraud involving fake investment schemes",
            "Cheating in property sale using forged documents",
            "Credit card fraud and identity theft",
            "Lottery fraud and fake prize money schemes",
            "Educational certificate forgery and fake degrees"
        ]
    },
    {
        "section": "61", "title": "Criminal breach of trust",
        "description": "Whoever commits criminal breach of trust shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "examples": [
            "Employee embezzling company funds for personal use",
            "Bank manager misappropriating customer deposits",
            "Trustee misusing trust property for personal gain",
            "Agent cheating principal by misusing entrusted property",
            "Public servant misappropriating government funds"
        ]
    },

    # CRIMES AGAINST PERSON
    {
        "section": "351", "title": "Kidnapping",
        "description": "Kidnapping is of two kinds: kidnapping from lawful guardianship, and kidnapping from the country.",
        "examples": [
            "Abduction of minor child from parents for ransom",
            "Kidnapping woman for forced marriage",
            "Child trafficking for labor exploitation",
            "Kidnapping businessman for extortion money",
            "Abduction of girl child from school premises"
        ]
    },
    {
        "section": "137", "title": "Defamation",
        "description": "Whoever defames another shall be punished with simple imprisonment for a term which may extend to two years, or with fine, or with both.",
        "examples": [
            "Publishing false statements damaging person's reputation online",
            "Spreading rumors about character of public figure",
            "Defamatory social media posts causing reputational harm",
            "False allegations of criminal conduct against individual",
            "Publishing defamatory article in newspaper about person"
        ]
    },
    {
        "section": "115", "title": "Voluntarily causing disappearance of evidence",
        "description": "Whoever voluntarily causes any thing which is evidence to disappear with the intention of preventing it from being produced as evidence shall be punished.",
        "examples": [
            "Destroying CCTV footage to hide criminal activity",
            "Burning documents related to financial fraud case",
            "Deleting computer files containing evidence of crime",
            "Hiding murder weapon to avoid prosecution",
            "Destroying medical records to cover negligence"
        ]
    },

    # CYBER CRIMES
    {
        "section": "66", "title": "Computer related offences",
        "description": "If any person dishonestly or fraudulently does any act referred to in section 43, he shall be punishable with imprisonment of either description for a term which may extend to three years or with fine which may extend to five lakh rupees or with both.",
        "examples": [
            "Hacking into computer systems to steal sensitive data",
            "Online banking fraud using stolen credentials",
            "Creating malware to damage computer networks",
            "Unauthorized access to government databases",
            "Cyber stalking and harassment through digital means"
        ]
    },

    # DRUG OFFENCES
    {
        "section": "27", "title": "Punishment for consumption of any narcotic drug or psychotropic substance",
        "description": "Whoever consumes any narcotic drug or psychotropic substance shall be punishable with rigorous imprisonment for a term which may extend to one year, or with fine which may extend to twenty thousand rupees, or with both.",
        "examples": [
            "Consumption of cocaine and other narcotic substances",
            "Drug addiction and substance abuse cases",
            "Possession of small quantities of drugs for personal use",
            "Consumption of psychotropic substances without prescription",
            "Drug abuse by students in educational institutions"
        ]
    },

    # TRAFFIC VIOLATIONS
    {
        "section": "279", "title": "Rash driving or riding on a public way",
        "description": "Whoever drives any vehicle, or rides, on any public way in a manner so rash or negligent as to endanger human life, or to be likely to cause hurt or injury to any other person, shall be punished with imprisonment of either description for a term which may extend to six months, or with fine which may extend to one thousand rupees, or with both.",
        "examples": [
            "Reckless driving causing accident and injury",
            "Drunk driving leading to collision with pedestrian",
            "Over speeding in residential area endangering lives",
            "Negligent driving causing damage to public property",
            "Racing on public roads causing traffic hazards"
        ]
    },

    # COMMERCIAL CRIMES
    {
        "section": "420", "title": "Cheating and dishonestly inducing delivery of property",
        "description": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "examples": [
            "Real estate fraud involving fake property documents",
            "Ponzi schemes defrauding investors of crores",
            "Fake company registration for fraudulent activities",
            "Insurance fraud involving false claims",
            "Multi-level marketing scams cheating participants"
        ]
    },

    # CORRUPTION
    {
        "section": "7", "title": "Public servant taking gratification other than legal remuneration in respect of an official act",
        "description": "Whoever, being, or expecting to be a public servant, accepts or obtains or agrees to accept or attempts to obtain from any person, for himself or for any other person, any gratification whatever, other than legal remuneration, as a motive or reward for doing or forbearing to do any official act or for showing or forbearing to show, in the exercise of his official functions, favour or disfavour to any person or for rendering or attempting to render any service or disservice to any person, with the Central Government or any State Government or Parliament or the Legislature of any State or with any local authority, corporation or Government company referred to in clause (c) of section 2, or with any public servant, whether named or otherwise, shall be punished with imprisonment of either description for a term which shall be not less than six months but which may extend to five years and shall also be liable to fine.",
        "examples": [
            "Government official taking bribe for approving license",
            "Police officer accepting money for not filing case",
            "Judge taking gratification for favorable judgment",
            "Municipal officer demanding money for property approval",
            "Tax officer accepting bribe for reducing tax liability"
        ]
    },

    # FAMILY/DOMESTIC CRIMES
    {
        "section": "498A", "title": "Husband or relative of husband of a woman subjecting her to cruelty",
        "description": "Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine.",
        "examples": [
            "Domestic violence and mental torture by husband",
            "Dowry harassment and cruelty by in-laws",
            "Physical abuse and emotional torture in marriage",
            "Harassment for not bringing sufficient dowry",
            "Mental cruelty and threats by husband's family"
        ]
    }
]

def get_training_data():
    """Return the BNS training dataset"""
    return BNS_TRAINING_DATA

def get_all_sections():
    """Get list of all BNS sections covered"""
    return [item["section"] for item in BNS_TRAINING_DATA]

def get_section_details(section_number):
    """Get details for a specific section"""
    for item in BNS_TRAINING_DATA:
        if item["section"] == section_number:
            return item
    return None

if __name__ == "__main__":
    print(f"📊 BNS Training Dataset Statistics:")
    print(f"   • Total Sections: {len(BNS_TRAINING_DATA)}")
    print(f"   • Total Examples: {sum(len(item['examples']) for item in BNS_TRAINING_DATA)}")
    print(f"   • Sections Covered: {', '.join(get_all_sections())}")
