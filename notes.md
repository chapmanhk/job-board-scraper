## Problem
SerpAPI has limits. Do I want to rely on it long term?

## Option 1: Keep using SerpAPI
- ✅ Easy to set up
- ✅ Works well for known roles
- ❌ 100/month limit
It's difficult to keep things recent/updated on a daily basis when I'll need to use multiple searches. SerpAPI searching through google doesn't use boolean logic as nicely as I'm used to. More complicated OR and AND terms limits what gets outputed, instead of simple ones like "data analyst".

## Option 2: Scrape Lever directly
- ✅ Unlimited
- ✅ More control
- ❌ Need list of companies
More reliable long term, and have a solid structure that doesn't rely on google searching. Could still use googling to try and find companies using lever/greenhouse.
Might run into scraping issues, but would still be scraping directly from the site either way.

## Proposal
Use SerpAPI for discovering companies that have associated postings on lever/glassdoor.
Then, scrape those company boards directly.

## Next steps
Creating a separate script that discovers companies, organizing files and folders