import requests
from lxml import html

url_plus = "https://manhuaplus.com/manga/demon-magic-emperor01/"
url_kun = "https://kunmanga.com/manga/in-this-life-i-will-raise-you-well-your-majesty/"

html_elements = requests.get(url_plus)
doc = html.fromstring(html_elements.content)

# Title Tag
title_tag = doc.xpath('//div[@class="post-title"]/h1')
if title_tag:
    title = title_tag[0].text_content().strip()
else:
    print("No Title Tag Found.")
#
# # Image Tag
# image_tag = doc.xpath('//div[@class="summary_image"]/a/img/@src')
# if image_tag:
#     print(image_tag[0])
# else:
#     print('NO Image Tag Found.')

a_tag = doc.xpath('//div[@class="summary_image"]/a')[0]
# Get the src attribute inside the <a> tag
src = a_tag.xpath('img/@src')[0]
manga_url = a_tag.get('href')

# latest chapter li Tag
li_tags = doc.xpath('//li[@class="wp-manga-chapter    "]/a')[0:3]
lis = []
for li in li_tags:
    chapter_number = li.text_content().strip()
    chapter_url = li.get('href')
    lis.append({'chapter_number': chapter_number, 'chapter_url': chapter_url})

dic = {'Title': title, 'Image': src, 'Url': manga_url,
       'Chapter_list': lis}
print(dic)
