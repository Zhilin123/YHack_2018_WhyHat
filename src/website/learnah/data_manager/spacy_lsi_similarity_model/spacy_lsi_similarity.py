from question_analyzer import question_analyzer
from gensim import corpora, models, similarities

from collections import OrderedDict
import json
import os
import re
import numpy as np

class spacy_lsi_sim:
    def __init__(self, main_folder="models_and_data", spacy_model='en_core_web_lg'):
        # load a question analyzer
        self.nlp = question_analyzer(spacy_model)

        # load main folder name
        self.folder = main_folder

        # initialize variables
        self.training_docs = []
        self.model_training_docs = []

    def load_all_models(self):
        # load every thing
        sim.load_topic_sim_model()
        sim.load_database_questions()
        sim.load_topic_sim_model()
        sim.load_question_sim_model()

    def save_training_docs(self, docs, file_name):
        # preprocess docs
        for i, doc in enumerate(docs):
            self.nlp.load_normal_text(doc)
            docs[i] = " ".join(self.nlp.keywords)

        # save the processed docs to json files
        with open(self.folder + "/training_docs/" + file_name, 'w') as f:
            json.dump(docs, f)

    def save_topics(self, topics):
        # preprocess docs
        defs = []
        names = []
        for t, doc in topics.items():
            self.nlp.load_normal_text(doc)
            defs.append(" ".join(self.nlp.keywords))
            names.append(t)

        # save the processed docs to json file
        with open(self.folder + "/topic_names", 'w') as f:
            json.dump(names, f)
        # save the processed docs to json file
        with open(self.folder + "/topic_defs", 'w') as f:
            json.dump(defs, f)

    def save_database_questions(self, questions):
        # preprocess questions
        uids = []
        qs = []
        for id, q in questions.items():
            qs.append(q)
            uids.append(id)

        # save the processed docs to json file
        with open(self.folder + "/question_uids", 'w') as f:
            json.dump(uids, f)
        # save the processed docs to json file
        with open(self.folder + "/questions", 'w') as f:
            json.dump(qs, f)

    def load_topics(self):
        # load all topics to class variables
        with open(self.folder + "/topic_names") as f:
            self.topic_names = json.load(f)
        with open(self.folder + "/topic_defs") as f:
            self.topic_defs = json.load(f)

    def load_database_questions(self):
        # load all database questions in the folder to class variables
        with open(self.folder + "/question_uids") as f:
            self.question_uids = json.load(f)
        with open(self.folder + "/questions") as f:
            self.questions = json.load(f)

    def load_training_docs(self):
        # load all training docs in the folder to class variable self.training_docs
        for file_name in os.listdir(self.folder + "/training_docs"):
            with open(self.folder + "/training_docs/" + file_name, 'r') as f:
                docs = json.load(f)
                self.training_docs += docs

    def train(self, stage="topic"):
        # prepare for different stage of training
        self.load_training_docs()
        self.load_topics()
        self.load_database_questions()
        self.model_training_docs = self.training_docs + self.topic_defs + self.questions

        # start training
        if stage == "topic":
            self.train_topic_sim_model()
        elif stage == "question":
            self.load_topic_sim_model()
            self.train_question_sim_models()

    def train_topic_sim_model(self):
        # prepare for dictionary tfidf, lsi and similarity index

        # prepare dictionary
        self.dictionary = corpora.Dictionary([doc.split() for doc in self.model_training_docs])
        self.dictionary.save(self.folder + "/dictionary")

        # prepare tfidf
        training_bows = [self.dictionary.doc2bow(doc.split()) for doc in self.model_training_docs]
        self.tfidf = models.TfidfModel(training_bows)

        # prepare lsi model
        self.lsi = models.LsiModel(self.tfidf[training_bows], 300, id2word=self.dictionary)

        # prepare index
        topic_lsi = self.lsi[self.tfidf[[self.dictionary.doc2bow(doc.split()) for doc in self.topic_defs]]]
        self.topic_index = similarities.MatrixSimilarity(topic_lsi)

        # save to file
        self.dictionary.save(self.folder + "/" + "dictionary")
        self.tfidf.save(self.folder + "/" + "tfidf")
        self.lsi.save(self.folder + "/" + "lsi")
        self.topic_index.save(self.folder + "/" + "topic_index")

    def train_question_sim_models(self):
        # prepare question similarity index based on current topic similarity index
        question_topic_vectors = [self.doc2topic_sim(q) for q in self.questions]

        # get index based on question topic vector
        self.question_index = question_topic_vectors

        # save to file
        np.save(self.folder + "/" + "question_index", question_topic_vectors)


    def load_question_sim_model(self):
        # load all saved models for question similarity
        self.question_index = np.load(self.folder + "/" + "question_index.npy")

    def load_topic_sim_model(self):
        # load all saved models for topic similarity
        self.dictionary = corpora.Dictionary.load(self.folder + "/" + "dictionary")
        self.tfidf = models.TfidfModel.load(self.folder + "/" + "tfidf")
        self.lsi = models.LsiModel.load(self.folder + "/" + "lsi")
        self.topic_index = similarities.MatrixSimilarity.load(self.folder + "/" + "topic_index")

    def search_question(self, question):
        # convert question to topic similarity vector
        question_topic_vector = self.doc2topic_sim(question)
        question_topic_vector /= question_topic_vector.sum()

        # get question similarity
        sim = [np.dot(v, question_topic_vector) for v in self.question_index]

        # process sims
        sim = self.process_question_sim(sim)

        return sim

    def search_topic(self, question):
        # load the question
        self.nlp.load_normal_text(question)
        question_lsi = self.lsi[self.tfidf[self.dictionary.doc2bow(self.nlp.keywords)]]

        # query similarity
        sim = self.topic_index[question_lsi]

        # process sims
        sim = self.process_topic_sim(sim)

        return sim

    def process_topic_sim(self, sim):
        # process topic similarity so it is more straightforward
        sim = sorted(enumerate(sim), key=lambda item: -item[1])
        sim = [(self.topic_names[i], s) for i, s in sim]
        return sim

    def process_question_sim(self, sim):
        # process question similarity so it is more straightforward
        sim = sorted(enumerate(sim), key=lambda item: -item[1])
        sim = [(self.questions[i], s) for i, s in sim]
        return sim

    def doc2topic_sim(self, doc):
        self.nlp.load_normal_text(doc)
        question_lsi = self.lsi[self.tfidf[self.dictionary.doc2bow(self.nlp.keywords)]]

        # query similarity
        sim = self.topic_index[question_lsi]

        # preprocess this similarity vector
        for i, v in enumerate(sim):
            if abs(v) < sim.max() / 2: # remove similarities that are too close to zero (therefore not characteristic)
                sim[i] = 0

        # normalize sim to unit vector
        sim /= np.linalg.norm(sim, ord=2)

        return sim

