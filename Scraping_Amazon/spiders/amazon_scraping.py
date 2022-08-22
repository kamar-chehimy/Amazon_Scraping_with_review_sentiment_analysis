import scrapy
from ..items import ScrapingAmazonItem
import numpy as np
from happytransformer import HappyTextClassification

class AmazonScrapingSpider(scrapy.Spider):
    name = 'amazon_scraping'
    count=1
    start_urls = ['https://www.amazon.com/s?k=hair+dryer' ]
    product=ScrapingAmazonItem()
    name_arr=[]
    url_arr=[]

    prod_nb=1

    def sentiment_analysis(self, prod_reviews):
        happy_tc = HappyTextClassification(model_type="DISTILBERT", model_name="distilbert-base-uncased-finetuned-sst-2-english", num_labels=2)
        prod_sent=[]
        all_prod_sent=[]
        for i in prod_reviews:
            try:
                one_prod_sent = happy_tc.classify_text(i)
                #print(type(one_prod_sent),one_prod_sent.label, one_prod_sent.score)
                prod_sent.append([[one_prod_sent.label, one_prod_sent.score]])
            except Exception as e:
                #print(e)
                prod_sent.append(["The text is too big to be classified"])
                
        all_prod_sent.append(prod_sent)
        print("Sentiment completed")
        return all_prod_sent

    def parse(self, response):
        
        try:
            prod_name=response.css('.a-size-base-plus.a-color-base.a-text-normal::text').extract() # len 64
        except Exception as e:
            prod_name="Unavailable"

        #try:
            #prod_nb_reviews=response.css('span.a-size-base.s-underline-text::text').extract() #len 63
        #except Exception as e:
            #prod_nb_reviews="Unavailable"   

        try:     
            prod_url=["https://www.amazon.com/" + s  for s in  response.css('.a-link-normal.s-no-outline').css("::attr(href)").extract()]  # len 64
            #print("URL", type(prod_url))
        except Exception as e:
            prod_url="Unavailable" 
        
        AmazonScrapingSpider.name_arr=prod_name
        AmazonScrapingSpider.url_arr=prod_url
        

        for link in prod_url:
            yield response.follow( url = link, callback = self.parse2 )
    
        AmazonScrapingSpider.count+=1
        
        nxt_page="https://www.amazon.com/s?k=hair+dryer&page="+str(AmazonScrapingSpider.count) #+"&qid=1624791620&ref=sr_pg_3"

        if AmazonScrapingSpider.count<3:
            yield response.follow(nxt_page,callback=self.parse)
    

    def parse2( self, response ):
        
        try:
            #prod_price=[response.css('span.a-offscreen::text').extract()[-1]] # there's better than it 
            #print("saved --------------------------",response.css('span.a-offscreen::text').extract()[-1] )
            prod_price=response.css('span.a-offscreen::text').extract_first()
            print("price --------------------------",prod_price)
            if prod_price=='Page 1 of 1':
                prod_price=""
        except Exception as e:
            prod_price=""

        try:
            prod_desc=response.css('.a-unordered-list.a-vertical.a-spacing-mini span::text').extract()
        except Exception as e:
            prod_desc=""

        try:
            prod_cat=response.css('#wayfinding-breadcrumbs_feature_div li>span>a::text').extract()
            prod_cat=[i.strip() for i in prod_cat]
        except Exception as e:
            prod_cat=[""]

        try:
            prod_manu=response.css('#bylineInfo::text').extract()[0]
            #print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^',prod_manu)
            if prod_manu.startswith('Visit the '):
                prod_manu=prod_manu.split('Visit the')[1]
                print("$############## manu: ",prod_manu )
            else:
                prod_manu=""

        except Exception as e:
            prod_manu=""
    
        try: 
            #print("LLLLLLLLLLLLL ", len(response.css('.a-size-medium.a-color-success::text').extract()), response.css('.a-size-medium.a-color-success::text').extract())
            if len(response.css('.a-size-medium.a-color-success::text').extract())>0: 
                prod_avail=response.css('.a-size-medium.a-color-success::text').extract() # in Stock
                #print("&&&&&&&&&&&&&&&&& avail", prod_avail)
            else: 
                prod_avail=response.css('#availability span::text').extract() # currently unavailable, out od stock, only left
                #print("!!!!!!!!!!!!!!!!!!!!!! avail",response.css('#availability span::text').extract())
            prod_avail=[i.strip() for i in prod_avail]
        
        except Exception as e:
            #prod_avail=[response.css('.a-color-price.a-text-bold::text').extract()] # not working properly
            #print(":::::::::::",[response.css('.a-color-price.a-text-bold::text').extract()] )
            prod_avail=[response.css('#availability span::text').extract()]
            #print("!!!!!!!!!!!!!!!!!!!!!!",response.css('#availability span::text').extract())


        try:
            span1=response.css('#mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE ::text').extract()
            span1="".join(span1).strip()
        except Exception as e:
            span1=""

        try:
            span2=response.css('#mir-layout-DELIVERY_BLOCK-slot-SECONDARY_DELIVERY_MESSAGE_LARGE ::text').extract()
            span2="".join(span2).strip()
        except Exception as e:
            span2=""

        prod_del_span=[span1, span2] # to count as one item

        try:
            prod_reviews=response.css('.a-expander-content.reviewText.review-text-content.a-expander-partial-collapse-content span::text').extract()
            if len(prod_reviews)>10:
                prod_reviews=prod_reviews[:10]

        except Exception as e:
            prod_reviews=""       
        try:
            prod_ships_from=response.css('.tabular-buybox-text.a-spacing-none span::text').extract_first()
        except Exception as e:
            prod_ships_from=""

        try:
            prod_sold_by=response.css('#sellerProfileTriggerId::text').extract_first()
        except Exception as e:
            prod_ships_from=""

        prod_rev_sent=self.sentiment_analysis(prod_reviews)

        prod_name=np.array(AmazonScrapingSpider.name_arr).flatten()
        prod_url=np.array(AmazonScrapingSpider.url_arr).flatten()

        self.product["Prod_name"]=prod_name[AmazonScrapingSpider.prod_nb]
        self.product["Prod_link"]=prod_url[AmazonScrapingSpider.prod_nb]
        
        self.product["Prod_price"]=prod_price
        self.product['Prod_category']=prod_cat
        self.product['Prod_manu']=prod_manu
        self.product['Prod_avail']=prod_avail
        
        self.product['Prod_ships_from']=prod_ships_from
        self.product['Prod_sold_by']=prod_sold_by
        self.product["Prod_del_span"]=prod_del_span
        self.product['Prod_desc']=prod_desc
        self.product['Prod_reviews']=prod_reviews
        self.product['Prod_rev_sent']=prod_rev_sent

        AmazonScrapingSpider.prod_nb+=1

        yield self.product
