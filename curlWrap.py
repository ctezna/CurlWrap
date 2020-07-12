import os, sys
from datetime import datetime
import sqlite3
from sqlite3 import Error


class Database():

    def __init__(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        database = os.path.join(basedir, 'curldata.db')
        if not os.path.isfile(database):
            open(database, 'a').close()
        self.session = self.create_connection(database)

        sql_create_table = """ CREATE TABLE IF NOT EXISTS curldata (
                                        id integer PRIMARY KEY,
                                        url text,
                                        ip text,
                                        port text,
                                        code text,
                                        ssl text,
                                        totaltime text,
                                        timedns text,
                                        dlsize text,
                                        headersize text,
                                        dlspeed text,
                                        numconn text,
                                        numredir text,
                                        localip text,
                                        localport text,
                                        contenttype text,
                                        timestamp text
                                    ); """

            # create tables
        if self.session is not None:
            # create projects table
            self.create_table(self.session, sql_create_table)
        else:
            print("Error! cannot create the database connection.")


    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

        return conn


    def create_table(self, conn, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def insert_data(self, sql, data):
        """
        Insert data into db
        :param conn:
        :param project:
        :return: project id
        """
        cur = self.session.cursor()
        cur.execute(sql, data)
        self.session.commit()
        return cur.lastrowid

    def query(self, sql):
        """
        Query all rows in the tasks table
        :param conn: the Connection object
        :return:
        """
        cur = self.session.cursor()
        cur.execute(sql)

        rows = cur.fetchall()

        for row in rows:
            print(row)

class CurlWrap():

    def build_curl(self, opts, urls):
        curl_cmd = 'curl -w "\n&&curl_test_389sk39&&\nURL:: %{url_effective}\nIP:: %{remote_ip}\nPort:: %{remote_port}\n' + \
        'Code:: %{response_code}\nSSL:: %{ssl_verify_result}\nTotal Time:: %{time_total}\n' + \
        'Time Lookup:: %{time_namelookup}\nDownload Size:: %{size_download}\n' + \
        'Header Size:: %{size_header}\nDownload Speed:: %{speed_download}\n' + \
        'Number Connects:: %{num_connects}\nNumber Redirects:: %{num_redirects}\n' + \
        'Local IP:: %{local_ip}\nLocal Port:: %{local_port}\nContent Type:: %{content_type}" '
        return (curl_cmd + opts + ' ' + urls)

    def run_curl(self, opts, urls):
        return self.extract_curl_data(os.popen(self.build_curl(opts, urls)).read())

    def extract_curl_data(self, curl_result):
        key = '&&curl_test_389sk39&&\n'
        data = curl_result[curl_result.find(key):].replace(key, '').split('\n')
        vals = [d.split('::')[1].strip() for d in data]
        keys = [d.split('::')[0].strip() for d in data]
        result = {}
        for i, val in enumerate(vals):
            result[keys[i]] = val

        return result


if __name__ == "__main__":
    curl = CurlWrap()
    db = Database()
    now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    result = curl.run_curl(sys.argv[1], sys.argv[2])
    result['timestamp'] = now
    sql = ''' INSERT INTO curldata(url,ip,port,code,ssl,totaltime,timedns,dlsize,headersize,\
                dlspeed,numconn,numredir,localip,localport,contenttype,timestamp)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    #data = tuple([v for k, v in result.items()])
    data = (result['URL'], result['IP'], result['Port'], result['Code'], \
            result['SSL'], result['Total Time'], result['Time Lookup'], \
            result['Download Size'], result['Header Size'], result['Download Speed'], \
            result['Number Connects'], result['Number Redirects'], result['Local IP'], \
            result['Local Port'], result['Content Type'], result['timestamp'],)
    log = db.insert_data(sql, data)
    #print(data)
    query = 'SELECT * FROM curldata WHERE url="http://www.fabysclean.com/"'
    db.query(query)
    pass