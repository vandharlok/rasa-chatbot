from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
import os.path
from typing import Optional
from babel.dates import format_date
from rasa_sdk.events import AllSlotsReset,Restarted,FollowupAction,SlotSet,UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
from typing import Dict, Text, Any, List, Tuple
from rasa_sdk import Action, Tracker
from datetime import datetime, timedelta
import pytz
import requests
import logging 
import dateparser
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


##FALLBACKS AND RESTART CONVERSATIONS, FEEDBACKS
class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Desculpe, não consegui entender. Pode tentar novamente?")
        logger.info("fallback triggered ")
        # Reverter a última fala do usuário
        return [UserUtteranceReverted()]

class ActionResetAll(Action):
    def name(self):
        return "action_reset_all"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Resetar todos os slots e o tracker
        logger.info("Conversation restarted")
        return [Restarted(), AllSlotsReset()]


# class ActionDefaultFallback(Action):
#     def name(self) -> Text:
#        return "action_default_fallback"
# 
#     def run(
#        self,
#         dispatcher: CollectingDispatcher,
#        tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
# 
#         # tell the user they are being passed to a customer service agent
#        dispatcher.utter_message(text="I am passing you to a human...")
# 
#         # assume there's a function to call customer service
#         # pass the tracker so that the agent has a record of the conversation between the user
#         # and the bot for context
#         call_customer_service(tracker)
# 
#        # pause the tracker so that the bot stops responding to user input
#        return [ConversationPaused(), UserUtteranceReverted()]
class ActionStoreFeedback(Action):
    def name(self) -> Text:
        return "action_store_feedback"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        feedback = tracker.latest_message.get('text')
        try:
            feedback = float(feedback)
        except ValueError:
            dispatcher.utter_message(text="Desculpe, eu não entendi. Por favor, avalie nossa conversa de 1 a 5.")
            return [SlotSet("feedback", None), FollowupAction("action_listen")]
        
        if 1 <= feedback <= 5:
            dispatcher.utter_message(text="Muito obrigado pelo seu feedback!")
            logger.info("Feedback provided")
            return [SlotSet("feedback", feedback)]
        else:
            dispatcher.utter_message(text="Desculpe, eu não entendi. Por favor, avalie nossa conversa de 1 a 5.")
            return [SlotSet("feedback", None), FollowupAction("action_listen")]


class ActionCustomFallback(Action):
    def name(self) -> str:
        return "action_custom_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        
        fallback_count = tracker.get_slot('fallback_count') or 0
        
        if fallback_count == 0.0:
            dispatcher.utter_message(response="utter_ask_rephrase")
            return [SlotSet("fallback_count", 1.0)]
        elif fallback_count == 1.0:
            dispatcher.utter_message(response="utter_default")
            dispatcher.utter_message(response="utter_show_options")
            logger.info("Custom Fallback triggered")
            return [SlotSet("fallback_count", 0.0)]  
        else:
            return [SlotSet("fallback_count", 0.0)]

    
    
#SIGNING UP THE USER ////////////////////////////////////  
#////////////////////////////////////  
class ActionSalvarCadastro(Action):
    def name(self) -> Text:
        return "action_salvar_cadastro"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nome = tracker.get_slot("nome")
        email = tracker.get_slot("email")
        cpf = tracker.get_slot("cpf")
        telefone = tracker.get_slot("telefone")
        data_nascimento=tracker.get_slot("data_nascimento")

        url = "http://backend:3010/usuario/cadastro"
        data = {
            "name": nome,
            "email": email,
            "cpf": cpf,
            "phoneNumber": telefone,
            "birth_date": data_nascimento
        }
        try:
            response = requests.post(url, json=data)
            if 200 <= response.status_code < 300:
                logger.info(f"Usuário de email : {email} registrado com sucesso.")       
                return [SlotSet("login_sucess", True)]
            else:
                dispatcher.utter_message(text="Falha ao cadastrar o usuário. Tente novamente.")
                logger.warning(f"Falha ao cadastrar usuario: {email}. Status code: {response.status_code}")
                return [SlotSet("login_sucess", False)]
        except requests.exceptions.RequestException as e:
            logger.error("Erro de conexão com o serviço de registro: %s", str(e))
            return [SlotSet("login_sucess", False)]

    
    
