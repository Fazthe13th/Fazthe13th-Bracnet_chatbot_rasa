# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from chatbot import actions
import psycopg2
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

    def db_connect(self):
        conn = psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password)
        return conn

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
        return [SlotSet("new_customer", False), SlotSet("existing_customer", True)]


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


class ValidateNameForm(FormValidationAction):
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
        return None
