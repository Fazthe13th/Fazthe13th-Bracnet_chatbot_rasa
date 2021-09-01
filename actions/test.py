import psycopg2
import itertools
from operator import itemgetter


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
        cur = conn.cursor()
        return cur

    def QuerySalesContact(self, cur):
        cur.execute(
            "SELECT contact_name,zone,sales_division,phone_number FROM public.tbl_sales_contact")
        row = cur.fetchall()
        cur.close()
        return row


DbObject = DatabaseConnection()
DBConnection = DbObject.db_connect()
sales_rows_list = [list(i) for i in DbObject.QuerySalesContact(DBConnection)]
contact_str = ''
for key, group in itertools.groupby(sorted(sales_rows_list, key=itemgetter(2)), lambda x: x[2]):
    for i in list(group):
        for j in i:
            contact_str = contact_str + str(j) + ","
        contact_str = contact_str[:-1]
        contact_str += "\n"
