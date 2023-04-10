from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import time, sleep
import random

driver = webdriver.Firefox()
driver.set_page_load_timeout(30)
driver.get("https://10ff.net/")
driver.implicitly_wait(10)
sleep(1)
username_input = driver.find_element(by=By.ID, value="username")
username_input.send_keys("IAlwaysWin")
username_input.send_keys(Keys.ENTER)
sleep(1)

overlayer_state = driver.find_element(by=By.CSS_SELECTOR, value=".overlayer")
while overlayer_state.get_attribute("class") == "overlayer active":
    sleep(0.01)

interface_el = driver.find_element(by=By.CLASS_NAME, value="interface")
input_element = interface_el.find_element(by=By.XPATH, value="//input")

beginning_time = time()
hope = True
writing = True
while writing:
    if time() - beginning_time > 25:
        hope = False
    try:
        curr_word = driver.find_element(by=By.CLASS_NAME, value="highlight").text
        print(curr_word)
        curr_word += " "

        for letter in curr_word:
            input_element.send_keys(letter)
            if hope:
                sleep(random.uniform(0.1, 0.3))
    except:
        writing = False
