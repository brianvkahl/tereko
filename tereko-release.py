#version 4.2.1 

import json, random, nltk, en_coref_lg
from timeit import default_timer as timer
nlp = en_coref_lg.load()

def format_grammar(text):
	final=text.replace("- ", "-").replace(" )", ")").replace("( ", "(").replace(" '", "'")
	return final

def split_text_into_sent(text):
	sentences=[]
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	for sent in tokenizer.tokenize(text):
		if ", and " in sent:
			doc=nlp(sent)
			sentence=""
			for token in doc:
				if token.text in ["and", "but"] and token.head.dep_ not in ["conj", "advmod", "npadvmod", "appos", "dobj", "relcl"] and "," in [t.text for t in token.head.children]:
					sentence=sentence[:-1]
					sentence+="."
					sentences.append(sentence)
					sentence=""
				else:
					if token.text in [".", ",", "!", "?", ";", "-", '''"''']:
						sentence+=token.text
					else: sentence+=" "+token.text
			sentences.append(sentence)
		else:
			sentences.append(sent)
	return sentences

def get_sent_subtree_token(token):
	sent=""
	give_subtree=token.subtree
	for t in give_subtree:
		if t.text in [".", ",", "!", "?", ";", ")", "-", '''"''']:
			sent+=t.text
		else: sent+=" "+t.text
	return sent.strip()

def get_variants_of_term(text):
	doc=nlp(text)
	noun_chunks=[]
	temp=[]
	final=[]
	for n_c in doc.noun_chunks: 
		if "this" in n_c.text: temp.append(n_c.text.replace("this ", "").strip())
		if "these" in n_c.text: temp.append(n_c.text.replace("these ", "").strip())
		if "This" in n_c.text: temp.append(n_c.text.replace("This ", "").strip())
		if "These" in n_c.text: temp.append(n_c.text.replace("These ", "").strip())
	for n_c in temp: 
		i=0
		doc=nlp(n_c)
		for token in doc: 
			if token.dep_=="poss":
				final.append(token.text)
				i=1
		if i==0: final.append(n_c)
	return final

def preprocess_sent(sent):
	sent=sent.replace("(*) ", "").replace("for 10 points, ", "").replace("For 10 points, ", "").replace(", for 10 points, ", "")
	if ", but " in sent:
		for t in ["isn't ", "is not", "'s not"]:
			if t in sent:
				doc=nlp(sent)
				conj_token=None
				for token in doc:
					if token.dep_=="conj": 
						conj_token=token
						break
				sent=get_sent_subtree_token(conj_token)
	return sent

def make_q(sent, varints):
	doc=nlp(sent)
	variants=varints
	sent=preprocess_sent(sent)
	replace_wrds=[["this", "what"], ["This", "What"], ["these", "what"], ["These", "What"]]
	for r_w in replace_wrds:
		sent=sent.replace(r_w[0], r_w[1])
	if "what" not in sent:
		prns=[]
		for token in doc: 
			if token.pos_=="PRON": prns.append(token.text)
		try:
			for prn in prns: sent=sent.replace(prn+" ", "what "+random.choice(variants)+" ")
		except IndexError: return "No question generated."
	sent=sent.replace("name what", "what is the").replace("identify what", "what is the")
	return format_grammar(sent.strip()[0].upper()+sent.strip()[1:-1]+"?").replace(" (*)", "")

with open("quizdb_sci_5.json", encoding='utf-8') as f:
    data=json.loads(f.read())

tossups=data["data"]["tossups"]

w=open('sci_q-release.txt', 'w')
for tossup in tossups:
	text=(tossup["text"])
	variants=get_variants_of_term(text)
	if tossup["answer"].find("&")!=-1: ans=tossup["answer"][:(tossup["answer"].find("&"))].strip()
	else: ans=tossup["answer"].strip()
	sentences=split_text_into_sent(text)
	for sent in sentences:
		w.write(make_q(sent, variants)+'\n')
		w.write("ANSWER: "+ans+'\n'+'\n')
