# NovelBK

爬取各大輕小說站，並將 txt 轉換成易於閱讀之 epub，使用 redis-spider 分散式爬蟲加快速度

## Support

* wenku8

## Run

* Redis-server

分散式爬蟲資料庫

```bash
docker run -p 6379:6379 -d                  \
    -v $PWD/redis-data:/bitnami/redis/data  \
    --name redis_cont                       \
    bitnami/redis:latest

```

* Master-side

負責檢測所有書籍 url 提供給 slver

```bash
cd NovelBK/spider
scrapy runspider master.py
```

* Wnku8Slaver-side

負責抓取有關 wenku8 的 url

```bash
cd NovelBK/spider
scrapy runspider slave_wenku8.py
```