#CONFIRMING USER
      
def confirm_user(cpf_user):
    url = f"http://backend:3010/usuario/consulta/{cpf_user}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logger.info(f"User validation successful")
        else:
            logger.warning(f"User validation failed with status code {response.status_code} for CPF: {cpf_user}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to user validation service for CPF {cpf_user}: {e}")
        return False
        

####VALIDANDO FORMS
####VALIDANDO FORMS
####VALIDANDO FORMS
####VALIDANDO FORMS

def validate_cpf_value(slot_value: Any, dispatcher: CollectingDispatcher) -> Dict[Text, Any]:
    if len(slot_value) == 11 and slot_value.isdigit():
        logger.info("CPF validated")
        return {"cpf": slot_value}
    else:
        logger.warning(f"Invalid CPF entered: {slot_value}")
        dispatcher.utter_message(text="CPF Inválido")
        return {"cpf": None}
        


def validate_cpf_bd(
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        ) -> Dict[Text,Any]:
    try:
        if confirm_user(slot_value):  
            return {"cpf" : slot_value}
        else:
            dispatcher.utter_message("Parece que você não está cadastrado.")
            logger.warning(f"CPF validation failed for {slot_value}. CPF not found.")
            return {"cpf" : None}
    except Exception as e:
        dispatcher.utter_message("Não conseguimos validar seu CPF")
        logger.error(f"Error during CPF validation for {slot_value}: {str(e)}")
        return {"cpf" : None}
    

class ValidateNome(FormValidationAction):
    def name(self):
        return "validate_cadastro_form"
    def validate_nome(
            self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,     
            ) -> Dict[Text,Any]:
            if not re.match(r'^[A-Za-z\s]+$', slot_value):
                dispatcher.utter_message(text="O nome deve conter apenas letras.")
                return {"nome": None}
            elif len(slot_value) <= 2:
                dispatcher.utter_message(text="O nome deve ter mais de 2 caracteres.")
                return {"nome": None}
            else:
                logger.info("Name validated")
                return {"nome": slot_value}   
        
    def validate_cpf(
            self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
            ) -> Dict[Text, Any]:
        return validate_cpf_value(slot_value, dispatcher)   
    
    
    def validate_telefone(
        self, 
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,     
        ) -> Dict[Text, Any]:
        # Verifica se o valor do slot é um número
        if slot_value.isdigit():
            logger.info("phone validated")
            return {"telefone": slot_value}
        else:
            dispatcher.utter_message(text="O telefone deve conter apenas números.")
            return {"telefone": None}
    
    def validate_data_nascimento(
            self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict
            ) -> Dict[Text, Any]:
    
        if not re.match(r"\d{2}/\d{2}/\d{4}", slot_value):
            dispatcher.utter_message(text="Formato inválido. Use DD/MM/AAAA.")
            return {"data_nascimento": None,"time":None}
  
        
        try:
            data_nasc = datetime.strptime(slot_value, "%d/%m/%Y")
        except ValueError:
            dispatcher.utter_message(text="Data inválida. Por favor, insira uma data válida.")
            return {"data_nascimento": None,"time":None}
        if data_nasc > datetime.now():
            dispatcher.utter_message(text="A data de nascimento não pode ser no futuro.")
            return {"data_nascimento": None,"time":None}
        
        logger.info("birthdate validated")
        return {"data_nascimento": slot_value,"time":None}
        
    def validate_email(
        self, 
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,     
        ) -> Dict[Text, Any]:
        # Expressão regular para validar formato de e-mail
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if re.match(email_pattern, slot_value):
            logger.info("email validated")
            return {"email": slot_value}
        else:
            dispatcher.utter_message(text="Insira um endereço de e-mail válido.")
            return {"email": None}
            
            
