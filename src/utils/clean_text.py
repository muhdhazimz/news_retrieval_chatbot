import re


def remove_greeting(text: str) -> str:
    """
    Removes the first sentence from the text if the sentences are directly concatenated
    without a space between the period and the next sentence.

    Args:
        text (str): The input string containing sentences.

    Returns:
        str: The modified string with the first sentence removed if it meets the condition.
             If no such condition is met, the original string is returned unchanged.

    Example:
        >>> remove_greeting("Hello.How are you? I hope you're doing well.")
        'How are you? I hope you're doing well.'

        >>> remove_greeting("I'm sorry, I was unable to compare your spending to others.However, I can tell you that you have made one transaction for $9397.83.")
        'However, I can tell you that you have made one transaction for $9397.83.'

        >>> remove_greeting("This is fine. No removal here.")
        'This is fine. No removal here.'
    """
    # Match the first sentence followed by a period with no space before the next sentence
    modified_text = re.sub(r"^[^0-9]+\.(?=[^\s])", "", text)
    cleaned_text = modified_text.replace("\n", " ")
    return cleaned_text.strip()
