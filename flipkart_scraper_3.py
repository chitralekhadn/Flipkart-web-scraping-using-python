from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import xlsxwriter




def target_url(input_term):
    '''Create a target url'''
    #url = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_1'
    url = 'https://www.flipkart.com/search?q={}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off'
    input_term = input_term.replace(' ','+')
    
    link = url.format(input_term)
    
    #To get next pages
    link += '&page{}'
    
    return link


def get_data(soup, link):
    source = ''
    name = ''
    price = ''
    rating = ''
    seller = ''
    replacement_policy = ''
    payment_options = []
    product_features = []
    image_urls = []
    
    try:
        #Rating
        rating = soup.find('div',{'class':'_3LWZlK'}).text.strip()
    except:
        rating = 'NA'
    
    try:
        #Source
        source = (link.split('www.'))[1].split('.com')[0]
    except:
        source = 'NA'
    
    try:
        #Product Name
        name = soup.find('h1').text.replace('\xa0','').strip()
    except:
        name = 'NA'
    
    try:
        #Price
        price = soup.find('div',{'class':'_30jeq3 _16Jk6d'}).text.replace('₹','').strip()
    except:
        price = 'NA'
    
    try:
        #Seller
        seller = soup.find('div',{'id':'sellerName'}).span.span.text
    except:
        seller = 'NA'
    
    try:
        #Replacement Policy
        replacement_policy = soup.find('div',{'class':'_2MJMLX'}).text.replace('?','')
    except:
        replacement_policy = 'NA'
    
    try:
        #Payment Options
        
        options = soup.find('div',{'class':'_250Jnj'})
        for i in options.select('._1Ma4bX'):
            payment_options.append(i.text)
    except:
        payment_options.append('NA')
    
    try:
        #Product Features
        
        features = soup.find('div',{'class':'_2418kt'})
        for i in features.select('._21Ahn-'):
            product_features.append(i.text)
    except:
        product_features.append('NA')
    
    
    try:
        #Image Urls
        
        imgs = soup.find('div',{'class':'_2mLllQ'})
        for i in imgs.select('._1AuMiq'):
            image_urls.append((i.find('div')['style']).replace('background-image:url','').replace(')(',''))
    except:
        image_urls.append('NA')
    
    result = (name , source,  price, rating, seller, replacement_policy, payment_options, product_features, image_urls)
    
    return result


def main():
    # Enter a name of product 
    term = input("Enter a name of product:")
    #Start Webdriver
    driver = webdriver.Chrome()
    records = []
    rating = 0
    url = target_url(term)
    
    #To get Total no of pages available
    #driver.get(url)
    #soup = BeautifulSoup(driver.page_source,'html.parser')
    #page_nos = int(soup.find('div',{'class':'_2MImiq'}).span.text.split('of')[1])
    page_no = int(input("Enter number of pages wants to scrape:"))
    delays = [2, 5, 4, 7, 3]
    delay = np.random.choice(delays)
    
    
    #To get data from all pages pass the range function as range(1, page_nos + 1)
    for page in range(1, page_no):
        time.sleep(delay)
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source,'html.parser')
            
        try:
            results = soup.find_all('div', {'class':'_2pi5LC col-12-12'})
            if len(results) == 0:
                results = soup.find_all('div', {'class':'_1AtVbE col-12-12'})
        except AttributeError:
            pass
        
        
        for item in results:
            time.sleep(delay)
            
            try:
                atag = item.find('a',{'class':'_1fQZEK'})
                if atag is None:
                    atag = item.find('a',{'class':'_2UzuFa'})
            except AttributeError:
                pass
            
            
            if atag is not None:
                desc = atag.get('href')
                product_link = 'https://www.flipkart.com' + desc
                driver.get(product_link)
                soup_ = BeautifulSoup(driver.page_source,'html.parser')
                try:
                    #Rating
                    rating = soup.find('div',{'class':'_3LWZlK'}).text.strip()
                except:
                    rating = 0
                #Product having lowest rating
                if float(rating) <= 2 :
                    record = get_data(soup_, product_link)
                    if record:
                        records.append(record)
    driver.close()
    #Save data in excel file
    # Create a Pandas dataframe from the data.
    if len(records) != 0:
        df = pd. DataFrame(records)
        df.columns = ['Product Name', 'Source', 'Price', 'Rating', 'Seller', 'Replacement Policy', 'Payment Options', 'Product Features', 'Image urls']
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter('result3.xlsx', engine='xlsxwriter')

        # Convert the dataframe to an XlsxWriter Excel object.
        df.to_excel(writer, sheet_name='{}'.format(term))
        writer.save()
    else:
        print('No records of products have lowest rating.')





main()
