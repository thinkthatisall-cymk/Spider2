import scrapy


class BookItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    description = scrapy.Field()
    price_amount = scrapy.Field()
    price_currency = scrapy.Field()
    rating_value = scrapy.Field()
    rating_count = scrapy.Field()
    publication_year = scrapy.Field()
    isbn = scrapy.Field()
    pages_cnt = scrapy.Field()
    publisher = scrapy.Field()
    book_cover = scrapy.Field()
    source_url = scrapy.Field()
