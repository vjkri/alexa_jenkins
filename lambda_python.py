import boto3
import json

# def lambda_handler(event, context):

#     sqs = boto3.resource('sqs')

#     queue = sqs.get_queue_by_name(QueueName='alexa-msg')

#     response = queue.send_message(MessageBody='123')

# ------------------------------Part1--------------------------------
# In this part we define a list that contains the brand names, and
# a dictionary with brand biographies

BrandNames_LIST = ["site_1", "site_3", "site_2"]
Env_LIST = ["uat", "stage", "training"]
Locale_LIST = ["en_us", "en_gb", "en_in"]
BrandNamesSendToSqs = {"site_1": "Which environment?"+ ', '.join(map(str, Env_LIST)) + ". ",

                       "site_3": "Which Environment?"+ ', '.join(map(str, Env_LIST)) + ". ",

                       "site_2": "Which Environment?"+ ', '.join(map(str, Env_LIST)) + ". "}

Env_LISTSendToSqs = {"uat": "Which locale on uat?",

                     "stage": "Which locale on stage?",

                     "training": "Which locale on training?"}

Locale_LISTSendToSqs = {"en_gb": "cleaning cache  on e n g b. your request will be processed in a minute. Thank you, Bye",

                     "en_in": "cleaning cache on e n i n. your request will be processed in a minute. Thank you, Bye",

                     "en_us": "cleaning cache on e n u s. your request will be processed in a minute. Thank you, Bye"}

BRAND_TO_SQS = "BRAND_NAME"
ENV_TO_SQS = "ENV_NAME"
LOCALE_TO_SQS = "LOCALE_NAME"
request_attributes = {}


# ------------------------------Part2--------------------------------
# Here we define our Lambda function and configure what it does when
# an event with a Launch, Intent and Session End Requests are sent. # The Lambda function responses to an event carrying a particular
# Request are handled by functions such as on_launch(event) and
# intent_scheme(event).

def lambda_handler(event, context):
    if event['session']['new']:
        on_start()
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event)
    elif event['request']['type'] == "IntentRequest":
        return intent_scheme(event)
    elif event['request']['type'] == "SessionEndedRequest":
        return on_end()


# ------------------------------Part3--------------------------------
# Here we define the Request handler functions

def on_start():
    request_attributes = {}
    print("Session Started.")


def on_launch(event):
    onlunch_MSG = "Hi, welcome to cache clean. I can clean cache on " + ', '.join(map(str, BrandNames_LIST)) + ". " \
    "Which Brand you want run on?"
    reprompt_MSG = "Which Brand you want to run on?"
    card_TEXT = "Pick a brand"
    card_TITLE = "Choose a brand"
    return output_json_builder_with_reprompt_and_card(onlunch_MSG, card_TEXT, card_TITLE, reprompt_MSG, False, "NONE", "NONE")

def on_end():
    print("Session Ended.")


# -----------------------------Part3.1-------------------------------
# The intent_scheme(event) function handles the Intent Request.
# Since we have a few different intents in our skill, we need to
# configure what this function will do upon receiving a particular
# intent. This can be done by introducing the functions which handle
# each of the intents.

def intent_scheme(event):
    intent_name = event['request']['intent']['name']

    if intent_name == "brandname":
        return brand_name(event)
    elif intent_name == "environmentname":
        return env_name(event)
    elif intent_name == "localename":
        return locale_name(event)
    elif intent_name in ["AMAZON.NoIntent", "AMAZON.StopIntent", "AMAZON.CancelIntent"]:
        return stop_the_skill(event)
    elif intent_name == "AMAZON.HelpIntent":
        return assistance(event)
    elif intent_name == "AMAZON.FallbackIntent":
        return fallback_call(event)


# ---------------------------Part3.1.1-------------------------------
# Here we define the intent handler functions

def brand_name(event):
    request_attributes = event['session']['attributes']
    name = event['request']['intent']['slots']['brand']['value']
    brand_list_lower = [w.lower() for w in BrandNames_LIST]
    if name.lower() in brand_list_lower:
        reprompt_MSG = "Which Environment you want to run visual regression on?"
        card_TEXT = "You've picked Brand " + name.lower()
        card_TITLE = "You've picked Brand " + name.lower()
        BRAND_TO_SQS = name
        return output_json_builder_with_reprompt_and_card(BrandNamesSendToSqs[name.lower()], card_TEXT, card_TITLE, reprompt_MSG, False, "brand", name)

    else:
        wrongname_MSG = "You haven't used the full name of a brand. If you have forgotten which brands you can pick say Help."
        reprompt_MSG = "Do you want to hear more about a particular brand?"
        card_TEXT = "Use the full name."
        card_TITLE = "Wrong name."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False, "NONE", "NONE")

