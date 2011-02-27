from django.shortcuts import render_to_response, get_object_or_404
from django.utils.simplejson import dumps as json_encode
from django.http import HttpResponse

from time import mktime
import datetime

import MySQLdb
import string

letters = string.lowercase + string.digits + '_'
colors = ( '#500000', '#075f87', '#000080', '#802020', '#075f87', '#075f87' )

# this gives us a cheap counter in a list comprehension
class Counter:
    def __init__(self, starting=0, inc=1): self.x, self.inc = starting,inc
    def next(self):
        self.x += self.inc
        return self.x


def _db():
    return MySQLdb.connect(
            user="twit02",
            passwd="frayedwell",
            db="twit02",
            host="hamm.cs.tamu.edu" )


def _db_cur():
    return _db().cursor(MySQLdb.cursors.DictCursor)


def powerlaw(request, plot_type, dt, maxnum=-1):
    if plot_type not in ('both', 'impact', 'indegree'):
        return HttpResponse("oops.  both, indegree or impact pls")

    cur = _db_cur()
    users = []

    # build a HUGE array consisting of tuple(deg,score03,username) for 
    # every user
    # for L in string.digits:
    for L in letters:
        table_name = "indeg_" + L
        sql = """
select to_user, as_of, deg, score03
from """ + table_name + """
where as_of = %s """
        cur.execute(sql, dt)
        for row in cur:
            users.append((row['deg'], row['score03'], row['to_user']))

    # now, sort and assign indexes
    if plot_type == 'both':
        indexes = ( ('indegree',0), ('impact',1)) # doing both
        users.sort(key=lambda x:x[1], reverse=1) # sorted by impact!!
    else:
        idx = {'indegree':0, 'impact':1}[plot_type]
        indexes = ( (plot_type,idx), ) 
        users.sort(key=lambda x:x[idx], reverse=1) # sorted by indeg!!
    if maxnum != -1:
        users = users[:int(maxnum)] # truncate our data if requested
    plots = []

    for label, idx in indexes:
        c = Counter()
        plots.append( {
            'label': label,
            'data':  json_encode( [ (c.next(), u[idx]) for u in users] ),
            'color': colors[idx],
            } )

    return render_to_response('twitter/chart.html', {'plots':plots})


def powercentrality(request, plot_type, dt, maxnum=-1):
    if plot_type not in ('both', 'impact', 'indegree'):
        return HttpResponse("oops.  both, indegree or impact pls")

    cur = _db_cur()
    users = []

    # build a HUGE array consisting of tuple(deg,score03,username) for
    # every user
    # for L in string.digits:
    for L in letters:
        table_name = "indeg_" + L
        sql = """
select to_user, as_of, degcentral, tdegcentral
from """ + table_name + """
where as_of = %s """
        cur.execute(sql, dt)
        for row in cur:
            users.append((row['degcentral'], row['tdegcentral'], row['to_user']))

    # now, sort and assign indexes
    if plot_type == 'both':
        indexes = ( ('degreecentrality',0), ('impactcentrality',1)) # doing both
        users.sort(key=lambda x:x[1], reverse=1) # sorted by impact!!
    else:
        idx = {'degree':0, 'impact':1}[plot_type]
        indexes = ( (plot_type,idx), )
        users.sort(key=lambda x:x[idx], reverse=1) # sorted by indeg!!
    if maxnum != -1:
        users = users[:int(maxnum)] # truncate our data if requested
    plots = []

    for label, idx in indexes:
        c = Counter()
        plots.append( {
            'label': label,
            'data':  json_encode( [ (c.next(), u[idx]) for u in users] ),
            'color': colors[idx],
            } )

    return render_to_response('twitter/chart.html', {'plots':plots})


ctime = lambda t: 1000 * mktime(t.timetuple())


def fill_in_the_date_holes(data):
    # assumes data is sorted by date ascending
    if not data: return data
    rows = []
    prev = data[0][0]
    oneday = datetime.timedelta(days=1)
    rows.append(data[0])
    for d in data[1:]:
        counter = 0
        while prev+oneday < d[0] and counter < 100000:
            rows.append( (prev+oneday,0,0,0,0,0,0,0) ) 
            prev += oneday
            counter += 1
        rows.append( d )
        prev = d[0]
    return rows


def account(request, screen_name, plot_type):
    if plot_type not in ('custom', 'all','impact5','tdegcen', 'degcen', 'impact', 'indegree'):
        return HttpResponse("oops.  all, degcen, indegree or impact pls")

    start_date = end_date = None
    if request.GET.has_key('sd'): start_date = request.GET['sd']
    if request.GET.has_key('ed'): end_date = request.GET['ed']

    cur = _db_cur()
    table_name = "indeg_" + screen_name[0].lower()
    sql = """
select as_of,
    ifnull(deg,0) as deg,
    ifnull(score03,0) as score03,
    ifnull(score50,0) as score50,
    ifnull(degcentral,0) as degcentral,
    ifnull(tdegcentral,0) as tdegcentral
from """ + table_name + """
where to_user = %s """
    args = [screen_name]
    if start_date:
        sql += " and as_of >= %s "
        args.append( start_date )
    if end_date:
        sql += " and as_of <= %s "
        args.append( end_date )
    cur.execute(sql, args)

    # now, sort and assign indexes
    if plot_type == 'both':
        indexes = ( ('indegree',2), ('impact',1)) # doing both
    elif plot_type == 'impact5':
        indexes = ( ('score03',1), ('score50',5) ) 
    elif plot_type == 'indegree':
        indexes = ( (plot_type,2), ) 
    elif plot_type == 'impact':
        indexes = ( (plot_type,1), ) 
    elif plot_type == 'degcen':
        indexes = ( (plot_type,3), ) 
    elif plot_type == 'tdegcen':
        indexes = ( (plot_type,4), ) 
    else:
        indexes = tuple()

    # data = [ (ctime(d['as_of']), d['score03'], d['deg'])  for d in cur ]
    data = [ (
        d['as_of'],
        d['score03'] or 0,
        d['deg'] or 0,
        d['degcentral'] or 0,
        d['tdegcentral'] or 0,
        d['score50'] or 0,
        )  for d in cur ]
    data.sort(key=lambda x:x[0]) # sorted by indeg!!
    data = fill_in_the_date_holes(data)

    plots = []
    for label, idx in indexes:
        plots.append( {
            'label': label,
            'data':  json_encode( [ (ctime(r[0]), r[idx]) for r in data] ),
            'color': colors[idx-1],
            } )

    return render_to_response(
        'twitter/chart.html', 
        { 'plots':plots, 'xaxis': '{ mode: "time" }' , }
        )


