import json
import csv, codecs, cStringIO
from datetime import timedelta, time, datetime
from django.db import connection

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def jsonhandler(obj):
    """Pass this function as the "default" keyword argument to json.dumps. This
    will handle converting dates and times to JSON"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, time):
        return str(time)
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

def querySetToJSON(qs):
    """Return a json string of a queryset object as an array containing dicts"""
    cursor = connection.cursor()
    #data = serializers.serialize('json', qs)
    cursor.execute(str(qs.query))
    return json.dumps(dictfetchall(cursor), default=jsonhandler)

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
