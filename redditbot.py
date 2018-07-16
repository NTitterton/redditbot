import time
import praw
import numpy as np

r = praw.Reddit(client_id="46VMiR99cMH94w",
				client_secret="vwKpTYxlmSddB0PanWKkdhpGPsk",
				username="comsciftw", password="REPLACE AT RUNTIME",
				user_agent="Creates markov chains based on individual comments. Created by /u/comsciftw")

for comment in r.subreddit("testcomsciftw").stream.comments():
	print("comment: " + comment.body)
	if comment.body.startswith("!markovchaincomment"):
		print("found comment!")
		comment_arr = comment.parent().body.split()
		words = {0:{comment_arr[0]:1}}
		for i in range(len(comment_arr)):
			if comment_arr[i] not in words:
				words[comment_arr[i]] = {}
			if i < len(comment_arr) - 1:
				if comment_arr[i + 1] not in words[comment_arr[i]]:
					words[comment_arr[i]][comment_arr[i + 1]] = 0
				words[comment_arr[i]][comment_arr[i + 1]] += 1
			else:
				words[comment_arr[i]][0] = 1
		keys, vals = list(words[0].keys()), list(words[0].values())
		tot = sum([int(val) for val in vals])
		rep, curr_word, count = "", np.random.choice(keys, p=[int(val)/tot for val in vals]), 0
		while curr_word != 0 and count < 256:
			rep += " " + curr_word
			keys, vals = list(words[curr_word].keys()), list(words[curr_word].values())
			tot = sum([int(val) for val in vals])
			curr_word = np.random.choice(keys, p=[int(val)/tot for val in vals])
			count += 1
		print("replied with: " + rep)
		comment.reply(rep)
