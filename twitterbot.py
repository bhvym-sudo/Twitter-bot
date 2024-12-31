from playwright.sync_api import sync_playwright
from typing import Dict
import jmespath
import time

def scrape_tweet(url: str) -> dict:
    _xhr_calls = []

    def intercept_response(response):
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()


        page.on("response", intercept_response)

        page.goto(url)
        page.wait_for_selector("[data-testid='tweet']")


        tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]
        for xhr in tweet_calls:
            data = xhr.json()
            return data['data']['tweetResult']['result']

def parse_tweet(data: Dict) -> Dict:
    """Parse Twitter tweet JSON dataset for the most important fields"""
    result = jmespath.search(
        """{
        created_at: legacy.created_at,
        attached_urls: legacy.entities.urls[].expanded_url,
        attached_urls2: legacy.entities.url.urls[].expanded_url,
        attached_media: legacy.entities.media[].media_url_https,
        tagged_users: legacy.entities.user_mentions[].screen_name,
        tagged_hashtags: legacy.entities.hashtags[].text,
        favorite_count: legacy.favorite_count,
        bookmark_count: legacy.bookmark_count,
        quote_count: legacy.quote_count,
        reply_count: legacy.reply_count,
        retweet_count: legacy.retweet_count,
        quote_count: legacy.quote_count,
        text: legacy.full_text,
        is_quote: legacy.is_quote_status,
        is_retweet: legacy.retweeted,
        language: legacy.lang,
        user_id: legacy.user_id_str,
        id: legacy.id_str,
        conversation_id: legacy.conversation_id_str,
        source: source,
        views: views.count
    }""",
        data,
    )
    result["poll"] = {}
    poll_data = jmespath.search("card.legacy.binding_values", data) or []
    for poll_entry in poll_data:
        key, value = poll_entry["key"], poll_entry["value"]
        if "choice" in key:
            result["poll"][key] = value["string_value"]
        elif "end_datetime" in key:
            result["poll"]["end"] = value["string_value"]
        elif "last_updated_datetime" in key:
            result["poll"]["updated"] = value["string_value"]
        elif "counts_are_final" in key:
            result["poll"]["ended"] = value["boolean_value"]
        elif "duration_minutes" in key:
            result["poll"]["duration"] = value["string_value"]
    user_data = jmespath.search("core.user_results.result", data)
    name = jmespath.search("legacy.name", user_data)
    followers_count = jmespath.search("legacy.followers_count", user_data)
    favourites_count = jmespath.search("legacy.favourites_count", user_data)
    profile_image_url = jmespath.search("legacy.profile_image_url_https", user_data)
    description = jmespath.search("legacy.description", user_data)
    verified = jmespath.search("legacy.verified", user_data)
    screen_name = jmespath.search("legacy.screen_name", user_data)
    location = jmespath.search("legacy.location", user_data)

    created = result['created_at']
    attachedurls = result['attached_urls']
    attachedmed = result['attached_media']
    taggedusers = result['tagged_users']
    taggedtags = result['tagged_hashtags']
    favcount = result['favorite_count']
    bookcount = result['bookmark_count']
    quotecount = result['quote_count']
    repcount = result['reply_count']
    retweetcount = result['retweet_count']
    text = result['text']
    isquote = result['is_quote']
    isretweet = result['is_retweet']

    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    
    log_message = f"\n{current_time}\n\n"


    log_message += f"Name: {name}\n"
    log_message += f"Followers Count: {followers_count}\n"
    log_message += f"Favourites Count: {favourites_count}\n"
    log_message += f"Profile Image URL: {profile_image_url}\n"
    log_message += f"Description: {description}\n"
    log_message += f"Verified: {verified}\n"
    log_message += f"Screen Name: {screen_name}\n"
    log_message += f"Location: {location}\n\n"


    log_message += f"Created At: {created}\n"
    log_message += f"Attached URLs: {attachedurls}\n"
    log_message += f"Attached Media: {attachedmed}\n"
    log_message += f"Tagged Users: {taggedusers}\n"
    log_message += f"Tagged Hashtags: {taggedtags}\n"
    log_message += f"Favorite Count: {favcount}\n"
    log_message += f"Bookmark Count: {bookcount}\n"
    log_message += f"Quote Count: {quotecount}\n"
    log_message += f"Reply Count: {repcount}\n"
    log_message += f"Retweet Count: {retweetcount}\n"
    log_message += f"Text: {text}\n"
    log_message += f"Is Quote: {isquote}\n"
    log_message += f"Is Retweet: {isretweet}\n\n"

    log_message += "-----------------------------------------------------------------------------------\n"
    log_message += "-----------------------------------------------------------------------------------\n"
    log_message+= "\n"
    log_message += "\n"



    with open('log.txt', 'a', encoding='utf-8') as file:
        file.write(log_message)

    return log_message