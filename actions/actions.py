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
import random
import string

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
  

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string



#CLASSES TO USE GOOGLE CALENDAR API

class ValidateAndAddEvent(Action):
    def name(self) -> Text:
        return "action_add_event"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        time_str = tracker.get_slot('time')
        cpf_user = tracker.get_slot('cpf')
        

        target_date = dateparser.parse(time_str, settings={'TIMEZONE': 'America/Sao_Paulo', 'RETURN_AS_TIMEZONE_AWARE': True})
        if not target_date:
            dispatcher.utter_message(text="Formato de data e hora incorreto. Por favor, tente novamente.")
            return [SlotSet("time", None), FollowupAction("action_listen")]
    
        new_end_time = target_date + timedelta(hours=1)
        
        string_length = 10  
        random_string = generate_random_string(string_length)
        
        start_time= target_date.isoformat()
        new_end_time_str = new_end_time.isoformat()

        try:
            url = "http://backend:3010/evento/cadastrar"
            data = {
                "codEvento": random_string,
                "cpfUser": cpf_user,
                "nomeUser": "vands",
                "dataInicial": start_time,
                "dataFinal": new_end_time_str
            }
            response = requests.post(url, json=data)
            if 200 <= response.status_code < 300:
                dispatcher.utter_message(text="Consulta marcada!")
                logger.info("Appointment created")
                return [SlotSet("time", None),SlotSet("event_completed", True), SlotSet("event_id", None),SlotSet("cpf", None)]
            else:
                dispatcher.utter_message(text="Falha ao cadastrar o usuário. Tente novamente.")
                logger.warning("Fail to sign up user.")
                return [SlotSet("time", None), SlotSet("cpf", None)]
            
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
        api_url = "http://backend:3010/eventos"
        free_slots = find_next_free_slots(api_url)

        if free_slots:
            dispatcher.utter_message(text=f"Os próximos horários disponíveis são: {', '.join(free_slots)}")
            return [SlotSet("free_slots", free_slots),SlotSet("time", None)]
        else:
            dispatcher.utter_message(text="Nenhum horário disponível dentro do intervalo especificado.")
            return [SlotSet("free_slots", []),SlotSet("time", None)]


def get_event_id_from_cpf(cpf_user):
    url_get = f"http://backend:3010/eventos/{cpf_user}"
    try:
        response_get = requests.get(url_get)
        if response_get.status_code == 200:
            data = response_get.json()
            events = data.get('eventos', [])
            if events:
                return events[0].get('codEvento'), None
            else:
                return None, "Não há consultas para cancelar."
        else:
            return None, f"Erro ao fazer a requisição: {response_get.status_code}"
    except Exception as e:
        logger.error(f"Failed to retrieve events for user {cpf_user}: {str(e)}")
        return None, "Erro ao acessar os eventos."

class ModifyGoogleCalendarEvent(Action):
    def name(self) -> str:
        return "action_modify_google_calendar_event"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        new_start_time_str = tracker.get_slot('time')
        cpf_user = tracker.get_slot('cpf')

        event_id, error_message = get_event_id_from_cpf(cpf_user)
        if not event_id:
            dispatcher.utter_message(text=error_message)
            return []

        try:
            target_date = dateparser.parse(new_start_time_str, settings={'TIMEZONE': 'America/Sao_Paulo', 'RETURN_AS_TIMEZONE_AWARE': True})
            if not target_date:
                dispatcher.utter_message(text="Formato de data e hora incorreto. Por favor, tente novamente.")
                return [SlotSet("time", None), FollowupAction("action_listen")]

            new_end_time = target_date + timedelta(hours=1)
            new_start_time_str = target_date.isoformat()
            new_end_time_str = new_end_time.isoformat()

            if modify_event(event_id, new_start_time_str, new_end_time_str):
                dispatcher.utter_message(text="Mudança de consulta concluída com sucesso!")
            else:
                dispatcher.utter_message(text="Não conseguimos mudar sua consulta de data!")

        except ValueError as e:
            dispatcher.utter_message(text=f"Erro ao processar as datas: {str(e)}")
            logger.error(f"Error processing dates: {e}")
            
        return [SlotSet("cpf", None), SlotSet("event_id", None)]
    