class ValidateCPFActionDelete(FormValidationAction):
    def name(self):
        return "validate_delete_event_form"

    def validate_cpf(
        self, 
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,     
        ) -> Dict[Text,Any]:
        return validate_cpf_bd(slot_value,dispatcher)
    

class ValidateCPFActionModify(FormValidationAction):
    def name(self):
        return "validate_modify_event_form"

    def validate_cpf(
        self, 
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,     
        ) -> Dict[Text,Any]:
        return validate_cpf_bd(slot_value,dispatcher)
    
    def validate_time(self, 
                      slot_value: Any,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict) -> Dict[Text, Any]:
        return validate_time_def(slot_value, dispatcher)

class ValidateCPFActionEvent(FormValidationAction):
    def name(self):
        return "validate_event_form"

    def validate_cpf(
        self, 
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,     
        ) -> Dict[Text,Any]:
        return validate_cpf_bd(slot_value,dispatcher)
        
    def validate_time(self, 
                      slot_value: Any,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict) -> Dict[Text, Any]:
        return validate_time_def(slot_value, dispatcher)
      
      
      




#CLASSES TO USE GOOGLE CALENDAR API
     
class ValidateAndAddEvent(Action):
    def name(self) -> Text:
        return "action_add_event"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        event_name = "Consulta" 
        time_str = tracker.get_slot('time')
        cpf_user = tracker.get_slot('cpf')
        
        target_date = dateparser.parse(time_str, settings={'TIMEZONE': 'America/Sao_Paulo', 'RETURN_AS_TIMEZONE_AWARE': True})
        if not target_date:
            dispatcher.utter_message(text="Formato de data e hora incorreto. Por favor, tente novamente.")
            return [SlotSet("time", None), FollowupAction("action_listen")]
        
        target_date = target_date.replace(minute=0, second=0, microsecond=0)
        
        
        try:
            event_id = add_event(event_name, target_date)  
            url = "http://backend:3010/evento/cadastrar"
            target_date_str = target_date.strftime("%Y-%m-%d %H:%M:%S")
            data = {
                "codEvento": event_id,
                "cpfUser": cpf_user,
                "data": target_date_str
            }
            response = requests.post(url, json=data)
            if 200 <= response.status_code < 300:
                dispatcher.utter_message(text="Consulta marcada!")
                logger.info("Appointment created")
                return [SlotSet("time", None),SlotSet("event_completed", True), SlotSet("event_id", None),SlotSet("cpf", None)]
            else:
                dispatcher.utter_message(text="Falha ao cadastrar o usuário. Tente novamente.")
                logger.warning("Fail to sign up user.")
                return [SlotSet("time", None), SlotSet("event_id", None),SlotSet("cpf", None)]
            
        except requests.exceptions.RequestException as e:
            #fazer um log aki
            dispatcher.utter_message(text="Erro ao conectar ao serviço de cadastro.")
            logger.error("Error to connect to service")
            return [SlotSet("time", None), SlotSet("event_id", None), SlotSet("cpf", None)]
        except Exception as e:
            logger.error("Error to connect to service")
            dispatcher.utter_message(text=f"Não foi possível adicionar o evento: {e}")
            return [SlotSet("time", None), SlotSet("event_id", None), SlotSet("cpf", None)]
        

class ActionFindFreeSlots(Action):
    def name(self) -> Text:
        return "action_find_free_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        service = get_calendar_service()
        free_slots = find_next_free_slots(service)

        if free_slots:
            dispatcher.utter_message(text=f"Os próximos horários disponíveis são: {', '.join(free_slots)}")
            return [SlotSet("free_slots", free_slots),SlotSet("time", None)]
        else:
            dispatcher.utter_message(text="Nenhum horário disponível dentro do intervalo especificado.")
            return [SlotSet("free_slots", []),SlotSet("time", None)]

