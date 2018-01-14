import json
import time
import pprint
import argparse
import getpass
from sys import exit, stdout
from pyhive import hive

def get_pretty_print(json_object):
    return json.dumps(json_object, sort_keys=True, indent=4, separators=(',', ': '))

def hive_connection_lh(_user,_pass,_host="thrift-host1"):
    try:
        conn = hive.Connection(host=_host, port=10000 , username=_user,password=_pass ,auth='LDAP')
        cursor = conn.cursor()
    except Exception as e:
        raise e
    return cursor , conn

def hive_connection_md(_user,_pass,_host="thrift-host2"):
    try:
        conn = hive.Connection(host=_host, port=10000 , username=_user,password=_pass ,auth='LDAP')
        cursor = conn.cursor()
    except Exception as e:
        raise e
    return cursor , conn

def msisdn_query(cursor,msisdn,schema):
    query = "select timestamp, local_ts , client_id, event , ctx_id , args  from %s.logevent where client_id = %s order by timestamp asc" % (schema,msisdn)
    cursor.execute(query)
    columns = cursor.description
    data = cursor.fetchall()
    return data

def get_project_data(cursor_lh,cursor_md):
    ## counters
    lh = 0
    md = 0
    project_data = {}
    query = "show schemas"
    cursor_lh.execute(query)
    data_lh = cursor_lh.fetchall()

    while lh < len(data_lh):
        if 'wr' in data_lh[lh][0]:
            tlc = data_lh[lh][0].split('_',1)[0].strip().upper()
            project_details = {"schema" : "%s" % data_lh[lh][0] , "dc" : "lh" }
            project_data[tlc] = project_details
        lh+=1

    cursor_md.execute(query)
    data_md = cursor_md.fetchall()

    while md < len(data_md):
        if 'wr' in data_md[md][0]:
            tlc = data_md[md][0].split('_',1)[0].strip().upper()
            project_details = {"schema" : "%s" % data_md[md][0] , "dc" : "md" }
            project_data[tlc] = project_details
        md+=1

    return project_data

def parse_data(data):
    items = []
    i = 1

    for row in data:
        utc_time = row[0]
        ls_time = row[1]
        msisdn = row[2]
        event = row[3]
        ctx_id = row[4]
        args = json.loads(row[5])
        ms_click = "Time UTC : "+utc_time+", Time Local : "+ls_time+" , User : "+msisdn+" , Event : "+event+"  , Page Type : "+args['page_type']
        args_pretty = get_pretty_print(args)

        ## dynamic items
        list_item = { "id" : i , "data" : "%s" % ms_click  , "args" : "%s" % args_pretty }
        i += 1

        items.append(list_item)

    return items

def parser():
    argparser = argparse.ArgumentParser('Hive Connection Tool')
    argparser.add_argument('-u','--username', help='LDAP Username', required=True)
    argparser.add_argument('-p','--password', help='LDAP Password')
    argparser.add_argument('--debug', help='Enable Debug Logging...' , action='store_true' )
    return argparser.parse_args()

if __name__ == '__main__':

    args = parser()

    username = args.username
    if not args.password:
        stdout.write("LDAP Crententials are needed for this action\n")
        password = getpass.getpass("LDAP Password: ")
    else :
        password = args.password

    ( cursor_lh , conn_lh )  = hive_connection_lh(session['username'],session['password'])
    ( cursor_md , conn_md )  = hive_connection_md(session['username'],session['password'])
    schemas = get_project_data(cursor_lh,cursor_md)
    conn_lh.close()
    conn_md.close()

    print (schemas)
