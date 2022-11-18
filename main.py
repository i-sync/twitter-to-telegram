import re
import time, random
import urllib

import tweepy
import telegram
from telegram import InputMediaPhoto, InputMediaVideo
from config import configs
from models import Twitter, Media


#send telegram message
bot = telegram.Bot(configs.telegram.token)
# bot.send_message(chat_id=group["id"], text= msg)

def main():

    # https://developer.twitter.com/zh-cn/docs/authentication/oauth-2-0/bearer-tokens
    #   curl -u 'key:secret' \
    #   --data 'grant_type=client_credentials' \
    #   'https://api.twitter.com/oauth2/token'
    client = tweepy.Client(bearer_token=configs.twitter.bearer_token)
    #tgtm = client.get_user(username="jamella_hoshino")
    # tweets = client.get_users_tweets(id=1500639956737597442)
    #https://gist.github.com/edsu/54e6f7d63df3866a87a15aed17b51eaf

    for username in configs.users:
        u = client.get_user(username=username)
        print(u)
        if not u.data:
            continue
        tweets = client.get_users_tweets(u.data.id)
        print(tweets)
        if not tweets.data:
            continue
        # print(type(tweets.data))
        for t in tweets.data:
            tmp = Twitter.get_or_none(Twitter.tw_id == t.id)

            if tmp:
                print(f"tweet exists, id: {t.id}")
                continue
            # print(tweet.id, tweet.text)
            tweet = client.get_tweet(id = t.id, expansions="attachments.media_keys", tweet_fields=["author_id"], media_fields=["url", "preview_image_url", "variants"])
            print(tweet)

            twitter = Twitter.create(tw_id = tweet.data.id, text=tweet.data.text, user_name="jamella_hoshino")

            print(twitter)
            medias = []
            if "media" in tweet.includes:
                for media in tweet.includes["media"]:
                    media_url = None
                    if media.type == "video" and hasattr(media, "variants"):
                        media_url = next(x["url"] for x in media.variants[::-1] if "content_type" in x and x["content_type"] == "video/mp4")
                    media_model = {
                        "media_id": media.media_key,
                        "media_type": media.type,
                        "media_url": media_url if media_url else media.url,
                        "preview_url": media.preview_image_url if media.preview_image_url else "",
                        "twitter": twitter
                    }

                    try:
                        tmp = Media.get(Media.media_id == media.media_key)
                        print("Got duplicated media_key on this tweet:")
                    except Media.DoesNotExist:
                        medias.append(media_model)

            if medias:
                Media.insert_many(medias).execute()

            # text = re.sub("https://t.co/\w{10}", "", tweet.data.text)
            text = tweet.data.text

            if medias:
                photos = [InputMediaPhoto(media=x["media_url"], caption=text) if x["media_type"] =="photo" else InputMediaVideo(media=x["media_url"], caption=text) for x in medias]
                bot.send_media_group(chat_id=configs.telegram.chat.id, media=photos)
            else:
                bot.send_message(chat_id=configs.telegram.chat.id, text=text)

            print("================")

        # sleep 30 second for each user.
        time.sleep(30)


if __name__ == "__main__":
    main()