class ActionFindSlotsForSpecificDate(Action):
    def name(self) -> str:
        return "action_find_slots_for_specific_date"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        specific_time = tracker.get_slot('time')
        service = get_calendar_service()  

        if not specific_time:
            dispatcher.utter_message(text="Por favor, especifique uma data válida.")
            return []

        availability_message = find_slots_for_specific_date(service, specific_time)
        dispatcher.utter_message(text=availability_message)
        
        return []


class ModifyGoogleCalendarEvent(Action):
    def name(self) -> str:
        return "action_modify_google_calendar_event"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        new_start_time_str = tracker.get_slot('time')
        cpf_user = tracker.get_slot('cpf')
        
        url_get = f"http://backend:3010/eventos/{cpf_user}"
        response_get = requests.get(url_get)
        if 200 <= response_get.status_code < 300:
            data = response_get.json()
            event_id = data['eventos'][0]['codEvento']
            logger.info(f"Event details retrieved successfully for CPF: {cpf_user}")
        else:
            dispatcher.utter_message(text=f"Erro ao fazer a requisição: {response_get.status_code}")
            logger.error(f"Failed to fetch event for CPF {cpf_user} with status code {response_get.status_code}")
            return []

        if not event_id or not new_start_time_str:
            dispatcher.utter_message(text="Faltam informações necessárias para alterar a consulta.")
            return []

        try:
            timezone = pytz.timezone('America/Sao_Paulo')
            target_date = dateparser.parse(new_start_time_str, settings={'TIMEZONE': 'America/Sao_Paulo', 'RETURN_AS_TIMEZONE_AWARE': True})
            if not target_date:
                dispatcher.utter_message(text="Formato de data e hora incorreto. Por favor, tente novamente.")
                return [SlotSet("time", None), FollowupAction("action_listen")]
            
            target_date = target_date.replace(minute=0, second=0, microsecond=0)

            new_end_time = target_date + timedelta(hours=1)

            if modify_event(event_id, target_date.isoformat(), new_end_time.isoformat()):
                formatted_date = target_date.strftime("%Y-%m-%d %H:%M:%S")
                url_put = f"http://backend:3010/evento/atualizar/{event_id}"
                data = {"data": formatted_date}
                response_put = requests.put(url_put, json=data)
                if 200 <= response_put.status_code < 300:
                    dispatcher.utter_message(text="Mudança de consulta concluída com sucesso!")
                    logger.info("Successfully rescheduled appointment")
                    return [SlotSet("time", None), SlotSet("event_modify_completed", True), SlotSet("event_id", None), SlotSet("cpf", None)]
                else:
                    dispatcher.utter_message(text=f"Erro ao fazer a requisição: {response_put.status_code}")
                    logger.error(f"Failed to update event on the server for {event_id} with status code {response_put.status_code}")

            else:
                dispatcher.utter_message(text="Falha ao atualizar o evento.")
                logger.warning(f"Failed to modify event in Google Calendar for event ID {event_id}")
            
        except ValueError as e:
            dispatcher.utter_message(text=f"Erro ao processar as datas: {str(e)}")
            logger.error(f"Error processing dates: {e}")
            
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text=f"Erro ao fazer a requisição: {str(e)}")
            logger.error(f"Request error during event modification for event ID {event_id}: {e}")

        return [SlotSet("cpf", None), SlotSet("event_id", None)]
    
    
