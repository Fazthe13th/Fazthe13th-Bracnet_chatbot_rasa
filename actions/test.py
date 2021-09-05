import psycopg2
import itertools
from operator import itemgetter
import json


class DatabaseConnection():
    def __init__(self) -> None:
        self.db_name = "bracnet_chatbot"
        self.db_user = "bracnet_chatbot"
        self.db_password = "W28ASu2b"
        self.db_host = "202.168.254.243"

    def db_connect(self):
        conn = psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password)
        return conn

    def QuerySalesContact(self, cur):
        cur.execute(
            "SELECT contact_name,zone,sales_division,phone_number FROM public.tbl_sales_contact")
        row = cur.fetchall()
        cur.close()
        return row

    def QueryPackageInfo(self, cur):
        cur.execute(
            """SELECT package_name, package_price, otc
            FROM public.tbl_internet_packages""")
        row = cur.fetchall()
        cur.close()
        return row

    def QueryIntentBySenderID(self, conn, sender_id):
        cur = conn.cursor()
        cur.execute(
            """SELECT intent_name
            FROM public.events where sender_id = %s and intent_name IN (
                'available_services','managed_services','video_conferencing',
                'smart_home','IP_phone','intranet','package_information','sales_contact')""", (sender_id,))
        row = cur.fetchall()
        cur.close()
        conn.close()
        return row

    def InsertIntoLeads(self, sender_id, client_name, client_phone, intents):
        DbObject = DatabaseConnection()
        conn = DbObject.db_connect()
        sql = """INSERT INTO tbl_leads(sender_id, client_name, client_phone, intents)
             VALUES(%s, %s, %s, %s)"""
        try:
            cur = conn.cursor()
            cur.execute(sql, (sender_id, client_name, client_phone, intents))
            # commit the changes to the database
            conn.commit()
            # close communication with the database
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            if conn is not None:
                conn.close()


# DbObject = DatabaseConnection()
# DBConnection = DbObject.db_connect()
# sales_rows_list = [list(i) for i in DbObject.QuerySalesContact(DBConnection)]
sender_id = '68941c21437140bb984af3c89f97d948'
DbObject = DatabaseConnection()
DBConnection = DbObject.db_connect()
intents = DbObject.QueryIntentBySenderID(DBConnection, sender_id)
count = 0
lst = []
for intent in intents:
    lst.append(("intent_"+str(count), intent[0]))
    count += 1

rs = json.dumps(dict(lst))
print(rs)
DbObject.InsertIntoLeads(sender_id, client_name="Evan",
                         client_phone="01836366667", intents=rs)
