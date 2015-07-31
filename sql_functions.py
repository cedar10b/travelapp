# -*- coding: utf-8 -*-

import itertools
import pandas as pd
import MySQLdb as mysql
from prettytable import from_db_cursor
from sqlalchemy import create_engine
#import pandas.io.sql as sql

host = 'localhost'
user = 'root'
passwd = '***'
db = 'city_data'

def show_databases():
  mydb = mysql.connect(host = host, user = user, 
                       passwd = passwd)
  cur = mydb.cursor()
  cur.execute('show databases')
  ptable = from_db_cursor(cur)
  cur.close()
  mydb.close()
  print ptable
  
def create_database(db_name):
  mydb = mysql.connect(host = host, user = user, 
                       passwd = passwd)
  cur = mydb.cursor()
  cur.execute('show databases')
  names = list(itertools.chain(*cur.fetchall()))
  if db_name not in names:
    cur.execute('CREATE DATABASE ' + db_name)
  cur.close()
  mydb.close()
    
  
def create_table(df, table_name):
  engine = create_engine('mysql://'+user+':'+passwd+'@'+host+'/'+db+'?charset=utf8')
  df.to_sql(name=table_name, con=engine, if_exists='replace', 
            flavor='mysql', index=False, chunksize=20000)
  
def read_table(table_name):
  engine = create_engine('mysql://'+user+':'+passwd+'@'+host+'/'+db+'?charset=utf8')
  df = pd.read_sql_query('select * from ' + table_name, engine)   
  return df
  
def query(cmd):
  mydb = mysql.connect(host = host, user = user, 
                       passwd = passwd, db = db)
  cur = mydb.cursor()
  cur.execute(cmd)
  df = cur.fetchall()
  cur.close()
  mydb.close()
  return df

def show_tables(db_name):
  mydb = mysql.connect(host = host, user = user, 
                       passwd = passwd, db = db)
  cur = mydb.cursor()
  cur.execute('SHOW TABLES FROM ' + db_name)
  ptables = from_db_cursor(cur)
  cur.close()
  mydb.close()
  print ptables    
  
def describe_table(table_name):
  mydb = mysql.connect(host = host, user = user, 
                       passwd = passwd, db = db)
  cur = mydb.cursor()
  cur.execute("DESCRIBE %s" %table_name)
  ptable = from_db_cursor(cur)
  cur.close()
  mydb.close()
  print ptable
  
def drop_table(table_name):
  mydb = mysql.connect(host = host, user = user, 
                       passwd = passwd, db = db)
  cur = mydb.cursor()
  cur.execute('DROP TABLE ' + table_name)
  cur.close()
  mydb.close()
  
    