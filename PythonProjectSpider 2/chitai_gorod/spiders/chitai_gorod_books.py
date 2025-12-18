import re

import scrapy
from scrapy.spiders import SitemapSpider

from chitai_gorod.items import BookItem


class ChitaiGorodBooksSpider(SitemapSpider):
    name = "chitai_gorod_books"
    allowed_domains = ["www.chitai-gorod.ru", "chitai-gorod.ru"]

    sitemap_urls = ["https://www.chitai-gorod.ru/sitemap.xml"]

    sitemap_rules = [
        (r"/product/", "parse_book"),
    ]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1.0,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "AUTOTHROTTLE_ENABLED": True,
    }

    def parse_book(self, response: scrapy.http.Response):
        item = BookItem()
        item["title"] = response.xpath("//h1/text()").get(default="").strip()

        item["author"] = response.xpath(
            "//a[contains(@href, '/author/')][1]/text()"
        ).get(default=None)

        description_parts = response.xpath(
            "//h2[contains(., 'Описание и характеристики')]/following-sibling::*[1]//text()"
        ).getall()
        description = " ".join([t.strip() for t in description_parts if t.strip()])
        item["description"] = description or None

        price_raw = response.xpath(
            "//meta[@itemprop='price']/@content | //span[@itemprop='price']/@content"
        ).get()
        if price_raw:
            digits = re.findall(r"\d+", price_raw.replace("\xa0", ""))
            item["price_amount"] = int("".join(digits)) if digits else None
        else:
            text_price = response.xpath(
                "//*[contains(text(), '₽') or contains(text(),'руб')][1]/text()"
            ).get()
            if text_price:
                digits = re.findall(r"\d+", text_price.replace("\xa0", ""))
                item["price_amount"] = int("".join(digits)) if digits else None
            else:
                item["price_amount"] = None

        item["price_currency"] = response.xpath(
            "//meta[@itemprop='priceCurrency']/@content"
        ).get() or "RUB"

        rating_text = response.xpath(
            "//*[contains(text(), 'оценк') or contains(text(),'оценок')]/text()"
        ).getall()
        rating_text = " ".join(rating_text)

        rating_value = response.xpath(
            "//meta[@itemprop='ratingValue']/@content"
        ).get()
        if not rating_value:
            rating_value = response.xpath(
                "//*[contains(text(), 'оценк')]/preceding::text()[1]"
            ).get()
        if rating_value:
            try:
                item["rating_value"] = float(
                    re.findall(r"\d+(?:[.,]\d+)?", rating_value.replace(",", "."))[0]
                )
            except (IndexError, ValueError):
                item["rating_value"] = None
        else:
            item["rating_value"] = None

        rating_count_match = re.search(r"(\d+)\s+оцен", rating_text)
        item["rating_count"] = (
            int(rating_count_match.group(1)) if rating_count_match else None
        )

        chars_block = response.xpath(
            "//*[contains(., 'Описание и характеристики')]/following::*"
        )

        def extract_first_int(xpath_expr: str):
            text = chars_block.xpath(xpath_expr).getall()
            text = " ".join(text)
            m = re.search(r"\d+", text)
            return int(m.group(0)) if m else None

        year_text = chars_block.xpath(
            ".//*[contains(., 'Год издания')]/text()"
        ).getall()
        year_text = " ".join(year_text)
        year_match = re.search(r"(19|20)\d{2}", year_text)
        item["publication_year"] = (
            int(year_match.group(0)) if year_match else None
        )

        isbn_text = chars_block.xpath(
            ".//*[contains(., 'ISBN')]/text()"
        ).getall()
        isbn_text = " ".join(isbn_text)
        isbn_match = re.search(r"[\d\-Xx]+", isbn_text)
        item["isbn"] = isbn_match.group(0) if isbn_match else None

        item["pages_cnt"] = extract_first_int(
            ".//*[contains(., 'Количество страниц')]/text()"
        )
        item["publisher"] = chars_block.xpath(
            ".//*[contains(., 'Издательство')]/a/text() | "
            ".//*[contains(., 'Издательство')]/following::a[1]/text()"
        ).get()

        item["book_cover"] = response.xpath(
            "(//img[contains(@src, '/product/') or contains(@class,'product')])[1]/@src"
        ).get()

        item["source_url"] = response.url

        yield item
