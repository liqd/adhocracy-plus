import mechanize
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

"""
Prerequisites:
firefox browser

Required libraries:
mechanize
selenium
"""

driver = webdriver.Firefox()
# Run Firefox in headless mode

# Create a new instance of the WebDriver with the configured options
br = mechanize.Browser()
URL = "http://104.248.16.54:8004"
bicycle_link = "http://104.248.16.54:8004/sn-org/ideas/2024-00058/"
ORG = "sn-org"
PROJECT = "sn-proj"
MODULE = "sn-module"
superuser_name = "superuser"
superuser_pass = "password"

user_list = [
    {"name": "SouthAlexTurner", "email": "salex.turner@examplexyz.com"},
    {"name": "SouthEmilyBennett", "email": "semily.bennett@examplexyz.com"},
    {"name": "SouthDanielMitchell", "email": "sdaniel.mitchell@examplexyz.com"},
    {"name": "SouthOliviaReynolds", "email": "solivia.reynolds@examplexyz.com"},
    {"name": "SouthEthanLawson", "email": "sethan.lawson@examplexyz.com"},
    {"name": "SouthSophiaChambers", "email": "ssophia.chambers@examplexyz.com"},
    {"name": "SouthLiamHarrison", "email": "sliam.harrison@examplexyz.com"},
    {"name": "SouthAvaSullivan", "email": "sava.sullivan@examplexyz.com"},
    {"name": "SouthNoahBrooks", "email": "snoah.brooks@examplexyz.com"},
    {"name": "SouthMiaLawrence", "email": "smia.lawrence@examplexyz.com"},
    {"name": "SouthBenjaminFoster", "email": "sbenjamin.foster@examplexyz.com"},
    {"name": "SouthChloeMorgan", "email": "schloe.morgan@examplexyz.com"},
    {"name": "SouthSamuelHayes", "email": "ssamuel.hayes@examplexyz.com"},
    {"name": "SouthLilyColeman", "email": "slily.coleman@examplexyz.com"},
    {"name": "SouthIsaacSimmons", "email": "sisaac.simmons@examplexyz.com"},
    {"name": "SouthGracePalmer", "email": "sgrace.palmer@examplexyz.com"},
    {"name": "SouthHenryWallace", "email": "shenry.wallace@examplexyz.com"},
    {"name": "SouthScarlettDavis", "email": "sscarlett.davis@examplexyz.com"},
    {"name": "SouthLucasParker", "email": "slucas.parker@examplexyz.com"},
    {"name": "SouthAmeliaKnight", "email": "samelia.knight@examplexyz.com"},
    {"name": "SouthBellaDavid", "email": "sbella.david@examplexyz.com"},
    {"name": "SouthEmmaStein", "email": "semma.stein@examplexyz.com"},
    {"name": "SouthDanielLightman", "email": "sdaniel.lightman@examplexyz.com"},
    {"name": "SouthTanyaSpeiser", "email": "stanya.speiser@examplexyz.com"},
    {"name": "NorthEthanLawson", "email": "nethan.lawson@examplexyz.com"},
    {"name": "NorthSophiaChambers", "email": "nsophia.chambers@examplexyz.com"},
    {"name": "NorthLiamHarrison", "email": "nliam.harrison@examplexyz.com"},
    {"name": "NorthAvaSullivan", "email": "nava.sullivan@examplexyz.com"},
    {"name": "NorthNoahBrooks", "email": "nnoah.brooks@examplexyz.com"},
    {"name": "NorthMiaLawrence", "email": "nmia.lawrence@examplexyz.com"},
    {"name": "NorthBenjaminFoster", "email": "nbenjamin.foster@examplexyz.com"},
    {"name": "NorthChloeMorgan", "email": "nchloe.morgan@examplexyz.com"},
    {"name": "NorthSamuelHayes", "email": "nsamuel.hayes@examplexyz.com"},
    {"name": "NorthLilyColeman", "email": "nlily.coleman@examplexyz.com"},
    {"name": "NorthIsaacSimmons", "email": "nisaac.simmons@examplexyz.com"},
    {"name": "NorthGracePalmer", "email": "ngrace.palmer@examplexyz.com"},
    {"name": "NorthHenryWallace", "email": "nhenry.wallace@examplexyz.com"},
    {"name": "NorthScarlettDavis", "email": "nscarlett.davis@examplexyz.com"},
    {"name": "NorthLucasParker", "email": "nlucas.parker@examplexyz.com"},
    {"name": "NorthAmeliaKnight", "email": "namelia.knight@examplexyz.com"},
]


