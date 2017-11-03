# horse_api

## Overview

## Description

## Demo

## Requirement


## Development

### 設定

設定ファイルを追加

```
# horse_api/application/config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://{YOUR_DB_SERVER}/{YOUR_DB}'
SECRET_KEY = '{YOUR_SECRET_KEY}'
SQLALCHEMY_TRACK_MODIFICATIONS = True
ADMINNAME = '{YOUR_ADMINISTRATOR_NAME}'
PASSWORD = '{YOUR_ADMINISTRATOR_PASSWORD}'
```

### 起動

Dockerイメージ生成

```
$ docker-compose -f docker-compose.dev.yml build
```

Dockerコンテナ起動

```
$ docker-compose -f docker-compose.dev.yml up
```

ブラウザで表示

http://localhost:5000/

### DB

テーブルの追加

```
$ docker-compose -f docker-compose.dev.yml exec app python manage.py init_db
```

テーブルの削除

```
$ docker-compose -f docker-compose.dev.yml exec app python manage.py drop_db
```

DBコンソール

```
$ docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres -d horse_api
```

### コマンド

pythonコンソール

```
$ docker-compose -f docker-compose.dev.yml exec app python
```

## Contribution

## Licence

## Author
