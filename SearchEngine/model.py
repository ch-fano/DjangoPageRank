from SearchEngine.index import Index
from whoosh import qparser
from whoosh.scoring import WeightingModel
from whoosh.scoring import BM25F

from SearchEngine.sentiment.sentiment_model import SentimentModel
from SearchEngine.word2vec.word2vec_model import Word2VecModel


class Recipe:

    def __init__(self, id, name, steps, n_steps, description, date, prep_time, rating, ingredients, n_ingredients):
        self.id = id
        self.name = name
        self.steps = steps
        self.n_steps = n_steps
        self.description = description
        self.date = date
        self.prep_time = prep_time
        self.rating = rating
        self.ingredients = ingredients
        self.n_ingredients = n_ingredients

    def __str__(self):
        return f'[{self.id}] {self.name}'


class IRModel:
    def __init__(self, index: Index, weighting_model: WeightingModel = BM25F):
        self.index = index
        self.model = weighting_model
        self.query = ''

    def search(self, query: str, res_limit=-1, sentiments=None, verbose=True):
        res_dict = []
        try:
            if isinstance(self.model, SentimentModel):
                self.model.set_user_sentiment(sentiments)
            elif isinstance(self.model, Word2VecModel):
                 self.model.set_query(query)

            s = self.index.index.searcher(weighting=self.model)
            qp = qparser.MultifieldParser(['recipe_name', 'description', 'ingredients'], schema=self.index.schema, group=qparser.OrGroup)

            parsedq = qp.parse(query)

            if verbose:
                print(f'Input query: {query}')
                print(f'Parsed query: {parsedq}')
            results = s.search(parsedq, terms=True, limit=res_limit) if res_limit > 0 else s.search(parsedq, terms=True)
            for i in results:
                res_dict.append(Recipe(i['recipe_id'], i['recipe_name'], i['steps'], i['n_steps'], i['description'],
                                           i['recipe_date'], i['prep_time'], i['rating'], i['ingredients'],
                                           i['n_ingredients']))

        except Exception as e:
            print(e)
        finally:
            s.close()
        #return correctedString, resDict
        return res_dict


if __name__ == '__main__':
    print('small debug-only CLI interface for query testing.')
    my_index = Index()
    model = IRModel(my_index)

    while True:
        query = input('Input your query: ')
        res = model.search(query, verbose=True)
        for row, (key, values) in enumerate(res):
            print(f'{row}: {key}: {values}')