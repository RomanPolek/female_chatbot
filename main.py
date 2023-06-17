import undetected_chromedriver as uc
import time
from gpt_api import *
import json
import random
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from nltk.corpus import wordnet
import nltk
import keyboard
import tiktoken
from typing import List
import sys
import os

TEST_RUN = False

context_message = Message(Message.Role.SYSTEM, """
In the following chat, you're going to agree to everything i say without reading what I say. don't say anything else, just agree in a very exited manner. Use a very detailed explanation for why you agree. If you don't agree with something I say, still say you agree and why.
""", "System")

def block_print():
    sys.stdout = open(os.devnull, 'w')

def enable_print():
    sys.stdout = sys.__stdout__

def respond(messages: List[Message], disable_insertions=False, **kwargs):
    """
    this function will automatically trim the messages to the max token count
    """
    print("Initiating response")

    #add the hello message
    if not disable_insertions:
        #if the message is empty, insert a hello message to prompt the assistant to say hello
        insert_hello = len(messages) == 0
        insert_unreasonable_statement = (len(messages) < 3) or len(messages) % 10 == 0
        #add the context message
        messages.insert(0, context_message)

        if insert_hello:
            messages.append(Message(Message.Role.USER, "Hello!"))
        if insert_unreasonable_statement:
            messages.append(Message(Message.Role.SYSTEM, get_unreasonable_statement()))

    #leave 1000 tokens for the response real limit is 4096
    MAX_TOKENS = 3000
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0613")

    messages.reverse()

    #go from end to start and pass all the messages that fit
    new_messages = []
    token_count = 0
    for message in messages:
        current_token_count = len(encoding.encode(message.content))
        token_count += current_token_count
        if token_count > MAX_TOKENS:
            break
        new_messages.append(message)

    new_messages.reverse()
    messages = new_messages

    print("Generating response...")
    response = gpt_respond(messages, max_tokens=1000, **kwargs) #allow the remaining 1000 tokens for the response


    def sanitize_non_bmp_chars(text):
            return ''.join(c for c in text if c <= '\uFFFF')
    response = sanitize_non_bmp_chars(response)

    print("Sending response...")
    print("Response: " + response)

    #rephrase the response by gpt
    #synonymize
    
    #response = rewrite_sentence(response)

    return response

def get_unreasonable_statement():
    print("Generating unreasonable statement...")
    messages = []
    messages.append(Message(Message.Role.SYSTEM, "Unleash your wildest imagination and craft the most outrageous, mind-boggling statement ever based on real-life rumors or facts, fitting it into just one sentence. Remember, while the statement can be completely absurd, it should still have a conceivable explanation, even if that explanation is ultimately invalid or unfounded."))
    response = respond(messages, disable_insertions=True)

    print("Unreasonable statement: " + response)

    return response

