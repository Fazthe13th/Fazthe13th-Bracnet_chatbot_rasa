import psycopg2
import mysql.connector
import datetime
import itertools
from operator import itemgetter
import json


class DatabaseConnection():
    def __init__(self) -> None:
        self.db_name = "bracnet_chatbot"
        self.db_user = "bracnet_chatbot"
        self.db_password = "W28ASu2b"
        self.db_host = "202.168.254.243"
        self.bnsystem_db_name = "bnsystem"
        self.bnsystem_db_user = "root"
        self.bnsystem_db_password = "9256174"
        self.bnsystem_db_host = "115.127.200.6"

    def db_connect(self):
        conn = psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password)
        return conn

    def bnsystem_db_connect(self):
        conn_bnsystem = mysql.connector.connect(
            host=self.bnsystem_db_host,
            user=self.bnsystem_db_user,
            password=self.bnsystem_db_password
        )
        return conn_bnsystem

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

    def QueryCRMID(self, conn, crm_id):
        cur = conn.cursor()
        cur.execute(
            """SELECT org_crm_id
            FROM public.tbl_organization_cred where org_crm_id = %s """, (crm_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row

    def QueryCRMLogin(self, conn, crm_id, crm_password):
        cur = conn.cursor()
        cur.execute(
            """SELECT org_crm_id,org_name
            FROM public.tbl_organization_cred where org_crm_id = %s and org_password = %s""", (crm_id, crm_password))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row

    def QueryLastPayment(self, conn, crm_id):
        cur = conn.cursor()
        cur.execute(
            """SELECT TransAmountAdd,TransAmountSub,TransDate,TransStatusId 
            FROM bnsystem.view_billing_account_trans_master 
            where ClientId = %s and TransStatusId in (11,13) 
            order by TransDate desc 
            limit 1""", (crm_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row

    def QueryNextPayment(self, conn, crm_id):
        cur = conn.cursor()
        cur.execute(
            """SELECT sum(UnitSalePrice),BillingStartDate, BilledUptoDate,CycleDayValue,BillingTypeName 
            FROM bnsystem.view_billing_clients_service_profile 
            where ClientId= %s and ServiceStatusId = 3 and BillingTypeName != "One Time Bill" 
            order by BilledUptoDate desc 
            limit 1""", (crm_id,))
        row = cur.fetchone()
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
    # def InsertIntoTicket(self, *args):
    #     DbObject = DatabaseConnection()
    #     conn = DbObject.db_connect()
    #     sql = """INSERT INTO bnsystem.tbl_technical_support_ticket
    #         (TicketID,
    #         TicketTypeId,
    #         StatusId,
    #         ModeId,
    #         SupportCateId,
    #         LevelId,
    #         PriorityId,
    #         BillServiceID,
    #         ClientId,
    #         POPId,
    #         AccountName,
    #         ContactName,
    #         ContactNumber,
    #         ContactCellNumber,
    #         ContactEmail,
    #         AddressId,
    #         AssignGroupId,
    #         TicketSubject,
    #         TicketDetails,
    #         SLAId,
    #         DueTime,
    #         FaultDetectionTime,
    #         DuebyTime,
    #         ResponseDueBy,
    #         CreatedOn,
    #         CreatedBy,
    #         LastEditBy,
    #         LastEditOn,
    #         PickupOn,
    #         TechID,
    #         PickupBy,
    #         PopEffectedClientIds,
    #         PopEffectedServiceIds,
    #         PopEffectedClientParentIds,
    #         PopEffectedTechIDs)
    #         VALUES(%s, %s, %s, %s)"""
    #     try:
    #         cur = conn.cursor()
    #         cur.execute(sql, (sender_id, client_name, client_phone, intents))
    #         # commit the changes to the database
    #         conn.commit()
    #         # close communication with the database
    #         cur.close()
    #     except (Exception, psycopg2.DatabaseError) as error:
    #         print(error)
    #     finally:
    #         if conn is not None:
    #             conn.close()


# DbObject = DatabaseConnection()
# DBConnection = DbObject.db_connect()
# sales_rows_list = [list(i) for i in DbObject.QuerySalesContact(DBConnection)]
crm_id = '1006458'.strip()
crm_password = "12345".strip()
DbObject = DatabaseConnection()
BnSystemDBConnection = DbObject.bnsystem_db_connect()
DBConnection = DbObject.db_connect()
intents = DbObject.QueryCRMLogin(DBConnection, crm_id, crm_password)
data = DbObject.QueryLastPayment(BnSystemDBConnection, crm_id)
# dummy_start_date = "00/00/0000"
# date_1 = datetime.datetime.strptime(dummy_start_date, "%m/%d/%y")
BnSystemDBConnection = DbObject.bnsystem_db_connect()

nextPayment = DbObject.QueryNextPayment(BnSystemDBConnection, crm_id)
print(nextPayment)
print(f"Your next bill amount is {nextPayment[0]}, Next possible bill date will be {nextPayment[1]+ datetime.timedelta(days=nextPayment[3]) if nextPayment[2] == '0000-00-00' else nextPayment[2]+ datetime.timedelta(days=nextPayment[3])}")
print(
    f"Paid amount {data[0]}, Billed amount {data[1]}, payment date {data[2]} and bill status {data[3]}")

# INSERT INTO bnsystem.tbl_technical_support_ticket
# (TicketID,
# TicketTypeId,
# StatusId,
# ModeId,
# SupportCateId,
# LevelId,
# PriorityId,
# BillServiceID,
# ClientId,
# POPId,
# AccountName,
# ContactName,
# ContactNumber,
# ContactCellNumber,
# ContactEmail,
# AddressId,
# AssignGroupId,
# TicketSubject,
# TicketDetails,
# SLAId,
# DueTime,
# FaultDetectionTime,
# DuebyTime,
# ResponseDueBy,
# CreatedOn,
# CreatedBy,
# LastEditBy,
# LastEditOn,
# PickupOn,
# TechID,
# PickupBy,
# PopEffectedClientIds,
# PopEffectedServiceIds,
# PopEffectedClientParentIds,
# PopEffectedTechIDs)
# VALUES
# (<{TicketID: }>,
# <{TicketTypeId: }>,
# <{StatusId: 0}>,
# <{ModeId: 0}>,
# <{SupportCateId: 0}>,
# <{LevelId: }>,
# <{PriorityId: 0}>,
# <{BillServiceID: 0}>,
# <{ClientId: 0}>,
# <{POPId: 0}>,
# <{AccountName: }>,
# <{ContactName: }>,
# <{ContactNumber: }>,
# <{ContactCellNumber: }>,
# <{ContactEmail: }>,
# <{AddressId: 0}>,
# <{AssignGroupId: 0}>,
# <{TicketSubject: }>,
# <{TicketDetails: }>,
# <{SLAId: }>,
# <{DueTime: 0000-00-00 00:00:00}>,
# <{FaultDetectionTime: 0000-00-00 00:00:00}>,
# <{DuebyTime: }>,
# <{ResponseDueBy: }>,
# <{CreatedOn: 0000-00-00 00:00:00}>,
# <{CreatedBy: 0}>,
# <{LastEditBy: 0}>,
# <{LastEditOn: CURRENT_TIMESTAMP}>,
# <{PickupOn: 0000-00-00 00:00:00}>,
# <{TechID: }>,
# <{PickupBy: 0}>,
# <{PopEffectedClientIds: }>,
# <{PopEffectedServiceIds: }>,
# <{PopEffectedClientParentIds: }>,
# <{PopEffectedTechIDs: }>);
