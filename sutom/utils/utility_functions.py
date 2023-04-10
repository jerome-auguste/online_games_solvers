import numpy as np
import pandas as pd


def entropy(p: np.array, eps: float = 1e-9) -> float:
    """Computes entropy of a probability distribution. In terms of information theory, this is the expected number of bits gained by a guess.

    Args:
        p (np.array): probability distribution

    Returns:
        float: entropy
    """
    # assert np.sum(p) <= 1 + 10e-6, f"Sum of probabilities is greater than 1 + eps: {np.sum(p)}"
    return -np.sum((p + eps) * np.log2(p + eps))


def sigmoid(x: float, offset: float = 0, scale: float = 1):
    return 1 / (1 + np.exp(-scale * (x - offset)))


def load_dataset(
    folder_path: str, word_length: int, first_letter: str, eps: float = 1e-9
) -> pd.DataFrame:
    dataset = pd.read_csv(
        folder_path + f"word_frequency_{word_length}.csv",
        dtype={"word": str, "frequency": float},
    )
    # dataset[dataset["word"].isna()] = "nan"
    if first_letter:
        dataset = dataset[dataset["word"].str.startswith(first_letter)]
    dataset["frequency"].apply(
        sigmoid, args=(dataset["frequency"].median(), dataset["frequency"].median())
    )
    dataset["frequency"] = (dataset["frequency"] + eps) / (
        dataset["frequency"].sum() + eps
    )
    dataset.reset_index(inplace=True)
    dataset["entropy"] = pd.Series(np.zeros(len(dataset)), index=dataset.index)
    return dataset


def evaluate_word(proposed_word: str, target: str) -> np.array:
    assert len(proposed_word) == len(
        target
    ), f"Proposed word is not the right length ({len(target)} expected, {len(proposed_word)} given)."
    result = [0] * len(target)
    not_hinted_letters = list(target)
    for i, letter in enumerate(proposed_word):
        if letter == target[i]:
            result[i] = 2
            not_hinted_letters.remove(letter)
    for i, letter in enumerate(proposed_word):
        if (letter in target) and (letter in not_hinted_letters) and (result[i] == 0):
            result[i] = 1
            not_hinted_letters.remove(letter)
    return result

    # Numpy vectorization
    # result = np.zeros(len(target), dtype=int)
    # not_hinted_letters = np.array(list(target))
    # match_indices = np.where(np.array(list(proposed_word)) == not_hinted_letters)[0]
    # result[match_indices] = 2
    # not_hinted_letters = np.delete(not_hinted_letters, match_indices)
    # in_target_indices = np.isin(np.array(list(proposed_word)), not_hinted_letters) & (result == 0)
    # result[in_target_indices] = 1
    # return result