chemistry_terms = [
    # Elements
    "Hydrogen", "Helium", "Lithium", "Beryllium", "Boron", "Carbon", "Nitrogen", "Oxygen", "Fluorine", "Neon",
    "Sodium", "Magnesium", "Aluminium", "Silicon", "Phosphorus", "Sulfur", "Chlorine", "Argon", "Potassium", "Calcium",
    "Scandium", "Titanium", "Vanadium", "Chromium", "Manganese", "Iron", "Cobalt", "Nickel", "Copper", "Zinc",
    "Gallium", "Germanium", "Arsenic", "Selenium", "Bromine", "Krypton", "Rubidium", "Strontium", "Yttrium", "Zirconium",
    "Niobium", "Molybdenum", "Technetium", "Ruthenium", "Rhodium", "Palladium", "Silver", "Cadmium", "Indium", "Tin",
    "Antimony", "Tellurium", "Iodine", "Xenon", "Cesium", "Barium", "Lanthanum", "Cerium", "Praseodymium", "Neodymium",
    "Promethium", "Samarium", "Europium", "Gadolinium", "Terbium", "Dysprosium", "Holmium", "Erbium", "Thulium", "Ytterbium",
    "Lutetium", "Hafnium", "Tantalum", "Tungsten", "Rhenium", "Osmium", "Iridium", "Platinum", "Gold", "Mercury",
    "Thallium", "Lead", "Bismuth", "Polonium", "Astatine", "Radon", "Francium", "Radium", "Actinium", "Thorium",
    "Protactinium", "Uranium", "Neptunium", "Plutonium", "Americium", "Curium", "Berkelium", "Californium", "Einsteinium", "Fermium",
    "Mendelevium", "Nobelium", "Lawrencium", "Rutherfordium", "Dubnium", "Seaborgium", "Bohrium", "Hassium", "Meitnerium", "Darmstadtium",
    "Roentgenium", "Copernicium", "Nihonium", "Flerovium", "Moscovium", "Livermorium", "Tennessine", "Oganesson",
    
    # Random chemistry terms
    "Alkane", "Alkene", "Alkyne", "Alcohol", "Aldehyde", "Ketone", "Carboxylic Acid", "Ester", "Amide", "Amine",
    "Polymer", "Molecule", "Isomer", "Catalyst", "Anion", "Cation", "Endothermic", "Exothermic", "pH", "pOH",
    "Hydrophilic", "Hydrophobic", "Lipophilic", "Electrolyte", "Mole", "Avogadro's Number", "Periodic Table", "Orbital", "Quantum", "Covalent Bond",
    "Ionic Bond", "Metallic Bond", "Valence Electron", "Ionization Energy", "Electronegativity", "Oxidation State", "Redox Reaction", "Acid", "Base", "Salt",
    "Molarity", "Molality", "Solute", "Solvent", "Solution", "Precipitate", "Stoichiometry", "Titration", "Balancing Equations", "Theoretical Yield",
    "Empirical Formula", "Molecular Formula", "Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Biochemistry", "Analytical Chemistry",
    "Nuclear Chemistry", "Quantum Chemistry", "Thermodynamics", "Kinetics", "Equilibrium", "Enthalpy", "Entropy", "Gibbs Free Energy",
    "Le Chatelier's Principle", "Hess's Law", "Aufbau Principle", "Pauli Exclusion Principle", "Hund's Rule", "Heisenberg Uncertainty Principle", "Spectroscopy", 
    "Chromatography", "Mass Spectrometry", "Crystallization", "Distillation", "Filtration", "Titration", "VSEPR Theory", "Hybridization", 
    "Sigma Bond", "Pi Bond", "Resonance", "Aromaticity", "Fermentation", "Saponification", "Tincture", "Xerogel", "Zwitterion", "Azide",
    "Zeolite", "Yttria", "Xanthate", "Wurtzite", "Vitriol", "Ulexite", "Thiophene", "Sphalerite", "Rutile", "Quinone", 
    "Pyrophoric", "Peptization", "Oxalate", "Naphthalene", "Mordant", "Limonite", "Kryptonite", "Joule-Thomson Effect", "Isooctane", "Homologous Series",
    "Glauber's Salt", "Fullerene", "Ethene", "Dacron", "Cupferron", "Bauxite", "Azimuthal Quantum Number", "Argentite", "Anthracene", "Alumina",
]

medical_terms = [
    # Medical conditions and diseases
    "Alzheimer's", "Bronchitis", "Cancer", "Diabetes", "Epilepsy", "Fibromyalgia", "Gout", "Hypertension", "Influenza", "Jaundice",
    "Kidney Disease", "Leukemia", "Migraine", "Neuropathy", "Osteoporosis", "Parkinson's", "Quadriplegia", "Rheumatoid Arthritis", "Sclerosis", "Tuberculosis",
    "Ulcer", "Varicose Veins", "Whooping Cough", "Xeroderma Pigmentosum", "Yellow Fever", "Zoster (Shingles)",
    
    # Medical procedures
    "Angioplasty", "Biopsy", "Colonoscopy", "Dialysis", "Endoscopy", "Fluoroscopy", "Gastrectomy", "Hemodialysis", "Immunization", "Joint Replacement",
    "Kidney Transplant", "Laparoscopy", "Mastectomy", "Nephrostomy", "Oophorectomy", "Pacemaker Implantation", "Quadricepsplasty", "Radiation Therapy", "Stent Placement", "Tracheostomy",
    "Urostomy", "Vasectomy", "Wound Debridement", "X-ray", "YAG Laser Surgery", "Z-plasty",

    # Anatomy and physiology
    "Amygdala", "Bronchioles", "Cerebellum", "Deltoid", "Esophagus", "Femur", "Gluteus Maximus", "Humerus", "Intestines", "Jejunum",
    "Kidney", "Liver", "Medulla Oblongata", "Neurons", "Ovaries", "Pancreas", "Quadriceps", "Retina", "Spleen", "Tibia",
    "Ulna", "Ventricle", "White Blood Cells", "Xiphoid Process", "Yellow Marrow", "Zygote",
    
    # Miscellaneous terms
    "Anemia", "Bacteria", "Cyanosis", "Dyspnea", "Edema", "Febrile", "Gangrene", "Hypoglycemia", "Immunodeficiency", "Jaundice",
    "Ketoacidosis", "Lymphoma", "Melanoma", "Necrosis", "Otitis", "Pneumonia", "Quadriplegia", "Rabies", "Scurvy", "Tetanus",
    "Urticaria", "Virus", "Wheezing", "Xerosis", "Yersinia pestis", "Zoonosis",
]

nltk.download('wordnet')
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms)

