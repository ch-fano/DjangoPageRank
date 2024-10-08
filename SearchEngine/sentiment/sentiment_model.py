from whoosh.scoring import BM25F
import math
from SearchEngine.sentiment.reviews_index import ReviewsIndex


class SentimentModel(BM25F):  
    def __init__(self, sentiment_index=ReviewsIndex(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_sentiment = None
        self.reviews_index = sentiment_index
        self.use_final = True

    @staticmethod
    def cosine_similarity(doc: dict, query: dict):
        '''
        Calcola cosine similarity.
        '''
        #denominatore
        d_norm = math.sqrt(sum(v ** 2 for v in doc.values()))  #radice norma documenti ritrovati
        q_norm = math.sqrt(sum(v ** 2 for v in query.values()))  #radice norma query
        denom = (d_norm * q_norm)

        #numeratore
        num = sum(doc[k] * query[k] for k in (doc.keys() & query.keys()))
        if denom:
            return num / denom
        return 0

    def get_sentiment_score(self, listing_id, sentiment):
        '''
        Cosine similarity tra: 
            - sentimenti di un certo documento
            - sentimenti query
        '''
        return self.cosine_similarity(self.reviews_index.get_sentiments(listing_id), sentiment)

    def set_user_sentiment(self, user_sentiment: list = None):
        '''
        Imposta i sentimenti in un dizionario dove le chiavi sono i sentimenti. 
        '''
        if user_sentiment:
            self.user_sentiment = {k: 1 for k in user_sentiment}
        else:
            self.user_sentiment = None

    def final(self, searcher, docnum, score):

        score = super().final(searcher, docnum, score)

        if not self.user_sentiment:
            return score

        id = searcher.stored_fields(docnum)['recipe_id']
        sentiment_score = self.get_sentiment_score(id, self.user_sentiment)
        return ((score / 30 * 70) + (sentiment_score * 30)) / 2


class ReviewSentimentModel(SentimentModel):
    '''.
    Modello che favorisce maggiormente i documenti con più recensioni.
    '''

    def final(self, searcher, docnum, score):
        score = super().final(searcher, docnum, score)
        if not self.user_sentiment:
            return score
        id = searcher.stored_fields(docnum)['recipe_id']
        sentiment_score = self.get_sentiment_score(id, self.user_sentiment)

        return ((score / 30 * 70) + (sentiment_score * 29) + (self.reviews_index.get_number_of_reviews(id))) / 3
