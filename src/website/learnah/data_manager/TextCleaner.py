import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim import models
import stop_words
from gensim.parsing.porter import PorterStemmer
import re

class TextCleaner():
    """
    A class that cleans up text data
    """
    def __init__(self, folder="../text_cleaner_models"):
        # load stop words
        self.stop_words = stop_words.get_stop_words("en")

        # prepare stemmer
        self.stemmer = PorterStemmer()
        
        # init model folder
        self.folder = folder
        try:
            os.mkdir(folder)
        except:
            pass
        
        # load phrase model
        self.bigram = models.phrases.Phraser.load(self.folder + "/bigram")
        self.trigram = models.phrases.Phraser.load(self.folder + "/trigram")
        
    def clean(self, text, phrasing=True, stemming=True):
        # remove non-alphanumerical letters
        text = re.sub("[^a-zA-Z']+", " ", text.lower())
        
        # remove stop words
        text = " ".join([word for word in text.split() if word not in self.stop_words])
        
        # stem words
        if stemming:
            text = self.stemmer.stem_sentence(text)
        
        # get phrases from text
        if phrasing:
            text = " ".join(self.trigram[self.bigram[text.split()]])
        
        return text