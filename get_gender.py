#!usr/bin/python2

import sys
import os
import subprocess
from sqlalchemy import create_engine

"""
python2 script that get gender info from samples_be.sqlite3 using sample_id e.g.17027602
"""

# author: Tengyue Zheng
# date: 12/02/2020

#drv = 'DRIVER={Microsoft Access Driver (*mdb, *.accdb)};'
#mdb = 'DBQ={};'.format(sample_db)
#server = 'Server=cmftgm03;'
#Database='Database=db_name'

#sample_db = "tz1@172.31.4.13:/SystemData$/D-LIMS/Live/Database/samples_be.mdb"
#sample_db = "/mnt/msad-lims/Live/Database/samples_be.mdb"
sample_db = "/users/tz1/git/decipher_api_upload/samples_be.db"

def connect_to_db(sample_db):

    # create engine to connect to samples database
    engine = create_engine('sqlite:///{0}'.format(sample_db))
    conn = engine.connect()

    return conn
    
def run_query_in_db(lab_id, conn):
    
    # parse SQL query to database
         
    query = "SELECT Gender from Samples where labno = {}".format(lab_id)
    print (query)

    result = conn.execute(query)
    for row in result:
        print (row[0])
        return str(row[0])

def disconnect_to_db(conn):
    conn.close()  
        
def main(lab_id):
    
    conn = connect_to_db(sample_db)
    gender = run_query_in_db(lab_id, conn)
    
if __name__ == "__main__":
    main(sys.argv[1])


