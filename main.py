import numpy as np

from scraper import scrape_posts_comments
from process_comments import process_comments


def get_inputs():
    post_url = input("Enter the post's url: ")
    pos_keywords = input("Enter positive keywords separated by semicolon (ex. good;great;love;live;fine): ").split(';')
    neg_keywords = input("Enter negative keywords separated by semicolon (ex. bad;fuck;prison;kill): ").split(';')

    return post_url, pos_keywords, neg_keywords


def main(post_url=None, pos_keywords=None, neg_keywords=None):
    if post_url is None or pos_keywords is None or neg_keywords is None:
        post_url, pos_keywords, neg_keywords = get_inputs()

    comments = scrape_posts_comments(post_url)
    compound_sentiment, num_pos_sentiment, num_neg_sentiment, \
    pos_keywords_counter, neg_keywords_counter, pos_comments, neg_comments = process_comments(comments, pos_keywords,
                                                                                              neg_keywords)

    compound_sentiment_h = 'Negative' if compound_sentiment < 0 else 'Positive' if compound_sentiment > 0 else 'Neutral'
    compound_sentiment_certainty = 50 + np.absolute(compound_sentiment) * 50

    print(
        f'\n\n\nNumber of positive comments: {num_pos_sentiment},\nNumber of negative comments: {num_neg_sentiment},\nCompound sentiment: {compound_sentiment_h} with {compound_sentiment_certainty:.1f}% certainty')

    print("################## Positive comments ##################\n")
    for pos_comment in pos_comments:
        print(pos_comment, end='\n\n')

    print("\n\n################## Negative comments ##################\n")
    for neg_comment in neg_comments:
        print(neg_comment, end='\n\n')

    return num_pos_sentiment, num_neg_sentiment, pos_keywords_counter, neg_keywords_counter


if __name__ == '__main__':
    main()
