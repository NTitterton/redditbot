def lambda_handler(event, context):
	import praw, random, boto3
	r = praw.Reddit(client_id="UslSnVNZH56Pzg", client_secret="y7RlHeFaF5vTmRvAV4_qkylPv5c", username="markovchaincomment", password="PLACEHOLDER", user_agent="Creates markov chains based on recent comments by a user. Created by /u/comsciftw")

	sqs = boto3.resource("sqs")
	queue = sqs.create_queue(QueueName="comments", Attributes={'DelaySeconds': '5'})
	
	def safe_reply(comment, rep):
		try:
			comment.reply(rep)
			return "Replied to " + str(comment.id) + " with: " + rep
		except praw.exceptions.APIException:
			queue.send_message(MessageBody=comment.id, MessageAttributes={"reply":{"StringValue":rep,"DataType":"String"}}, DelaySeconds=540)
			return "Reply to " + str(comment.id) + " failed. Node added back to queue with 9 minute delay."
		except Exception:
			return "The bot appears to be banned."
	
	try:
		comment = r.comment(event["Records"][0]["body"])
	except:
		print("Comment ID " + str(comment.id) + " not valid.")
		return

	if "messageAttributes" in event["Records"][0] and "reply" in event["Records"][0]["messageAttributes"]:
		rep = event["Records"][0]["messageAttributes"]["reply"]["stringValue"]
		print(safe_reply(comment, rep))
		return

	try:
		u = r.redditor(comment.body.split()[1])
	except:
		print(safe_reply(comment, comment.body.split()[1] + " does not exist."))
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
	try:
		rep, curr_word, count = "", random.choices(keys, weights=vals)[0], 0
	except ValueError:
		print(safe_reply(comment, "That user appears to have no comments."))
		return
	while curr_word and count < 256: # generate markov chain, cap at 256 words
		rep += " " + curr_word
		try: # for some reason this is giving a KeyError: '0', so this is a temp fix
			keys, vals = list(words[curr_word].keys()), list(words[curr_word].values())
		except KeyError:
			print(safe_reply(comment, "Bot says: Oh no! Something went wrong!"))
			return
		curr_word = random.choices(keys, weights=vals)[0]
		count += 1

	print(safe_reply(comment, rep))