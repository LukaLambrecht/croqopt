# Colruyt product scraper

### How to use
Run `python3 scrape_colruyt.py -h` for a list of options.

Before running, you will need to create a file name `urls_private.py`, which holds the following content:
```
XCG_API_KEY = "<your x-cg api key>"
USER_AGENT = "<your user agent (just google 'my user agent')>"
```

### Status
Has worked on some small examples, but at some point it seem to have been blocked by Colruyt's anti-bot mechanisms... Not sure how to proceed.

### References
Based on the following examples:
- [colruyt-scraper](https://github.com/SimonGulix/colruyt_scraper/tree/main)
- [colruyt-product-scraper](https://github.com/BelgianNoise/colruyt-products-scraper/tree/main)
