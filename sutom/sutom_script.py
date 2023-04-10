from selenium import webdriver
from selenium.webdriver.common.by import By
from utils.algos import EntropySolver
from utils.utility_functions import entropy
from time import sleep


if __name__ == "__main__":

    driver = webdriver.Firefox()
    sutom_web_url = "https://sutom.nocle.fr/"
    driver.set_page_load_timeout(30)
    driver.get(sutom_web_url)
    driver.implicitly_wait(20)
    driver.find_element(by=By.ID, value="panel-fenetre-bouton-fermeture").click()
    driver.implicitly_wait(20)
    input_area = driver.find_element(by=By.ID, value="input-area")
    grille_element = driver.find_element(by=By.ID, value="grille")
    result_mapping = {
        "non-trouve": 0,
        "mal-place": 1,
        "bien-place": 2,
    }
    
    first_letter = grille_element.find_element(by=By.XPATH, value="//table/tr[1]/td[1]").text
    word_length = len(grille_element.find_elements(by=By.XPATH, value="//table/tr[1]/td"))
    folder_path = "C:/Users/jerom/projects/online_games_solvers/sutom/word_frequency_vocab/"
    
    print(f"\n==================== Setting up Solver ====================")
    sutom_solver = EntropySolver(word_length, folder_path, first_letter)
    print(f"Estimated entropy of this game: {entropy(sutom_solver.dataset['frequency']):.2f}")
    keyboard = {el.get_attribute('data-lettre').lower(): el for el in input_area.find_elements(by=By.XPATH, value="//div[@data-lettre]")}
    result = [2] + [0]*(word_length-1)
    curr_row = 1
    print("=================================================\n")
    
    while (curr_row < 6) and (min(result) < 2):
        print(f"\n==================== Round {curr_row} ====================")
        guesses = sutom_solver.return_best_guesses()
        print(f"Possible guesses:\n {guesses}")
        guess = guesses["word"].iloc[0]
        print("Testing word: ", guess)
        for letter in guess:
            keyboard[letter].click()
            sleep(0.1)
        keyboard["_entree"].click()
        sleep(0.3*word_length)

        notif_el = driver.find_element(by=By.ID, value="notification")
        if notif_el.text == "Ce mot n'est pas dans notre dictionnaire.":
            sutom_solver.remove_word(guess)
            for _ in range(word_length):
                keyboard["_effacer"].click()
        
        curr_row_el = grille_element.find_elements(by=By.XPATH, value=f"//table/tr[{curr_row}]/td")
        result = [result_mapping[el.get_attribute("class").split(" ")[0]] for el in curr_row_el]
        sutom_solver.update_possibilities(guess, result)
        curr_row += 1
        print("=================================================\n")
    
    if min(result) == 2:
        print(f"Congrats you found the word {guess} in {curr_row-1} guesses!")
    elif curr_row == 6:
        print("You lost! Better luck next time!")
