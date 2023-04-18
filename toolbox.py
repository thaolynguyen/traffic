import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import re
import logging



def is_element_enabled(driver, selector):
    try:
        # Is the element enabled on the web page
        return driver.find_element(By.CSS_SELECTOR,selector).is_enabled()
    except:
        # if the element is not enabled, return False
        return False

def is_element_visible(driver, selector):
    try:
        # wait until the element is visible on the web page
        return WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector))).get_attribute("innerHTML") != ''
    except:
        # if the element is not visible, return False
        return False

def random_path(driver,input_df):
    '''Randomly select an element from the input_df and return the selected element name and a dataframe containing
    information about the selected element.
    
    Args:
        driver: An instance of Selenium webdriver.
        input_df: A Pandas dataframe containing information about the elements to select.
    
    Returns:
        A tuple containing the name of the selected element and a Pandas dataframe containing information about the
        selected element.
    '''

    # Else randomly select a section.
    random_section_selected = random.choices(input_df["levelname"], weights=input_df["ProbaToSelect"])[0]
    output_df = pd.DataFrame(input_df[input_df["levelname"]==random_section_selected])

    # Exception HP : Case when "Cart" not available => Quit
    if random_section_selected == 'cart':
        selector = output_df[output_df['levelname'] == 'cart']['selector'].to_string(index=False)
        try:
            driver.find_element(By.CSS_SELECTOR,selector).is_enabled()
        except:
            driver.quit()
            logging.info("NAVIGATION END")

    return random_section_selected,output_df


def website_actions(driver, level_df, previous_level_df):
    '''Website navigation: action sequence'''

    # Check if driver is OK
    try:
        current_url = driver.current_url

        # Initialize new dataframe
        if str("ProductThumbnail") in level_df['levelname'].to_string(index=False):
            # Product selected
            num_product = int(level_df['levelname'].to_string(index=False).replace('ProductThumbnail',''))
            # New DataFrame > Sublevels
            new_level_df = pd.DataFrame(level_df['sublevels'].to_list()[0])
            new_level_df['levelname'] = new_level_df['levelname'].apply(lambda x: x.format(num_product))
            new_level_df['selector'] = new_level_df['selector'].apply(lambda x: x.format(num_product))
        else:
            new_level_df = pd.DataFrame(level_df['sublevels'].to_list()[0])

        # Define action
        if float(level_df['ProbaToClick']) > 0.0:

            # New variables init
            ProbaToClick = float(level_df["ProbaToClick"])
            NbActions = int(level_df['NbActions'])
            action = random.choices(["click","continue"], weights=[ProbaToClick,1.0-ProbaToClick])[0]

            # Action
            if NbActions==0:
                #new_level_df = pd.DataFrame(level_df['sublevels'].to_list()[0])
                return "No action", pd.DataFrame(new_level_df)
            elif NbActions==1:
                if action == 'click':
                    if str("ListElement") in level_df["levelname"].to_string(index=False):
                        selector = level_df['selector'].to_string(index=False)
                        driver.find_element(By.XPATH,selector).click()
                    else:
                        selector = level_df['selector'].to_string(index=False)
                        driver.find_element(By.CSS_SELECTOR,selector).click()
                    return "One action - Click", pd.DataFrame()
                else:
                    #new_level_df = pd.DataFrame(level_df['sublevels'].to_list()[0])
                    return "continue", pd.DataFrame(new_level_df)
            elif NbActions>1:
                if action == 'click':
                    product = driver.find_element(By.CSS_SELECTOR,previous_level_df['selector'].to_string(index=False))
                    quickview = driver.find_element(By.CSS_SELECTOR,level_df['selector'].to_string(index=False))
                    actions = ActionChains(driver)
                    actions.move_to_element(product)
                    actions.click(on_element=quickview)
                    actions.perform()
                    return "Two actions - Click", pd.DataFrame()
                else:
                    #new_level_df = pd.DataFrame(level_df['sublevels'].to_list()[0])     
                    return "continue", pd.DataFrame(new_level_df)

        elif float(level_df['ProbaToClick'])==0.0:
            #new_level_df = pd.DataFrame(level_df['sublevels'].to_list()[0])
            return "continue", pd.DataFrame(new_level_df)
        
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        return "stop", pd.DataFrame()


