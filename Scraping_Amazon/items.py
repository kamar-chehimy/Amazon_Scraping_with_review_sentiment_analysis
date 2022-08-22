# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapingAmazonItem(scrapy.Item):
    Prod_name = scrapy.Field()
    Prod_price = scrapy.Field()
    Prod_link= scrapy.Field()
    #Prod_nb_reviews= scrapy.Field()
    Prod_category= scrapy.Field()
    Prod_manu= scrapy.Field()
    Prod_avail=scrapy.Field()
    Prod_del_span= scrapy.Field()
    Prod_sold_by= scrapy.Field()
    Prod_ships_from= scrapy.Field()
    
    Prod_desc= scrapy.Field()
    Prod_reviews= scrapy.Field()
    Prod_rev_sent= scrapy.Field()
    