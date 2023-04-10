import pandas as pd
import numpy as np
from typing import List
from utils.utility_functions import entropy, load_dataset, evaluate_word
from time import perf_counter

class EntropySolver:
    def __init__(self, nb_letters: int, folder_path: str, first_letter: str="", eps: float=1e-13) -> None:
        self.word_length = nb_letters
        self.folder_path = folder_path
        self.eps = eps
        self.first_letter = first_letter.lower()
        
        t0 = perf_counter()
        self.dataset = load_dataset(folder_path=self.folder_path, word_length=self.word_length, first_letter=self.first_letter, eps=self.eps)
        t1 = perf_counter()
        print(f"Loading dataset took {t1-t0:.2f} seconds.")
        
        self.result_matrix = self._init_result_matrix()
        t2 = perf_counter()
        print(f"Initializing result matrix took {t2-t1:.2f} seconds.")
        
        self.compute_entropy()
        t3 = perf_counter()
        print(f"Computing entropy took {t3-t2:.2f} seconds.")
        print(f"Total time: {t3-t0:.2f} seconds.")

    def _init_result_matrix(self) -> np.array:
        # Single processing with nested loops
        result_matrix = np.zeros((len(self.dataset), len(self.dataset), self.word_length))
        for i, input in enumerate(self.dataset["word"]):
            for j, target in enumerate(self.dataset["word"]):
                result = evaluate_word(input, target)
                result_matrix[i, j, :] = result
        return result_matrix
    
    def update_possibilities(self, proposed_word: str, result: List[int], use_word_frequency: bool=True):
        assert len(proposed_word) == self.word_length, f"Proposed word is not the right length ({self.word_length} expected)."
        assert len(result) == self.word_length, f"Result is not the right length ({self.word_length} expected)."
        word_idx = self.dataset[self.dataset["word"] == proposed_word].index
        for j in self.dataset.index:
            if np.max(self.result_matrix[word_idx, j, :] != result) == True:
                self.dataset.drop(j, inplace=True)
        self.dataset["frequency"] = (self.dataset["frequency"] + self.eps) / (self.dataset["frequency"].sum() + self.eps)
        self.compute_entropy(use_word_frequency)
    
    def compute_entropy(self, use_word_frequency: bool=True):        
        for input_idx in self.dataset.index:
            _, inverse_indexes = np.unique(self.result_matrix[input_idx, self.dataset.index, :], return_inverse=True, axis=0)
            # idx_mask = np.in1d(inverse_indexes, self.dataset.index)
            if use_word_frequency:
                # p = np.bincount(inverse_indexes[idx_mask], weights=self.dataset["frequency"])
                p = np.bincount(inverse_indexes, weights=self.dataset["frequency"])
            else:
                # p = np.bincount(inverse_indexes[idx_mask])
                p = np.bincount(inverse_indexes)
            self.dataset.loc[input_idx, "entropy"] = entropy(p, self.eps)
    
    def return_best_guesses(self) -> str:
        best_entropy = self.dataset["entropy"].max()
        best_guesses = self.dataset[self.dataset["entropy"] == best_entropy]
        if len(best_guesses) > 1:
            best_guesses.sort_values(by="frequency", ascending=False, inplace=True)
        return best_guesses
    
    def remove_word(self, word: str):
        word_idx = self.dataset[self.dataset["word"] == word].index
        self.dataset.drop(word_idx, inplace=True)
        self.dataset["frequency"] = (self.dataset["frequency"] + self.eps) / (self.dataset["frequency"].sum() + self.eps)
        self.compute_entropy()
