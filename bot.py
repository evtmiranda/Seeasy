import time
import json
import watson_developer_cloud
from slackclient import SlackClient
from collections import namedtuple

slack_token = ''
sc = SlackClient(slack_token)

conversation = watson_developer_cloud.ConversationV1(
    username='',
    password='',
    version='2017-05-26'
)

def consultar_watson(mensagem):
    response = conversation.message(
        workspace_id='',
        message_input={
            'text': mensagem
        }
    )

    return response

def responder_mensagem(id_mensagem, resposta):
    sc.api_call(
        method='chat.postMessage',
        as_user='true',
        text=resposta,
        channel='U5273VD4J'
    )

# Conexão em tempo real com o slack
if sc.rtm_connect(with_team_state=False):
    while True:
        # Guarda os dados recebidos pelo socket
        data_json = sc.rtm_read()

        # Se o socket não receber informações, parte para a próxima iteração
        if data_json.__len__() == 0:
            continue

        # Converte o objeto recebido em um dicionário
        x = json.loads(json.dumps(data_json, indent=2), object_hook=lambda d: namedtuple(
            'X', d.keys())(*d.values()))[0]

        print(x)

        # Se o usuário enviar uma mensagem, consulta o watson
        if x.type == 'message':
            print(x)
            response_watson_json = consultar_watson(x.text)
            response_watson = json.dumps(response_watson_json, indent=2)

            for key, value in response_watson_json.items():
                print(key, value)

                if(key == "input"):
                    input_user = json.loads(json.dumps(value, indent=2), object_hook=lambda d: namedtuple(
                        'input_user', d.keys())(*d.values()))

                if(key == "context"):
                    value = json.dumps(value).replace('_node_output_map','node_output_map').replace('-','_')

                    context = json.loads(value, object_hook=lambda d: namedtuple(
                        'context', d.keys())(*d.values()))

                if(key == "entities"):
                    entities = json.loads(json.dumps(value, indent=2), object_hook=lambda d: namedtuple(
                        'entities', d.keys())(*d.values()))

                if(key == "output"):
                    output = json.loads(json.dumps(value, indent=2), object_hook=lambda d: namedtuple(
                        'output', d.keys())(*d.values()))

                if(key == "intents"):
                    intents = json.loads(json.dumps(value, indent=2), object_hook=lambda d: namedtuple(
                        'intents', d.keys())(*d.values()))

            print(input_user)
            print(context.conversation_id)
            print(entities)
            print(output)
            print(intents)

            mensagem = ""

            if (hasattr(context, 'validateDate') and hasattr(context, 'dateMeeting')):
                # Se a variável de contexto 'validateDate' for true, verifica se a data da reunião está preenchida
                if (context.validateDate == "true" and context.dateMeeting is None):
                    mensagem = "Não consegui entender a data. Pode me dizer novamente por favor?";
                    responder_mensagem(x.ts, mensagem)
                    continue

            if (hasattr(context, 'validateHour') and hasattr(context, 'hourMeeting')):
                # Se a variável de contexto 'validateHour' for true, verifica se o horário da reunião está preenchido
                if (context.validateHour == "true" and context.hourMeeting is None):
                    mensagem = "Não consegui entender o horário. Pode me dizer novamente por favor?"
                    responder_mensagem(x.ts, mensagem)
                    continue

            if(hasattr(output, 'text')):
                responder_mensagem(x.ts, output.text)
            else:
                print('não entrou no responder mensagem')

            time.sleep(1)
else:
    print("connection failed")
