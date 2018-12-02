import numpy as np
from gensim import corpora, models, similarities
from stop_words import get_stop_words
from random import shuffle
import stop_words
from gensim.parsing.porter import PorterStemmer
import time
import re
import json, os, pickle

from data_manager.TextCleaner import TextCleaner

class InterestVectorizer():
    """
    The class for training topic model
    """
    def __init__(self, folder="./asym_150_both", cl_folder="../text_cleaner_models_without_subjects", 
                 existing_video_index=None
                ):
        """
        Initialize and load all models
        """
        # init model folder
        self.folder = folder

        # load topic models if no training is needed
        self.dictionary = corpora.Dictionary.load(self.folder + "/dictionary")
        self.model = models.LdaModel.load(self.folder + "/model")
        self.vec_len = self.model.num_topics
        
        # load topic_index, indexed_topic, topic_vec, video_index, indexed_video, video_vec, video_topic_vec
        self.topic_vec = np.load(self.folder + "/topic_vec.npy")
        self.video_vec = np.load(self.folder + "/video_vec.npy")
        self.video_topic_vec = np.load(self.folder + "/video_topic_vec.npy")
        self.topic_video_vec = self.video_topic_vec.T
        with open(self.folder + "/topic_index.pkl", 'rb') as f:
            self.topic_index = pickle.load(f)
        with open(self.folder + "/indexed_topic.pkl", 'rb') as f:
            self.indexed_topic = pickle.load(f)
        if existing_video_index is None:
            with open(self.folder + "/video_index.pkl", 'rb') as f:
                self.video_index = pickle.load(f)
            with open(self.folder + "/indexed_video.pkl", 'rb') as f:
                self.indexed_video = pickle.load(f)
        else:
            self.video_index = existing_video_index["video_index"]
            self.indexed_video = existing_video_index["indexed_video"]
        
        # load string cleaner
        self.cl = TextCleaner(folder=cl_folder)
    
    def score_video_based_on_interest_vector(self, interest_vec, thresh=0.05):
        """
        With the input interest vector, return a score for all the videos
        Removing video whose similarity to the topic is less then thresh
        Be advised, do not normalize video topic vec as we are not summing the simlarities of videos
            to different 
        """
        print("Start interest vector score ranking")
        if interest_vec.sum() == 0: # normally distributed interest if no interest is registered
            normed_interest_vector = np.ones_like(interest_vec)
            normed_interest_vector /= normed_interest_vector.sum()
        else:
            normed_interest_vector = interest_vec / interest_vec.sum()
        video_score = np.dot(self.video_topic_vec, normed_interest_vector).reshape(-1)
        print("Finish interest vector score ranking")
        
        return video_score
    
    def index_text(self, text, norm=1, thresh=0.05):
        """
        Index a given string use topic model
        """
        # clean the text
        cleaned_text = self.cl.clean(text)

        # get topic model index
        model_vec = self.model.inference([self.dictionary.doc2bow(cleaned_text.split())])[0][0]
        
        # topics that has prob lower than thresh would be set to zero
        model_vec -= thresh
        model_vec[model_vec<0] = 0
        
        # return zero array if no significant topic possibility
        if model_vec.sum() == 0:
            return model_vec
        
        # do norm if necessary
        if norm is None:
            return model_vec
        else:
            return model_vec / np.linalg.norm(model_vec, ord=norm)

