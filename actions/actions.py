# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


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
        # SlotSet("existing_customer", False)
        # return [SlotSet("new_customer", True)]
        return [SlotSet("new_customer", True), SlotSet("existing_customer", False)]


class ActionSetExistingCustomer(Action):

    def name(self) -> Text:
        return "action_old_customer_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response="utter_old_customer_response")
        # SlotSet("new_customer", False)
        # return [SlotSet("existing_customer", True)]
        return [SlotSet("new_customer", False), SlotSet("existing_customer", True)]


class ActionPackageInformation(Action):

    def name(self) -> Text:
        return "action_package_information"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        package_text = "package"
        dispatcher.utter_message(text=package_text)
        return []


class ActionSalesContact(Action):

    def name(self) -> Text:
        return "action_sales_contact"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        package_text = "contact"
        dispatcher.utter_message(text=package_text)
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


class ValidateRestaurantForm(Action):
    def name(self) -> Text:
        return "leads_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        required_slots = ["client_name", "client_phone"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]


class ActionSubmit(Action):
    def name(self) -> Text:
        return "action_submit_survey_from"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_details_thanks",
                                 Name=tracker.get_slot("name"),
                                 Mobile_number=tracker.get_slot("number"))
