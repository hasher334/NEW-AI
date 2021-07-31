import random

import pandas as pd


def set_viewport_size(driver, width, height):
    window_size = driver.execute_script("""
        return [window.outerWidth - window.innerWidth + arguments[0],
          window.outerHeight - window.innerHeight + arguments[1]];
        """, width, height)
    driver.set_window_size(*window_size)


def get_random_user_agent(min_version=0):
    user_agents_df = pd.read_csv('user_agents.csv')
    user_agents_df = user_agents_df.drop_duplicates(subset='user_agent')

    user_agents_df['version'] = pd.to_numeric(user_agents_df['version'])
    user_agents_df = user_agents_df[user_agents_df['version'] >= min_version]

    return random.choice(user_agents_df['user_agent'].tolist())
