import praw

reddit = praw.Reddit(client_id='iW3F2X0p_3e9ag',
                     client_secret='ciLt6KkvKawJYzLG5wWQTzADMq0',
                     user_agent='Cloud Computing Project (catappstrophe) by sgalang3')

print(reddit.read_only)  # Output: False

for submission in reddit.subreddit('aww').new(limit=10):
    print(submission.title.encode('utf-8'))
    #print(submission.permalink) link to the page
    #print(submission.created_utc) time created
    print(submission.url) # if subdomain is https://i.redd.it/, then is a pullable image
