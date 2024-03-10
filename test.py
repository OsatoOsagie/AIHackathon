import chainlit as cl
import json

def parse_report(response):
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
    
    content = "Please find your consulation report below: \n\n Name: " + name + "\n Gender: " + gender + "\n Age: " + str(age) + "\n Diagnosis Possible: " + str(diagnosis_possible) + "\n Main Symptoms: " + str(main_symptoms) + "\n Duration of Main Symptoms: " + duration + "\n Additional Symptoms: " + str(additional_symptoms) + "\n Unsure Symptoms: " + str(unsure_symptoms) + "\n Advice: " + advice + "\n Advice Level: " + advice_level + "\n Influencing Factors: " + str(influencing_factors)
    
    print(content)



with open("report2.json", "r") as read_file:
    response = json.load(read_file)


def main():
    parse_report(response)

if __name__ == "__main__":
    main()