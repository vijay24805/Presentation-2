import logging

log = logging.getLogger()
log.setLevel('DEBUG')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

#import Cluster from Cassandra python driver

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

# keyspace is the container for your application data, similar to a schema in a relational database.
KEYSPACE = "classdemo"


def main():
    #Refers to the cluster at local host.
    cluster = Cluster(['127.0.0.1'])
	#all queries are executed using session
    session = cluster.connect()

    rows = session.execute("SELECT keyspace_name FROM system.schema_keyspaces")
    if KEYSPACE in [row[0] for row in rows]:
        log.info("dropping existing keyspace...")
        session.execute("DROP KEYSPACE " + KEYSPACE)

    # Creates the Keyspace
    log.info("creating keyspace...")
    session.execute("""
        CREATE KEYSPACE %s
        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
        """ % KEYSPACE)

    log.info("setting keyspace...")
    session.set_keyspace(KEYSPACE)

    log.info("creating table...")
    session.execute("""
        CREATE TABLE mytable (
            thekey text,
            col1 text,
            col2 text,
            PRIMARY KEY (thekey, col1)
        )
        """)
	
	#insert Rows into the Table
    enter_rows = SimpleStatement("""
        INSERT INTO mytable (thekey, col1, col2)
        VALUES (%(key)s, %(a)s, %(b)s)
        """, consistency_level=ConsistencyLevel.ONE)

    prepared = session.prepare("""
        INSERT INTO mytable (thekey, col1, col2)
        VALUES (?, ?, ?)
        """)

	#Inserting 10 rows
    for i in range(10):
        log.info("inserting row %d" % i)
        session.execute(enter_rows, dict(key="key%d" % i, a='data1', b='data2'))
        session.execute(prepared, ("key%d" % i, 'data3', 'data4'))

    #Fetch All the Rows and displays them
    select_all_rows = session.execute_async("SELECT * FROM mytable")
    log.info("key\tcol1\tcol2")
    log.info("---\t----\t----")

    try:
        rows = select_all_rows.result()
    except Exception:
        log.exeception()

    for row in rows:
        log.info('\t'.join(row))

    # Drop keyspace after all operations
    session.execute("DROP KEYSPACE " + KEYSPACE)

if __name__ == "__main__":
    main()



