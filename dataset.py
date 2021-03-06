import pandas as pd
import re
import csv
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

class Dataset:
    def __init__(self, isTrainfile=True, file_name='./airline_sentiment_analysis.csv'):
        self.file_name = file_name
        self.data = None
        self.isTrainFile = isTrainfile
        self.stop_words = stopwords.words('english')
        self.porter_stemmer = PorterStemmer()

    def is_valid_word(self, word):
        # Check if word begins with an alphabet
        return re.search(r'^[a-zA-Z][a-z0-9A-Z\._]*$', word) is not None

    def preprocess(self,text):
        replace = [
            # Convert more than 2 letter repetitions to 2 letter funnnnny --> funny
            [r'(.)\1+', r'\1\1'],
            # Replaces URLs with the word URL
            [r'((www\.[\S]+)|(https?://[\S]+))', ' URL '],
            [r'http*', ' URL '],
            # Replace username
            [r'@[\S]+', 'USER_MENTION'],
            # Replace 2+ dots with space
            [r'\.{2,}', ' '],
            # handle emojis
            [r'(:\s?\)|:-\)|\(\s?:|\(-:|:\'\))', ' EMO_POS '],  # Smile -- :), : ), :-), (:, ( :, (-:, :')
            [r'(:\s?D|:-D|x-?D|X-?D)', ' EMO_POS '],  # Laugh -- :D, : D, :-D, xD, x-D, XD, X-D
            [r'(<3|:\*)', ' EMO_POS '],  # Love -- <3, :*
            [r'(;-?\)|;-?D|\(-?;)', ' EMO_POS '],  # Wink -- ;-), ;), ;-D, ;D, (;,  (-;
            [r'(:\s?\(|:-\(|\)\s?:|\)-:)', ' EMO_NEG '],  # Sad -- :-(, : (, :(, ):, )-:
            [r'(:,\(|:\'\(|:"\()', ' EMO_NEG '],  # Cry -- :,(, :'(, :"(
            [r"i'm", "i am"],
            [r"he's", "he is"],
            [r"she's", "she is"],
            [r"it's", "it is"],
            [r"that's", "that is"],
            [r"what's", "that is"],
            [r"where's", "where is"],
            [r"how's", "how is"],
            [r"\'ll", " will"],
            [r"\'ve", " have"],
            [r"\'re", " are"],
            [r"\'d", " would"],
            [r"\'re", " are"],
            [r"won't", "will not"],
            [r"can't", "cannot"],
            [r"n't", " not"],
            [r"n'", "ng"],
            [r"'bout", "about"],
            [r"'til", "until"],
            # remove spacial characters
            [r"[-_'()\"#/@;:<>{}`+=~|.!?,]", ""]
        ]
        # convert to lowercase
        text = text.lower()
        # Remove firsr username
        if text[0] == '@': text = text[text.find(' '):]
        # Remove punctuation
        text = text.strip('\'"?!,.():;')
        for r in replace:
            text = re.sub(r[0], r[1], text)
        text = text.split()
        processed_text = []
        for word in text:
            # check if word is valid
            if self.is_valid_word(word):
                # remove invalid word and stop words
                word = str(self.porter_stemmer.stem(word))
                processed_text.append(word)
        return str(' '.join(processed_text))


    def preprocess_dataset(self):
        raw_data = pd.read_csv(self.file_name)
        processed_data = []
        for i in range(len(raw_data['text'])):
            processed_text = self.preprocess(raw_data['text'][i])
            if self.isTrainFile:
                lbl = raw_data['airline_sentiment'][i].lower()
                # skip labels that are not in proper format
                if lbl =='negative' or lbl =='positive':
                    data = dict()
                    data['text'] = processed_text
                    data['airline_sentiment'] = lbl
                    processed_data.append(data)
            else:
                data = dict()
                data['text'] = processed_text
                processed_data.append(data)
        try:
            # open new csv file and write processed data
            with open('processed_data.csv', 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=list(data.keys()))
                writer.writeheader()
                for data in processed_data:
                    writer.writerow(data)
        except IOError:
            print("I/O error")