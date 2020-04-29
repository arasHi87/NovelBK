# NovelBK

crawler base on reids-scrapy, can help you get Novel from other site and covert txt to epub.

## Settings

All settings are in `NovelBK/settings.py`.

* `REDIS_HOST`: redis server ip
* `REDIS_PORT`: redis server port
* `REDIS_DATA_DICT`: this can help you filter the url has been seen
* `DB_NAME`: mongoDB name
* `DB_HOST`: mongoDB server ip
* `DB_PORT`: mongoDB server port
* `DB_USER`: mongoDB user name
* `DB_PWD`: mongoDB password
* `WENKU8_MAX_AID`: the nax book id will be crawled
* `DEBUG_MOD`: debug mod, it will allow get same url

## Install

if want to run scrapy in python3, it must be in virtualen

```bash
sudo apt install python3-venv
python3 -m venv ~/venv/NovelBK
source ~/venv/NovelBK/bin/activate
pip install -r requirements.txt
```

## Enviroment

setting important information in environment variables, you can set in every time when reboot, or just write in `.bashrc`

```bash
export DB_USER=<your mongodb user name>
export DB_PWD=<your mongodb password>
```

## Run

run redis server.

```bash
docker-compose up -d -f redis-compose.yml
```

run mongoDB server.

```bash
docker-compose up -d -f mongo-compose.yml
```

run wenku8 slave, it will help u crawler book content.

```bash
scrapy runspider NovelBK/spiders/slave_wenku8.py
```

run master, it will provide the slave spider url.

```bash
scrapy runspider NovelBK/spiders/master.py
```
