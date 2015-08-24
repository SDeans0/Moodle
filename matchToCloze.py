# Written by Sam Deans. 
# Twitter/GitHub: @sdeans0
# Licensed under the Apache License, Version 2.0 (see below)

# This program is for turning matching type Moodle questions to Cloze type questions in 
# Moodle xml format.
# Run it from the command line by importing the moduleand running the 
# matchToCloze.main('filename') function.

import xml.etree.ElementTree as ET
from random import random

def main(filename):
    '''This takes a Moodle xml document and writes a new one with the matching type questions 
    from the old one parsed as Clozes'''
    root = loadXML(filename)
    questions = getQuestions(root)
    answers = getAnswers(root)
    stems = getStems(root)
    gotName = getName(root)
    gotGeneralFeedback = getGeneralFeedback(root)
    gotPenalty = getPenalty(root)
    gotHidden = getHidden(root)
    quiz = ET.Element('quiz')
    for index in range(len(gotName)):
        wrappedClozeText = clozeSyntactify(questions[index],answers[index], stems[index])
        quiz = clozeSkeleton(quiz,gotName[index],wrappedClozeText,gotGeneralFeedback[index],gotPenalty[index],gotHidden[index])
    
    newFileName = changeFileName(filename)
    output = ET.ElementTree(quiz)
    output.write(newFileName, method = 'html')
    # It might be worth importing xml.minidom to make a more neatly formatted XML document
    # - this does not seem to be a problem in Moodle though

def loadXML(filename):
	'''Loads and xml file and returns the root of the tree'''
    tree = ET.parse(filename)
    root = tree.getroot()
    return root

def changeFileName(filename):
    '''Alters the filename inputted to reflect that the output is of Clozes derived from 
    matching type questions'''
    newFileName = filename[:-4] + '-Match-to-Cloze.xml'
    return newFileName

def getQuestions(root):
	'''Returns the text of each matching subquestions in a nested list:
	[[Subquestions from Q1],[Subquestions from Q2],etc]'''
    questions = []
    for index in range(0,len(root)):
    	if root[index].attrib == {'type':'matching'}:
            subquestions = []
            for element in root[index].findall('subquestion'):
                subquestions.append(element[0].text[3:-4])
            questions.append(subquestions)
    return questions

def getAnswers(root):
    '''Returns the answers to each subquestion in a nested list:
	[[Answers to subquestions from Q1],[Answers to subquestions from Q2],etc]'''
    answers = []
    for index in range(0,len(root)):
    	if root[index].attrib == {'type':'matching'}:
            subquestions = []
            for subquestion in root[index].findall('subquestion'):
                for answer in subquestion.findall('answer'):
                    subquestions.append(answer[0].text)
            answers.append(subquestions)
    return answers
    
def getName(root):
	'''Returns a list of the titles of each matching question'''
    names = []
    for index in range(0,len(root)):
        if root[index].attrib == {'type':'matching'}:
            names.append(root[index][0][0].text)
    return names

def getStems(root):
	'''Returns the content of the "Question Text" box which explains the theme of the 
	subquestions'''
    stems = []
    for index in range(0,len(root)):
        if root[index].attrib == {'type':'matching'}:
            stems.append(root[index][1][0].text)
    print stems
    return stems

def getGeneralFeedback(root):
    '''Returns the content of the "General Feedback" box which explains the solutions to  
	the subquestions'''
    genFeedbacks = []
    for index in range(0,len(root)):
        if root[index].attrib == {'type':'matching'}:
            genFeedbacks.append(root[index][2][0].text)
    return genFeedbacks

def getPenalty(root):
    '''Returns a list of the penalties for multiple tries (percent of whole marks)
    for each matching question'''
    penalties = []
    for index in range(0,len(root)):
        if root[index].attrib == {'type':'matching'}:
            penalties.append(root[index][4].text)
    return penalties
    
def getHidden(root):
    '''Returns a list of whether each question is hidden (0 or 1)'''
    hiddens = []
    for index in range(0,len(root)):
        if root[index].attrib == {'type':'matching'}:
            hiddens.append(root[index][4].text)
    return hiddens
    
def clozeSyntactify(question, answers, stem): #Questions and answers are lists of the same length
    '''Takes the list of subquestions, answers to these, and the overall stem of a matching
    question and returns the text of a Cloze analog with newlines between each question'''
    clozeExpressionList = []
    if len(question) != len(answers):
        print 'You have fucked up'
    for index in range(len(answers)):
    	answerList = []
    	for item in answers:
    		if item == answers[index]:
    		    continue
    		else:
    		    answerList.append(item)
        clozeExpression = '<p><br>' + question[index] + ' {1:MC:=%s' % (answers[index])
        for item in answerList:
            clozeExpression += '~%s' % (item)
        clozeExpression += '}</p>\n'
        clozeExpressionList.append(clozeExpression)
    clozeText = stem + ' \n <br>' + ''.join(clozeExpressionList)
    return clozeText

def safeHTML(clozeText):
    '''Designed to add a CDATA tag to the Cloze text'''
    # This needs some attention - it might be better to work this in terms of forming an 
    # element instance rather than adding plain text.
    wrappedClozeText = '<![CDATA[' + clozeText + ']]'
    return wrappedClozeText
    
def clozeSkeleton(quiz,gotName,wrappedClozeText,gotGeneralFeedback,gotPenalty,gotHidden):
    '''clozeSkeleton takes the cloze text, the name, the general feedback, penalty and
    whether the question is hidden, and creates an element which is a full cloze question
    in Moodle XML format. It builds this as an sub element of the quiz entered.'''
    
    serialNumber = int(6 * 10**6 + random() * 10*4) #At some point in the future this could 
    # become a bug. Just make it 10**7 or 10**8 or something to avoid the indexing being
    # the same. Could replace with hash('gotName')
    
    comment = ET.Comment(' question: %d  ' % (serialNumber))
    quiz.append(comment)
    
    question = ET.SubElement(quiz, 'question', {'type':'cloze'})
    
    name = ET.SubElement(question, 'name')
    nametext = ET.SubElement(name, 'text')
    nametext.text = gotName
    
    questiontext = ET.SubElement(question, 'questiontext')
    questiontexttext = ET.SubElement(questiontext, 'text')
    questiontexttext.text = wrappedClozeText
    
    generalfeedback = ET.SubElement(question, 'generalfeedback')
    generalfeedbacktext = ET.SubElement(generalfeedback, 'text')
    generalfeedbacktext.text = gotGeneralFeedback
    
    penalty = ET.SubElement(question, 'penalty')
    penalty.text = gotPenalty
    
    hidden = ET.SubElement(question, 'hidden')
    hidden.text = gotHidden

    return quiz
    
# Copyright 2015 Sam Deans
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
  
    
    
    
    