def UserConnexion(driver,connexion_df,email,password):    
    '''Connexion  to user account'''
    driver.find_element(By.CSS_SELECTOR,connexion_df[connexion_df['levelname']=='EmailForm']['selector'].to_string(index=False)).send_keys(email)
    driver.find_element(By.CSS_SELECTOR,connexion_df[connexion_df['levelname']=='PasswordForm']['selector'].to_string(index=False)).send_keys(password)
    driver.find_element(By.CSS_SELECTOR,connexion_df[connexion_df['levelname']=='ConnexionButton']['selector'].to_string(index=False)).click()

def ConnexionNavigation(driver,actions,account,email,password,gender,firstname,lastname,birthdate):
    ''' Navigation on connexion page '''
    output = PageNavigation(driver,actions,email,password)
    if output is not None:
        if account == True:
            # Connextion to the account
            new_level_df = pd.DataFrame(output['sublevels'].to_list()[0])
            connexion_df = pd.DataFrame(new_level_df['sublevels'][0])
            UserConnexion(driver,connexion_df,email,password)
            logging.info("Account true >> Connexion to profile")
        else:
            # If account does not exist, create one
            selector = "#content > div > a"
            driver.find_element(By.CSS_SELECTOR,selector).click()
            logging.info("Account false >> Create an account")
            driver.implicitly_wait(1)
            # Gender
            if gender == 'M':
                driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(1) > div.col-md-6.form-control-valign > label:nth-child(1) > span > input[type=radio]").click()
            else:
                driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(1) > div.col-md-6.form-control-valign > label:nth-child(2) > span > input[type=radio]").click()   
            # First Name
            driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(2) > div.col-md-6 > input").send_keys(firstname)
            # Last Name
            driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(3) > div.col-md-6 > input").send_keys(lastname)
            # Email
            driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(4) > div.col-md-6 > input").send_keys(email)
            # Password
            driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(5) > div.col-md-6 > div > input").send_keys(password)
            # Birthdate
            driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(6) > div.col-md-6 > input").send_keys(birthdate)
            # Customer Data Privacy
            driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(8) > div.col-md-6 > span > label > input[type=checkbox]").click() 
            # General terms and conditions
            driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(10) > div.col-md-6 > span > label > input[type=checkbox]").click() 
            # Continue
            driver.find_element(By.CSS_SELECTOR,"#customer-form > footer > button").click() 
            logging.info("Account created")
    else:
        pass


    
