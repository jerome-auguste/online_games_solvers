from selenium import webdriver
from selenium.webdriver.common.by import By
from time import time, sleep
import random

driver = webdriver.Firefox()
driver.set_page_load_timeout(30)
driver.get("https://10fastfingers.com/advanced-typing-test/french")
driver.implicitly_wait(20)
driver.find_element(by=By.ID, value="CybotCookiebotDialogBodyButtonDecline").click()
sleep(1)

beginning_time = time()
input_element = driver.find_element(by=By.ID, value="inputfield")

while time() - beginning_time < 60:
    curr_word = driver.find_element(by=By.CLASS_NAME, value="highlight").text
    print(curr_word)
    curr_word += " "

    for letter in curr_word:
        input_element.send_keys(letter)
        sleep(random.uniform(0.02, 0.07))
