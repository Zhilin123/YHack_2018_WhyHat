import json
import csv
from data_manager.models import Subject, Unit, Topic, Area
import os
def import_areas():
    area_list = ['Politics', 'Learning', "Women's Fashion and Style", "Men's Fashion and Style", 'Venture Capital', 'Apple (company)', 'Academic Research', 'The Universe', 'Movies', 'Colleges and Universities', 'Pizza', 'Travel Hacks', 'Banking', 'Food', 'Entertainment', 'Parenting', 'Invention and Inventions', 'Television Series', 'History of Europe', 'Chemistry', 'Computer Programming', 'Academic Papers', 'Macroeconomics', 'Higher Education', 'Smartphones', 'Marketing', 'Songs', 'The Human Race and Condition', 'Web Design', 'Blogs', 'Visiting and Travel', 'Startup Founders and Entrepreneurs', 'Computer Science', 'Working Out', 'Pharmaceuticals', 'Politics of the United States of America', 'Painting and Paintings (art)', 'Graphic Design', 'Pianos', 'International Economics', 'Fashion and Style', 'Doctors', 'Water', 'Contemporary Art', 'Startups', 'World History', 'Military History and Wars', 'Design', 'Exams and Tests', 'Graduate School Education', 'Academia', 'YouTube', 'Military', 'Investing', 'Problem Solving', 'Art Collecting', 'Healthy Living', 'National Football League', 'Philosophy', 'Economics', 'Schools', 'Fine Art', 'Pop Music', 'Probability (statistics)', 'Recipes', 'Professional Sports', 'Psychology', 'Genetics and Heredity', 'Physics', 'Movie Recommendations', 'Fitness', 'Product Design of Physical Goods', 'Career Advice', 'International Travel', 'Software Engineering', 'Poetry', 'Friendship', 'Bollywood Movies', 'Writing', 'Astrophysics', 'Vegetarian Food', 'Cakes', 'Chocolate', 'Hedge Funds', 'World War II', 'The High School Experience', 'Shoes', 'National Basketball Association (NBA)', 'Finance', 'Relativity (physics)', 'Mobile Applications', 'Literature', 'Software and Applications', 'Technology Startups', 'Airlines', 'Jeans', 'Science', 'Cooking', 'Health', 'Study Habits', 'Technology', 'Philosophy of Science', 'Diet', 'Weight Loss', 'Life Advice', 'Mental Illness', 'Clinical Psychology', 'Celebrities', 'Business Models', 'Geometry', 'Reading', 'Children', 'Advertising and Advertisements', 'Rock Music', 'Investment Banking', 'Intelligence', 'Small Businesses', 'Data Structures', 'Grammar', 'Cognitive Psychology', 'Studying', 'Business Development', 'India', 'Vacations', 'Algebra', 'Metaphysics', 'Blogging', 'User Interfaces', 'The Arts', 'International Relations', 'Mental Health', 'Google (company)', 'Modern Art', 'Information Technology', 'Clothing Fashion', 'Android (operating system)', 'Thinking', 'Shopping', 'Gravity', 'Life and Living', 'Art History', 'Quantum Mechanics', 'YouTube Videos', 'Teaching', 'English (language)', 'Classical Music', 'Fast Food', 'Dating and Relationships', 'Social Advice', 'Artwork', 'Medical Conditions and Diseases', 'Space Exploration', 'Air Travel', 'Exercise', 'Personal Finance', 'Clothing and Apparel', 'Baking', 'Android Applications', 'Innovation', 'Business Ideas', 'Artificial Intelligence', 'Technology Companies', 'Designers', 'History', 'Web Development', 'Cognitive Science', 'Eating', 'China', 'The Future', 'Germany', 'Atoms', 'Association Football', 'Movie Production', 'Restaurants', 'TED', 'Glasses', 'Ethics', 'User Experience', 'Startup Strategy', 'Morals and Morality']
    for area_name in area_list:
        if Area.objects.filter(name=area_name).count() == 0:
            area = Area()
            area.name = area_name
            area.save()
            print(area)
    print('import finished: ' + str(Area.objects.all().count()) + " areas.")



