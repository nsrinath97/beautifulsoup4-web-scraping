import requests
from bs4 import BeautifulSoup
import time
import pandas as pd


def get_subreddit_page(reddit_url):
    """Get an html snapshot of a page for any subreddit"""

    # Required to scrape Reddit as it mimics a browser visit
    headers = {'User-Agent': 'data-science-project'}

    # Use requests to grab a snapshot of the webpage
    response = requests.get(reddit_url, headers=headers)

    # Check if download was sucessful
    if not 200 <= response.status_code <= 299:
        raise Exception('Unable to download page {}'.format(reddit_url))

    # Get the HTML
    page_contents = response.text

    return page_contents


def get_bs4_doc(page_contents):
    """Get a BeautifulSoup document from an html snapshot of a page"""

    # Create a local copy of the html of the page
    with open('subreddit.html', 'w', encoding="utf-8") as f:
        f.write(page_contents)

    # Read the local copy
    with open('subreddit.html', 'r', encoding='utf-8') as f:
        html_source = f.read()

    # Create a Beautiful Soup document from the local copy of the html page
    bs4_doc = BeautifulSoup(html_source, 'html.parser')

    return bs4_doc


def get_posts(doc):
    """Parse the HTML document to get tags for the first 25 posts"""

    # All post classes begin with 'thing'
    div_tags = doc.find_all('div', class_='thing')

    # Return a list of posts
    return [post for post in div_tags]


def get_post_info(post):
    """Get information about an individual post in a subreddit"""

    # The post title
    title = post.find('p', class_="title").text.strip()

    # The username of the poster; if the account is deleted, the username shows up as [Deleted]
    try:
        username = post.find('a', class_='author').text
    except AttributeError:  # A deleted username throws up an attribute error as the 'a' tag doesn't exist in the html
        username = '[Deleted]'

    # The date that the post was submitted
    date = post.find('time', class_='live-timestamp')['title']

    # Number of comments on the post
    comments = post.find('a', class_='comments').text.split()[
        0]  # shows up as a list e.g. [10 comments], so I split to get the number
    if comments == 'comment':  # comments will equal 'comment' if there are 0 comments
        comments = 0  # therefore I am replacing it with 0 if that is the case

    # Number of upvotes on the post
    upvotes = post.find('div', class_='score unvoted')['title']

    # The link to the post
    link = post.find('a', class_='comments')['href']

    # A dictionary containing the post info scraped above
    post_info = {
        "Title": title,
        "Username": username,
        "Date": date,
        "Comments": comments,
        "Upvotes": upvotes,
        "Link": link}
    return post_info


def scrape_subreddit(reddit_url):
    """Scrape the top posts of a subreddit and return a list of dictionaries containg post info
    ready to be written to a CSV file"""

    # Start the counter for posts
    post_number = 1

    # Get the first page
    subreddit_html = get_subreddit_page(reddit_url)
    subreddit_page = get_bs4_doc(subreddit_html)

    # The list that all of the post info will be stored in and later written to csv
    post_info_list = []

    while post_number <= 100:  # Maximum of 100 posts

        # Get the first page of top posts
        top_sub_posts = get_posts(subreddit_page)

        # Get the info for each post in the page and append it to the list
        # Increment the post counter
        for post in top_sub_posts:
            post_info_list.append(get_post_info(post))
            post_number += 1

        # Find the button to go to the next page
        next_page_button = subreddit_page.find('span', class_='next-button')

        # Grab the link for the next page attached to the button href tag
        next_page_link = next_page_button.find('a').attrs['href']
        time.sleep(2)
        subreddit_html = get_subreddit_page(next_page_link)
        subreddit_page = get_bs4_doc(subreddit_html)
    top_100_posts_df = pd.DataFrame(post_info_list)
    return top_100_posts_df


top_100_posts = scrape_subreddit('https://old.reddit.com/r/gaming/top/?t=all')
top_100_posts.to_csv('Top 100 posts in a subreddit.csv', sep='|')
pd.set_option('display.max_rows', 100)