def FileSelector(driver,pagesnav_actions,conversion_actions):
    '''Define the file to select according to the web page'''

    current_url = driver.current_url
    # define the URLs for different pages
    categorypage_url = "https:\/\/avisia-tools\.fr\/site-formation-ecommerce\/\d+-(\w+)"
    productpage_url = "https:\/\/avisia-tools\.fr\/site-formation-ecommerce\/\S+\/\d+-\S+\.html"

    if current_url == "https://avisia-tools.fr/site-formation-ecommerce/connexion?back=my-account":
        # if the user is on the login page, set the page name as 'Connexion' and get the file and params
        page = 'Connexion'
        file = pagesnav_actions[pagesnav_actions['Page'] == page]['file'].to_string(index=False)
        params = ''
        logging.info(f"Page : {page}")
    elif current_url == "https://avisia-tools.fr/site-formation-ecommerce/panier?action=show":
        # if the user is on the cart page, set the page name as 'Cart' and get the file and params
        page = 'Cart'
        file = pagesnav_actions[pagesnav_actions['Page'] == page]['file'].to_string(index=False)
        params = conversion_actions[conversion_actions['Page']==page] 
        logging.info(f"Page : {page}")
    elif current_url == "https://avisia-tools.fr/site-formation-ecommerce/commande":
        # if the user is on the order page, set the page name as 'OrderPage' and get the file and params
        page = 'OrderPage'
        file = pagesnav_actions[pagesnav_actions['Page'] == page]['file'].to_string(index=False)
        params = ''
        logging.info(f"Page : {page}")
    elif "https://avisia-tools.fr/site-formation-ecommerce/confirmation-commande" in current_url:
        # if the user is on the order confirmation page, set the page name as 'OrderConfirmation' and get the file and params
        page = 'OrderConfirmation'
        file = ''
        params = ''
        logging.info(f"Page : {page}")
    elif current_url == "https://avisia-tools.fr/site-formation-ecommerce/mon-compte":
        # if the user is on the order account page, set the page name as 'Account' and get the file and params
        page = 'Account'
        file = ''
        params = ''
        logging.info(f"Page : {page}")
    elif current_url == "https://avisia-tools.fr/site-formation-ecommerce/":
        if is_element_visible(driver, ".modal-content") and is_element_visible(driver, "#myModalLabel"):
            # if the user has added a product to the cart and is confirming the addition, set the page name as 'ConfirmAddToCart' and get the params
            page = 'ConfirmAddToCart'    
            file = ''
            params = conversion_actions[conversion_actions['Page']==page] 
            logging.info(f"Page : {page}")
        elif is_element_visible(driver, ".modal-content"):
            # if a modal is open on the page, set the page name as 'Modal' and get the params
            page = 'Modal'    
            file = ''
            params = conversion_actions[conversion_actions['Page']==page] 
            logging.info(f"Page : {page}")
        else:
            # if the user is on the homepage, set the page name as 'Homepage' and get the file and params
            page = 'Homepage'
            file = pagesnav_actions[pagesnav_actions['Page'] == page]['file'].to_string(index=False)
            params = ''
            logging.info(f"Page : {page}")
    elif re.match(categorypage_url, current_url): 
        # Check if the ConfirmAddToCart modal is visible, otherwise check if the Modal is visible or else set the page to Category.
        if is_element_visible(driver, ".modal-content") and is_element_visible(driver, "#myModalLabel"):
            page = 'ConfirmAddToCart'    
            file = ''
            params = conversion_actions[conversion_actions['Page']==page] 
            logging.info(f"Page : {page}")
        elif is_element_visible(driver, ".modal-content"):
            page = 'Modal'    
            file = ''
            params = conversion_actions[conversion_actions['Page']==page] 
            logging.info(f"Page : {page}")
        else:
            page = 'Category'
            file = pagesnav_actions[pagesnav_actions['Page'] == page]['file'].to_string(index=False)
            params = conversion_actions[conversion_actions['Page']==page]
            logging.info(f"Page : {page}")
    elif re.match(productpage_url, current_url): 
        # Check if the ConfirmAddToCart modal is visible, otherwise set the page to ProductPage.
        if is_element_visible(driver, "#myModalLabel"):
            page = 'ConfirmAddToCart'    
            file = ''
            params = conversion_actions[conversion_actions['Page']==page] 
            logging.info(f"Page : {page}")
        else:
            page = 'ProductPage'
            file = pagesnav_actions[pagesnav_actions['Page'] == page]['file'].to_string(index=False)
            params = conversion_actions[conversion_actions['Page']==page] 
            logging.info(f"Page : {page}")
    
    # Return the determined page, file, and parameters.
    return page, file, params


