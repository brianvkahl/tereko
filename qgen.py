#first version 
import json
import nltk.data

def split_text_into_sent(text):
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	return (tokenizer.tokenize(text))

def get_q(sent):
	sent=sent.lower()
	if "for 10 points, " in sent:
		sent=sent.replace("for 10 points, ", "").replace("name this", "the").replace("name these", "the").replace(".", "?")
		return "What is the name of "+sent
	else: 
		sent=sent.replace("this", "what").replace("these", "what").replace(".", "?").replace("(*) ", "")
		return sent

with open('quizdb-20180830162251.json') as f:
	data=json.load(f)

tossups=data["data"]["tossups"]

for tu in tossups:
	text=tu["text"]
	ans=tu["answer"]
	text=split_text_into_sent(text)
	for sent in text:
		print get_q(sent)+'\n', ans
		print '\n'



