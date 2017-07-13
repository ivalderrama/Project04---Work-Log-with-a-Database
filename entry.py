import datetime

from peewee import *


db = SqliteDatabase('entries.db')


class Entry(Model):
    """
    Entry database model that stores the employee's name, date,
    task title, time spent, and notes.
    """
    employee_name = TextField()
    date = DateTimeField(default=datetime.datetime.now)
    task_name = TextField()
    minutes = IntegerField()
    notes = TextField(null=True)

    class Meta:
        database=db


def initialise():
    """Create the database and the tables if they don't exist."""
    db.connect()
    db.create_tables([Entry], safe=True)