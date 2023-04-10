import pandas as pd
import numpy as np

from utils.utility_functions import entropy, load_dataset, evaluate_word

class SutomEnv:
    def __init__(self, folder_path: str, target_word: str="", word_length: int=5, first_letter: str="", show_first_letter: bool=True, eps: float=1e-13) -> None:
        self.folder_path = folder_path
        self.eps = eps
        if target_word:
            self.first_letter = target_word[0]
            self.target_word = target_word.lower()
            self.word_length = len(self.target_word)
        else:
            assert first_letter, "If no target word is given, a first letter must be given."
            assert word_length, "If no target word is given, a word length must be given."
            self.first_letter = first_letter.lower()
            self.word_length = word_length
        self.dataset = load_dataset(folder_path=self.folder_path, word_length=self.word_length, first_letter=self.first_letter, eps=self.eps)
        self.possible_words = self.dataset["word"].values
        if target_word:
            assert self.target_word in self.dataset["word"].values, "Target word not in dataset."
        else:
            self.target_word = self.dataset["word"].sample().values[0]
        self.display_word = " ".join(self.first_letter + ("_" * (self.word_length - 1)) if show_first_letter else ("_" * self.word_length))
        self.remaining_entropy = self.compute_remaining_entropy()
        print(f"{self.display_word}     ({self.remaining_entropy:.2f} bits remaining)")
    
    def compute_remaining_entropy(self, use_word_frequency: bool=True):
        if use_word_frequency:
            p = self.dataset["frequency"].values
        else:
            p = np.ones(len(self.dataset)) / len(self.dataset)
        return entropy(p)
    
    def make_proposal(self, proposed_word: str) -> float:
        assert len(proposed_word) == self.word_length, f"Proposed word is not the right length ({self.word_length} expected, {len(proposed_word)} given)."
        assert proposed_word in self.possible_words, "Proposed word not in dataset."
        result = evaluate_word(proposed_word.lower(), self.target_word)
        self.update_dataset_on_proposal(result)
        self.remaining_entropy = self.compute_remaining_entropy()
        print(f"{' '.join(proposed_word)}     ({self.remaining_entropy:.2f} bits remaining)")
        print(" ".join([str(r) for r in result]))
        if result == [2] * self.word_length:
            print("You found the word, congrats!")
        return result

    def update_dataset_on_proposal(self, result):
        for idx in self.dataset.index:
            word = self.dataset.loc[idx, "word"]
            word_result = evaluate_word(word, self.target_word)
            if np.max(word_result != result):
                self.dataset.drop(idx, inplace=True)
        self.dataset["frequency"] = (self.dataset["frequency"] + self.eps) / (self.dataset["frequency"].sum() + self.eps)
            
        
        
        