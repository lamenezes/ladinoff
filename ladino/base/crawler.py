from concurrent import futures
import datetime
from lxml import html
import requests
import re

from django.db import IntegrityError
from base.models import Author, Category, FanFiction, SubCategory


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


def crawl_fic_archive_urls(url, timeout=30):
    """
    The URL from the first page of the list of fanfics
    """

    page = requests.get(url, timeout=timeout)
    tree = html.fromstring(page.text)
    a = tree.xpath('body//center//a[text()="Last"]')
    last_page_url = a[0].values()[0]
    last_page = re.search('=(?P<last>\d+)$', last_page_url).groupdict()['last']
    urls = [url + '&p=%s' % page_num for page_num in range(1, int(last_page))]
    return urls


def crawl_fics_data(url, timeout=30):
    try:
        page = requests.get(url, timeout=timeout)
    except:
        try:
            page = requests.get(url, timeout=timeout)
        except:
            with open('error_log.txt', 'a') as f:
                f.write(url)
            return [], []
    tree = html.fromstring(page.text)
    div = tree.xpath('//div[@id="content_wrapper_inner"]')[0]
    fic_blocks_start = 0
    for block in div:
        values = block.values()
        if values:
            if 'z-list zhover zpointer' in values[0]:
                break
        fic_blocks_start += 1

    fic_blocks = div[fic_blocks_start:fic_blocks_start + 25]
    authors = []
    fics = []
    print("crawling from {}".format(url))
    for block in fic_blocks:
        title_data = block[0]
        title = title_data.text_content()
        link = 'http://fanfiction.net' + title_data.values()[1]

        author_data = block[1]
        if author_data.text_content() == '':
            author_data = block[2]
        author_link = 'http://fanfiction.net' + author_data.values()[0]
        nickname = author_data.text_content()
        author_id = re.search('/u/(?P<id>\d+)/', author_link).groupdict()['id']

        fic_meta = block[-1].text_content()
        fic_meta_start = re.search('Rated', fic_meta).start()
        fic_meta = fic_meta[fic_meta_start:]
        regex = ('Rated: (?P<rated>[\\w+ ]+) - '
                 '(?P<language>[\\w ]+) - '
                 '((?P<genre>[\\w/\- ]+) - )?'
                 '(Chapters: (?P<chapters>[\\d ]+) - )?'
                 'Words: (?P<words>[\\d, ]+) - '
                 '(Reviews: (?P<reviews>[\\d\\w, ]+) - )?'
                 '(Favs: (?P<favorites>[\\d\\w, ]+) - )?'
                 '(Follows: (?P<follows>[\\d\\w, ]+) - )?'
                 '(Updated: (?P<updated>[\\d\\w/ ]+) - )?'
                 'Published: (?P<publish_date>[\\w\\d/ ]+)'
                 "((?P<ship>[\[\]\\w.,\-/' ]+) - )?"
                 '(Status: (?P<status>[\w ]+) - )?')
        try:
            fic_meta = re.search(regex, fic_meta).groupdict()
        except AttributeError:
            print('erro ao pegar {}\n{}'.format(fic_meta, regex))
            continue
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

        fic_meta['title'] = title
        fic_meta['link'] = link

        fic = FanFiction()
        for attr, val in fic_meta.items():
            setattr(fic, attr, val)

        try:
            author = Author.objects.get(_id=author_id)
        except Author.DoesNotExist:
            author = Author(_id=author_id, nickname=nickname, link=author_link)
            authors.append(author)
        fic.author = author
        fics.append(fic)

    return authors, fics


def crawl_many(url, max_workers=20, block_size=500, start_page=0, total_pages=0):
    urls = crawl_fic_archive_urls(url)

    if not total_pages:
        total_pages = len(urls)

    blocks = [urls[start_page + block_start:start_page + block_start + block_size]
                for block_start in range(0, total_pages, block_size)]
    for block in blocks:
        all_authors = []
        all_fics = []
        with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            to_do_map = {}
            print('ready')
            for url in block:
                future = executor.submit(crawl_fics_data, url)
                to_do_map[future] = url
            print('steady')
            done_iter = futures.as_completed(to_do_map)
            print('go')
            for future in done_iter:
                try:
                    authors, fics = future.result()
                except:
                    import traceback
                    print(traceback.print_exc())
                    continue

                all_authors += authors
                all_fics += fics

        print('crawled {} blocks of fics! time to write them to the db :D'.format(len(block)))
        all_authors = filter(None, all_authors)
        if all_authors:
            sorted_authors = sorted(all_authors, key=lambda author: author._id)
            all_authors = []
            if len(authors) > 1:
                for (first_author, author) in zip(sorted_authors, sorted_authors[1:] + [sorted_authors[0]]):
                    if first_author._id != author._id:
                        all_authors.append(first_author)
            to_insert = []
            for author in all_authors:
                try:
                    author = Author.objects.get(pk=author.id)
                except Author.DoesNotExist:
                    to_insert.append(author)
            try:
                Author.objects.bulk_create(to_insert)
            except IntegrityError:
                for author in to_insert:
                    try:
                        author = Author.objects.get(pk=author.id)
                    except Author.DoesNotExist:
                        try:
                            author = Author.objects.get(_id=author._id)
                        except Author.DoesNotExist:
                            author.save()
        print('inserting {} fics'.format(len(all_fics)))
        FanFiction.objects.bulk_create(all_fics)
