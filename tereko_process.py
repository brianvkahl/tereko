from tereko_alg import *
import json

with open("quizdb_sci_5.json", encoding='utf-8') as f:
    data=json.loads(f.read())

tossups=data["data"]["tossups"]

output_data={}
questions=[]
for tossup in tossups:
	qs=Text(tossup["text"]).qs
	if tossup["answer"].find("&")!=-1: ans=tossup["answer"][:(tossup["answer"].find("&"))].strip()
	else: ans=tossup["answer"].strip()
	try: questions.append({'questions': qs, 'answer': ans, 'subject': tossup['subcategory']['name'], 'citation': tossup["tournament"]["name"]})
	except KeyError: questions.append({'questions': qs, 'answer': ans, 'citation': tossup["tournament"]["name"]})

output_data['all_questions']=questions

with open('data.json', 'w') as outfile:
    json.dump(output_data, outfile)