def PageNavigation(driver,df_output,email,password):
    """
    Function that navigates a website using a dataframe that defines the possible paths and actions.

    Parameters:
    driver (WebDriver): the Selenium WebDriver object used to navigate the website
    df_output (DataFrame): the dataframe that contains the possible paths and actions
    email (str): email address for website login (if applicable)
    password (str): password for website login (if applicable)

    Returns:
    DataFrame: the final dataframe after navigation is complete
    """
    # Log the current URL
    logging.info(f'Current URL: {driver.current_url}')

    # Initialisation
    step = 0
    statut = 'continue'

    # Boucle While
    while statut == 'continue':
        if step == 0:
            # Select a random path from the dataframe and apply filters
            random_selection,df_output_filtered = random_path(driver,df_output)
            if random_selection == 'exit':
                statut='exit'
                logging.info("Step" + str(step) + " : " + random_selection + ' >> NAVIGATION END')
                driver.quit()
                return None
            else:
                statut='continue'
                logging.info("Step" + str(step) + " : " + random_selection + ' >> ' + statut)
        elif step > 0:
            df_output_prev = df_output.copy()
            df_output_filtered_prev = df_output_filtered.copy()

            # Select a random path from the filtered dataframe
            random_selection,df_output_filtered= random_path(driver,df_output_prev)
            if random_selection =='exit':
                statut = 'exit'
                logging.info("Step" + str(step) + " : NAVIGATION END")
                driver.quit()
                return None
            elif random_selection == 'wrapper':
                # Stop navigation and return filtered dataframe if random path leads to shopping cart
                statut = 'stop'
                logging.info("Step" + str(step) + " : " + random_selection + ' >> ' + statut)
                return df_output_filtered
            else:
                # Perform website actions for selected path
                statut,df_output = website_actions(driver,df_output_filtered,df_output_filtered_prev)
                logging.info("Step" + str(step) + " : " + random_selection + ' >> ' + statut)
    
        step += 1
        driver.implicitly_wait(1) 


def HomepageNavigation(driver,actions,email,password):
    output = PageNavigation(driver,actions,email,password)
    if output is not None:
        new_level_df = pd.DataFrame(output['sublevels'].to_list()[0])
        PageNavigation(driver,new_level_df,email,password)
    else:
        pass
    driver.implicitly_wait(1) 


