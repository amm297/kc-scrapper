import os

import scrapy
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim


class BlogSpider(scrapy.Spider):
    count = os.getenv('START_PAGE', 0)
    name = 'blogspider'
    geolocator = Nominatim(user_agent="el-tenedor")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    start_urls = ['https://www.eltenedor.es/search/?cityId=328022']

    def get_lat_lng(self, address):
        try:
            location = self.geocode(address)
            return location.latitude, location.longitude, 0
        except Exception as e:
            return 0, 0, 0

    def parse_restuaurant(self, response):
        try:
            print('------------RESTAURANT----------')
            title_block = response.css('div._2EkA4 div._1x8V- div._3Vhpd')
            type_tags = [it for it in title_block.xpath('//div[@data-test="restaurant-page-restaurant-tags"]').css(
                "p span ::text").extract() if '.css' not in it]
            resturant_type = type_tags[-2] if len(type_tags) >= 2 else type_tags[0]
            title = title_block.css('div._2r661 h1 ::text').extract_first().strip()
            rating = title_block.css('div._2r661 div._3eEzZ span span ::text').extract_first()
            rating = rating.strip() if rating else '0'
            reviews = title_block.css('div._2r661 div._3eEzZ div ::text').extract_first()
            reviews = reviews.strip().split(' ')[0] if reviews else '0'
            address = title_block.css('div a.n3G0C span ::text').extract_first().strip().replace(';', ',')
            latitude, longitude, postal_code = self.get_lat_lng(address)
            price = \
                title_block.css('div p.css-1af5316 ::text').extract_first().strip().replace(u'\xa0', u' ').split(' ')[
                    -2]

            details_block = response.css('div._2kPlw div._3YHBo')
            description = ''.join([it for it in details_block.xpath(
                '//div[@name="insiderSection"]/div/div[@class="_2-dPr"]/div/div/p/text()').extract() if it])
            tags = ', '.join([it for it in details_block.xpath(
                '//div[@name="infoSection"]/div/div/h2[contains(span, "Caract")]/following-sibling::p[1]/span').css(
                'a ::text').extract() if it])

            yield {
                'title': title,
                'type': resturant_type,
                'rating': rating,
                'reviews': reviews,
                'address': address,
                'latitude': latitude,
                'longitude': longitude,
                'postal_code': postal_code,
                'price': price,
                'description': description,
                'tags': tags
            }
        except Exception as e:
            yield {
                'error': e,
                'url': response.request.url
            }

    def parse(self, response):
        # Aqui scrapeamos los datos y los imprimimos a un fichero
        for restaurant in response.css('div.card div.css-lyxfhu'):
            follow_url = restaurant.css(
                'div.content div.css-1tzarfj div.css-m4cdiw h2 a ::attr(href)').extract_first().strip()
            yield response.follow(url=follow_url, callback=self.parse_restuaurant)

        # Aqui hacemos crawling (con el follow)
        next_page_url = response.css('nav._1hQ59 ul li a ::attr(href)')[-1].get()
        if next_page_url is not None:
            self.count += 1
            print(f'-----------Request next page {self.count} {next_page_url}------------')
            yield response.follow(url=next_page_url, callback=self.parse)