class ActionDeleteGoogleCalendarEvent(Action):
    def name(self):
        return "action_delete_google_calendar_event"

    def run(self, dispatcher, tracker, domain):
        cpf_user = tracker.get_slot('cpf')
        event_id, error_message = get_event_id_from_cpf(cpf_user)

        if not event_id:
            dispatcher.utter_message(text=error_message)
            return []

        url_delete = f"http://backend:3010/evento/deletar/{event_id}"
        try:
            response_delete = requests.delete(url_delete)
            if 200 <= response_delete.status_code < 300:
                dispatcher.utter_message(text="Consulta cancelada com sucesso!")
                logger.info(f"Appointment {event_id} successfully cancelled.")
                return [SlotSet("event_delete_completed", True), SlotSet("cpf", None)]
            else:
                dispatcher.utter_message(text="Parece que não conseguimos cancelar sua consulta, tente mais tarde novamente.")
                logger.warning(f"Failed to delete event {event_id} from local database: {response_delete.status_code}")
                return []
        except Exception as e:
            dispatcher.utter_message(text="Erro ao deletar a consulta, tente novamente mais tarde!")
            logger.error(f"Failed to communicate with local database for deleting event {event_id}: {str(e)}")
            return []
            
        

############################################    FUNCITONS TO ME MOVED



