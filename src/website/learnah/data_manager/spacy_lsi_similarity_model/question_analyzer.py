import spacy
import re
import chemdataextractor
from fuzzywuzzy import fuzz
import stop_words
from gensim.parsing.porter import PorterStemmer


class question_analyzer:
    def __init__(self, spacy_model="en"):

        # prepare for string cleaner
        # several re pattern matcher
        # matching question index, eg (i), (a)
        self.re_question_index = re.compile("\(?[ivxa-fA-F]{1,4}\)")
        # matching (x mark), [x mark], can also match "(x mark) 6" etc.
        self.re_x_mark = re.compile("[\(|\[]\d+ marks?[\]|\)]( +\d+)?")
        # matching (extra space), [Extra space] etc.
        self.re_extra_space = re.compile("(?i)[\(|\[]extra space[\]|\)]")
        # match end of sent marks
        self.re_end_of_sentence = re.compile("[?!]")
        # matching alphanumeral and .,-
        self.re_major = re.compile("[^\w.,']+")

        # store stop words
        self.stop_words = stop_words.get_stop_words("en")

        # prepare parsing for question
        if not type(spacy_model) is str:
            self.nlp = spacy_model
        else:
            self.nlp = spacy.load(spacy_model, disable=["ner"])

        # prepare stemmer
        self.stemmer = PorterStemmer()

        print("loaded spacy pipline: ", self.nlp.pipe_names)

    def load_normal_text(self, string, remove_pure_digit=True, connect_cem_entity=False):
        """
        load a normal text and extract keywords from it
        """
        # clean up the normal text
        string = self.clean_question(string, remove_pure_digit)

        # connect chemical entities in the normal text
        if connect_cem_entity:
            string = self.connect_cem_entity(string)

        # process the normal text string use spacy nlp pipeline
        self.question = self.nlp(string)

        # store sentences of the normal text
        self.sents = list(self.question.sents)

        # extract keywords from it
        self.keywords = self.extract_keywords(self.sents)

    def load_question(self, string, remove_pure_digit=True, connect_cem_entity=False):
        """
        load the string of a question and preprocess it for further analysis
        """
        # clean up the question string
        string = self.clean_question(string, remove_pure_digit)

        # connect chemical entities in the question string
        if connect_cem_entity:
            string = self.connect_cem_entity(string)

        # process the question string use spacy nlp pipeline
        self.question = self.nlp(string)

        # store sentences of the question
        self.sents = list(self.question.sents)

        # extract question sentences of the question
        self.extract_question_sents()

        # extract sub question of the input question
        self.extract_sub_questions()

        # extract keywords from sub questions
        self.keywords = [self.extract_keywords(sents) for sents in self.sub_questions]

    def clean_question(self, string, remove_pure_digit=True):
        """
        clean up the question string
        1. remove question index
        2. remove (mark) notes
        3. remove (extra space) notes
        4. remove overly special letters, optionally remove pure digits
        """
        string = self.re_question_index.sub('.', string)
        string = self.re_x_mark.sub('.', string)
        string = self.re_extra_space.sub('.', string)
        string = self.re_end_of_sentence.sub('.', string)
        if remove_pure_digit:
            string = " ".join([re.sub("[\d]*.?[\d]+", "", token) if re.sub("[^\w]+", "", token).isdigit() else token
                               for token in self.re_major.sub(' ', string).split()])
        else:
            string = " ".join([token for token in self.re_major.sub(' ', string).split()])
        # clean up space caused by previous steps
        string = re.sub("  +", " ", string)
        # clean up . caused by previous steps
        string = re.sub("( *\.+ +)(\.+ *)*", " . ", string)

        return string

    def connect_cem_entity(self, string, repl="-"):
        """
        connect complicated chemical entities with "repl"
            to simplify the dependency parsing later
        """
        chemicals = chemdataextractor.Document(string).cems
        self.chemicals = [cem.text for cem in chemicals]
        for cem in self.chemicals:
            string = string.replace(cem, cem.replace(" ", repl))
        return string

    def extract_question_sents(self):
        """
        Extract sentences in the given preprocessed question string if it is a imperitive sentence.
        and n sentences before each of them
        (Usually the question sentence of a question is in the form of imperitive sentence or interrogative sentence.)

        Two cases are considered for imperitive sentences:
            1. If a sentence is a proper sentence, then its root, or root's conjunction, which are usually verbs,
            should have no subject. This can be checked using the dep parsing.

            2. If the first word of a sentence has POS tag VERB, then we are pretty sure the sentence is a imperitive
            one. However, boundary cases like -ing form being a noun phrase need to considered

        Three cases are considered for interrogative sentence:
            3. If the first word is a question word: (who, whom, whose, why, what, when, where, which, how)

            4. If the first word has a lemma_: (be, do)

            5. If the first word has dep_: aux
        """
        self.question_sents = []
        self.question_sent_indices = []
        for i, sent in enumerate(self.sents):
            # remove Ture over the page:
            if sent[0].lemma_ in ("turn"):
                continue

            is_question_sent = False
            # check for question sentences:
            if not is_question_sent and sent[0].dep_ == "aux":
                is_question_sent = True

            # check for case 4
            if not is_question_sent and sent[0].lemma_ in ("be", "do"):
                is_question_sent = True

            # check for case 3
            if not is_question_sent and sent[0].text in (
            "who", "whom", "whose", "why", "what", "when", "where", "which", "how"):
                is_question_sent = True

            # check for case 2
            if not is_question_sent and sent[0].pos_ == "VERB" and sent[0].dep_ not in ("csubj", "passcsubj") \
                    or sent[0].lemma_ in ("outline"):
                is_question_sent = True

            # check based on dep parsing (case 1)
            if not is_question_sent:
                possible_roots = list(sent.root.conjuncts)
                possible_roots.append(sent.root)
                for possible_root in possible_roots:
                    for token in possible_root.children:
                        if token.dep_ in ("nsubj", "csubj", "agent"):  # check if it has a subject
                            is_question_sent = True
                            break
                    if is_question_sent:
                        break

            # add the sent to question sent list, and also store their index
            if is_question_sent:
                self.question_sent_indices.append(i)
                self.question_sents.append(sent)

    def extract_sub_questions(self, n=1):
        """
        seperate questions based on each question sentences (and n sentences that are not question sents)
        find coreference sentences in previous sentences.
        combined they form one sub question from the main quesiton loaded
        """
        self.sub_questions = []
        for i, q_sent in enumerate(self.question_sents):
            # find the end of question description and from there get consecutive n sents
            # as related sents to this question sent
            sub_question_core = [q_sent]
            j = self.question_sent_indices[i] - 1
            counter = 0
            has_start_recording = False
            while j >= 0:
                if j in self.question_sent_indices:
                    if has_start_recording:
                        break
                else:
                    if counter == n:
                        break
                    else:
                        has_start_recording = True
                        counter += 1
                        sub_question_core.append(self.sents[j])
                j -= 1

            # find sents in the previous part of the question that are has coreference of nc in
            # currently gathered sub question sents
            sub_question_coref = self.extract_coref_sents(sub_question_core, no_sents=self.question_sents)

            sub_question = sub_question_core + sub_question_coref

            self.sub_questions.append(sub_question)

    def extract_keywords(self, sents, remove_stop_words=True, stem=True):
        """
        collect lemmatized keywords from sents, including:
        1. noun chunks (with det removed and no -PRON-)
        2. verb related to each noun chunks (apart from "be" and "aux")
        3. adj related to each noun chunks
        return a list string
        """
        keywords = []
        for sent in sents:
            # collect all noun chunks, except -PRON-, and not nc tokens
            nc_set = set([token for nc in sent.noun_chunks for token in nc])
            # collect processed noun chunk tokens
            if remove_stop_words:
                keywords += [token for nc in sent.noun_chunks \
                             for token in self.clean_nc(nc).split() if not token == "-PRON-" \
                             and not len(token) <= 1 and token not in self.stop_words]
            else:
                keywords += [token for nc in sent.noun_chunks \
                             for token in self.clean_nc(nc).split() if not token == "-PRON-" and not len(token) <= 1]
            # collect not noun chunk tokens
            no_nc = []
            for token in sent:
                if token not in nc_set:
                    no_nc.append(token)

            # collect all verbs and adj
            for token in no_nc:
                # collect proper verb and adj
                tmp = False
                if token.pos_ == "VERB" and token.lemma_ not in ("be") and token.dep_ not in ("aux", "auxpass"):
                    tmp = token.lemma_
                elif token.pos_ == "ADJ":
                    tmp = token.lemma_
                if tmp:
                    if remove_stop_words:
                        if tmp not in self.stop_words:
                            keywords.append(tmp)
                    else:
                        keywords.append(tmp)
        if stem:
            [self.stemmer.stem(token) for token in keywords]

        return keywords

    def extract_coref_sents(self, sents, no_sents=[]):
        """
        Collect relative sents to given sents in all the question sents apart from no_sents
        1. collect noun chunks in the given sents
        2. resolve coreference of these nc in all sents of the question
        3. return all these questions that have coreferenced ncs in given sents (not including given sents)
        """
        # extract ncs from given sents
        core_ncs = [nc for sent in sents for nc in sent.noun_chunks if not nc.lemma_ == "-PRON-"]

        # extract noun chunks from all sents apart from no sents in the question
        candidate_ncs = [nc for sent in self.sents for nc in sent.noun_chunks \
                         if not nc.lemma_ == "-PRON-" and sent not in no_sents and sent not in sents]

        # resolve coreference of core_ncs in candidate_ncs
        coref_ncs = self.resolve_coref(core_ncs, candidate_ncs)

        # return sents that contain one of coref_ncs
        return list(set([nc.sent for nc in coref_ncs]))

    def clean_nc(self, nc, remove_amod=False):
        """
        Return a cleaned up noun chunk's text
        """
        # if nc is a long string of short non-sense, substite it for -CHEM-
        if sum([len(token) for token in nc]) / len(nc) <= 3 and len(nc) >= 3:
            return "-CHEM-"

        # remove det and nummod, but not PH (a bad yet important wrong parsing)
        bad_dep = ["det", "nummod"]
        if remove_amod:
            bad_dep.append("amod")
        tokens = [token.lemma_ for token in nc if
                  not token.dep_ in bad_dep or token.text.lower() == "ph"]

        return " ".join(tokens)

    def resolve_coref(self, core_ncs, candidate_ncs):
        """
        Look for coreference of input noun chunks in candidate noun chunks
        Core noun chunks are ncs of root references.
        Candidate noun chunks are ncs that might be coreferences of root references
        """
        # we remove also the amod for each candidate nc, but not for each core nc,
        # as we consider core ncs to be significantly more valuable
        core_nc_texts = [self.clean_nc(nc) for nc in core_ncs]
        candidate_nc_texts = [self.clean_nc(nc, remove_amod=True) for nc in candidate_ncs]

        coref_nc = []
        for i, nc in enumerate(candidate_nc_texts):
            # ignore -CHEM-
            if nc == "-CHEM-":
                continue
            for j, core_nc in enumerate(core_nc_texts):
                # ignore -CHEM-
                if nc == "-CHEM-":
                    continue

                # if nc == core_nc, then it is definitely a coref
                if nc == core_nc:
                    # print(nc, core_nc, fuzz.partial_token_set_ratio(nc, core_nc))
                    coref_nc.append(candidate_ncs[i])
                    break

                # if one of the nc has only one word of length less than 3
                # directly check if the word exist in the other nc
                # this is to avoid cases like, sim("X", "exclamation D") == 100
                if len(nc) < 3:
                    small_nc = nc
                    big_nc = core_nc.split()
                elif len(core_nc) < 3:
                    small_nc = core_nc
                    big_nc = nc.split()
                # only do partial similarity when both of the ncs has more than one letter
                elif fuzz.partial_token_sort_ratio(nc, core_nc) > 90:
                    # print(nc, core_nc, fuzz.partial_token_set_ratio(nc, core_nc))
                    coref_nc.append(candidate_ncs[i])
                    break

                    # check if small nc is in big nc
                try:
                    if small_nc in big_nc:
                        # print(small_nc, big_nc)
                        # print(nc, ",", core_nc, 2000)
                        coref_nc.append(candidate_ncs[i])
                        break
                except:
                    pass

        return coref_nc

    def __str__(self):
        return "***Question full text:\n" + self.question.text + \
               "\n***Question core parts:\n" + str(self.core_parts) + \
               "\n***Question key elements:\n" + str(self.key_elements)