class ActionDeleteGoogleCalendarEvent(Action):
    def name(self):
        return "action_delete_google_calendar_event"

    def run(self, dispatcher, tracker, domain):
        cpf_user = tracker.get_slot('cpf')

        url_get = f"http://backend:3010/eventos/{cpf_user}"
        try:
            response_get = requests.get(url_get)
            if response_get.status_code == 200:
                data = response_get.json()
                events = data.get('eventos', [])
                if events:
                    event_id = events[0].get('codEvento')
                else:
                    dispatcher.utter_message(text="Não há consultas para cancelar.")
                    return []
            else:
                dispatcher.utter_message(text=f"Erro ao fazer a requisição: {response_get.status_code}")
                return []
        except Exception as e:
            dispatcher.utter_message(text="Erro ao acessar os eventos.")
            logger.error(f"Failed to retrieve events for user {cpf_user}: {str(e)}")
            return []

        try:
            service = get_calendar_service()
            service.events().delete(calendarId='primary', eventId=event_id).execute()
        except Exception as e:
            dispatcher.utter_message(text=f"Não foi possível cancelar a consulta no Google Calendar: {str(e)}")
            logger.error(f"Failed to delete Google Calendar event {event_id}: {str(e)}")
            return []

        try:
            # Deletando no banco
            url_delete = f"http://backend:3010/evento/deletar/{event_id}"
            response_delete = requests.delete(url_delete)
            if 200 <= response_delete.status_code < 300:
                dispatcher.utter_message(text="Consulta cancelada com sucesso!")
                logger.info(f"Appointment {event_id} successfully cancelled in both local and Google Calendar.")
                return [SlotSet("event_delete_completed", True), SlotSet("cpf", None)]
            else:
                dispatcher.utter_message(text=f"Erro ao fazer a requisição para deletar: {response_delete.status_code}")
                logger.warning(f"Failed to delete event {event_id} from local database: {response_delete.status_code}")
                return []
        except Exception as e:
            dispatcher.utter_message(text=f"Erro ao deletar a consulta do banco de dados: {str(e)}")
            logger.error(f"Failed to communicate with local database for deleting event {event_id}: {str(e)}")
            return []
        
        

############################################    FUNCITONS TO ME MOVED

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_next_free_slots(service, max_slots=5):
    timezone = pytz.timezone('America/Sao_Paulo')
    current_time = datetime.now(tz=timezone)
    free_slots = []

    while len(free_slots) < max_slots:
        start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        try:
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_of_day.isoformat(),
                timeMax=end_of_day.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
        except Exception as e:
            logger.error(f"Failed to fetch events: {str(e)}")
            break  

        last_end_time = max(start_of_day + timedelta(hours=7), datetime.now(tz=timezone))

        if not events:
            while last_end_time < end_of_day and last_end_time.hour < 18 and len(free_slots) < max_slots:
                free_slots.append(last_end_time.strftime('%d/%m %H:%M'))
                last_end_time += timedelta(hours=1)
        else:
            for event in events:
                start_event = datetime.fromisoformat(event['start']['dateTime']).astimezone(timezone)
                end_event = datetime.fromisoformat(event['end']['dateTime']).astimezone(timezone)

                while last_end_time < start_event and last_end_time.hour < 18 and len(free_slots) < max_slots:
                    free_slots.append(last_end_time.strftime('%d/%m %H:%M'))
                    last_end_time += timedelta(hours=1)
                last_end_time = max(last_end_time, end_event)
                logger.debug(f"Adjusted last_end_time after event: {last_end_time.isoformat()}")

            while last_end_time < end_of_day and last_end_time.hour < 18 and len(free_slots) < max_slots:
                free_slots.append(last_end_time.strftime('%d/%m %H:%M'))
                last_end_time += timedelta(hours=1)

        current_time = end_of_day

    return free_slots[:max_slots]



