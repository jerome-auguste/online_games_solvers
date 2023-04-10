import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup


def download_sutom_vocab(driver, sutom_web_url):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    possible_words_script = soup.find(
        name="script", attrs={"src": re.compile(".*/listeMotsProposables.*.js")}
    ).get("src")

    vocab_category = (
        re.search(r"listeMotsProposables\.(.*)(?=.js)", possible_words_script)
        .group(1)
        .split(".")
    )
    if not os.file.exists("possible_words_" + ".".join(vocab_category) + ".csv"):
        possible_words_url = sutom_web_url + possible_words_script
        js_script = requests.get(possible_words_url).text
        possible_words_extracted = re.search(
            r"ListeMotsProposables\.Dictionnaire = \[(.*)\];", js_script, re.DOTALL
        ).group(1)
        possible_words_list = re.findall(
            r"\w{" + vocab_category[0] + r"}", possible_words_extracted
        )
        possible_words_df = pd.Series(possible_words_list)
        possible_words_df.to_csv(
            "possible_words_" + ".".join(vocab_category) + ".csv", index=False
        )
