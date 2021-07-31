import random
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException, TimeoutException,
    ElementClickInterceptedException,
)

from utils import set_viewport_size, get_random_user_agent


def scrape_posts_comments(post_url):
    chromedriver_path = './chromedriver'

    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument("start-maximized")

    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })
    # options.add_argument('--headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("--user-data-dir=Profile")

    user_agent = get_random_user_agent(min_version=86)

    options.add_argument('--user-agent=%s' % user_agent)

    driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    set_viewport_size(driver, 1920, 1080)

    ############# SCRAPING THE POST #############
    print('############# Post scraping started #############')
    driver.get(url=post_url)
    wait = WebDriverWait(driver, 5)

    # Stop video playing
    if driver.current_url.startswith('https://www.facebook.com/watch/?v'):
        driver.find_element_by_css_selector('.i09qtzwb.rq0escxv.n7fi1qx3.pmk7jnqg.j9ispegn.kr520xx4.nhd2j8a9').click()

    # Open comments section when the post is a video
    if driver.current_url.startswith('https://www.facebook.com/facebook/videos/'):
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.gmql0nx0 .jq4qci2q.m9osqain'))).click()
        view_more_comments_selector = '.dhix69tm .fv0vnmcu .m9osqain'
    elif driver.current_url.startswith('https://www.facebook.com/watch/'):
        view_more_comments_selector = '.hpfvmrgz .a3bd9o3v.m9osqain'
    else:
        view_more_comments_selector = '.fv0vnmcu .m9osqain'

    counter = 1
    try:
        view_more_comments_btn = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, view_more_comments_selector)))
        while True:
            if 'view' in view_more_comments_btn.text.lower() and 'comment' in view_more_comments_btn.text.lower():
                try:
                    driver.execute_script("arguments[0].scrollIntoView(); window.scrollTo(0, window.scrollY - 200);",
                                          view_more_comments_btn)
                    view_more_comments_btn.click()
                    print(counter, '- view more comments')
                    counter += 1
                    sleep(random.random() + 0.5)
                    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, view_more_comments_selector)))
                    view_more_comments_btn = driver.find_element_by_css_selector(view_more_comments_selector)
                    if not (
                            'view' in view_more_comments_btn.text.lower() and 'comment' in view_more_comments_btn.text.lower()):
                        raise TimeoutException
                except ElementClickInterceptedException:
                    page_height = driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight); return document.body.scrollHeight;")
            else:
                raise TimeoutException
    except (StaleElementReferenceException, TimeoutException) as e:
        print('Comments are fully expanded')

    # Expand all the replies
    tags_to_text = lambda tags: list(map(lambda tag: tag.text, tags))
    counter = 1

    if driver.current_url.startswith('https://www.facebook.com/watch/'):
        reply_btns_selector = '.hpfvmrgz .a3bd9o3v.m9osqain'
    else:
        reply_btns_selector = '.mtfd0dr2 , .fv0vnmcu .m9osqain'

    while True:
        is_reply_expanded = False
        reply_btns = driver.find_elements_by_css_selector(reply_btns_selector)
        for reply_btn in reply_btns:
            try:
                if 'repl' in reply_btn.text.lower() and not (
                        'hide' in reply_btn.text.lower() or 'write' in reply_btn.text.lower()):
                    driver.execute_script("arguments[0].scrollIntoView(); window.scrollTo(0, window.scrollY - 240);",
                                          reply_btn)
                    sleep(random.random() + 0.5)
                    reply_btn.click()
                    print(counter, '- show replies')
                    counter += 1
                    sleep(random.random() + 0.5)
                    is_reply_expanded = True
                    continue
            except (StaleElementReferenceException, ElementClickInterceptedException) as e:
                print(e)
        if not is_reply_expanded:
            print('Replies are fully expanded')
            break

    # Show more all the comments
    if driver.current_url.startswith('https://www.facebook.com/watch/'):
        show_more_btns_selector = '.hcukyx3x .oo9gr5id.gpro0wi8'
    else:
        show_more_btns_selector = 'div.lrazzd5p'

    show_more_btns = driver.find_elements_by_css_selector(show_more_btns_selector)
    counter = 1

    for show_more_btn in show_more_btns:
        try:
            if 'See More' == show_more_btn.text:
                driver.execute_script("arguments[0].scrollIntoView(); window.scrollTo(0, window.scrollY - 200);",
                                      show_more_btn)

                sleep(random.random() + 0.5)
                show_more_btn.click()
                print(counter, '- expand long comment')
                counter += 1
                sleep(random.random() + 0.5)
        except (StaleElementReferenceException, ElementClickInterceptedException) as e:
            pass
    else:
        print('Long comments are fully expanded')

    # Scraping the comments
    comments_selector = '.hcukyx3x.c1et5uql div'
    raw_comments = tags_to_text(driver.find_elements_by_css_selector(comments_selector))

    # Remove post text if when it's captured
    if driver.current_url.startswith('https://www.facebook.com/watch/') or driver.current_url.startswith(
            'https://www.facebook.com/facebook/videos/'):
        raw_comments = raw_comments[1:]

    names_comments_selector = '.gpro0wi8 .nc684nl6 span'
    names_comments = set(tags_to_text(driver.find_elements_by_css_selector(names_comments_selector)))

    names_comments_filt = []
    for names_comment in names_comments:
        if len(names_comment.split()) >= 2:
            names_comments_filt.append(names_comment)

    comments = []
    for raw_comment in raw_comments:
        if raw_comment not in names_comments:
            comments.append(raw_comment)

    print(f'{len(comments)} comments and {len(names_comments_filt)} profile links scraped')
    return comments
