#!usr/bin/python2

import sys
import os
import subprocess
#from sqlalchemy import create_engine
#import pyodbc


"""
python2 script that get gender info from samnpledb, using sample_id e.g.17027602
"""

# author: Tengyue Zheng
# date: 20/01/2020

"""
mdb = r'DBQ=/mnt/msad-lims/Live/Database/samples_be.mdb;'
drv = r'DRIVER={Microsoft Access Driver (*.mdb,*.accdb)};'
query = "select Gender from Samples where labno = {}".format(lab_id)
"""
sample_db = "tz1@172.31.4.13:/SystemData$/D-LIMS/Live/Database/samples_be.mdb"

"""
def connect_to_db(sample_db):

    engine = create_engine('mssql+pyodbc://'.format(sample_db))
    
    conn = engine.connect()
    #conn = pyodbc.connect('%s %s' % (drv, mdb))
    print (engine.table_names)
    return conn
    
    #cursor = conn.cursor()
    #return cursor
"""

def run_query_in_db(lab_id):
    
    # parse SQL query to database
    
    #data_rows = cursor.execute(query).fetchall()
    
    #cursor.close()
    
    cmd = "echo 'select Gender from Samples where labno = \'%s\'' | mdb-sql -FHp /mnt/msad-lims/Live/Database/samples_be.mdb" % lab_id
    output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    print (output)
    #data_rows = subprocess.Popen([mdb, flag, db], stdin=sql_query.stdout, universal_newlines=True, shell=True, stdout=subprocess.PIPE).stdout
    #print (data_rows)
    
    """
    for row in data_rows:
        if row.startswith("1"):
            print ("{}: {}".format(labid, "male"))
            return "male"
        
        elif row.startswith("2"):
            print ("{}: {}".format(labid, "female"))
            return "female"
        else:
            break
    """
    
def main(lab_id):
    
    #conn = connect_to_db(sample_db)
    gender = run_query_in_db(lab_id)
    
if __name__ == "__main__":
    main(sys.argv[1])


