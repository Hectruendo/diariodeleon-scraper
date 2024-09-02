# Scraper for Diario de Leon

Simple scraper for Diario de Leon. It scrapes sitemap and saves them in a JSON file.

## Installation

Set up the virtual environment and install the requirements with Poetry:

```bash
poetry install
```

## Usage

Run the scraper with the following command:

```bash
scrapy crawl diariodeleon
```

__Cache__: It is using the HttpCacheMiddleware to cache the requestss therefore if you stop the scraper it would not be a big deal: the next time you run it, it will scrape all the previously scraped results very quickly because they will be stored in the cache avoiding making requests to diariodeleon.com

__Policy__: It is using a very polite scraping policy, you dont have to worry about being blocked.

__Proxies__: In case of desiring to use proxies, you can set them in the __settings.py__ file inside the ROTATING_PROXY_LIST variable.

## Results

The results are saved in a JSON file inside the __/results__ directory.