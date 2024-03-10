import chainlit as cl
from backend import healthily
import json



#Disctionary to define questions
initial_questions = {
    "name": "Please enter your Name.",
    "gender": "Please enter your Gender.",
    "yob": "Please enter your Year of Birth.",
    "symptoms": "Please help me with the symptoms you are experiencing today.",
    #"medical_history": "Explain your medical history (chronic diseases, smoking and drinking habits).",
}

# Dictionary to store user answers
user_answers = {
    "name": None,
    "gender": None,
    "yob": None,
    "symptoms": None,
} 

user_agreed = False

all_ids = []          # List to store all available IDs
chosen_ids = []       # List to store selected IDs
not_chosen_ids = []   # List to store IDs not selected

all_values = []          # List to store all available IDs
chosen_values = []       # List to store selected IDs
not_chosen_values = []   # List to store IDs not selected




async def conversation():
    # Iterate over questions
    for key, question in initial_questions.items():
        answer = await cl.AskUserMessage(content=question).send()
        user_answers[key] = answer['output'] if answer else None

    # Storing user answers in variables
    user_name =  user_answers["name"]
    user_gender = user_answers["gender"]
    user_yob = user_answers["yob"]
    user_symptoms = user_answers["symptoms"]
    #user_medical_history = user_answers["medical_history"]

    # Do something with the stored user answers
    #print("User's Details:", user_name, user_gender, user_yob)
    #print("User's Symptoms:", user_symptoms)
    #print("User's Medical History:", user_medical_history)
    api = healthily.HealthilyApi()
    response = await api.start_conversation(user_name, user_gender, user_yob, user_symptoms)
    # Parse JSON data
    #data = json.loads(response)

    # Extract question and choices
    while 'report' not in response:
        await next_question(response)
       

async def next_question(response):
    global all_ids
    question = ' '.join([question['value'] for question in response['question']['messages']])
    choices = {choice['id']: choice['label'] for choice in response['question']['choices']}
    answer_type = response['question']['type']
    options = ', '.join(choices.values())
    all_ids = list(choices.keys())
    elements = [
        cl.Text(name=question, content=options, display="inline")
    ]

    await cl.Message(
        content="",
        elements=elements,
    ).send()
    
    user_response = await  cl.AskUserMessage(content="Select what option(s) apply to you.",).send()

    user_input = user_response['output']
    chosen_values = user_input.split(', ')

    for choice_value in chosen_values:
        for a_key in choices.keys():
            if choices[a_key] == choice_value :
                chosen_ids.append(a_key)
    
    for id in all_ids:
        if id not in chosen_ids:
            not_chosen_ids.append(id)


    api = healthily.HealthilyApi()
    response = await api.respond_to_healthily(chosen_ids, not_chosen_ids, answer_type)

    return response

'''for choice_id, choice_label in choices.items():
        action = cl.Action(name="Further_Actions", value=choice_id, label=choice_label, description=choice_label)
        actions.append(action)
    selected_action = await cl.AskActionMessage(content=question, actions=actions).send()
    #await cl.Message(content=question, actions=actions).send()
    await further_action(selected_action)'''


    
'''async def further_action(action):
    global chosen_ids, not_chosen_ids
    not_chosen_ids = all_ids.copy()
    # Get the selected ID from the action
    selected_id = action["value"]

    # Add the selected ID to the chosen_ids dictionary
    chosen_ids[selected_id] = all_ids[selected_id]

    # Remove the selected ID from the not_chosen_ids dictionary
    del not_chosen_ids[selected_id]

    print("All:", all_ids)
    print("Choosen:", chosen_ids)
    print("Not Choosen:", not_chosen_ids)

    actions = []
    for choice_id, choice_label in not_chosen_ids.items():
        action = cl.Action(name="Further_Actions", value=choice_id, label=choice_label, description=choice_label)
        actions.append(action)
    selected_action = await cl.AskActionMessage(content="Select more option or submit", actions=actions).send()
    
'''



@cl.action_callback("Initial Assessment")
async def on_action(action):
    global user_agreed
    user_agreed = True
    # Remove the action button from the chatbot user interface
    await action.remove()
    cl.Text(name="simple_text", content="You have agreed to the Terms and Conditions", display="inline")
    response = await conversation()  # Trigger the conversation after the user has agreed
    #print(response)
    return True


@cl.on_chat_start
async def main():
    await cl.Avatar(
        name="Zenith Care",
        url="public/favicon.png",
    ).send()
    actions = [
        cl.Action(name="Initial Assessment", value="Agree", label="Agree", description="Agree")
    ]
    content = "Welcome to Zenith Care. Please agree to the Terms and Conditions to start using Zenith Care"
    await cl.Message(content=content, actions=actions).send()
