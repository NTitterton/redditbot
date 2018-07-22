import praw, time, boto3, numpy as np

sqs = boto3.resource("sqs")
queue = sqs.create_queue(QueueName="comments", Attributes={'DelaySeconds': '5'})

def start(r):
	try:
		for comment in r.subreddit("testcomsciftw").stream.comments():
			if comment.body.startswith("!markovchaincomment"):
				print("found comment! " + comment.body)
				comment.refresh()
				comment.replies.replace_more(limit=0)
				if r.user.me().fullname in {c.author.fullname for c in comment.replies.list()}:
					print("already replied to comment")
					continue
				b = comment.body.split() # you can do this part more efficiently but it's cleaner this way
				if len(b) < 2:
					print("No username specified. Queueing...")
					queue.send_message(MessageBody=comment.id, MessageAttributes={"reply":{"StringValue":"no username specified","DataType":"String"}})
					continue
				print("Queueing...")
				queue.send_message(MessageBody=comment.id)
	except Exception as e: # should be more specific but the docs' prawcore.OAuthException doesn't work
		print(e)
		r = praw.Reddit(client_id="UslSnVNZH56Pzg", client_secret="y7RlHeFaF5vTmRvAV4_qkylPv5c", username="markovchaincomment", password="Important@123!", user_agent="Creates markov chains based on recent comments by a user. Created by /u/comsciftw")
		start(r)

r = praw.Reddit(client_id="UslSnVNZH56Pzg", client_secret="y7RlHeFaF5vTmRvAV4_qkylPv5c", username="markovchaincomment", password="Important@123!", user_agent="Creates markov chains based on recent comments by a user. Created by /u/comsciftw")
start(r)