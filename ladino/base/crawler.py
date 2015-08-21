from concurrent import futures
import datetime
from lxml import html
import requests
import re
import time

from models import Author, Category, FanFiction, SubCategory


def crawl_subcategories():
    base_url = 'http://fanfiction.net/'
    subcategories = []
    for category in Category.objects.all():
        url = base_url + category.title
        page = requests.get(url)
        tree = html.fromstring(page.text)
        print(u'Categoria:', category.title)
        table = tree.get_element_by_id('list_output')
        tr = table[0][0]
        for td in tr:
            for line in td:
                raw = line.text_content()
                s = re.search("(?P<title>.+) \((?P<qty>.+)\)", raw)
                title = s.groupdict()['title']
                qty = s.groupdict()['qty']
                link = base_url + line[0].values()[0]
                subcategory = SubCategory(title=title,
                                          category=category,
                                          fanfic_qty=qty,
                                          link=link)
                subcategories.append(subcategory)

    return subcategories


def crawl_fic_links(cls, categories=[]):
    search = '/?&srt=1&r=10'
    if not categories:
        categories = SubCategory.objects.all()

    for category in categories:
        # search = re.search('p=(?P<page_number>\d+)', category.link)
        # if search:
        #     page_number = int(search.groupdict()['page_number'])

        page_number = 1
        found = True
        while found:
            if page_number > 1:
                current_url = category.link + search + ('&p=%d' % page_number)
            else:
                current_url = category.link + search
            try:
                page = requests.get(current_url)
            except requests.exceptions.ConnectionError:
                print(u'Connection Error')
                time.sleep(10)
                continue
            tree = html.fromstring(page.text)
            links = tree.xpath('//a[@class="stitle"]')
            if not links:
                found = False
                print('Nao achei, chente')
            links = {link.get('href'): link[0].tail for link in links}
            fics = []
            for link, title in links.items():
                fic = FanFiction(title=title, link=link, category=category)
                fics.append(fic)
            FanFiction.objects.bulk_create(fics)
            print('Parsing page %d' % page_number)
            print(fic)
            page_number += 1


def crawl_fic(fic, timeout):
    if fic.is_complete:
        return (fic.author, fic, False)

    page = requests.get(url='http://fanfiction.net' + fic.link)
    tree = html.fromstring(page.text)
    span = tree.find('body//span[@class="xgray xcontrast_txt"]')
    try:
        fic_meta = span.text_content()
    except AttributeError:
        return (None, fic, False)

    regex = ('Rated: (?P<rated>[\\w+ ]+) - '
             '(?P<language>[\\w ]+) - '
             '((?P<genre>[\\w/- ]+) - )?'
             "((?P<ship>[\[\]\\w.,-/' ]+) - )?"
             '(Chapters: (?P<chapters>[\\d ]+) - )?'
             'Words: (?P<words>[\\d, ]+) - '
             '(Reviews: (?P<reviews>[\\d\\w, ]+) - )?'
             '(Favs: (?P<favorites>[\\d\\w, ]+) - )?'
             '(Follows: (?P<follows>[\\d\\w, ]+) - )?'
             '(Updated: (?P<updated>[\\d\\w/ ]+) - )?'
             'Published: (?P<publish_date>[\\w\\d/ ]+) - '
             '(Status: (?P<status>[\w ]+) - )?'
             'id')
    try:
        fic_meta = re.search(regex, fic_meta).groupdict()
    except AttributeError:
        print(fic)
        print(regex)
        print(fic_meta)
        print()
        return (None, fic, False)
    pub = fic_meta['publish_date']
    try:
        fic_meta['publish_date'] = datetime.datetime.strptime(pub, '%m/%d/%Y')
    except ValueError:
        try:
            fic_meta['publish_date'] = datetime.datetime.strptime(pub, '%m/%d')
        except ValueError:
            fic_meta['publish_date'] = datetime.datetime.today()

    if 'updated' in fic_meta and fic_meta['updated']:
        updated = fic_meta['updated']
        try:
            fic_meta['updated'] = datetime.datetime.strptime(updated, '%m/%d/%Y')
        except ValueError:
            try:
                fic_meta['updated'] = datetime.datetime.strptime(updated, '%m/%d')
            except ValueError:
                fic_meta['updated'] = datetime.date.today()
    fic_meta['words'] = fic_meta['words'].replace(',', '')
    if 'reviews' in fic_meta and fic_meta['reviews']:
        fic_meta['reviews'] = fic_meta['reviews'].replace(',', '')
    if 'favorites' in fic_meta and fic_meta['favorites']:
        fic_meta['favorites'] = fic_meta['favorites'].replace(',', '')
    if 'follows' in fic_meta and fic_meta['follows']:
        fic_meta['follows'] = fic_meta['follows'].replace(',', '')

    b = tree.find('body//b[@class="xcontrast_txt"]')
    fic_meta['title'] = b.text_content()

    for attr, val in fic_meta.items():
        setattr(fic, attr, val)

    a = tree.find('body//div[@id="profile_top"]//a[@class="xcontrast_txt"]')
    nickname = a.text_content()
    link = a.values()[1]
    s = re.search('/u/(?P<id>\d+)/', link)
    _id = s.groupdict()['id']

    if not fic.author:
        try:
            author = Author.objects.get(_id=_id)
        except Author.DoesNotExist:
            author = Author(_id=_id, nickname=nickname, link=link)
    else:
        author = fic.author

    fic.author = author
    fic.is_complete = True

    return (author, fic, True)


def crawl_many_fics(fanfics):
    authors = []
    fics = []
    curr = 1
    total = len(fanfics)
    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        to_do_map = {}
        print('ready')
        for ff in fanfics:
            future = executor.submit(crawl_fic, ff, 20)
            to_do_map[future] = ff
        print('steady')
        done_iter = futures.as_completed(to_do_map)
        print('go!')
        for future in done_iter:
            try:
                author, fic, status = future.result()
            except:
                import traceback
                traceback.print_exc()

            if status:
                authors.append(author)
                fics.append(fic)

            if curr % 250 == 1:
                print('{}/{} crawled!'.format(curr, total))

            curr += 1

    print('Crawleado! Inserindo no banco...')
    Author.objects.bulk_create(authors)
    FanFiction.objects.bulk_create(fics)
