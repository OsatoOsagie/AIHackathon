from chainlit import ChainLit

# Initialize ChainLit
chainlit = ChainLit()

# Define the conversation state
conversation_state = {
    "id": "55da5543-e34f-4fd0-9c3a-3f8deed42b7b",
    "scenario": "consultation_routine",
    "phase": "symptom_check",
    "available_commands": ["STOP_CONVERSATION"]
}

# Define the initial question
initial_question = {
    "type": "generic",
    "messages": [
        {"type": "generic", "value_type": "TEXT", "value": "Sorry you're unwell, Frank.", "meta": {}},
        {"type": "generic", "value_type": "TEXT", "value": "Just to check, are these your symptoms?", "meta": {}},
        {"type": "generic", "value_type": "TEXT", "value": "Please choose all the ones you have. (If something's missing, you can add it later.)", "meta": {}}
    ],
    "mandatory": True,
    "multiple": True,
    "choices": [
        {"type": "generic", "id": "assessment_C0010200", "label": "Cough"},
        {"type": "generic", "id": "clarify_CM001658", "label": "Shaking"}
    ]
}

# Define the user's initial data
user_data = {
    "name": "Frank",
    "gender": "m",
    "age": 45,
    "year_of_birth": 1978,
    "other": False,
    "initial_symptom": "shaking and coughing"
}

# Start the conversation
chainlit.start_conversation(conversation_state, initial_question, user_data)

# Retrieve user response
user_response = chainlit.get_user_response()

# Process user response
if user_response:
    symptoms = user_response.get("response", [])
    print("User symptoms:", symptoms)
else:
    print("No user response received.")