def CheckoutNavigation(driver,account,gender,firstname,lastname,email,password,birthdate,address,postcode,city):
    ''' Checkout actions : define driver and user informations'''
    try:
        if driver.find_element(By.CSS_SELECTOR,"#checkout-personal-information-step").is_displayed():

            if account == True:
                driver.find_element(By.CSS_SELECTOR,"#checkout-personal-information-step > div > ul > li:nth-child(3) > a").click()
                # Email
                element = driver.find_element(By.CSS_SELECTOR,"#login-form > section > div:nth-child(2) > div.col-md-6 > input")
                element.clear()
                element.send_keys(email)
                # Password
                element = driver.find_element(By.CSS_SELECTOR,"#login-form > section > div:nth-child(3) > div.col-md-6 > div > input")
                element.clear()
                element.send_keys(password)
                # Continue
                driver.find_element(By.CSS_SELECTOR,"#login-form > footer > button").click()    
            else:
                # Gender
                if gender == 'M':
                    driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(1) > div.col-md-6.form-control-valign > label:nth-child(1) > span > input[type=radio]").click()
                else:
                    driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(1) > div.col-md-6.form-control-valign > label:nth-child(2) > span > input[type=radio]").click()   
                # First Name
                driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(2) > div.col-md-6 > input").send_keys(firstname)
                # Last Name
                driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(3) > div.col-md-6 > input").send_keys(lastname)
                # Email
                driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(4) > div.col-md-6 > input").send_keys(email)
                # Password
                driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(5) > div.col-md-6 > div > input").send_keys(password)
                # Birthdate
                driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(6) > div.col-md-6 > input").send_keys(birthdate)
                # Customer Data Privacy
                driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(8) > div.col-md-6 > span > label > input[type=checkbox]").click() 
                # General terms and conditions
                driver.find_element(By.CSS_SELECTOR,"#customer-form > section > div:nth-child(10) > div.col-md-6 > span > label > input[type=checkbox]").click() 
                # Continue
                driver.find_element(By.CSS_SELECTOR,"#customer-form > footer > button").click() 

    except:
        try:
            driver.find_element(By.CSS_SELECTOR,"#checkout-personal-information-step > div > div.clearfix > form > button").click() 
        except:
            pass

    driver.implicitly_wait(2) 

    # 2.Addresses
    try:
        # Address
        element = driver.find_element(By.CSS_SELECTOR,"#delivery-address > div > section > div:nth-child(8) > div.col-md-6 > input")
        element.clear()
        element.send_keys(address)
        # Postcode
        element = driver.find_element(By.CSS_SELECTOR,"#delivery-address > div > section > div:nth-child(10) > div.col-md-6 > input")
        element.clear()
        element.send_keys(postcode)
        # City
        element = driver.find_element(By.CSS_SELECTOR,"#delivery-address > div > section > div:nth-child(11) > div.col-md-6 > input")
        element.clear()
        element.send_keys(city)
        # Continue
        driver.find_element(By.CSS_SELECTOR,"#delivery-address > div > footer > button").click()
    except:
        # Continue
        driver.find_element(By.CSS_SELECTOR,"#checkout-addresses-step > div > div > form > div.clearfix > button").click()

    driver.implicitly_wait(2) 

    # 3.Delivery modes
    delivery_selectors_list = ['#delivery_option_1','#delivery_option_2']
    random_delivery_selector = random.choices(delivery_selectors_list, weights=[0.5,0.5])[0]
    try:
        driver.find_element(By.CSS_SELECTOR,random_delivery_selector).click()
        driver.find_element(By.CSS_SELECTOR,"#js-delivery > button").click()
    except:
        driver.find_element(By.CSS_SELECTOR,"#js-delivery > button").click()

    driver.implicitly_wait(2) 
        
    # 4.Payment
    payment_selectors_list = ['#payment-option-1','#payment-option-2']
    random_payment_selector = random.choices(payment_selectors_list, weights=[0.5,0.5])[0]
    driver.find_element(By.CSS_SELECTOR,random_payment_selector).click()
    #driver.implicitly_wait(1) 
    driver.find_element(By.CSS_SELECTOR,"#conditions_to_approve\[terms-and-conditions\]").click()
    #driver.implicitly_wait(1) 
    driver.find_element(By.CSS_SELECTOR,"#payment-confirmation > div.ps-shown-by-js > button").click()

    logging.info("Order confirmed >> Stop")