def find_next_free_slots(api_url: str, max_slots=5):

    timezone = pytz.timezone('America/Sao_Paulo')
    current_time = (datetime.now(tz=timezone) + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
    free_slots = []

    while len(free_slots) < max_slots:
        start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        last_end_time = start_of_day + timedelta(hours=7)  

        try:
            response = requests.get(api_url + f'?dataInicial={start_of_day.isoformat()}&dataFinal={end_of_day.isoformat()}')
            response.raise_for_status()
            events_result = response.json()
            events = events_result.get('eventos', [])
        except Exception as e:
            print(f"Failed to fetch events: {str(e)}")
            break

        if not events:
            while last_end_time < end_of_day and last_end_time.hour < 18 and len(free_slots) < max_slots:
                free_slots.append(last_end_time.strftime('%d/%m %H:%M'))
                last_end_time += timedelta(hours=1)
        else:
            for event in events:
                start_event = datetime.fromisoformat(event['dataInicial'].replace("Z", "+00:00")).astimezone(timezone)
                end_event = datetime.fromisoformat(event['dataFinal'].replace("Z", "+00:00")).astimezone(timezone)

                while last_end_time < start_event and last_end_time.hour < 18 and len(free_slots) < max_slots:
                    free_slots.append(last_end_time.strftime('%d/%m %H:%M'))
                    last_end_time += timedelta(hours=1)
                last_end_time = max(last_end_time, end_event)

            while last_end_time < end_of_day and last_end_time.hour < 18 and len(free_slots) < max_slots:
                free_slots.append(last_end_time.strftime('%d/%m %H:%M'))
                last_end_time += timedelta(hours=1)

        current_time = end_of_day

    return free_slots[:max_slots]




    
def modify_event(event_id: str, start_time: str, end_time: str) -> bool:
    url = f"http://backend:3010/evento/atualizar/{event_id}"  
    data = {
        "dataInicial": start_time,
        "dataFinal": end_time
    }
    
    try:
        response = requests.put(url, json=data)
        response.raise_for_status()  
        

        logger.info(f'Evento atualizado com sucesso: {response.json()}') 
        return True
    except requests.exceptions.RequestException as error:
        logger.error(f'Ocorreu um erro ao atualizar o evento {event_id}: {error}')
        return False



def normalize_date(slot_value: str, dispatcher: CollectingDispatcher) -> Optional[datetime]:
    target_date = dateparser.parse(slot_value, settings={'TIMEZONE': 'America/Sao_Paulo', 'RETURN_AS_TIMEZONE_AWARE': True})
    if target_date is None:
        dispatcher.utter_message(text="Não consegui entender a data: " + slot_value)
        logger.info("Error in date.")
        return None

    return target_date

def check_availability(date: datetime, dispatcher: CollectingDispatcher, api_url: str) -> Tuple[bool, List[str]]:
    available_slots = []
    num_slots_needed = 5  

    while len(available_slots) < num_slots_needed:
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            events_result = response.json()
            events = events_result.get('eventos', [])
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
            is_free = True
            for event in events:
                event_start = datetime.fromisoformat(event['dataInicial'].replace("Z", "+00:00"))
                event_end = datetime.fromisoformat(event['dataFinal'].replace("Z", "+00:00"))
                if event_start <= check_time < event_end:
                    is_free = False
                    break

            if is_free:
                formatted_time = check_time.strftime('%d/%m %H:%M')
                daily_slots.append(formatted_time)

        if daily_slots:
            available_slots.extend(daily_slots[:max(0, num_slots_needed - len(available_slots))])
        else:
            if date.day == 1:
                dispatcher.utter_message(text="Verificando os próximos horários disponíveis para este mês.")
            else:
                dispatcher.utter_message(text="Não temos horário para este dia. Verificando os próximos horários disponíveis.")

        date += timedelta(days=1)  # Avança para o próximo dia

    if available_slots:
        return True, available_slots
    else:
        logger.warning("No available slots found after checking multiple days.")
        return False, []
    
    #######################

def validate_time_def(slot_value: str, dispatcher: CollectingDispatcher) -> Dict[Text, Any]:
    api_url = "http://backend:3010/eventos"
    normalized_date = normalize_date(slot_value, dispatcher)
    if normalized_date is not None:
        if normalized_date.hour == 0 and normalized_date.minute == 0:# Somente a data foi fornecida entao ele traz os prox hor livre
            is_available, available_times = check_availability(normalized_date, dispatcher, api_url)
            if is_available:
                slots_message = ', '.join(available_times)
                formatted_date = format_date(normalized_date, format='d MMMM', locale='pt_BR')
                dispatcher.utter_message(text=f"Próximos horários disponíveis: {slots_message}")
                return {"time": None}
            else:
                formatted_date = format_date(normalized_date, format='d MMMM', locale='pt_BR')
                dispatcher.utter_message(text=f"Não há horários disponíveis em {formatted_date}.")
                return {"time": None}
        else:
            pass

            try:
                response = requests.get(api_url)
                response.raise_for_status()
                events_result = response.json()
                events = events_result.get('eventos', [])
            except Exception as e:
                logger.error(f"Failed to fetch events for {normalized_date.strftime('%d-%m-%Y')}: {str(e)}")
                dispatcher.utter_message(text="Erro ao recuperar eventos do calendário.")
                return {"time": None}

            check_time_iso = normalized_date.isoformat()
            if not any(event['dataInicial'] <= check_time_iso < event['dataFinal'] for event in events):
                dispatcher.utter_message(f"{normalized_date.strftime('%d-%m-%Y %H:%M:%S')} está disponível")
                return {"time": normalized_date.isoformat(), "form_completed": True}
            else:
                dispatcher.utter_message(text="Infelizmente, esse horário não está disponível. Vou te mostrar outros horários próximos.")
                normalized_date = normalized_date.replace(hour=0, minute=0, second=0, microsecond=0)
                is_available, available_times = check_availability(normalized_date, dispatcher, api_url)
                if is_available:
                    slots_message = ', '.join(available_times)
                    formatted_date = format_date(normalized_date, format='d MMMM', locale='pt_BR')
                    dispatcher.utter_message(text=f"Próximos horários disponíveis: {slots_message}")
                return {"time": None}
    else:
        logger.error("Failed to normalize date")
        dispatcher.utter_message(text="Data fornecida é inválida.")
    return {"time": None}
