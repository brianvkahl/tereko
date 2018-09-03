#v. 5

import json, random, nltk, en_coref_lg

nlp = en_coref_lg.load()

class Text(object):
	def get_cats_from_text(self):
		doc=nlp(self.text)
		noun_chunks=[]
		temp=[]
		cats=[]
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
					cats.append(token.text)
					i=1
			if i==0: cats.append(n_c)
		self.cats=cats

	def get_sents_from_text(self):
		sents=[]
		tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
		for sent in tokenizer.tokenize(self.text):
			if ", and " in sent:
				doc=nlp(sent)
				sent2=""
				for token in doc:
					if token.text in ["and"] and token.head.dep_ not in ["conj", "advmod", "npadvmod", "appos", "dobj", "relcl"] and "," in [t.text for t in token.head.children]:
						sent2=sent2[:-1]
						sent2+="."
						sents.append(sent2)
						sent2=""
					else:
						if token.text in [".", ",", "!", "?", ";", "-", '''"''']:
							sent2+=token.text
						else: sent2+=" "+token.text
				sents.append(sent2)
			else:
				sents.append(sent)
		self.sents=sents

	def __init__(self, text):
		self.text=text
		self.cats=None
		self.sents=None
		self.get_cats_from_text()
		self.get_sents_from_text()
		self.qs=[]
		for sent in self.sents:
			self.qs.append(Sent(sent, self.cats).q)

class Sent(object):
	def __init__(self, sent, cats):
		self.sent=sent
		self.preprocess_sent()
		self.cats=cats
		self.q=None
		self.make_q()

	def format_grammar(self, text):
		final=text.replace("- ", "-").replace(" )", ")").replace("( ", "(").replace(" '", "'")
		return final

	def get_sent_subtree_token(self, token):
		sent=""
		give_subtree=token.subtree
		for t in give_subtree:
			if t.text in [".", ",", "!", "?", ";", ")", "-", '''"''']:
				sent+=t.text
			else: sent+=" "+t.text
		return sent.strip()

	def preprocess_sent(self):
		sent=self.sent.replace("(*) ", "").replace("for 10 points, ", "").replace("For 10 points, ", "").replace(", for 10 points, ", "")
		if ", but " in sent:
			for t in ["isn't ", "is not", "'s not"]:
				if t in sent:
					doc=nlp(sent)
					conj_token=None
					for token in doc:
						if token.dep_=="conj": 
							conj_token=token
							break
					sent=self.get_sent_subtree_token(conj_token)
		self.sent=sent

	def make_q(self):
		sent=self.sent
		doc=nlp(sent)
		cats=self.cats
		replace_wrds=[["this", "what"], ["This", "What"], ["these", "what"], ["These", "What"]]
		for r_w in replace_wrds:
			sent=sent.replace(r_w[0], r_w[1])
		if "what" not in sent:
			prns=[]
			for token in doc: 
				if token.pos_=="PRON": prns.append(token.text)
			try:
				for prn in prns: sent=sent.replace(prn+" ", "what "+random.choice(cats)+" ")
			except IndexError: return "No question generated."
		sent=sent.replace("name what", "what is the").replace("identify what", "what is the").strip()
		temp=self.format_grammar(sent[0].upper()+sent[1:-1]+"?")
		self.q=temp.replace(" (*)", "")



