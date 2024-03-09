import chainlit as cl


#Disctionary to define questions
questions = {
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

# Rename the chatbot author
@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"Chatbot": "Zenith Care"}
    return rename_dict.get(orig_author, orig_author)

async def conversation():
    # Iterate over questions
    for key, question in questions.items():
        answer = await cl.AskUserMessage(content=question).send()
        user_answers[key] = answer['output'] if answer else None

    # Storing user answers in variables
    user_name =  user_answers["name"]
    user_gender = user_answers["gender"]
    user_yob = user_answers["yob"]
    user_symptoms = user_answers["symptoms"]
    #user_medical_history = user_answers["medical_history"]

    # Do something with the stored user answers
    print("User's Details:", user_name, user_gender, user_yob)
    print("User's Symptoms:", user_symptoms)
    #print("User's Medical History:", user_medical_history)

@cl.action_callback("Agree")
async def on_action(action):
    global user_agreed
    user_agreed = True
    # Remove the action button from the chatbot user interface
    await action.remove()
    cl.Text(name="simple_text", content="You have agreed to the Terms and Conditions", display="inline")
    await conversation()  # Trigger the conversation after the user has agreed
    return True

@cl.on_chat_start
async def main():
    actions = [
        cl.Action(name="Agree", value="true", description="Agree")
    ]
    content = "Welcome to Zenith Care. Please agree to the Terms and Conditions to start using Zenith Care"
    await cl.Message(content=content, actions=actions).send()

    

