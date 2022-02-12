from googletrans import Translator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class Sentiment_Analyzer():

    def __init__(self):

        self.vader = SentimentIntensityAnalyzer()
        self.translator = Translator(service_urls=[
      'translate.google.com'])
        print('Sentiment Analyzer/Translator Initiated')

    def translate(self, text, src_lang = None, dest_lang = None):
        if src_lang and target_lang:
            return self.translator.translate(text, dest = dest_lang, src = src_lang)
        elif src_lang:
            return self.translator.translate(text, src = src_lang)
        elif dest_lang:
            return self.translator.translate(text, dest = dest_lang)
        else:
            return self.translator.translate(text)

    def sentiment(self, text):
        data = dict()
        sentiment = self.vader.polarity_scores(text)
        data['original_text'] = text
        data['translated_text'] = None
        data['src_lang'] = 'en'
        data['dest_lang'] = None
        data['sentiment_compound'] = sentiment['compound'] * 100
        data['sentiment_negative'] = sentiment['neg'] * 100
        data['sentiment_neutral'] = sentiment['neu'] * 100
        data['sentiment_positive'] = sentiment['pos'] * 100
        return data



    def translate_and_analyze(self, text, src_lang = None, dest_lang = None):
        try:
            translated = self.translate(text, src_lang = None, dest_lang = None)
        except:
            print('Could not translate tweet.')
            return None
        # try:
        sent = dict(self.sentiment(translated.text.replace('.', '. ')))
        # except:
        #     print('Could not get the tweet sentiment.')
        #     return None

        data = dict()
        data['original_text'] = text
        data['translated_text'] = translated.text.replace('.', '. ')
        data['src_lang'] = translated.src
        data['dest_lang'] = translated.dest
        for key in sent.keys():
            if 'sentiment' in key:
                data[key] = sent[key]
        print(data)
        return data

if __name__ == '__main__':
    sa = Sentiment_Analyzer()
    tt = sa.translate_and_analyze('Vraiment un batard. Je le deteste. pas content.')
    print(tt)
