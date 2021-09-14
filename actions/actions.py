# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from chatbot import actions
import psycopg2
import mysql.connector
import datetime
import itertools
import json
from operator import itemgetter
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict


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

    def QuerySalesContact(self, conn):
        cur = conn.cursor()
        cur.execute(
            "SELECT contact_name,zone,sales_division,phone_number FROM public.tbl_sales_contact")
        row = cur.fetchall()
        cur.close()
        conn.close()
        return row

    def QueryPackageInfo(self, conn):
        cur = conn.cursor()
        cur.execute(
            """SELECT package_name, package_price, otc
            FROM public.tbl_internet_packages""")
        row = cur.fetchall()
        cur.close()
        conn.close()
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
    # 360 specific functions

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


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []


class ActionSetNewCustomer(Action):

    def name(self) -> Text:
        return "action_new_customer_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response="utter_new_customer_response")
        dispatcher.utter_message(response="utter_what_info_new_customer_needs")
        return [SlotSet("new_customer", True), SlotSet("existing_customer", False)]


class ActionSetExistingCustomer(Action):

    def name(self) -> Text:
        return "action_old_customer_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response="utter_old_customer_response")
        dispatcher.utter_message(response="utter_ask_oraganization_RDP")
        return [SlotSet("new_customer", False), SlotSet("existing_customer", True)]


class ActionOrganizationClient(Action):

    def name(self) -> Text:
        return "action_organization_client"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # dispatcher.utter_message(response="utter_old_customer_response")
        # dispatcher.utter_message(response="utter_ask_oraganization_RDP")
        return [SlotSet("organization_client", True), SlotSet("rdp_client", False)]


class ActionRDPClient(Action):

    def name(self) -> Text:
        return "action_rdp_client"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response="utter_old_customer_response")
        # dispatcher.utter_message(response="utter_ask_oraganization_RDP")
        return [SlotSet("oganization_client", False), SlotSet("rdp_client", True)]


class ActionPackageInformation(Action):

    def name(self) -> Text:
        return "action_package_information"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
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
        dispatcher.utter_message(text=package_str)
        return []


class ActionSalesContact(Action):

    def name(self) -> Text:
        return "action_sales_contact"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        DbObject = DatabaseConnection()
        DBConnection = DbObject.db_connect()
        sales_rows_list = [list(i)
                           for i in DbObject.QuerySalesContact(DBConnection)]
        contact_str = ''
        for key, group in itertools.groupby(sorted(sales_rows_list, key=itemgetter(2)), lambda x: x[2]):
            for i in list(group):
                for j in i:
                    contact_str = contact_str + str(j) + ","
                contact_str = contact_str[:-1]
                contact_str += "\n"
        dispatcher.utter_message(text=contact_str)
        return []


class ActionAvailableZone(Action):

    def name(self) -> Text:
        return "action_available_zones"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        package_text = "zone"
        dispatcher.utter_message(text=package_text)
        return []


class ValidateLeadsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_leads_form"

    def validate_client_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `client_name` value."""
        if len(slot_value) <= 2:
            dispatcher.utter_message(
                text=f"That's a very short name. I'm assuming you mis-spelled.")
            return {"client_name": None}
        else:
            return {"client_name": slot_value}

    def validate_client_phone(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `client_phone` value."""
        if len(slot_value) <= 2:
            dispatcher.utter_message(
                text=f"That's a very short name. I'm assuming you mis-spelled.")
            return {"client_phone": None}
        else:
            return {"client_phone": slot_value}


class ActionSubmitLeadsForm(Action):
    def name(self) -> Text:
        return "action_submit_leads_form"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        client_name_full = tracker.get_slot("client_name")
        client_phone_number = tracker.get_slot("client_phone")
        sender_id = tracker.current_state()['sender_id']
        dispatcher.utter_message(
            text=f"Thank you for your information, your name is {client_name_full} and phone number is {client_phone_number} and sender_id is {sender_id}")
        DbObject = DatabaseConnection()
        DBConnection = DbObject.db_connect()
        intents = DbObject.QueryIntentBySenderID(DBConnection, sender_id)
        count = 0
        lst = []
        for intent in intents:
            lst.append(("intent_"+str(count), intent[0]))
            count += 1

        rs = json.dumps(dict(lst))
        DbObject.InsertIntoLeads(sender_id, client_name_full,
                                 client_phone_number, rs)
        return [SlotSet("client_name", tracker.get_slot("client_name")), SlotSet("client_phone", tracker.get_slot("client_phone"))]


class ValidateOraganizationForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_organization_form"

    def validate_crm_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `crm_id` value."""
        crm_id = str(slot_value).strip()
        DbObject = DatabaseConnection()
        DBConnection = DbObject.db_connect()
        crm_id_row = DbObject.QueryCRMID(DBConnection, crm_id)
        if crm_id_row is None:
            dispatcher.utter_message(
                text=f"Sorry cound not find any branch id with {crm_id}")
            return {"crm_id": None}
        else:
            return {"crm_id": slot_value}

    def validate_crm_password(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `crm_password` value."""
        crm_id = str(tracker.get_slot("crm_id")).strip()
        crm_password = str(tracker.get_slot("crm_password")).strip()
        DbObject = DatabaseConnection()
        DBConnection = DbObject.db_connect()
        login = DbObject.QueryCRMLogin(DBConnection, crm_id, crm_password)
        if login is None:
            dispatcher.utter_message(
                text=f"Sorry your username and password did not match. Please give the password again.")
            return {"crm_password": None}
        else:
            dispatcher.utter_message(text=f"Welcome {login[1]}")
            return {"crm_password": slot_value}
        # if len(slot_value) <= 2:
        #     dispatcher.utter_message(
        #         text=f"Password should not be that short.")
        #     return {"crm_password": None}
        # else:
        #     return {"crm_password": slot_value}


class ActionSubmitOrganizationForm(Action):
    def name(self) -> Text:
        return "action_submit_organization_form"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        crm_id = str(tracker.get_slot("crm_id")).strip()
        crm_password = str(tracker.get_slot("crm_password")).strip()
        dispatcher.utter_message(response="utter_ask_organization_options")
        return [SlotSet("crm_id", crm_id), SlotSet("crm_password", crm_password), SlotSet("org_logged_in", True), SlotSet("rdp_logged_in", False)]


# class ActionOraganizationNumberofLinks(Action):

#     def name(self) -> Text:
#         return "action_organization_number_of_links"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(text="Organization number of links")
#         return []


# class ActionOrganizationBandwidth(Action):

#     def name(self) -> Text:
#         return "action_organization_bandwidth"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(text="Organization Bandwidth")
#         return []


class ActionOrganizationLastPaymentInfo(Action):

    def name(self) -> Text:
        return "action_organization_last_payment_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        DbObject = DatabaseConnection()
        if tracker.get_slot("org_logged_in") is True:
            crm_id = str(tracker.get_slot("crm_id")).strip()
            # crm_password = str(tracker.get_slot("crm_password")).strip()
            BnSystemDBConnection = DbObject.bnsystem_db_connect()
            lastPayment = DbObject.QueryLastPayment(
                BnSystemDBConnection, crm_id)
            dispatcher.utter_message(
                text=f"Paid amount {lastPayment[0]}, Billed amount {lastPayment[1]}, payment date {lastPayment[2]} and bill status is {'unapproved' if lastPayment[3] == 11 else 'approved'}")
        else:
            dispatcher.utter_message(text="Your are not logged in yet")
            dispatcher.utter_message(response="utter_ask_oraganization_RDP")
        return []


# class ActionOrganizationCurrentPackage(Action):

#     def name(self) -> Text:
#         return "action_organization_current_package"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(text="Organization current package")
#         return []


class ActionOrganizationNextPayment(Action):

    def name(self) -> Text:
        return "action_oraganization_next_payment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        DbObject = DatabaseConnection()
        if tracker.get_slot("org_logged_in") is True:
            crm_id = str(tracker.get_slot("crm_id")).strip()
            # crm_password = str(tracker.get_slot("crm_password")).strip()
            BnSystemDBConnection = DbObject.bnsystem_db_connect()
            nextPayment = DbObject.QueryNextPayment(
                BnSystemDBConnection, crm_id)
            dispatcher.utter_message(
                text=f"Your next bill amount is {nextPayment[0]}, Next possible bill date will be {nextPayment[1]+ datetime.timedelta(days=nextPayment[3]) if nextPayment[2] == '0000-00-00' else nextPayment[2]+ datetime.timedelta(days=nextPayment[3])}")
        else:
            dispatcher.utter_message(text="Your are not logged in yet")
            dispatcher.utter_message(response="utter_ask_oraganization_RDP")

        return []


class ActionOrganizationCreateTicket(Action):

    def name(self) -> Text:
        return "action_oraganization_create_ticket"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("org_logged_in") is True:
            dispatcher.utter_message(text="Organization create ticket")
        else:
            dispatcher.utter_message(text="Your are not logged in yet")
            dispatcher.utter_message(response="utter_ask_oraganization_RDP")

        return []


class ActionOrganizationCurrentActiveTicket(Action):

    def name(self) -> Text:
        return "action_organization_current_active_ticket"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("org_logged_in") is True:
            dispatcher.utter_message(text="Organization current active ticket")
        else:
            dispatcher.utter_message(text="Your are not logged in yet")
            dispatcher.utter_message(response="utter_ask_oraganization_RDP")

        return []
# Fall back action override


class ActionDefaultFallback(Action):

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # custom behavior
        if tracker.slots.get("new_customer") is True:
            dispatcher.utter_message(
                response="utter_ask_rephrase")
            dispatcher.utter_message(
                response="utter_what_info_new_customer_needs")
        elif tracker.slots.get("org_logged_in") is True and tracker.slots.get("rdp_logged_in") is False:
            dispatcher.utter_message(
                response="utter_ask_rephrase")
            dispatcher.utter_message(
                response="utter_ask_organization_options")
        else:
            dispatcher.utter_message(
                response="utter_ask_rephrase")
        return None
