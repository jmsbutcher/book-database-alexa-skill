# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import datetime
import mysql.connector
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Global database and cursor variables, so doesn't have to reconnect every time an intent is triggered
mydb = None
cursor = None

def connect_to_database():
    """ Global mydb and cursor variables ensure you only need to connect once per session """
    global mydb
    global cursor
    if mydb is None:
        mydb = mysql.connector.connect(
                host="**************",
                port=3306,
                user="*****************",
                password="**************"
                )
        cursor = mydb.cursor()
        cursor.execute("USE aws_sql_test")
    return mydb, cursor


# Converter between spoken month name and how it is represented in the database tables
months_dict = {
        "" : "",  # To handle NULL months (which actually consist of empty strings, not NULL)
        "january": "Jan",
        "february": "Feb",
        "march": "Mar",
        "april": "Apr",
        "may": "May",
        "june": "Jun",
        "july": "Jul",
        "august": "Aug",
        "september": "Sep",
        "october": "Oct",
        "november": "Nov",
        "december": "Dec"
    }

reverse_months_dict = {v:k for k,v in months_dict.items()}

def months_converter(month_input):
    """ Catches any incorrect spoken month values and returns an empty string. """
    if month_input.lower() in months_dict.keys():
        return months_dict[month_input.lower()]
    else:
        return ""


def format_converter(format_input):
    """ Converter between spoken format input and format representation in tables """
    formats = {
        "audiobook": "Audiobook",
        "kindle": "Ebook",
        "print book": "Book",
        "book": "Book"
        }
    if format_input.lower() in formats.keys():
        return formats[format_input.lower()]
    else:
        return ""
    
def overall_format_converter(old_format, added_format):
    """ Handles updates to overall_format column in books table when a new read instance is added. """
    if old_format == added_format:
        return old_format
    elif (old_format == "Audiobook" and added_format == "Book") or \
         (old_format == "Book" and added_format == "Audiobook"):
        return "Book/Audio"
    elif (old_format == "Ebook" and added_format == "Audiobook") or \
         (old_format == "Audiobook" and added_format == "Ebook"):
        return "Ebook/Audio"
    elif (old_format == "Ebook" and added_format == "Book") or \
         (old_format == "Book" and added_format == "Ebook"):
        return "Book/Ebook"
    elif (old_format == "Book/Ebook" and added_format == "Audiobook") or \
         (old_format == "Book/Audio" and added_format == "Ebook") or \
         (old_format == "Ebook/Audio" and added_format == "Book"):
        return "Book/Ebook/Audio"
    else:
        return old_format


# Forces unsure_input into either a 0 (default if none given) or a 1 (if any unsure response)
def unsure_converter(unsure_input):
    if unsure_input == "0":
        return "0"
    else:
        return "1"


# Separator between context strings in books table when a new read_instance is added
context_separator = " -- "

def context_converter(context_input):
    """ Removes apostrophes and quotation marks from context text to 
        avoid syntax errors with SQL queries.
        Also converts null response "no" into an empty string. """
    context_input = context_input.replace("'" , "")
    context_input = context_input.replace("\"" , "")
    if context_input == "no":
        return ""
    else:
        return context_input


def get_slot_value(slots, slot_name, default_value):
    """ Get the spoken text provided to the slot "slot_name".
        If the slot is empty, return the default_value. """
    if slots[slot_name].value is not None:
        slot_value = slots[slot_name].value
    else:
        slot_value = default_value
    return slot_value


class LaunchRequestHandler(AbstractRequestHandler):
    """ [Built-in] Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to your book database."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GetLastReadIntentHandler(AbstractRequestHandler):
    """ [My own custom] Handler for Get Last Read Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GetLastReadIntent")(handler_input)

    def handle(self, handler_input):
        mydb, cursor = connect_to_database()
        
        cursor.execute("SELECT title, author FROM read_instances WHERE id = (SELECT MAX(id) FROM read_instances)")
        title, author = cursor.fetchone()
        
        speak_output = "<speak>The last book you <w role='amazon:VBD'>read</w> was {} by {}.</speak>".format(title, author)
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("anything else?")
                .response
        )


