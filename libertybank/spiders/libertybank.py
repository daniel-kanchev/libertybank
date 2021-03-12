import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from libertybank.items import Article


class LibertybankSpider(scrapy.Spider):
    name = 'libertybank'
    start_urls = ['https://www.libertybank.ge/en/chven-shesakheb/kompaniis-shesakheb/siakhleebi-da-pres-relizebi']

    def parse(self, response):
        links = response.xpath('//div[@class="col-md-4 col-sm-6 col-xs-12"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="item next"]/@href').get()
        if next_page and 'javascript' not in next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()
        else:
            return

        date = response.xpath('//span[@class="date medium"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="pagetext fullwidth"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
