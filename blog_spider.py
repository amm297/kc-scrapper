import json

import scrapy


# DOWNLOAD_DELAY = 2

# key = "AIzaSyAiJC7FXGcrQwS7_25H8oBMQk5G9zFGDiU"
# URL = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}"

class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.civitatis.com/es/madrid/']
    base_path = 'https://www.civitatis.com{}'
    count

    def parse_activity(self, response):
        lat_lng = response.css('div.o-activity-meeting-point div.m-map ::attr(data-markers)').extract_first()
        response.meta.get('category')
        if 'traslados' in response.url:
            print('caca')
        try:
            yield {
                'link': response.url,
                'meeting_point': response.css('div.o-activity-meeting-point p ::text').extract_first(),
                'latitude': json.loads(lat_lng)[0].get('lat') if lat_lng else 0,
                'longitude': json.loads(lat_lng)[0].get('lng') if lat_lng else 0,
                'image': response.meta.get('image'),
                'title': response.meta.get('title'),
                'rating': response.meta.get('rating'),
                'reviews': response.meta.get('reviews'),
                'description': response.meta.get('description'),
                'time': response.meta.get('time'),
                'language': response.meta.get('language'),
                'cancellation': response.meta.get('cancellation'),
                'price': response.meta.get('price')
            }
        except Exception as e:
            print(e)

    def parse(self, response):
        # sel = scrapy.Selector(response)
        for item in response.css('div.o-search-list__item'):
            link = self.base_path.format(item.css('a._activity-link ::attr(href)').extract_first())

            if link:
                req = scrapy.Request(link, callback=self.parse_activity)
                req.meta['image'] = item.css(
                    'div.comfort-card__img img ::attr(src)').extract_first(
                    default='')  # Pending obtiene el base no la url
                content = item.css('div.comfort-card__content')
                req.meta['title'] = content.css('div.__left h3 ::text').extract_first(default='').strip()
                req.meta['rating'] = content.css('div.m-rating span ::text').extract_first(default='')
                req.meta['reviews'] = \
                    content.css('div.m-rating span.text--rating-total ::text').extract_first(default='').split(' ')[0]
                req.meta['description'] = ' '.join(
                    content.css('div.__center div.comfort-card__text ::text').extract()).strip().replace(';', ',')

                extra_info = content.css('div.__right div.comfort-card__extra-info')
                req.meta['time'] = extra_info.css(
                    'div.comfort-card__extra-info span._duration ::text').extract_first(default='').strip()
                req.meta['language'] = extra_info.css(
                    'div.comfort-card__extra-info span._lang ::text').extract_first(default='').strip()
                req.meta['cancellation'] = extra_info.css(
                    'div.comfort-card__cancelation span ::text').extract_first(default='No reembolsable').strip()
                req.meta['price'] = content.css('div.comfort-card__price div span ::text').extract_first(
                    default='').strip()
                yield req

        for next_page in response.css('a.next-element'):
            yield response.follow(next_page, self.parse)
