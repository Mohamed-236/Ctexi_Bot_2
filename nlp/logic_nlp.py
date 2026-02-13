import spacy


nlp = spacy.load("fr_core_news_sm")

# Cette fonction prend un message en entree, le traite avec spacy pour le tokeniser et le lemmatiser, et retourne une liste de lemme pour normaliser les mots et facilite la comprehension
def comprehension(message):
    doc = nlp(message.lower())
    return [ token.lemma_ for token in doc]