def env_name(event):
    request_attributes = event['session']['attributes']
    name = event['request']['intent']['slots']['env']['value']
    env_list_lower = [w.lower() for w in Env_LIST]
    if name.lower() in env_list_lower:
        reprompt_MSG = "Which Environment you want to run visual regression on?"
        card_TEXT = "You've picked Environment " + name.lower()
        card_TITLE = "You've picked Environment " + name.lower()
        ENV_TO_SQS = name
        return output_json_builder_with_reprompt_and_card(Env_LISTSendToSqs[name.lower()], card_TEXT, card_TITLE, reprompt_MSG, False, "env", name)
    else:
        wrongname_MSG = "You haven't used the full name of a environment. If you have forgotten which brands you can pick say Help."
        reprompt_MSG = "Do you want to hear more about a particular brand?"
        card_TEXT = "Use the full name."
        card_TITLE = "Wrong name."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False, "NONE", "NONE")

def locale_name(event):
    request_attributes = event['session']['attributes']
    name = event['request']['intent']['slots']['locale']['value']
    name = name[0:2].lower()+"_"+name[2:4].lower()
    locale_list_lower = [w.lower() for w in Locale_LIST]
    if name.lower() in locale_list_lower:
        reprompt_MSG = "Which Locale you want to run visual regression on?"
        card_TEXT = "You've picked Locale " + name.lower()
        card_TITLE = "You've picked Locale " + name.lower()
        LOCALE_TO_SQS = name
        sqs = boto3.resource('sqs')
        queue = sqs.get_queue_by_name(QueueName='alexa-msg')
        response = output_json_builder_with_reprompt_and_card(Locale_LISTSendToSqs[name.lower()], card_TEXT, card_TITLE, reprompt_MSG, True, "locale", name)
        queue.send_message(MessageBody=json.dumps(response['sessionAttributes']))
        response["sessionAttributes"] = {}
        request_attributes = {}
        return response
        
    
    else:
        wrongname_MSG = "You haven't used the full name of a environment. If you have forgotten which brands you can pick say Help."
        reprompt_MSG = "Do you want to hear more about a particular brand?"
        card_TEXT = "Use the full name."
        card_TITLE = "Wrong name."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False, "NONE", "NONE")

def stop_the_skill(event):
    stop_MSG = "Thank you. Bye!"
    reprompt_MSG = ""
    card_TEXT = "Bye."
    card_TITLE = "Bye Bye."
    return output_json_builder_with_reprompt_and_card(stop_MSG, card_TEXT, card_TITLE, reprompt_MSG, True, "NONE", "NONE")


def assistance(event):
    assistance_MSG = "You can choose among these brands: " + ', '.join(
        map(str, Player_LIST)) + ". Be sure to use the full name when asking about the brand."
    reprompt_MSG = "Do you want to hear more about a particular brand?"
    card_TEXT = "You've asked for help."
    card_TITLE = "Help"
    return output_json_builder_with_reprompt_and_card(assistance_MSG, card_TEXT, card_TITLE, reprompt_MSG, False, "NONE", "NONE")


def fallback_call(event):
    fallback_MSG = "I can't help you with that, try rephrasing the question or ask for help by saying HELP."
    reprompt_MSG = "Do you want to hear more about a particular brand?"
    card_TEXT = "You've asked a wrong question."
    card_TITLE = "Wrong question."
    return output_json_builder_with_reprompt_and_card(fallback_MSG, card_TEXT, card_TITLE, reprompt_MSG, False, "NONE", "NONE")


# ------------------------------Part4--------------------------------
# The response of our Lambda function should be in a json format.
# That is why in this part of the code we define the functions which
# will build the response in the requested format. These functions
# are used by both the intent handlers and the request handlers to
# build the output.

def plain_text_builder(text_body):
    text_dict = {}
    text_dict['type'] = 'PlainText'
    text_dict['text'] = text_body
    return text_dict


def reprompt_builder(repr_text):
    reprompt_dict = {}
    reprompt_dict['outputSpeech'] = plain_text_builder(repr_text)
    return reprompt_dict


def card_builder(c_text, c_title):
    card_dict = {}
    card_dict['type'] = "Simple"
    card_dict['title'] = c_title
    card_dict['content'] = c_text
    return card_dict

def session_builder(c_key, c_value):
    c_dict = request_attributes 
    #if c_key is not "NONE":
    #c_dict = {}
    c_dict[c_key] = c_value
    return c_dict
    
def response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value):
    speech_dict = {}
    speech_dict['outputSpeech'] = plain_text_builder(outputSpeach_text)
    speech_dict['card'] = card_builder(card_text, card_title)
    speech_dict['reprompt'] = reprompt_builder(reprompt_text)
    speech_dict['shouldEndSession'] = value
    return speech_dict


def output_json_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value, c_key, c_value):
    response_dict = {}
    response_dict['version'] = '1.0'
    response_dict['response'] = response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value)
    response_dict['sessionAttributes'] = session_builder(c_key, c_value)
    return response_dict

