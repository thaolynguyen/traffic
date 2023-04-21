# # Avisia Web Traffic

# ## Start browser
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import logging
import toolbox as toolbox


# Import actions
pd.set_option('display.max_colwidth', None)
    # Homepage
with open('parameter files/homepage_actions.json') as js:
    hp_actions = pd.read_json(js)
    # Category page
with open('parameter files/category_actions.json') as js:
    category_actions = pd.read_json(js)
    # Product Page
with open('parameter files/productpage_actions.json') as js:
    productpage_actions = pd.read_json(js)
    # Connexion Page
with open('parameter files/connexion_actions.json') as js:
    connexion_actions = pd.read_json(js)
    # Navigation accross pages
with open('parameter files/pagesnav_actions.json') as js:
    pagesnav_actions = pd.read_json(js)
    # Cart, Modal and Product Pages parameters
with open('parameter files/conversion_actions.json') as js:
    conversion_actions = pd.read_json(js)
    # Cart actions
with open('parameter files/cart_actions.json') as js:
    cart_actions = pd.read_json(js)
    # User information
with open('parameter files/user_informations.json') as js:
    user_informations = pd.read_json(js)


## COMPILATION #################

# Driver
#driver = webdriver.Chrome('/opt/homebrew/bin/chromedriver')
#driver.implicitly_wait(2) # seconds
#driver.get("https://avisia-tools.fr/site-formation-ecommerce/")



from selenium import webdriver

driver = webdriver.Remote(
   command_executor='http://127.0.0.1:4444/wd/hub',
   options=webdriver.ChromeOptions()
)

driver.get("https://avisia-tools.fr/site-formation-ecommerce/")

# Init
pagesnav_actions_file=pagesnav_actions

# Parameters
size = user_informations.loc[0, 'size']
email = user_informations.loc[0, 'email']
password = user_informations.loc[0, 'password']
account = user_informations.loc[0, 'account']=='True'
gender = user_informations.loc[0, 'gender']
firstname = user_informations.loc[0, 'firstname']
lastname = user_informations.loc[0, 'lastname']
birthdate = user_informations.loc[0, 'birthdate']
address = user_informations.loc[0, 'address']
postcode = str(user_informations.loc[0, 'postcode'])
city = user_informations.loc[0, 'city']

# Page Nav
npage = 1
next = "continue"

# Configure logging
logging.basicConfig(filename='logs/navigation.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Navigation
logging.info("NAVIGATION START")
while next == "continue":
    try:
        page,actions,parameters = toolbox.FileSelector(driver,pagesnav_actions_file,conversion_actions)
        logging.info("Page" + str(npage) + " - NEXT ACTION : Continue on page " + page)
        if page == 'Homepage':
            toolbox.HomepageNavigation(driver,vars()[actions],email,password)
        elif page == 'Category':
            toolbox.CategoryPageNavigation(driver,vars()[actions],email,password)
        elif page == 'ProductPage':
            toolbox.ProductPageNavigation(driver,vars()[actions],parameters,size,email,password)
        elif page == 'Modal':
            toolbox.ModalNavigation(driver,parameters,size)
        elif page == 'Cart':
            toolbox.CartNavigation(driver,vars()[actions],parameters,email,password)
        elif page == 'ConfirmAddToCart':
            toolbox.ConfirmAddToCartNavigation(driver,parameters)
        elif page == 'OrderPage':
            toolbox.CheckoutNavigation(driver,account,gender,firstname,lastname,email,password,birthdate,address,postcode,city)
        elif page == 'Connexion':
            toolbox.ConnexionNavigation(driver,vars()[actions],account,email,password,gender,firstname,lastname,birthdate)
        elif page == 'Account':
            # Go back on homepage
            driver.find_element(By.CSS_SELECTOR, "#_desktop_logo > a > img").click()
                
    except Exception as e:
        logging.error(f'An error occurred: {e}')

    driver.implicitly_wait(3)
    if page == 'OrderConfirmation':
        next = "end"
        logging.info("Order confirmed >> NAVIGATION END")
        driver.quit()
        break
    else:
        next = "continue"
        npage+=1
        continue