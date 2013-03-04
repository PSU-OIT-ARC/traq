import json
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
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, time):
        return str(time)
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

def querySetToJSON(qs):
    cursor = connection.cursor()
    cursor.execute(str(qs.query))
    return json.dumps(dictfetchall(cursor), default=jsonhandler)