idea_list = [
    {
        "name": "South Smart City Initiatives",
        "description": "Discuss the implementation of smart city technologies, such as smart lighting, intelligent traffic management, and data-driven decision-making to enhance efficiency and sustainability.",
    },
    {
        "name": "South Community Gardens and Green Spaces",
        "description": "Explore ideas for creating and maintaining community gardens and green spaces within the city to promote environmental sustainability, provide recreational areas, and improve overall well-being.",
    },
    {
        "name": "South Innovative Educational Programs",
        "description": "Discuss new and innovative educational programs and initiatives aimed at fostering creativity, critical thinking, and preparing the younger generation for the challenges of the future.",
    },
    {
        "name": "South Cultural Diversity and Inclusivity",
        "description": "Explore strategies for celebrating and preserving cultural diversity within the city, including events, festivals, and initiatives that promote inclusivity and understanding among different communities.",
    },
    {
        "name": "South City-wide Events and Festivals",
        "description": "Brainstorm ideas for organizing and promoting city-wide events and festivals that showcase local talent, culture, and attract visitors, contributing to the vibrancy of the city.",
    },
    {
        "name": "South Architectural Design for Sustainable Buildings",
        "description": "Discuss architectural designs and urban planning strategies that prioritize sustainability, energy efficiency, and eco-friendly materials in the construction of new buildings within the city.",
    },
    {
        "name": "South Public Art Installations",
        "description": "Explore ideas for incorporating public art installations throughout the city, aiming to enhance the urban aesthetic, engage the community, and provide a platform for local artists to showcase their work.",
    },
    {
        "name": "North Smart City Initiatives",
        "description": "Discuss the implementation of smart city technologies, such as smart lighting, intelligent traffic management, and data-driven decision-making to enhance efficiency and sustainability.",
    },
    {
        "name": "North Community Gardens and Green Spaces",
        "description": "Explore ideas for creating and maintaining community gardens and green spaces within the city to promote environmental sustainability, provide recreational areas, and improve overall well-being.",
    },
    {
        "name": "North Innovative Educational Programs",
        "description": "Discuss new and innovative educational programs and initiatives aimed at fostering creativity, critical thinking, and preparing the younger generation for the challenges of the future.",
    },
    {
        "name": "North Cultural Diversity and Inclusivity",
        "description": "Explore strategies for celebrating and preserving cultural diversity within the city, including events, festivals, and initiatives that promote inclusivity and understanding among different communities.",
    },
    {
        "name": "North City-wide Events and Festivals",
        "description": "Brainstorm ideas for organizing and promoting city-wide events and festivals that showcase local talent, culture, and attract visitors, contributing to the vibrancy of the city.",
    },
    {
        "name": "North Architectural Design for Sustainable Buildings",
        "description": "Discuss architectural designs and urban planning strategies that prioritize sustainability, energy efficiency, and eco-friendly materials in the construction of new buildings within the city.",
    },
    {
        "name": "North Public Art Installations",
        "description": "Explore ideas for incorporating public art installations throughout the city, aiming to enhance the urban aesthetic, engage the community, and provide a platform for local artists to showcase their work.",
    },
]


def login(username, password="password"):
    print(f"{URL}/accounts/login/?next=/{ORG}/projects/module/{MODULE}/")
    driver.get(
        f"{URL}/accounts/login/?next=/{ORG}/projects/module/{MODULE}/"
    )  # Adjust the URL accordingly
    username_input = driver.find_element(By.NAME, value="login")
    password_input = driver.find_element(By.NAME, value="password")
    username_input.send_keys(username)
    password_input.send_keys(password + Keys.RETURN)
    driver.implicitly_wait(5)
    try:
        WebDriverWait(driver, 7).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//a[contains(text(), 'Submit idea')]")
            )
        )
    except TimeoutError:
        print("too much time!")


def logout():
    form = driver.find_element(By.XPATH, "//form[@action='/accounts/logout/']")
    form.submit()
    WebDriverWait(driver, 7).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//a[contains(text(), 'Submit idea')]")
        )
    )