class AddReadInstanceIntentHandler(AbstractRequestHandler):
    """ [My own custom] Handler for Add Read Instance Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AddReadInstanceIntent")(handler_input)
        
    def handle(self, handler_input):
        mydb, cursor = connect_to_database()
        
        # Get all the required read instance fields provided by the user
        slots = handler_input.request_envelope.request.intent.slots
        title = get_slot_value(slots, "title", "default_title").title()
        author = get_slot_value(slots, "author", "default_author").title()
        year = get_slot_value(slots, "read_year", "0000")
        month = months_converter(get_slot_value(slots, "read_month", ""))
        unsure = unsure_converter(get_slot_value(slots, "unsure_of_date", "0"))
        read_format = format_converter(get_slot_value(slots, "read_format", ""))
        context = context_converter(get_slot_value(slots, "read_context", ""))
        
        # Insert a row into the read_instances table
        insert_command = "INSERT INTO read_instances VALUES (DEFAULT," # DEFAULT takes the place of the id field, which auto-increments
        insert_command += "'{}',".format(title)
        insert_command += "'{}',".format(author) 
        insert_command += "'{}',".format(year)
        insert_command += "'{}',".format(month)
        insert_command += "'{}',".format(unsure)
        insert_command += "'{}',".format(read_format)
        insert_command += "'{}')".format(context)
        cursor.execute(insert_command)
        
        # Update books table
        command = "SELECT * FROM books WHERE title = '{}' AND author = '{}'".format(title, author)
        cursor.execute(command)
        row = cursor.fetchone()
        
        # If new book reading already exists in the books table:
        if row:
            # Increment times_read by 1
            command = "UPDATE books SET times_read = times_read + 1 WHERE id = {}".format(row[0])
            cursor.execute(command)
            
            # Update last_read_year and last_read_month
            command = "UPDATE books SET last_read_year = '{}', last_read_month = '{}' WHERE id = {}".format(year, month, row[0])
            cursor.execute(command)
            
            # Update read format
            updated_format = overall_format_converter(row[9], read_format)
            command = "UPDATE books SET overall_format = '{}' WHERE id = '{}'".format(updated_format, row[0])
            cursor.execute(command)
            
            # Concatenate new reading context onto overall context
            overall_context = context_converter(row[10]) + context_separator + context
            command = "UPDATE books SET overall_context = '{}' WHERE id = {}".format(overall_context, row[0])
            cursor.execute(command)
            
        # If it doesn't already exist, create a new book entry
        else:
            command = "INSERT INTO books VALUES (DEFAULT, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format( 
                        title, 
                        author, 
                        year,       # First read year
                        month,      # First read month
                        unsure, 
                        year,       # Last read year
                        month,      # Last read month
                        1,          # Initialize times read to 1
                        read_format, 
                        context)
            cursor.execute(command)
        
        mydb.commit()
        
        speak_output = "Okay. Added."
        #speak_output = title + " " + author + " " + year + " " + month + " " + unsure + " " + read_format + " " + context

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("anything else?")
                .response
        )

    
class DeleteLastReadInstanceIntentHandler(AbstractRequestHandler):
    """ [My own custom] Handler for Delete Last Read Instance Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DeleteLastReadInstanceIntent")(handler_input)

    def handle(self, handler_input):
        mydb, cursor = connect_to_database()
        
        # Get title and author of read instance to be deleted, to use for updating books table
        cursor.execute("SELECT title, author FROM read_instances ORDER BY id DESC LIMIT 1")
        title, author = cursor.fetchone()
        
        # Delete last row
        cursor.execute("DELETE FROM read_instances ORDER BY id DESC LIMIT 1")

        # Get all the row info of the deleted read instance's book in the books table
        command = "SELECT * FROM books WHERE title = '{}' AND author = '{}'".format(title, author)
        cursor.execute(command)
        row = cursor.fetchone()
        
        # If times_read is only 1, delete from the books table too
        if row[8] == 1:
            command = "DELETE FROM books WHERE id = {}".format(row[0])
            cursor.execute(command)
            
        else:
            # Decrement times read
            command = "UPDATE books SET times_read = times_read - 1 WHERE id = {}".format(row[0])
            cursor.execute(command)
            
            # Revert back to last read month and year by finding next most recent reading in read_instances.
            # If there isn't one, do nothing (The original last read date can't be recovered automatically.)
            command = "SELECT read_year, read_month FROM read_instances WHERE title = '{}' AND author = '{}' ORDER BY ID DESC LIMIT 1".format(title, author)
            cursor.execute(command)
            most_recent_reading = cursor.fetchone()
            if most_recent_reading:
                next_most_recent_year, next_most_recent_month = most_recent_reading
                command = "UPDATE books SET last_read_year = {}, last_read_month = '{}' WHERE id = {}".format(next_most_recent_year, next_most_recent_month, row[0])
                cursor.execute(command)
            
            # Remove last part of overall_context
            original_overall_context = row[10]
            separator_index = original_overall_context.rfind(context_separator)
            if separator_index != -1:
                updated_overall_context = original_overall_context[0: separator_index]
                command = "UPDATE books SET overall_context = '{}' WHERE id = {}".format(updated_overall_context, row[0])
                cursor.execute(command)
        
        mydb.commit()
        
        speak_output = "<speak>Okay. I deleted the last book you <w role='amazon:VBD'>read</w>. {} by {}. Want to add a new one?</speak>".format(title, author)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Okay. Anything else?")
                .response
        )