def load_topics_and_questions(pairs_dir="../../resource/chemguide_questions/questions_and_answers.json",
                                     topic_dir="../../resource/chemguide"):
    """
    return all topic question answer pairs
    :param file_dir: the directory of where the data sits
    :return: [topic def, topic name, question list, answer list] pairs
    """
    with open(pairs_dir) as f:
        pairs = json.load(f)

        # compile pattern matcher

        prefix = "https://www.chemguide.co.uk/"
        suffix = ".html#top"
        p = re.compile(prefix + "(.*)" + suffix)

        # load content for each topic
        topics = {}
        questions = {}
        for topic in pairs:
            url = topic[0]

            # rephrase url into file name
            name = p.findall(url)[0]
            name = name.replace("/", "_")
            name += ".txt"

            # read txt file into string
            with open(topic_dir+"/"+name, 'r') as chemguide_file:
                topic_content = chemguide_file.read()

            # load topic content into data storage
            topics[topic[1]] = topic_content

            # load questions against topic name
            questions[topic[1]] = topic[2]

    return topics, questions

def testing(sim, questions, top_n=10):
    counter = 0
    success = 0
    for t in questions:
        for q in questions[t]:
            counter += 1
            similarity = sim.search_topic(q)
            top_n_set = [s[0] for s in similarity[:top_n]]
            if t in top_n_set:
                success += 1
            else:
                print(q)
                print(t)
                max = 0
                for ts, s in similarity:
                    if s > max:
                        max = s
                    if ts == t:
                        print(s)
                print(max)
                print()
    print(success / counter)


topics, questions = load_topics_and_questions()

with open("../../resource/chemguide_questions/2000_questions.json") as f:
    qs = json.load(f)
    for i in qs:
        qs[i] = " ".join(qs[i])

sim = spacy_lsi_sim()
# sim.train("question")
sim.load_all_models()

q = "2. The electronic structure of carbon is 1s22s22px\n 12py\n 1.\n \
a) With the help of a simple sketch, explain the shape of the 1s orbital.\n \
b) How does a 2s orbital differ from a 1s orbital?\n \
c) Draw a simple sketch to show the shape of a 2px orbital.\n \
d) How does a 2py orbital differ from a 2px orbital?\n e) Carbon has 4 electrons in the 2-level.  \
With the help of a simple energy diagram, explain why the \n2-level electrons don't arrange themselves as 2s12px\n 12pz\n1.\n \
12py\n www.chemguide.co.uk\n"

q = "define the term ionisation energy"

s = sim.search_question(q)

while True:
    print()
    q = input("input a question: \n")
    s = sim.search_question(q)
    print()

print()