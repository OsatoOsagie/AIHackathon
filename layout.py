import chainlit as cl
from backend import healthily, login
import json
from fpdf import FPDF



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

async def next_question(response, api):
    global all_ids
    if response['question']['type'] in ["name","health_background","factor", "symptoms", "symptom"]:
        question = ' '.join([question['text'] for question in response['question']['messages']])
    else:
        question = ' '.join([question['value'] for question in response['question']['messages']])
    choices = {}

    if 'choices' in response['question']:
        choice_value = 'label'
        if response['question']['type'] == 'health_background':
            choice_value = 'long_name'
        elif response['question']['type'] in ["factor","symptoms", "symptom"]:
            choice_value = 'text'
        choices = {choice['id']: choice[choice_value] for choice in response['question']['choices']}
        options = ', '.join(choices.values())
        all_ids = list(choices.keys())
        chosen_ids = [] 
        not_chosen_ids = []
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

        print("All:", all_ids)
        print("Choosen:", chosen_ids)
        print("Not Choosen:", not_chosen_ids)
    else:
        user_response = await  cl.AskUserMessage(content=question,).send()
    answer_type = response['question']['type']

    response = await api.respond_to_healthily(chosen_ids, not_chosen_ids, answer_type)

    return response

async def parse_report(response):
    name = response['user']['name']
    gender = response['user']['gender']
    age = response['user']['age']
    #message = ' '.join([message['value'] for message in response['question']['messages']])
    diagnosis_possible = response['report']['summary']['diagnosis_possible']
    main_symptoms = [symptom['name'] for symptom in response['report']['summary']['extracted_symptoms']]
    duration = response['report']['summary']['duration']
    additional_symptoms = [symptom['name'] for symptom in response['report']['summary']['additional_symptoms']]
    unsure_symptoms = [symptom['name'] for symptom in response['report']['summary']['unsure_symptoms']]
    advice = response['report']['summary']['consultation_triage']['triage_advice']
    advice_level = response['report']['summary']['consultation_triage']['level']
    #articles = response['report']['summary']['articles_v3']['content']
    influencing_factors = []
    for inf_factor in response['report']['summary']['influencing_factors']:
        if inf_factor['value']['value'] == True:
            influencing_factors.append(inf_factor['long_name'])

    #show report
    actions = [
        cl.Action(name="Download Report", value="Download", label="Download", description="Download Report")
    ]
    content = "Please find your consultation report below: \n\n Name: " + name + "\n Gender: " + gender + "\n Age: " + str(age) + "\n\n Diagnosis Possible: " + str(diagnosis_possible) + "\n Main Symptoms: " + str(main_symptoms) + "\n Duration of Main Symptoms: " + duration + "\n\n Additional Symptoms: " + str(additional_symptoms) + "\n Unsure Symptoms: " + str(unsure_symptoms) + "\n\n Advice: " + advice + "\n Advice Level: " + advice_level + "\n Influencing Factors: " + str(influencing_factors)
    await cl.Message(content=content, actions=actions).send()

@cl.action_callback("Download Report")
async def download_pdf(content):
    # Create an instance of the FPDF class
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set the font (you can choose other fonts as well)
    pdf.set_font("Arial", size=15)

    # Insert a cell with the title
    pdf.cell(200, 10, txt="Consultation Report", ln=1, align='C')

    # Insert a cell with the description
    pdf.cell(200, 10, txt=content, ln=2, align='C')

    # Save the PDF with the filename "GFG.pdf"
    pdf.output("report.pdf")

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

    global user_details

    user_details = ','.join(user_name)
    user_details = ','.join(user_gender)
    user_details = ','.join(user_yob)
    user_details = ','.join(user_symptoms)

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
        new_reponse = await next_question(response, api)
        response = new_reponse

    #Generate report
    if 'report' in response:
        await parse_report(response)
       


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
    content = "Welcome to Zenith Care. Please agree to the following terms to start using Zenith Care: \n 1. I'm over 18. \n 2. Zenith Care and Healthily can process my health data to help me manage my health with recommendations, information, and care options, as described in the Privacy Policy. \n"
    await cl.Message(content=content, actions=actions).send()
