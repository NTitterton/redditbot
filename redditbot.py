import time
import praw
import numpy as np

r = praw.Reddit("Creates markov chains based on individual comments. Created by /u/comsciftw")
r.login()

for comment in praw.helpers.comment_stream(r, "all"):
	if comment.startswith("/u/markov_chain_comment_bot"):
		comment_arr = comment.body.split()
		words = {0:{comment_arr[0]:1}}
		for i in range(len(comment_arr)):
			if comment_arr[i] not in words:
				comment_arr[i] = {}
			if i < len(comment_arr) - 1:
				if comment_arr[i + 1] not in comment_arr[i]:
					comment_arr[i][comment_arr[i + 1]] = 0
				comment_arr[i][comment_arr[i + 1]] += 1
			else:
				comment_arr[i][0] = 1
		keys, vals = comment_arr[0].keys(), comment_arr[0].values()
		tot = sum(vals)
		rep, curr_word = "", np.random.choice(keys, p=[val/tot for val in vals])
		while curr_word != 0:
			rep += " " + curr_word
			keys, vals = comment_arr[curr_word].keys(), comment_arr[curr_word].values()
			tot = sum(vals)
			curr_word = np.random.choice(keys, p=[val/tot for val in vals])
		comment.reply(rep)
