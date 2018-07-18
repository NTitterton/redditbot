import praw, time, numpy as np

r = praw.Reddit(client_id="UslSnVNZH56Pzg",
				client_secret="y7RlHeFaF5vTmRvAV4_qkylPv5c",
				username="markovchaincomment", password="PLACEHOLDER",
				user_agent="Creates markov chains based on recent comments by a user. Created by /u/comsciftw")
backlog = []
		
def main(comment, username):
	try:
		u = r.redditor(username)
	except Error:
		safe_reply(comment, username + " does not exist")
		return
	words = {0:{}} # add special start state
	discount_rate = 1

	for c in u.comments.new(): # default limit is 100
		comment_arr = c.body.split()
		if comment_arr[0] not in words[0]:  # update special start state
			words[0][comment_arr[0]] = 0
		words[0][comment_arr[0]] += discount_rate
		for i in range(len(comment_arr)): # add states (words) and transitions between states (adjacent words) to graph
			if comment_arr[i] not in words:
				words[comment_arr[i]] = {}
			if i < len(comment_arr) - 1:
				if comment_arr[i + 1] not in words[comment_arr[i]]:
					words[comment_arr[i]][comment_arr[i + 1]] = 0
				words[comment_arr[i]][comment_arr[i + 1]] += discount_rate
			else:
				if 0 not in words[comment_arr[i]]: # update special end state
					words[comment_arr[i]][0] = 0
				words[comment_arr[i]][0] += discount_rate
		discount_rate *= 0.98

	keys, vals = list(words[0].keys()), list(words[0].values())
	tot = sum([float(val) for val in vals])
	rep, curr_word, count = "", np.random.choice(keys, p=[float(val)/float(tot) for val in vals]), 0
	while curr_word != 0 and count < 256: # generate markov chain, cap at 256 words
		rep += " " + curr_word
		try: # for some reason this is giving a KeyError: '0', so this is a temp fix
			keys, vals = list(words[curr_word].keys()), list(words[curr_word].values())
		except KeyError as e:
			print(e)
			try:
				comment.reply("Oh no! Something went wrong!")
			except praw.exceptions.APIException as e:
				print(e)
				return
			return
		tot = sum([float(val) for val in vals])
		curr_word = np.random.choice(keys, p=[float(val)/float(tot) for val in vals])
		count += 1

	safe_reply(comment, rep)

def safe_reply(comment, rep, from_backlog=False):
	if from_backlog:
		print("replied from backlog with: " + rep)
	else:
		print("replied with: " + rep)
	try:
		comment.reply(rep)
	except praw.exceptions.APIException as e:
		backlog.append((comment, rep))
		print(e)
		print("added to backlog and sleeping for 10 minutes...")
		time.sleep(600)

for comment in r.subreddit("testcomsciftw").stream.comments():
	# print("comment: " + comment.body)
	while len(backlog) > 0:
		print("clearing out comment from backlog")
		comment, rep = backlog.pop(0)
		safe_reply(comment, rep, True)
	comment.refresh()
	comment.replies.replace_more(limit=0)
	if comment.body.startswith("!markovchaincomment") and r.user.me().fullname not in {c.author.fullname for c in comment.replies.list()}:
		print("found comment! " + comment.body)
		b = comment.body.split()
		if len(b) < 2:
			print("no username specified")
			safe_reply(comment, "no username specified")
			continue
		main(comment, comment.body.split()[1])