class SubjectVectorizer():
    """
    The class for training topic model
    """
    def __init__(self, folder="./subject_models", cl_folder="../text_cleaner_models_with_subjects/", 
                 existing_video_index=None
                ):
        """
        Initialize and load all models
        """
        # init model folder
        self.folder = folder

        # load topic models if no training is needed
        self.dictionary = corpora.Dictionary.load(self.folder + "/dictionary")
        self.model = models.LdaModel.load(self.folder + "/model")
        self.vec_len = self.model.num_topics
        
        # load topic_index, indexed_topic, topic_vec, video_index, indexed_video, video_vec, video_topic_vec
        self.topic_vec = np.load(self.folder + "/topic_vec.npy")
        self.video_vec = np.load(self.folder + "/video_vec.npy")
        self.video_topic_vec = np.load(self.folder + "/video_topic_vec.npy")
        self.topic_video_vec = self.video_topic_vec.T
        with open(self.folder + "/topic_index.pkl", 'rb') as f:
            self.topic_index = pickle.load(f)
        with open(self.folder + "/indexed_topic.pkl", 'rb') as f:
            self.indexed_topic = pickle.load(f)
        if existing_video_index is None:
            with open(self.folder + "/video_index.pkl", 'rb') as f:
                self.video_index = pickle.load(f)
            with open(self.folder + "/indexed_video.pkl", 'rb') as f:
                self.indexed_video = pickle.load(f)
        else:
            self.video_index = existing_video_index["video_index"]
            self.indexed_video = existing_video_index["indexed_video"]
        
        # load string cleaner
        self.cl = TextCleaner(folder=cl_folder)
    
    def score_video_based_on_topic(self, topics, thresh=0.6):
        """
        With the input topics, return a score for all the videos
        Removing video whose similarity to the topic is less then thresh
        """
        print("Start subject topic vector score ranking")
        if len(topics) == 0:
            return np.ones(len(self.indexed_video)) / len(self.indexed_video)
        
        video_score_sum = np.zeros(len(self.indexed_video))
        for t in topics:
            ti = self.topic_index[t]
            video_score = self.topic_video_vec[ti].copy()
            video_score[video_score<thresh] = 0
            video_score_sum += video_score
        video_score_sum[video_score_sum<thresh] = 0
        
        if not video_score_sum.any():
            print("no matching video for these toipcs: ", topics)
            return np.ones(len(self.indexed_video)) / len(self.indexed_video)
        
        print("Finishing subject topic vector score ranking")
            
        return video_score_sum / len(topics)

class VideoVectorizer():
    def __init__(self, folder="."):
        """
        Load from folder vectorizer for interest and subject
        """
        # load vectorizer
        self.interest = InterestVectorizer(folder=folder + "/asym_150_both", cl_folder=folder + "/text_cleaner_models_without_subjects")
        self.subject = SubjectVectorizer(folder=folder + "/subject_models", cl_folder=folder + "/text_cleaner_models_with_subjects")
        
        # get the common video index
        self.indexed_video = self.interest.indexed_video
        self.video_index = self.subject.video_index
        
    def update_interest_vector(self, prev_interest_vec, prev_video, update_constant=0.1):
        """
        update interest vector with EMS
        """
        prev_video_interest_vec = self.interest.video_topic_vec[self.video_index[prev_video]]
        
        interest_vec = update_constant * (prev_video_interest_vec - prev_interest_vec) + prev_interest_vec
        
        return interest_vec
        
    def get_ranked_video(self, subjects, interest_vec, subject_weight=0.75, subject_mask_value=1, thresh=0):
        print("Start video ranking")
        print("Interest vector shape: ", interest_vec.shape)
        # get score for each video based on topics and interests
        interest_score = self.interest.score_video_based_on_interest_vector(interest_vec)
        subject_score = self.subject.score_video_based_on_topic(subjects)
        interest_score /= interest_score.sum()
        subject_score /= subject_score.sum()
        
        print("Start final score combining")
        # get the final score, NB video that does not match a subject would not be presented
        final_score = subject_weight * subject_score + (1 - subject_weight) * interest_score
        # get subject mask to mask the final result
        subject_mask = subject_score.copy()
        subject_mask[subject_mask>0] = 1
        subject_mask[subject_mask==0] = subject_mask_value
        # get finally masked result
        final_score *= subject_mask
        print("Finish final score combining")
        
        # give ranked url and title out
        sorted_score = sorted(enumerate(final_score), key=lambda x:x[1], reverse=True)
        
        print("Final score acquired, starting ranking")
        ranked_video = []
        for index, score in sorted_score:
            if score < thresh:
                break
            ranked_video.append((self.indexed_video[index], score))
        return ranked_video