def find_slots_for_specific_date(service, specific_date,dispatcher):
    target_date = dateparser.parse(specific_date, settings={'TIMEZONE': 'America/Sao_Paulo', 'RETURN_AS_TIMEZONE_AWARE': True})

    if target_date is None:
        logger.error(f"Failed to parse the date: {specific_date}")
        dispatcher.utter_message(text="Data inválida")


    start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = target_date.replace(hour=23, minute=59, second=59)

    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            logger.info(f"No events found for {specific_date}.")
            return []


        if target_date.time() == datetime.min.time():
            current_time = start_of_day.replace(hour=7, minute=0)  
            while current_time <= end_of_day:
                current_time_iso = current_time.isoformat()
                if not any(event['start']['dateTime'] <= current_time_iso < event['end']['dateTime'] for event in events):
                    logger.info(f"Next free slot is at {current_time.strftime('%d/%m %H:%M')}.")
                    dispatcher.utter_message(text=f"O próximo horário livre é {current_time.strftime('%d/%m %H:%M')}")
                    return []
                current_time += timedelta(hours=1)
            return []
        else:
            if not any(event['start']['dateTime'] <= start_of_day.isoformat() < event['end']['dateTime'] for event in events):
                logger.info(f"The time {start_of_day.strftime('%d/%m %H:%M')} is free.")
                dispatcher.utter_message(text=f"O horário {start_of_day.strftime('%d/%m %H:%M')} está livre.")
                return []
            else:
                logger.info(f"The time {start_of_day.strftime('%d/%m %H:%M')} is booked.")
                dispatcher.utter_message(text=f"O horário {start_of_day.strftime('%d/%m %H:%M')} possui compromissos.")
                return []
    except Exception as e:
        logger.error(f"Error fetching events for date {specific_date}: {str(e)}")
        return []


def add_event(event_name, start_time):
    service = get_calendar_service()
    end_time = start_time + timedelta(hours=1)

    event_body = {
        "summary": event_name,
        "description": "Consulta agendada",
        "start": {"dateTime": start_time.isoformat(), "timeZone": 'America/Sao_Paulo'},
        "end": {"dateTime": end_time.isoformat(), "timeZone": 'America/Sao_Paulo'},
    }

    try:
        event_result = service.events().insert(calendarId='primary', body=event_body).execute()
        logger.info(f"Evento criado: {event_result.get('summary')} às {event_result.get('start').get('dateTime')} com ID {event_result.get('id')}")
        return event_result['id']
    except Exception as e:
        logger.error(f"Falha ao adicionar evento: {e}")
        raise


def get_calendar_service():
    creds = None
    token_pickle = 'token.pickle'
    credentials_file = './credentials.json'
    scopes = ['https://www.googleapis.com/auth/calendar']

    if os.path.exists(token_pickle):
        with open(token_pickle, 'rb') as token:
            creds = pickle.load(token)
            logger.info("Credentials loaded from pickle file.")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Credentials refreshed successfully.")
            except Exception as e:
                logger.error(f"Failed to refresh credentials: {e}")
                raise
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
                creds = flow.run_local_server(port=0)
                logger.info("New credentials fetched and authenticated.")
            except Exception as e:
                logger.error(f"Failed during the authentication process: {e}")
                raise
        with open(token_pickle, 'wb') as token:
            pickle.dump(creds, token)
            logger.info("Credentials saved to pickle file.")

    try:
        service = build('calendar', 'v3', credentials=creds)
        logger.info("Google Calendar service created successfully.")
        return service
    except Exception as e:
        logger.error(f"Failed to build the Google Calendar service: {e}")
        raise
    
def modify_event(event_id: str, start_time: str, end_time: str) -> bool:
        service = get_calendar_service()
        try:
            event = {'start': {'dateTime': start_time}, 'end': {'dateTime': end_time}}
            updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
            logger.info(f'Evento atualizado: {updated_event.get("htmlLink")}')
            return True
        except HttpError as error:
            logger.error(f'Ocorreu um erro ao atualizar o evento {event_id}: {error}')
            return False
        
        
