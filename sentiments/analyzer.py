import nltk

class Analyzer():
    """Implements sentiment analysis."""

    def __init__(self, positives, negatives):
        """Initialize Analyzer."""

        """Open positives and negatives file, strip out any non-word lines and whitespace, then store in a set"""
        with open(positives, "r") as positivesFile:
            words = []
            for line in positivesFile:
                if line[0].isalpha():
                    words.append(line.strip())
            self.positiveWords = frozenset(words)

        with open(negatives, "r") as negativesFile:
            words = []
            for line in negativesFile:
                if line[0].isalpha():
                    words.append(line.strip())

            self.negativeWords = frozenset(words)

    def analyze(self, text):
        """Analyze text for sentiment, returning its score."""
        tokenizer = nltk.tokenize.TweetTokenizer()
        score = 0
        for word in tokenizer.tokenize(text):
            if word.lower() in self.positiveWords:
                score += 1
            elif word.lower() in self.negativeWords:
                score -= 1
        return score