def import_topics():
    f = open('data_manager/tree.json')
    res = json.load(f)['children']
    for node in res:
        node_name = node['name']
        if node_name == 'bio':
            subject_name = "Biology"
        elif node_name == 'phy':
            subject_name = 'Physics'
        elif node_name == 'chem':
            subject_name = 'Chemistry'
        print(subject_name)
        subject = Subject.objects.get(name=subject_name)

        for sub_node in node['children']:
            unit_name = sub_node['name']
            print("-", unit_name)
            if Unit.objects.filter(name=unit_name, subject=subject).count() == 0:
                new_unit = Unit()
                new_unit.name = unit_name
                new_unit.subject = subject
                new_unit.save()
            unit = Unit.objects.get(name=unit_name, subject=subject)

            for sub_sub_node in sub_node['children']:
                topic_name = sub_sub_node['name']
                print ("--", topic_name)
                if Topic.objects.filter(name=topic_name, unit=unit).count() == 0:
                    new_topic = Topic()
                    if topic_name[0:4]=='sub_':
                        new_topic.name = topic_name[4:]
                    else:
                        new_topic.name = topic_name
                    new_topic.real_name = topic_name
                    new_topic.unit = unit
                    print(new_topic)
                    new_topic.save()


    #subject = Subject.objects.get(name="Chemistry")

    '''
    from os import listdir
    from os.path import isfile, join
    mypath = os.getcwd() + '/data_manager'

    dir_names = ['bio_textbook_txt', 'phy_textbook_txt', 'chem_textbook_txt']

    for dir_name in dir_names:
        if dir_name == 'bio_textbook_txt':
            subject_name = "Biology"
        elif dir_name == 'phy_textbook_txt':
            subject_name = 'Physics'
        elif dir_name == 'chem_textbook_txt':
            subject_name = 'Chemistry'
        subject = Subject.objects.get(name=subject_name)
        sub_path = mypath + '/' + dir_name
        onlyfiles = [f for f in listdir(sub_path) if isfile(join(sub_path, f)) and f != "_DS_Store"]
        print(onlyfiles)
        for file in onlyfiles:
            if file[-4:]=='.txt':
                strs = file.split('_')
                if strs[0] == '':
                    strs=strs[1:]
                unit_name = strs[0]
                topic_name = strs[1][:-4]
                print(subject_name, unit_name, "|", topic_name)
                if Unit.objects.filter(name=unit_name, subject=subject).count() == 0:
                    new_unit = Unit()
                    new_unit.name = unit_name
                    new_unit.subject = subject
                    new_unit.save()
                unit = Unit.objects.get(name=unit_name, subject=subject)
                if Topic.objects.filter(name=topic_name, unit=unit).count() == 0:
                    new_topic = Topic()
                    new_topic.name = topic_name
                    new_topic.unit = unit
                    new_topic.save()
    '''


def import_chemistry_topics():
    f = open('data_manager/chemistry_parent_to_children.json')
    res = json.load(f)
    subject = Subject.objects.get(name="Chemistry")

    for unit_name in res.keys():
        print("PARENT:", unit_name)
        if Unit.objects.filter(name=unit_name, subject=subject).count() == 0:
            new_unit = Unit()
            new_unit.name = unit_name
            new_unit.subject = subject
            new_unit.save()
        unit = Unit.objects.get(name=unit_name, subject=subject)
        for topic_name in res[unit_name]:
            print("--", topic_name)
            if Topic.objects.filter(name=topic_name, unit=unit).count() == 0:
                new_topic = Topic()
                new_topic.name = topic_name
                new_topic.unit = unit
                new_topic.save()

    print(Unit.objects.all().count())
    print(Topic.objects.all().count())

    return True

def import_physics_topics():
    with open('data_manager/biology_and_physics_Topic_parents.csv') as csvfile:
        csvreader = csv.reader(csvfile)
        res = list(csvreader)
    subject_name = "Physics"
    for row in res:
        if row[0] == "Biology":
            subject_name = "Biology"
        subject = Subject.objects.get(name=subject_name)
        unit_name = row[2]
        topic_name = row[1]
        print("PARENT:", unit_name)
        print("--", topic_name)
        if Unit.objects.filter(name=unit_name, subject=subject).count() == 0:
            new_unit = Unit()
            new_unit.name = unit_name
            new_unit.subject = subject
            new_unit.save()
        unit = Unit.objects.get(name=unit_name, subject=subject)
        if Topic.objects.filter(name=topic_name, unit=unit).count() == 0:
            new_topic = Topic()
            new_topic.name = topic_name
            new_topic.unit = unit
            new_topic.save()

    print(Unit.objects.all().count())
    print(Topic.objects.all().count())

    return True