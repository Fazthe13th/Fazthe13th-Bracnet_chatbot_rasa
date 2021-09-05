# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from chatbot import actions
import psycopg2
import itertools
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

# class ValidateLeadsForm(Action):
#     def name(self) -> Text:
#         return "leads_form"

#     def run(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> List[Dict[Text, Any]]:
#         required_slots = ["client_name", "client_phone"]

#         for slot_name in required_slots:
#             if tracker.slots.get(slot_name) is None:
#                 # The slot is not filled yet. Request the user to fill this slot next.
#                 return [SlotSet("requested_slot", slot_name)]

#         # All slots are filled.
#         return [SlotSet("requested_slot", None)]


class ActionSubmitLeadsForm(Action):
    def name(self) -> Text:
        return "action_submit_leads_form"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Thank you for your information")
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
