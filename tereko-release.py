#version 4.1

import json, random, nltk, en_coref_lg
nlp = en_coref_lg.load()

def split_text_into_sent(text):
	sentences=[]
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	for sent in tokenizer.tokenize(text):
		if ", and " in sent:
			doc=nlp(sent)
			sentence=""
			for token in doc:
				if token.text=="and" and token.head.dep_ not in ["conj", "advmod", "npadvmod", "appos"] and "," in [t.text for t in token.head.children]:
					sentence=sentence[:-1]
					sentence+="."
					sentences.append(sentence)
					sentence=""
				else:
					if token.text in [".", ",", "!", "?", ";", ")", "-", '''"''']:
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
		if "this " in n_c.text: temp.append(n_c.text.replace("this ", ""))
		if "these " in n_c.text: temp.append(n_c.text.replace("these ", ""))
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
	sent=sent.replace("(*) ", "").replace("for 10 points, ", "").replace("For 10 points, ", "")
	if ", but " in sent:
		doc=nlp(sent)
		ROOT=False
		nsubj=False
		conj_token=None
		for token in doc:
			if token.dep_=="ROOT" and token.text in ["'s", "is"]: ROOT=True
			if token.dep_=="nsubj" and token.text=="It": nsubj=True
			if token.dep_=="conj": conj_token=token
		if ROOT and nsubj:
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
		for prn in prns: sent=sent.replace(prn, "what "+random.choice(variants))
	sent=sent.replace("name what", "What is the").replace("identify what", "What is the")
	return sent.strip()[:-1]+"?"

with open("quizdb-20180829202657.json", encoding='utf-8') as f:
    data=json.loads(f.read())

tossups=data["data"]["tossups"]
w=open('sci_q.txt', 'w')
for tossup in tossups:
	text=(tossup["text"])
	variants=get_variants_of_term(text)
	ans=tossup["answer"][:tossup["answer"].find("&")].strip()
	sentences=split_text_into_sent(text)
	for sent in sentences:
		w.write(make_q(sent, variants)+'\n')
		w.write("ANSWER: "+ans+'\n'+'\n')