def CartNavigation(driver,cart_actions,cart_parameters,email,password):
    """
    Perform cart navigation actions on a website using Selenium WebDriver.

    Args:
        driver: Selenium WebDriver object.
        cart_actions (pd.DataFrame): DataFrame containing the actions that can be performed on the cart.
        cart_parameters (pd.DataFrame): DataFrame containing the parameters for the cart actions.
        email (str): User email.
        password (str): User password.

    Returns:
        None
    """
    # Wrapper
    df_wrapper = PageNavigation(driver,cart_actions,email,password)
    df_wrapper = pd.DataFrame(df_wrapper['sublevels'].to_list()[0])
    # Define next action
    actions = df_wrapper[df_wrapper['levelname'] != 'PageList']['levelname'].to_list()
    probas = df_wrapper[df_wrapper['levelname'] != 'PageList']['ProbaToSelect'].to_list()
    random_action = random.choices(actions, weights=probas)[0]
    # Define next action
    new_level_df = pd.DataFrame(df_wrapper[df_wrapper['levelname'] == random_action])

    if random_action == 'Panier':

        # DataFrame
        df = pd.DataFrame(new_level_df['sublevels'].to_list()[0])
        # Products in cart
        selector = new_level_df['selector'].to_string(index=False)
        products = driver.find_elements(By.CLASS_NAME,selector)
        nb_products = len(products)
        # Selectors to add products
        add_selectors_list = [df[df['levelname'] == 'more products']['selector'].to_string(index=False).format(i+1) for i in range(nb_products)]
        nb_products_to_add = cart_parameters['NbProductsToAdd'].tolist()[0]
        proba_nb_products_to_add = cart_parameters['ProbaNbProductsToAdd'].tolist()[0]
        # Selectors to delete prodcuts
        delete_selectors_list = [df[df['levelname'] == 'delete product']['selector'].to_string(index=False).format(i+1) for i in range(nb_products)]
        # Products names
        productsnames_selectors_list = ["#main > div > div.cart-grid-body.col-xs-12.col-lg-8 > div > div.cart-overview.js-cart > ul > li:nth-child({0}) > div > div.product-line-grid-body.col-md-4.col-xs-8 > div:nth-child(1) > a".format(i+1) for i in range(nb_products)]     
        # Actions on products
        for i in range(nb_products):
            product_name = driver.find_element(By.CSS_SELECTOR,productsnames_selectors_list[i]).text
            productid = "Product" + str(i)
            # Define action
            proba_actions_list = df['ProbaToSelect'].tolist()
            random_action = random.choices(df['levelname'], weights=proba_actions_list)[0]
            # Action
            if random_action == 'more products':
                selector = add_selectors_list[i]
                products_to_add = random.choices(nb_products_to_add, weights=proba_nb_products_to_add)[0]
                for nbclicks in range(products_to_add):
                    driver.find_element(By.CSS_SELECTOR,selector).click()
                logging.info(str(productid) + ' : ' + str(product_name) + ' >> ' + str(products_to_add) + ' products to add')
            elif random_action == 'delete product':
                selector = delete_selectors_list[i]
                driver.find_element(By.CSS_SELECTOR,selector).click()
                logging.info(str(productid) + ' : ' + str(product_name) + ' >> Product to delete')
            else:
                logging.info(str(productid) + ' : ' + str(product_name) + ' >> No action')

        # Cart validation
        selector = cart_parameters['CartValidationSelector'].to_string(index=False)
        driver.find_element(By.CSS_SELECTOR,selector).click()
        logging.info("Cart validated >> stop")

    else:
        selector = new_level_df['selector'].to_string(index=False)
        driver.find_element(By.CSS_SELECTOR,selector).click()
        logging.info("Continue shopping >> stop")