class GetNumberOfTimesReadIntentHandler(AbstractRequestHandler):
    """ [My own custom] Handler for Get Number of Times Read Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GetNumberOfTimesReadIntent")(handler_input)

    def handle(self, handler_input):
        mydb, cursor = connect_to_database()
        
        slots = handler_input.request_envelope.request.intent.slots
        title = slots["title"].value.title()

        if slots["author"].value is not None:
            author = slots["author"].value.title()
            cursor.execute("SELECT times_read FROM books WHERE title LIKE '%{}%' and author LIKE '%{}%'".format(title, author))
        else:
            cursor.execute("SELECT times_read FROM books WHERE title LIKE '%{}%'".format(title))
            
        times_read = cursor.fetchone()[0]
        
        speak_output = str(times_read)
        
        #speak_output = "<speak>You've <w role='amazon:VBD'>read</w> {} {} times.</speak>".format(title, times_read)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Anything else?")
                .response
        )


class LastTimeReadIntentHandler(AbstractRequestHandler):
    """ [My own custom] Handler for Last Time Read Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("LastTimeReadIntent")(handler_input)

    def handle(self, handler_input):
        mydb, cursor = connect_to_database()
        
        slots = handler_input.request_envelope.request.intent.slots
        title = slots["title"].value
        
        title_split = title.split(' ')
        refined_title = []
        for item in title_split:
            refined_item = item.strip('.')
            refined_item = refined_item.strip(',')
            refined_item = refined_item.strip(':')
            refined_item = refined_item.strip('!')
            refined_item = refined_item.strip('?')
            refined_title.append(refined_item)
        refined_title_list = ' '.join(refined_title)
        
        regexp_title = '[a-z :.,!?]*[0-9]*'.join(refined_title_list)
        regexp_title += '[a-z :.,!?]*[0-9]*'
        
        cursor.execute("SELECT title, last_read_year, last_read_month FROM books WHERE title REGEXP '{}'".format(regexp_title))
        result = cursor.fetchall()
        if result:
            speak_output = "<speak>"
            for row in result:
                title, read_year, read_month = row
                read_month = reverse_months_dict[read_month]
                speak_output += "You <w role='amazon:VBD'>read</w> {} in {} {}. ".format(title, read_month, read_year)
            speak_output += "</speak>"
        else:
            speak_output = "I couldn't find {} in the books table.".format(title)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Anything else?")
                .response
        )


class HowManyBooksReadDuringYearIntent(AbstractRequestHandler):
    """ [My own custom] Handler for How Many Books Read During a Year Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("HowManyBooksReadDuringYearIntent")(handler_input)

    def handle(self, handler_input):
        mydb, cursor = connect_to_database()
        
        slots = handler_input.request_envelope.request.intent.slots
        year = slots["year"].value

        if year:
            # If the user provided a specified year
            cursor.execute("SELECT COUNT(*) FROM read_instances WHERE read_year = {}".format(year))
            count = cursor.fetchone()[0]
            speak_output = "<speak>You <w role='amazon:VBD'>read</w> {} books in {}</speak>".format(count, year)
        else:
            # Use the current year - covering the utterance "How many books did I read this year?"
            cursor.execute("SELECT COUNT(*) FROM read_instances WHERE read_year = {}".format(datetime.datetime.now().year))
            count = cursor.fetchone()[0]
            speak_output = "<speak>You <w role='amazon:VBD'>read</w> {} books so far this year.</speak>".format(count)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Anything else?")
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """ [Built-in] Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """ [Built-in] Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """ [Built-in] Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """ [Built-in] Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """ [Built-in] The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """ [Built-in] Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, please try again. "

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetLastReadIntentHandler())
sb.add_request_handler(AddReadInstanceIntentHandler())
sb.add_request_handler(DeleteLastReadInstanceIntentHandler())
sb.add_request_handler(GetNumberOfTimesReadIntentHandler())
sb.add_request_handler(LastTimeReadIntentHandler())
sb.add_request_handler(HowManyBooksReadDuringYearIntent())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
