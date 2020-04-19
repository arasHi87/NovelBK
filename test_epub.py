import json
import random
from ebooklib import epub
from pprint import pprint

data = 'NovelBK/spiders/data/乘秋千飞翔的圣修伯里/乘秋千飞翔的圣修伯里.json'
j_data = json.load(open(data, 'r'))[0]
base_name = list(j_data.keys())[0]

for volume in j_data[base_name]:
    chapter_list = []
    toc_list = []
    vname = volume[0]
    book_name = base_name + vname
    book = epub.EpubBook()
    book.set_identifier('{}{}'.format(book_name, random.randint(0, 100000000)))
    book.set_title(book_name)
    book.add_author('meow')
    book.set_language('en')
    del volume[0]

    for chapter_name in volume:
        chapter_id = str(random.randint(0, 100000000))
        chapter = epub.EpubHtml(title = chapter_name, file_name = chapter_id + '.xhtml')
        print(chapter_name)

        with open('NovelBK/spiders/data/{}/{}/{}.txt'.format(base_name, vname, chapter_name), 'r') as fp:
            chapter.content = fp.read().replace('\n', '<br>')

        book.add_item(chapter)
        chapter_list.append(chapter)
        toc_list.append(epub.Link(chapter_id + '.xhtml', chapter_name, chapter_id))

    book.toc = tuple(toc_list)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + chapter_list
    epub.write_epub(book_name + '.epub', book, {})