#!/usr/bin/env python

import MySQLdb

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="XXX",  # your password
                     db="molecular_rotors",
                     charset='utf8')        # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()
table_name="energies"
oldcolumn_name="s1min_t"
newcolumn_name="s1min_t"

command="ALTER TABLE {} CHANGE {} {} double(12,9)".format(table_name,oldcolumn_name,newcolumn_name)


for i in range(1,2):
    old=oldcolumn_name+str(i)
    new=newcolumn_name+str(i)
    command="ALTER TABLE {} CHANGE {} {} decimal(12,9)".format(table_name,old,new)
    cur.execute(command)
