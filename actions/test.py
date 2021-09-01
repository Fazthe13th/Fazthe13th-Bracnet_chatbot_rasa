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

    def QueryPackageInfo(self, cur):
        cur.execute(
            """SELECT package_name, package_price, otc
            FROM public.tbl_internet_packages""")
        row = cur.fetchall()
        cur.close()
        return row


# DbObject = DatabaseConnection()
# DBConnection = DbObject.db_connect()
# sales_rows_list = [list(i) for i in DbObject.QuerySalesContact(DBConnection)]
package_str = ''
DbObject = DatabaseConnection()
DBConnection = DbObject.db_connect()
package_info_list = [list(i)
                     for i in DbObject.QueryPackageInfo(DBConnection)]
for i in package_info_list:
    package_str = package_str + \
        str(i[0])+", package price: "+str(i[1]) + \
        ", Installation charge: "+str(i[2])
    package_str = package_str[:-1]
    package_str += "\n"
print(package_str)
