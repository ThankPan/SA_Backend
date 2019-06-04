from neomodel import *

# config the neo4j DB
config.DATABASE_URL = "bolt://neo4j:123456@www.buaatech.top:7687"

# clear the database
clear_neo4j_database(db)

# config the datasource
paper_data_path = "path1"
patent_data_path = "path2"
author_data_path = "path3"

#import the data
'''
    do some code here
'''