# MAL_predictor
Scrapes MAL(MyAnimeList) profiles, predicts shows for user based on their scores, and creates network visualizations for a set of shows.


# Workflow:

1. PageScrape -> scrapes information for a single show. Used as the basis for other components.
2. UserScraper -> scrapes all the shows from a user's profile. (Prereq: 1)
3. MAL_Scraper -> scrapes a lot of shows off the website. (Prereq: 1)
4. MAL_Predictor -> given a show or set of shows, predicts what the user would rate it based on the user's current shows and scores. (Prereq: 2, 3)
5. MAL_Network -> NetworkX and other Python libraries used to make visualizations for similarity between shows (Prereq: 2?, 3)