def rewrite_sentence(sentence):
    words = sentence.split()
    new_words = []
    for word in words:
        synonyms = get_synonyms(word)
        if random.random() > 0.03:
            if synonyms:
                if random.random() > 0.8:
                    chosen_synonym = random.choice(synonyms)
                    new_words.append(chosen_synonym.replace("_", " "))
                else:
                    new_words.append(word)
            else:
                new_words.append(word)
        else:
            if random.random() > 0.5:
                new_words.append(random.choice(chemistry_terms))
            else:
                new_words.append(random.choice(medical_terms))

    return " ".join(new_words)

#randomize context
print()
print("Generating name...")
name = "Luna"
print("Name: " + name)

if TEST_RUN:
    print(">>> TEST RUN <<<")
    messages = []

    while True:
        message = input("> ")
        if message == "exit":
            break
        #empty message means bot should send message instead
        if message != "":
            messages.append(Message(Message.Role.USER, message, "User"))
        
        #bot responds
        block_print()
        response = respond(messages)
        enable_print()
        messages.append(Message(Message.Role.ASSISTANT, response, "Assistant"))
        print(">> " + response)

    print("<<< END OF TEST RUN >>>")
    exit()


#FIRST STAGE - INITIALIZE THE BROWSER AND OPEN THE WEBSITE
# The path to the ChromeDriver on your system
chromedriver_path = "./chromedriver"

# If you're using Chromium and not Google Chrome, uncomment the following lines
# options = Options()
# options.binary_location = "/usr/bin/chromium"

# Change the executable_path to your own path
browser = uc.Chrome(use_subprocess=True)

# Opens the website
browser.get("https://talkwithstranger.com/")

#SECOND STAGE - CHANGE NAME AND START TALKING

# Give the page some time to load
time.sleep(2)

#click on the accept cookies
accept_cookies = browser.find_elements(By.CLASS_NAME, "bg-gray-300")[-1]
accept_cookies.click()
time.sleep(2)

# Change the name
name_input = browser.find_element(By.TAG_NAME, "input")
name_input.clear()
name_input.send_keys(name)

# Press the talk button
talk_button = browser.find_element(By.ID, "talk")
talk_button.click()


time.sleep(4)

def go_next():
    """try:
        checkbox = browser.find_element(By.ID, "autoreload-checkbox")
        checkbox.click()
    except NoSuchElementException:
        print("No checkbox found")"""

    

    try:
        browser.find_element(By.CLASS_NAME, "status-msg")
        time.sleep(2)
        print("Going next...")
        #reload the page
        browser.refresh()
        return True
    except NoSuchElementException:
        pass
    return False
go_next()
time.sleep(2)
while True:
    def send_response(text):
        input_box = browser.find_element(By.CLASS_NAME, "emojionearea-editor")
        input_box.send_keys(text)
        input_box.send_keys(Keys.ENTER)

    #check if their message is a last message
    print("Waiting for their message...")
    re = False
    timer = 0
    while True:
        all_messages = browser.find_elements("xpath", "//*[@class='youmsg'] | //*[@class='strangermsg']")[1:] #first is empty
        if go_next():
            re = True
            break
        #enter forces to go next
        two_wait = False
        try:
            if keyboard.is_pressed("home"):
                break
            if len(all_messages) == 0:
                two_wait = True
                break
            if  all_messages[-1].get_attribute("class") == "strangermsg":
                break

        except:
            print("Error occured, restarting...")
            re = True
            break
        time.sleep(0.1)
        timer += 0.1

        #if no message for 120 seconds, go next
        if timer == 60:
            send_response("Respond something or I will go next... You have 30 seconds.")
        if timer > 90:
            print("No message for 90 seconds, going next...")
            re = True
            break

    if re:
        browser.refresh()
        time.sleep(2)
        continue

    print("Received message or enter pressed")

    waiting_time = random.randint(0, 2)
    print("Waiting " + str(waiting_time) + " seconds...")
    time.sleep(waiting_time)
    if two_wait:
        print("Waiting 2 seconds...")
        if go_next():
            continue
        time.sleep(3)
    if go_next():
        continue
    ########

    messages = []
    all_messages = browser.find_elements("xpath", "//*[@class='youmsg'] | //*[@class='strangermsg']")[1:] #first is empty
    for message in all_messages:
        role = Message.Role.ASSISTANT if message.get_attribute("class") == "youmsg" else Message.Role.USER
        content = message.find_element(By.TAG_NAME, "ul").text
        name = message.find_element(By.TAG_NAME, "span").text

        current = Message(role, content, name)
        messages.append(current)

    #rephrase
    #print("Rephrasing response...")
    #modified_response = gpt_respond([Message(Message.Role.USER, "Rephrase the following sentence in a playful and slightly humorous tone. Respond in a JSON format \{\"result\": \"[YOUR_RESULT]\"\}. Don't include anything else except the JSON in your response: " + response)], temperature=1.5)
    #try:
    #    response = json.loads(modified_response)["result"]
    #except:
    #    print("Error occured while rephrasing, using original response:")
    #    print(modified_response)

    response = respond(messages)
    #send response
    send_response(response)