def CategoryPageNavigation(driver,category_actions,email,password):

    '''Navigation on Category Page'''

    output = PageNavigation(driver,category_actions,email,password)

    try:
        if output is not None:
            new_level_df = pd.DataFrame(output['sublevels'].to_list()[0])
            # If the list of pages does not exist, delete it from the nexxt actions options.
            selector = "#js-product-list > nav > div.col-md-6.offset-md-2.pr-0 > ul"
            if is_element_enabled(driver, selector):
                actions = new_level_df['levelname'].to_list()
                probas = new_level_df['ProbaToSelect'].to_list()
            else:
                actions = new_level_df[new_level_df['levelname'] != 'PageList']['levelname'].to_list()
                probas = new_level_df[new_level_df['levelname'] != 'PageList']['ProbaToSelect'].to_list()
            # Define Next action
            random_action = random.choices(actions, weights=probas)[0]
            logging.info("Product Page : navigation in wrapper")
            # If product
            if random_action == 'products':
                productlist_level_df = pd.DataFrame(new_level_df[new_level_df['levelname'] == random_action])
                #product_sublevel_df = pd.DataFrame(product_level_df['sublevels'].to_list()[0])
                # Define the products available on the page.
                nb_products = len(driver.find_elements(By.XPATH, "//div[contains(@itemprop, 'itemListElement')]"))
                productid_list = [i for i in range(1,nb_products+1)]
                # Define the probabilities of selecting each product.
                proba = 1.00 / float(nb_products)
                proba_list = [proba]*nb_products
                # Randomly select a product.
                random_section_selected = random.choices(productid_list, weights=proba_list)[0]
                # Randomly select Quickview or Product
                product_level_df = pd.DataFrame(productlist_level_df['sublevels'].to_list()[0])
                product_sublevel_df = pd.DataFrame(product_level_df['sublevels'].to_list()[0])
                #product_level_df['levelname'] = product_level_df['levelname'].apply(lambda x: x.format(random_section_selected))
                options = product_sublevel_df['levelname'].to_list()
                proba_options = product_sublevel_df['ProbaToSelect'].to_list()
                random_subsection_selected = random.choices(options, weights=proba_options)[0]
                random_subsection_selected
                product_sublevel_filtered_df = product_sublevel_df[product_sublevel_df['levelname'] == random_subsection_selected]
                # Get the web element corresponding to the selected page.
                product_level_selector = product_level_df['selector'].to_string(index=False).format(random_section_selected)
                product_sublevel_selector = product_sublevel_filtered_df['selector'].to_string(index=False).format(random_section_selected)
                # Click on the element
                #If product thumbnail
                if "Product" in random_subsection_selected:
                    logging.info(f"Click on {random_subsection_selected}".format(random_section_selected))
                    driver.find_element(By.CSS_SELECTOR,product_level_selector).click()
                #Elif product quickview
                elif "QuickView" in random_subsection_selected:
                    product = driver.find_element(By.CSS_SELECTOR,product_level_selector)
                    quickview = driver.find_element(By.CSS_SELECTOR,product_sublevel_selector)
                    actions = ActionChains(driver)
                    actions.move_to_element(product)
                    actions.click(on_element=quickview)
                    logging.info(f"Click on {random_subsection_selected}".format(random_section_selected))
                    actions.perform()
            # Elif PageList
            elif random_action == 'PageList':
                # Define list elements
                ListElements = driver.find_elements(By.CSS_SELECTOR,".page-list.clearfix.text-sm-center .js-search-link")
                NbListElements = len(ListElements)
                ListElements_list = [f"ListElement{i}" for i in range(1,NbListElements+1)]
                # Define the probabilities of selecting each page.
                proba = 1.00 / float(NbListElements)
                proba_list = [proba]*NbListElements
                # Randomly select a page.
                random_section_selected = random.choices(ListElements_list, weights=proba_list)[0]
                # Get the web element corresponding to the selected page.
                element = ListElements[int(random_section_selected.replace('ListElement',''))-1]
                # Click on the element
                logging.info(f"Click on {random_section_selected}")
                element.click()
            # Elif Filters
            elif random_action == 'filters':
                logging.info(f"{random_action} >> No action")
        else:
            pass
            #logging.info("Continue navigation")
    except Exception as e:
        logging.error(f"Error in CartNavigation function: {e}")
        pass


def ProductPageNavigation(driver, ProductPage_actions, ProductPage_parameters, size, email, password):

    driver.implicitly_wait(1) 

    # Navigation on page
    output = PageNavigation(driver, ProductPage_actions, email, password)

    # If Wrapper : select if product or social
    if output is not None:    
        new_level_df = pd.DataFrame(output['sublevels'].to_list()[0])
        # Define Next action
        actions = new_level_df['levelname'].to_list()
        probas = new_level_df['ProbaToSelect'].to_list()
        random_action = random.choices(actions, weights=probas)[0]

        if random_action == 'Product':
            
            # Define action: add product or no action
            ProbaAddProducts = float(ProductPage_parameters['ProbaAddProducts'])
            random_action = random.choices(['add products','no action'], weights=[ProbaAddProducts,1.0-ProbaAddProducts])[0]

            # If product available
            add_to_cart_selector = ProductPage_parameters['AddToCartSelector'].to_string(index=False)
            product_name = driver.find_element(By.CSS_SELECTOR,".row.product-container .h1").text
            if driver.find_element(By.CSS_SELECTOR,add_to_cart_selector).is_enabled():
                # Select DropDown menu and select size
                try:
                    if driver.find_element(By.CSS_SELECTOR,"#group_1").is_enabled():
                        sel = Select(driver.find_element(By.CSS_SELECTOR,"#group_1"))
                        sel.select_by_visible_text("M")
                        product_name = product_name + ' SIZE ' + size
                except:
                    pass
                # Action: add product or no action
                if random_action == 'add products':
                    selector = ProductPage_parameters['ProductsToAddSelector'].to_string(index=False)
                    ProbaNbProductsToAdd = ProductPage_parameters['ProbaNbProductsToAdd'].tolist()[0]
                    NbProductsToAdd = ProductPage_parameters['NbProductsToAdd'].tolist()[0]
                    products_to_add = random.choices(NbProductsToAdd, weights=ProbaNbProductsToAdd)[0]
                    for nbclicks in range(products_to_add):
                        driver.find_element(By.CSS_SELECTOR,selector).click()
                    logging.info(f"{product_name}: {products_to_add} products to add >> Add to cart")
                else:
                    logging.info(f"{product_name}: No action >> Add to cart")
                # Add to cart
                driver.find_element(By.CSS_SELECTOR,add_to_cart_selector).click()
            # Else quit
            else:
                driver.back()
                logging.info(f"{product_name} >> Back")     
        else:
            pass


