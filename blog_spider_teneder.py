import os
import re
import scrapy
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim


class BlogSpider(scrapy.Spider):
    count = 0
    name = 'blogspider'
    geolocator = Nominatim(user_agent="el-tenedor")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    start_urls = ['https://www.eltenedor.es/search/?cityId=328022']


    def get_lat_lng(self, address):
        try:
            location = self.geocode(address)
            return location.latitude, location.longitude, address.split(',')[-2]
        except Exception as e:
            return 0, 0, 0

    def parse(self, response):
        # Aqui scrapeamos los datos y los imprimimos a un fichero
        for restaurant in response.css('div.card div.css-lyxfhu'):

            address = re.sub(r"\n[ ]+", " ", restaurant.css('div.content div.css-1tzarfj p.css-1r9v7b9 ::text').extract_first().strip())
            ratings = restaurant.css('div.content div.css-8u6uxj span.css-17f8ytt span ::text').get(default=0)

            # Print a un fichero
            if (ratings != 0):
                latitude, longitude, postal_code = self.get_lat_lng(address)
                try:
                    title = restaurant.css('div.content div.css-1tzarfj div.css-m4cdiw h2 a ::text').extract_first().strip()
                    print(f"RETURN {title} from page {self.count}")
                    yield {
                        'title':  title,
                        'address': address,
                        'postal_code': postal_code,
                        'latitude': latitude,
                        'longitude': longitude,
                        'tags': ', '.join([it.strip() for it in restaurant.css('div.content div.css-1r59wqd p span ::text').extract() if it.strip() and '.css' not in it]),
                        'reviews': restaurant.css('div.content div.css-8u6uxj span.css-1b3lju4 span ::text').get(default=0).strip(),
                        'ratings': ratings,
                        'price': restaurant.css('div.content p.css-yodg87 span ::text')[1].get().replace(u'\xa0', u' ')
                    }
                except Exception as e:
                    print('------------EXCEPTION---------------')
                    print(e)
                    yield {}

        # Aqui hacemos crawling (con el follow)
        next_page_url = response.css('nav._1hQ59 ul li a ::attr(href)')[-1].get()
        if next_page_url is not None and self.count <= int(os.getenv('MAX_PAGES', 0)):
            self.count += 1
            yield response.follow(url=next_page_url, callback=self.parse)
