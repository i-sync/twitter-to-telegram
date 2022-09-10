import datetime

import tweepy
from peewee import (Model, DateTimeField, ForeignKeyField, BigIntegerField, CharField,
                    IntegerField, TextField, OperationalError, BooleanField)
from playhouse.migrate import migrate, SqliteMigrator, SqliteDatabase


db = SqliteDatabase('peewee.db', timeout=10)

class BaseModel(Model):
    class Meta:
        database = db

class Twitter(BaseModel):

    tw_id = BigIntegerField(unique=True)
    text = TextField()

    created_at = DateTimeField(default=datetime.datetime.now)
    user_name = CharField()

    # photo_url = CharField("")

class Media(BaseModel):
    media_id = CharField()
    media_type = CharField()
    media_url = CharField('')
    preview_url = CharField('')
    twitter = ForeignKeyField(Twitter, related_name="medias")


for t in [Twitter, Media]:
    t.create_table(fail_silently=True)