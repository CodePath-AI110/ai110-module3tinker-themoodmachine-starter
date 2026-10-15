# mood_analyzer.py
"""
Rule based mood analyzer for short text snippets.

This class starts with very simple logic:
  - Preprocess the text
  - Look for positive and negative words
  - Compute a numeric score
  - Convert that score into a mood label
"""

import re
from typing import List, Dict, Tuple, Optional

from dataset import POSITIVE_WORDS, NEGATIVE_WORDS


class MoodAnalyzer:
    """
    A very simple, rule based mood classifier.
    """

    def __init__(
        self,
        positive_words: Optional[List[str]] = None,
        negative_words: Optional[List[str]] = None,
    ) -> None:
        # Use the default lists from dataset.py if none are provided.
        positive_words = positive_words if positive_words is not None else POSITIVE_WORDS
        negative_words = negative_words if negative_words is not None else NEGATIVE_WORDS

        # Store as sets for faster lookup.
        self.positive_words = set(w.lower() for w in positive_words)
        self.negative_words = set(w.lower() for w in negative_words)

    # ---------------------------------------------------------------------
    # Preprocessing
    # ---------------------------------------------------------------------

    def preprocess(self, text: str) -> List[str]:
        """
        Convert raw text into a list of tokens the model can work with.

        Improvement instructions:
          - Normalize text to lowercase.
          - Keep words, contractions, simple emoticons, and selected emojis
            as separate tokens so scoring can recognize them.
          - Add more token patterns here if the dataset introduces new
            slang, punctuation, or emoji styles.
        """
        cleaned = text.strip().lower()
        token_pattern = r"[a-z0-9]+(?:'[a-z]+)?|[:;]-?[)(]|[😂🤣😄😁😊😍🥲😢😭😞😔😡😠💀]"
        return re.findall(token_pattern, cleaned)

    # ---------------------------------------------------------------------
    # Scoring logic
    # ---------------------------------------------------------------------

    def score_text(self, text: str) -> int:
        """
        Compute a numeric "mood score" for the given text.

        Positive words increase the score.
        Negative words decrease the score.

        Improvement instructions:
          - Start with one point for each positive or negative signal.
          - Count repeated words instead of only checking whether a word exists.
          - Flip the next mood signal after "not", "never", or "no" to handle
            simple phrases such as "not happy" and "not bad".
          - Treat "lowkey" and "highkey" as neutral intensity modifiers for
            the next mood word, and treat "no cap" as neutral slang.
          - Expand the emoji and slang signal sets as you learn from failures.
        """
        tokens = self.preprocess(text)
        positive_signals = {":)", ":-)", "😂", "🤣", "😄", "😁", "😊", "😍"}
        negative_signals = {":(", ":-(", "🥲", "😢", "😭", "😞", "😔", "😡", "😠", "💀"}
        negation_words = {"not", "never", "no"}
        score = 0
        negate_next = False
        intensity = 1

        for index, token in enumerate(tokens):
            if token == "no" and index + 1 < len(tokens) and tokens[index + 1] == "cap":
                continue
            if token == "cap" and index > 0 and tokens[index - 1] == "no":
                continue
            if token == "lowkey":
                intensity = 1
                continue
            if token == "highkey":
                intensity = 2
                continue
            if token in negation_words:
                negate_next = True
                continue

            signal = 1 if token in self.positive_words or token in positive_signals else 0
            signal = -1 if token in self.negative_words or token in negative_signals else signal

            if signal:
                score += (-signal if negate_next else signal) * intensity
                negate_next = False
                intensity = 1

        return score

    # ---------------------------------------------------------------------
    # Label prediction
    # ---------------------------------------------------------------------

    def predict_label(self, text: str) -> str:
        """
        Turn the numeric score for a piece of text into a mood label.

        The default mapping is:
          - score > 0  -> "positive"
          - score < 0  -> "negative"
          - score == 0 -> "neutral"

        Improvement instructions:
          - Use the score sign for clear positive and negative predictions.
          - Treat "but" as a contrast marker and return "mixed" when it
            appears, even if one side is difficult to classify.
          - Treat slang such as "lowkey", "highkey", and "no cap" as
            modifiers rather than mood words.
          - Check whether both positive and negative signals appear so balanced
          emotions can be labeled "mixed" instead of "neutral".
          - Adjust these thresholds or signal sets after reviewing evaluation
          mistakes in the labeled dataset.
        """
        tokens = self.preprocess(text)
        negation_words = {"not", "never", "no"}
        positive_signals = self.positive_words | {":)", ":-)", "😂", "🤣", "😄", "😁", "😊", "😍"}
        negative_signals = self.negative_words | {":(", ":-(", "🥲", "😢", "😭", "😞", "😔", "😡", "😠", "💀"}
        has_positive = False
        has_negative = False
        negate_next = False

        if "but" in tokens:
          return "mixed"

        for index, token in enumerate(tokens):
          if token == "no" and index + 1 < len(tokens) and tokens[index + 1] == "cap":
            continue
          if token == "cap" and index > 0 and tokens[index - 1] == "no":
            continue
          if token in {"lowkey", "highkey"}:
            continue
          if token in negation_words:
            negate_next = True
            continue
          if token in positive_signals:
            if negate_next:
              has_negative = True
            else:
              has_positive = True
            negate_next = False
          elif token in negative_signals:
            if negate_next:
              has_positive = True
            else:
              has_negative = True
            negate_next = False

        if has_positive and has_negative:
          return "mixed"

        score = self.score_text(text)
        if score > 0:
          return "positive"
        if score < 0:
          return "negative"
        return "neutral"

    # ---------------------------------------------------------------------
    # Explanations (optional but recommended)
    # ---------------------------------------------------------------------

    def explain(self, text: str) -> str:
        """
        Return a short string explaining WHY the model chose its label.

        TODO:
          - Look at the tokens and identify which ones counted as positive
            and which ones counted as negative.
          - Show the final score.
          - Return a short human readable explanation.

        Example explanation (your exact wording can be different):
          'Score = 2 (positive words: ["love", "great"]; negative words: [])'

        The current implementation is a placeholder so the code runs even
        before you implement it.
        """
        tokens = self.preprocess(text)

        positive_hits: List[str] = []
        negative_hits: List[str] = []
        score = 0

        for token in tokens:
            if token in self.positive_words:
                positive_hits.append(token)
                score += 1
            if token in self.negative_words:
                negative_hits.append(token)
                score -= 1

        return (
            f"Score = {score} "
            f"(positive: {positive_hits or '[]'}, "
            f"negative: {negative_hits or '[]'})"
        )
