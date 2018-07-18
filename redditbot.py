import praw
import time
import numpy as np

r = praw.Reddit(client_id="UslSnVNZH56Pzg",
				client_secret="y7RlHeFaF5vTmRvAV4_qkylPv5c",
				username="markovchaincomment", password="PLACEHOLDER",
				user_agent="Creates markov chains based on recent comments by a user. Created by /u/comsciftw")
		
def main(comment, username):
	try:
		u = r.redditor(username)
	except Error:
		print(username + " does not exist")
		try:
			comment.reply(username + "does not exist")
		except praw.exceptions.APIException as e:
			print(e)
			print("sleeping for 10 minutes...")
			time.sleep(600)
			return
		return
	words = {0:{}}
	discount_rate = 1

	for c in u.comments.new(): # default limit is 100
		comment_arr = c.body.split()
		if comment_arr[0] not in words[0]: # add special start state
			words[0][comment_arr[0]] = 0
		words[0][comment_arr[0]] += discount_rate
		for i in range(len(comment_arr)): # add states (words) and transitions between states (adjacent words) to graph
			if comment_arr[i] not in words:
				words[comment_arr[i]] = {}
			if i < len(comment_arr) - 1:
				if comment_arr[i + 1] not in words[comment_arr[i]]:
					words[comment_arr[i]][comment_arr[i + 1]] = 0
				words[comment_arr[i]][comment_arr[i + 1]] += discount_rate
			else: # add special end state
				if 0 not in words[comment_arr[i]]:
					words[comment_arr[i]][0] = 0
				words[comment_arr[i]][0] += discount_rate
		discount_rate *= 0.98

	keys, vals = list(words[0].keys()), list(words[0].values())
	tot = sum([float(val) for val in vals])
	rep, curr_word, count = "", np.random.choice(keys, p=[float(val)/float(tot) for val in vals]), 0
	while curr_word != 0 and count < 256: # generate markov chain, cap at 256 words
		rep += " " + curr_word
		keys, vals = list(words[curr_word].keys()), list(words[curr_word].values())
		tot = sum([float(val) for val in vals])
		curr_word = np.random.choice(keys, p=[float(val)/float(tot) for val in vals])
		count += 1
	print("replied with: " + rep)
	try:
		comment.reply(rep)
	except praw.exceptions.APIException as e:
		print(e)
		print("sleeping for 10 minutes...")
		time.sleep(600)

for comment in r.subreddit("testcomsciftw").stream.comments():
	# print("comment: " + comment.body)
	comment.refresh()
	comment.replies.replace_more(limit=0)
	if comment.body.startswith("!markovchaincomment") and r.user.me().fullname not in {c.author.fullname for c in comment.replies.list()}:
		print("found comment! " + comment.body)
		b = comment.body.split()
		if len(b) < 2:
			print("no username specified")
			continue
		main(comment, comment.body.split()[1])