def ModalNavigation(driver,modal_actions,size):

    '''Modal actions'''

    driver.implicitly_wait(1) 

    # Define action : add product or no action
    ProbaAddProducts = float(modal_actions['ProbaAddProducts'])
    random_action = random.choices(['add products','no action'], weights=[ProbaAddProducts,1.0-ProbaAddProducts])[0]

    # If product available
    add_to_cart_selector = modal_actions['AddToCartSelector'].to_string(index=False)
    product_name = driver.find_element(By.CSS_SELECTOR,".modal-body .h1").text
    if driver.find_element(By.CSS_SELECTOR,add_to_cart_selector).is_enabled():
        # Select DropDown menu and select size
        try:
            if driver.find_element(By.CSS_SELECTOR,"#group_1").is_enabled():
                sel = Select(driver.find_element(By.CSS_SELECTOR,"#group_1"))
                sel.select_by_visible_text(size)
                product_name = product_name + ' SIZE ' + size
        except:
            pass
        # Action : add product or no action
        if random_action == 'add products':
            selector = modal_actions['ProductsToAddSelector'].to_string(index=False)
            ProbaNbProductsToAdd = modal_actions['ProbaNbProductsToAdd'].tolist()[0]
            NbProductsToAdd = modal_actions['NbProductsToAdd'].tolist()[0]
            products_to_add = random.choices(NbProductsToAdd, weights=ProbaNbProductsToAdd)[0]
            for nbclicks in range(products_to_add):
                driver.find_element(By.CSS_SELECTOR,selector).click()
            message = f"{product_name} : {products_to_add} products to add >> Add to cart"
            logging.info(message)
        else:
            message = f"{product_name} : No action >> Add to cart"
            logging.info(message)
        # Add to cart
        driver.find_element(By.CSS_SELECTOR,add_to_cart_selector).click()
    # Else quit modal
    else:
        selector = modal_actions['QuitModalSelector'].to_string(index=False)
        driver.find_element(By.CSS_SELECTOR,selector).click()
        message = f"{product_name} >> Quit"
        logging.info(message)
    
    driver.implicitly_wait(1) 


def ConfirmAddToCartNavigation(driver,actions):
    '''confirmation add to cart actions'''
    driver.implicitly_wait(1) 

    ProbaOrder = float(actions['ProbaOrder'])
    random_action = random.choices(['order', 'continue'], weights=[ProbaOrder, 1 - ProbaOrder])[0]

    if random_action == 'order':
        selector = actions['OrderSelector'].to_string(index=False)
        driver.find_element(By.CSS_SELECTOR, selector).click()
        logging.info("Order button")
    else:
        # Click on Continue shopping button
        selector = actions['ContinueSelector'].to_string(index=False)
        driver.find_element(By.CSS_SELECTOR, selector).click()
        # Go back on the previous page
        driver.back()
        logging.info("Continue shopping button")