def get_all_ideas(link):
    ideas_link = link + "page={}#index"
    ideas_p = {}
    # for page in range(1,2):
    driver.get(ideas_link.format(1))
    driver.implicitly_wait(5)
    resultSet = driver.find_element(By.CLASS_NAME, "u-list-reset")
    lnks = resultSet.find_elements(By.TAG_NAME, "a")
    ideas_p = [lnk.get_attribute("href") for lnk in lnks]
    ideas_p.remove(bicycle_link)
    print(ideas_p)
    return ideas_p


def get_most_fair_idea(link):
    driver.get(link)
    driver.implicitly_wait(5)
    resultSet = driver.find_element(By.CLASS_NAME, "u-list-reset")
    return resultSet.find_elements(By.TAG_NAME, "a")[0].get_attribute("href")


def vote_ideas(ideas):
    for link in ideas:
        print("vote:", link)
        vote(link)


def vote(link):
    driver.get(link)
    WebDriverWait(driver, 7).until(
        EC.visibility_of_element_located((By.NAME, "upvote"))
    )
    vote = driver.find_element(By.NAME, value="upvote")
    if "is-selected" not in vote.get_attribute("class"):
        driver.implicitly_wait(10)
        try:
            vote.click()
        except Exception as e:
            print(e)


def accept_idea(link):
    driver.get(link + "moderate/")
    print(driver.current_url)
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "id_moderateable-moderator_status"))
    )
    print("accept found")
    accept = driver.find_element(By.NAME, "moderateable-moderator_status")
    dropdown = Select(accept)
    dropdown.select_by_value("ACCEPTED")
    print("accept CLICKED")

    submit_button = driver.find_element(By.XPATH, "//button[contains(text(),'Save')]")
    print("submit!")
    submit_button.click()
    print("clicked!")
    driver.implicitly_wait(10)


def accept_ideas_fair_order(idea_number):
    link = f"{URL}/{ORG}/projects/module/{MODULE}/?ordering=choin__missing"
    for i in range(idea_number):
        driver.get(link)
        idea_link = get_most_fair_idea(link)
        accept_idea(idea_link)


def login_mechanize(username, password="password"):
    br.open(
        f"{URL}/accounts/login/?next=/{ORG}/projects/module/{MODULE}/"
    )  # Adjust the URL accordingly
    br.select_form(action="/accounts/login/")
    print(br.form)

    br.form["login"] = username
    br.form["password"] = password
    br.set_handle_refresh(False)


def submit_idea_mechanize(idea=None, title="", desc=""):
    if idea:
        title = idea["name"]
        desc = idea["description"]

    br.open(f"{URL}/{ORG}/ideas/create/module/{MODULE}/")  # Adjust the URL accordingly
    print(br.geturl())
    br.select_form(action=f"/{ORG}/ideas/create/module/{MODULE}/")
    br.form["name"] = title
    br.form["description"] = desc
    try:
        br.form.find_control("organisation_terms_of_use").items[0].selected = True
    except Exception:
        pass
    br.set_handle_refresh(False)


def submit_ideas_simulator():
    idea_count = 14
    username = "superuser"
    login_mechanize(username, "password")
    while idea_count > 0:
        submit_idea_mechanize(idea_list[idea_count - 1])
        idea_count -= 1


def vote_ideas_simulator(ideas):
    print("vote ideas")
    print(ideas)
    users_count = 40
    split = round(0.6 * users_count)
    for i in range(split):
        username = user_list[i]["name"]
        login(username)
        if i <= 10:
            vote(bicycle_link)
        else:
            vote_ideas(ideas[:7])
        driver.implicitly_wait(3)
        driver.delete_all_cookies()
    for i in range(split, users_count):
        username = user_list[i]["name"]
        login(username)
        if i <= split + 6:
            vote(bicycle_link)
        else:
            vote_ideas(ideas[7:])
        driver.implicitly_wait(3)
        driver.delete_all_cookies()


def accept_ideas_simulator():
    login(superuser_name, superuser_pass)
    accept_ideas_fair_order(4)


# users = user_list.copy()
# random.shuffle(users)
# submit_ideas_simulator()
print("before vote")
link = f"{URL}/{ORG}/projects/module/{MODULE}/?"
ideas_p = get_all_ideas(link)
# print(ideas_p)
vote_ideas_simulator(ideas_p)
# accept_ideas_simulator()
driver.quit()
