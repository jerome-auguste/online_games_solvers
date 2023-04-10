from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from utils.algos import EntropySolver
from utils.utility_functions import entropy
from time import sleep


if __name__ == "__main__":
    GAME_MODE = "Mot du jour"

    driver = webdriver.Firefox()
    sutom_web_url = "https://www.tusmo.xyz/"
    driver.set_page_load_timeout(100)
    driver.get(sutom_web_url)
    driver.implicitly_wait(100)
    sleep(0.5)

    # Selecting french language
    language_button = driver.find_elements(
        by=By.CSS_SELECTOR, value="button[class='menu-button w-12']"
    )[-1]
    if language_button.get_attribute("alt") != "fr":
        language_button.click()
        sleep(0.5)
        language_group_el = driver.find_element(
            by=By.CLASS_NAME, value="langs-container"
        )
        languages = language_group_el.find_elements(
            by=By.CSS_SELECTOR, value="button[class='menu-button w-12']"
        )
        for language in languages:
            if (
                language.find_element(by=By.TAG_NAME, value="img")
                .get_attribute("alt")
                .lower()
                == "fr"
            ):
                language.click()
                break
        sleep(0.5)

    # Selecting gaming mode
    if GAME_MODE == "Mot du jour":
        driver.find_element(
            by=By.XPATH, value="/html/body/div/div/div[2]/div[1]/div[1]/button"
        ).click()
        num_rounds = 1
    elif GAME_MODE == "Suite du jour":
        driver.find_element(
            by=By.XPATH, value="/html/body/div/div/div[2]/div[1]/div[2]/button"
        ).click()
        num_rounds = 5
    sleep(0.5)

    result_mapping = {
        "-": 0,
        "y": 1,
        "r": 2,
    }

    for round in range(num_rounds):
        driver.refresh()
        keyboard_el = driver.find_element(by=By.CLASS_NAME, value="keyboard")
        grille_element = driver.find_element(by=By.CLASS_NAME, value="motus-grid")
        notif_el = driver.find_element(by=By.CLASS_NAME, value="alert-zone")
        keyboard_key_list = keyboard_el.find_elements(by=By.CLASS_NAME, value="key")
        keyboard = {el.text.lower(): el for el in keyboard_key_list if el.text}
        keyboard["_entree"] = keyboard_el.find_element(
            by=By.CLASS_NAME, value="fa-sign-in-alt"
        )
        grid_cells = grille_element.find_elements(
            by=By.CLASS_NAME, value="cell-content"
        )

        first_letter = grid_cells[0].text
        word_length = len(grid_cells) // 6
        folder_path = (
            "C:/Users/jerom/projects/online_games_solvers/sutom/word_frequency_vocab/"
        )

        print(f"\n=========== Game {round+1}: Setting up Solver ===========")
        sutom_solver = EntropySolver(word_length, folder_path, first_letter)
        print(
            f"Estimated entropy of this game: {entropy(sutom_solver.dataset['frequency']):.2f}"
        )

        result = [2] + [0] * (word_length - 1)
        curr_row = 1
        print("=================================================\n")

        while (curr_row < 6) and (min(result) < 2):
            print(f"\n==================== Round {curr_row} ====================")
            guesses = sutom_solver.return_best_guesses()
            print(f"Possible guesses:\n {guesses}")
            if guesses.empty:
                print("The word is not in the lexique, can't find it :\(")
                break
            guess = guesses["word"].iloc[0]
            print("Testing word: ", guess)
            for letter in guess:
                keyboard[letter].click()
                sleep(0.05)
            keyboard["_entree"].click()
            sleep(0.1 * word_length)
            try:
                if notif_el.text == "Ce mot n'est pas dans la liste !":
                    print("Word not in list! Removing from possibilities")
                    sutom_solver.remove_word(guess)
                    sleep(0.2 * word_length)
                else:
                    grid_cells = grille_element.find_elements(
                        by=By.CLASS_NAME, value="cell-content"
                    )
                    curr_row_el = grid_cells[
                        (curr_row - 1) * word_length : curr_row * word_length
                    ]
                    result = [
                        result_mapping[el.get_attribute("class").split(" ")[1]]
                        for el in curr_row_el
                    ]
                    sutom_solver.update_possibilities(guess, result)
                    curr_row += 1
                print("=================================================\n")
            except StaleElementReferenceException:
                result = [2] * word_length
                break

        sleep(5)
        if min(result) == 2 and curr_row < 6:
            print(f"Congrats you found the word {guess} in {curr_row} guesses!")
        elif curr_row == 6:
            print("You lost! Better luck next time!")
