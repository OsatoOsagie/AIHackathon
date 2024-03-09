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
    while  "report" not  in response:
        question = ' '.join([question['value'] for question in response['question']['messages']])
        choices = {choice['id']: choice['label'] for choice in response['question']['choices']}
        #print(question)
        #print(choices)
        await next_question(question,choices)
       

async def next_question(question,choices):
    actions = []

    for choice_id, choice_label in choices.items():
        action = cl.Action(name=choice_id, value=choice_id, label=choice_label, description=choice_label)
        actions.append(action)

    await cl.Message(content=question, actions=actions).send()

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
    actions = [
        cl.Action(name="Initial Assessment", value="Agree", label="Agree", description="Agree")
    ]
    content = "Welcome to Zenith Care. Please agree to the Terms and Conditions to start using Zenith Care"
    await cl.Message(content=content, actions=actions).send()
