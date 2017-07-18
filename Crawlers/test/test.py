import urlparse


url=urlparse.urlparse('http://www.baidu.com/news/index.php?username=guol')

print url
url = urlparse.urlunsplit((url.scheme,url.netloc,'','',''))

print url
# u = urlparse.urlunparse(url)

u = urlparse.urljoin(url,"/inasdd.php")

print u