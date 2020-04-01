from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


def scrape_all():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "hemisphere_images": mars_hemispheres(browser),
      "last_modified": dt.datetime.now()
    }  
    browser.quit()
    return data


def mars_news(browser):
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=2)
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        slide_elem.find("div", class_='content_title')
        news_title = slide_elem.find("div", class_='content_title').get_text()
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    
    return news_title, news_p

def featured_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    browser.is_element_present_by_text('more info', wait_time=2)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    try:
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url



def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)
    return df.to_html()




def mars_hemispheres(browser):
    
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)


    hemispheres = []
    for x in range(0,4):
       
        itemLink = browser.find_by_css('.description .itemLink', wait_time=5)[x]
        itemLink.click()
        soup = BeautifulSoup(browser.html)
        hemisphere_url = soup.find('img', class_='wide-image')['src']   
        hemisphere_url_full = f'https://astrogeology.usgs.gov{hemisphere_url}'
        hemisphere_title = (soup.find('h2', class_='title')).text
        hemispheres.append({
            "img_url": hemisphere_url_full,
            "title": hemisphere_title
        })
      
        browser.back()
    
    return hemispheres



if __name__ == "__main__":
    
    print(scrape_all())



