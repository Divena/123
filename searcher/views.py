from django.shortcuts import render
from django.http import HttpResponse
from l3 import settings
from .models import index, Page
import json
import urllib
import threading
import re
import Queue


def home(request):
    return render(request, 'index.html', {'STATIC_URL' : settings.STATIC_URL})

def search(request):
    _words = request.POST['search']
    words = _words.split(' ')
    all_urls = []
    urls_of_word = []
    for w in words:
        if index.objects.filter(word=w).count() > 0:
            tag = index.objects.get(word=w)
            urls_of_word.append(tag.url.all())
    prior_dict = {}
    for val in urls_of_word:
        for v in val:
            if v in all_urls:
                prior_dict[v] += 1
            else:
                all_urls.append(v)
                prior_dict[v] = 0
    res_urls = []
    if not all_urls:
        urls = [{'url':'Not found', 'prior': 0}]
        return HttpResponse(json.dumps(urls), content_type='application/json')
    else:
        for u in all_urls:
            res_urls.append({'url' : u.url ,'prior': prior_dict[u]})
        answer = json.dumps(res_urls, ensure_ascii=False)
        return HttpResponse(answer, content_type='application/json')


def add_url(request):
    urls_ = request.POST['add_url']
    urls_ = urls_.split(',')
    urls = []
    threads = []
    for u in urls_:
        urls.append(u.strip(' '))
    for u in urls:
        t = threading.Thread(target=add_url_manage, args=(u,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return HttpResponse(json.dumps({'message': 'Ready!'}), content_type='application/json')



def add_url_manage(url):
    url = check_url(url)
    if not url:
        return None
    dict_url = dict()
    deep = 0
    dict_url.setdefault(url,deep)
    q = Queue.Queue()
    q.put(url)
    while (not q.empty()):
        current = q.get()
        deep = dict_url[current]
        if deep > 100:
            continue
        html = None
        try:
            html = urllib.urlopen(current).read()
        except IOError:
            pass
        if not html:
            continue
        text = get_text(html)
        index_text(text, current, html)
        domen = get_domen(current)
        l = get_urls_from_page(html,domen)
        for u in l:
            if u not in dict_url and len(u) < 255:
                q.put(u)
                dict_url.setdefault(u,deep+1)

def check_url(url):
    if url[0:2] == '//':
        url = url[2:]
    if not re.match(r'^http(s?)://', url):
        url = 'http://' + url
    url = url + ('/' if url[-1] != '/' else '')
    if not re.match('(https?:\/\/(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})', url):
        return None
    else:
        return url

def get_urls_from_page(page, domen):
    list_url = list()
    list_a = re.findall(r'<a[\s\S]*?>', page)
    for elem in list_a:
        element = re.findall(r'href="[^"]*"', elem)
        if len(element) == 0:
            continue
        element = element[0].split('"')
        for el in element:
            el = check_url(el)
            if el != None:
                if el not in list_url:
                    list_url.append(el)
    return list_url

def get_text(page):
    w1 = re.findall(r'(<p[\s\S]*?>[\s\S]*</p>)', page)
    w2 = re.findall(r'(<h[\s\S]*?>[\s\S]*</h[1-6]>)',page)
    w3 = re.findall(r'(<b[\s\S]*?>[\s\S]*</b>)',page)
    w4 = re.findall(r'(<title[\s\S]*?>[\s\S]*</title>)',page)
    l = w1 + w2 + w3 + w4
    body = ' '
    body = body.join(l)
    reth = re.sub(r'<(.*?)>',' ',body)
    reth = re.split(r'[",.]+',reth)
    body = ' '
    body = body.join(reth)
    return body

def index_text(text,Url, html):
    text = re.sub('[^[A-z]^\s',' ',text)
    l = re.split(r'[\s]+', text)
    words_set = set()
    for elem in l:
        words_set.add(elem)
    for elem in words_set:
      if len(elem) < 255:
        i = None
        if index.objects.filter(word = elem).count() == 1:
            i = index.objects.get(word = elem)
        else:
            i = index(word=elem)
        if Page.objects.filter(url=Url).count() == 1:
            p = Page.objects.get(url=Url)
            p.text = html
        else:
            p = Page(url=Url, text=html)
            p.save()
        i.save()
        i.url.add(p)

def get_domen(url):
    reth = re.split('/',url)
    for elem in reth:
        if re.match('.+[.].+',elem):
            return elem
