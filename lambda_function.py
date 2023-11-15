# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import ask_sdk_core.utils as ask_utils
import requests
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_model import Response
from ask_sdk_model.services import ServiceException
import re

news_api = "https://prod-125.westus.logic.azure.com/workflows/5701ecc5d3a64927a1cdbdd75d36b8d9/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=pslH-KjmE8GOJ7gEBaJj2UARwikcxYZHWTL6JBo0JD4"
username_api = "https://api.amazonalexa.com/v2/accounts/~current/settings/Profile.givenName"
useremail_endpoint = "https://api.amazonalexa.com/v2/accounts/~current/settings/Profile.email"

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)
        
    def handle(self, handler_input):
        try:
            accesstoken = str(handler_input.request_envelope.context.system.api_access_token)
            api_access_token = "Bearer " + accesstoken 
            headers = {"Authorization": api_access_token}
            
            user_email = requests.get(useremail_endpoint, headers=headers).json()
            username = requests.get(username_api, headers=headers).json()
            body = {"email":str(user_email)}
            news = requests.post(news_api, json=body)
            
            pattern = re.compile(r'\bACCESS_DENIED\b')
            output = pattern.search(str(username))
            if str(output.group()) == "ACCESS_DENIED":
                speak_output = "Aceite o compartilhamento do email e do nome do usuário"
                return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
        except:
            if str(news.text) == "Nenhuma notícia encontrada":
                speak_output = 'Faça cadastro no site do Alfred News para receber suas notícias, usando o email cadastrado na Alexa.'
                return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
            else:
                speak_output = "Olá\n" + str(username) + "\nsuas notícias são:\n" + str(news.text) 
                return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)
    def handle(self, handler_input):
        speak_output = "Talvez você não tenha cadastro no site do Alfred, ou suas notícias não estão prontas. Você já se cadastrou no site?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Tchauzinho!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Não tenho certeza, peça ajuda pra mim, dizendo: 'pode me judar'"
        reprompt = "Não entendi, como posso ajudar?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
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
        speak_output = "A skill foi acionada " + intent_name + "." + "\nmas não está mostrando o comportamento adequeado no momento, aguarde para futura correções."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        erro = logger.error(exception, exc_info=True)

        speak_output = "Não foi possível trazer a notícia. Aconteceu um erro de:" + erro

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) 
sb.add_exception_handler(CatchAllExceptionHandler())



lambda_handler = sb.lambda_handler()
