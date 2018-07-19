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
	words = {False:{}} # add special start state
	discount_rate = 1
	for c in u.comments.new(): # default limit is 100
		comment_arr = c.body.split()
		if comment_arr[0] not in words[False]:  # update special start state
			words[False][comment_arr[0]] = 0
		words[False][comment_arr[0]] += discount_rate
		for i in range(len(comment_arr)): # add states (words) and transitions between states (adjacent words) to graph
			if comment_arr[i] not in words:
				words[comment_arr[i]] = {}
			if i < len(comment_arr) - 1:
				if comment_arr[i + 1] not in words[comment_arr[i]]:
					words[comment_arr[i]][comment_arr[i + 1]] = 0
				words[comment_arr[i]][comment_arr[i + 1]] += discount_rate
			else:
				if False not in words[comment_arr[i]]: # update special end state
					words[comment_arr[i]][False] = 0
				words[comment_arr[i]][False] += discount_rate
		discount_rate *= 0.98

	keys, vals = list(words[False].keys()), list(words[False].values())
	tot = sum([float(val) for val in vals])
	try:
		rep, curr_word, count = "", np.random.choice(keys, p=[float(val)/float(tot) for val in vals]), 0
	except ValueError as e:
		print("ValueError: " + str(e))
		safe_reply(comment, "That user appears to have no comments.")
		return
	while curr_word and count < 256: # generate markov chain, cap at 256 words
		rep += " " + curr_word
		try: # for some reason this is giving a KeyError: '0', so this is a temp fix
			keys, vals = list(words[curr_word].keys()), list(words[curr_word].values())
		except KeyError as e:
			print("missing key: " + str(e))
			safe_reply(comment, "Bot says: Oh no! Something went wrong!")
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
		print("added to backlog and sleeping for 9 minutes...")
		time.sleep(540)

for comment in r.subreddit("testcomsciftw").stream.comments():
	# print("comment: " + comment.body)
	while len(backlog) > 0:
		print("clearing out comment from backlog")
		comment, rep = backlog.pop(0)
		safe_reply(comment, rep, True)
	if comment.body.startswith("!markovchaincomment"):
		print("found comment! " + comment.body)
		comment.refresh()
		comment.replies.replace_more(limit=0)
		if r.user.me().fullname in {c.author.fullname for c in comment.replies.list()}:
			print("already replied to comment")
			continue
		b = comment.body.split()
		if len(b) < 2:
			print("no username specified")
			safe_reply(comment, "no username specified")
			continue
		main(comment, comment.body.split()[1])