def validate_time_def(slot_value: str, dispatcher: CollectingDispatcher) -> Dict[Text, Any]:
    service = get_calendar_service()
    normalized_date = normalize_date(slot_value, dispatcher)
    if normalized_date is not None:
        if normalized_date.hour == 0 and normalized_date.minute == 0:  # Somente a data foi fornecida
            is_available, available_times = check_availability(normalized_date, dispatcher, service)
            if is_available:
                slots_message = ', '.join(available_times)
                formatted_date = format_date(normalized_date, format='d MMMM', locale='pt_BR')
                dispatcher.utter_message(text=f"Próximos horários disponíveis : {slots_message}")
                return {"time": None}
            else:
                formatted_date = format_date(normalized_date, format='d MMMM', locale='pt_BR')
                dispatcher.utter_message(text=f"Não há horários disponíveis em {formatted_date}.")
                return {"time": None}
        else:  
            start_of_day = normalized_date.replace(hour=7, minute=0, second=0, microsecond=0)
            end_of_day = normalized_date.replace(hour=18, minute=0, second=0, microsecond=0)
            time_min = start_of_day.isoformat()
            time_max = end_of_day.isoformat()

            try:
                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                events = events_result.get('items', [])
            except Exception as e:
                logger.error(f"Failed to fetch events for {normalized_date.strftime('%d-%m-%Y')}: {str(e)}")
                dispatcher.utter_message(text="Erro ao recuperar eventos do calendário.")
                return {"time": None}

            check_time_iso = normalized_date.isoformat()
            if not any(event['start']['dateTime'] <= check_time_iso < event['end']['dateTime'] for event in events):
                dispatcher.utter_message(f"{normalized_date.strftime('%d-%m-%Y %H:%M:%S')} está disponível")
                return {"time": normalized_date.strftime('%Y-%m-%dT%H:%M:%S'), "form_completed": True}
            else:
                dispatcher.utter_message(text="Infelizmente, esse horário não está disponível. Vou te mostrar outros horários próximos.")
                normalized_date = normalized_date.replace(hour=0, minute=0, second=0, microsecond=0)
                is_available, available_times = check_availability(normalized_date, dispatcher, service)
                if is_available:
                    slots_message = ', '.join(available_times)
                    formatted_date = format_date(normalized_date, format='d MMMM', locale='pt_BR')
                    dispatcher.utter_message(text=f"Próximos horários disponíveis: {slots_message}")
                return {"time": None}
    else:
        logger.error("Failed to normalize date")
        dispatcher.utter_message(text="Data fornecida é inválida.")
    return {"time": None}


def normalize_date(slot_value: str, dispatcher: CollectingDispatcher) -> Optional[datetime]:
    target_date = dateparser.parse(slot_value, settings={'TIMEZONE': 'America/Sao_Paulo', 'RETURN_AS_TIMEZONE_AWARE': True})
    if target_date is None:
        dispatcher.utter_message(text="Não consegui entender a data: " + slot_value)
        logger.info("Error in date.")
        return None

    return target_date

def check_availability(date: datetime, dispatcher: CollectingDispatcher, service) -> Tuple[bool, List[str]]:
    available_slots = []
    num_slots_needed = 5 

    while len(available_slots) < num_slots_needed:
        start_of_day = date.replace(hour=7, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=18, minute=0, second=0, microsecond=0)
        time_min = start_of_day.isoformat()
        time_max = end_of_day.isoformat()

        try:
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            logger.debug(f"Retrieved events for {date.strftime('%Y-%m-%d')}")
        except Exception as e:
            logger.error(f"Error retrieving events for {date.strftime('%Y-%m-%d')}: {str(e)}")
            dispatcher.utter_message(text="Erro ao recuperar eventos do calendário.")
            return False, []

        daily_slots = []
        for hour in range(7, 18):
            if len(available_slots) >= num_slots_needed:
                break
            check_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            check_time_iso = check_time.isoformat()
            if not any(event['start']['dateTime'] <= check_time_iso < event['end']['dateTime'] for event in events):
                formatted_time = check_time.strftime('%d/%m %H:%M')
                daily_slots.append(formatted_time)

        if daily_slots:
            available_slots.extend(daily_slots[:max(0, num_slots_needed - len(available_slots))])
        else:
            if date.day == 1:
                dispatcher.utter_message(text="Verificando os próximos horários disponíveis para este mês.")
            else:
                dispatcher.utter_message(text="Não temos horário para este dia. Verificando os próximos horários disponíveis.")

        date += timedelta(days=1)  

    if available_slots:
        return True, available_slots
    else:
        logger.warning("No available slots found after checking multiple days.")
        return False, None
    