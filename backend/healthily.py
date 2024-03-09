import httpx
import asyncio
import json
import os
import hashlib
# Assuming these endpoints are defined somewhere in your Python config
healthily_chat_endpoint = "https://portal.your.md/v4/chat"
search_endpoint = "https://portal.your.md/v4/search/symptoms"
healthily_api_token = os.getenv('HEALTHILY_API_TOKEN', 'jmK9KVKDXsJpyRsnrTe9r1aMEEfAGSsq.X1rf6MAlzM3S2ySVZwM82fbSCdLAo25P')
healthily_login_endpoint = "https://portal.your.md/v4/login"
healthily_api_key = os.getenv('HEALTHILY_API_KEY', 'bt2xkYywWw9RDaLJv2PaU5dWwawfhUXH1tBYMpUI')

async def login_http_request(url, body=None, header={}, method="GET"):
    headers = {"x-api-key": healthily_api_key, "Content-Type": "application/json"}
    headers.update(header)

    async with httpx.AsyncClient() as client:
        if method == "POST":
            response = await client.post(url, content=json.dumps(body) if body else None, headers=headers)
        else:  # GET request
            response = await client.get(url, headers=headers)
        
        response.raise_for_status()  # Raises an exception for 4XX/5XX responses

        if response.status_code not in [204, 404]:
            return {
                "status": response.status_code,
                "hasError": response.status_code >= 400,
                "body": response.json()
            }
        else:
            return {
                "status": response.status_code,
                "hasError": response.status_code >= 400,
                "body": None
            }

async def auth_request(url, body={}, header={}):
    try:
        return await login_http_request(url, body, header, "POST")
    except httpx.HTTPStatusError as error:
        print(f"HTTP REQUEST ERROR: {{'url': {url}, 'message': {error.response.text}}}")
        raise

def create_hash(stringified):
    hash_object = hashlib.sha256()
    # Update the hash object with the bytes-like object (encode the string to bytes)
    hash_object.update(stringified.encode())

    # Get the hexadecimal digest of the hash
    return hash_object.hexdigest()


async def get_access_token(hash_object):
    body = {"id": str(hash_object)}
    header = {"Authorization": healthily_api_token}
    response = await auth_request(healthily_login_endpoint, body, header)
    return response["body"].get("access_token")

async def http_request(url, token, body=None, method="POST"):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        if method == "POST":
            response = await client.post(url, json=body, headers=headers)
        else:  # for GET
            response = await client.get(url, headers=headers)
        
        response.raise_for_status()  # Raises exception for 4XX or 5XX status codes
        return response.json()

async def initial_query(token, query=None):
    try:
        body = await http_request(healthily_chat_endpoint, token, body=query or {}, method="POST")
        return body
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400 and query:
            print(f"Error initiating request with query parameters: {query.get('answer', {})}")
            # Retry with empty body if the initial request with query fails with status 400
            body = await http_request(healthily_chat_endpoint, token, body={}, method="POST")
            return body
        else:
            raise

async def send_response_query(query, token):
    body = await http_request(healthily_chat_endpoint, token, body=query, method="POST")
    return body

async def search(query, token):
    url = f"{search_endpoint}?text={query}"
    body = await http_request(url, token, method="GET")
    return body

def generate_answer_object(chosen_ids,not_chosen_ids, answer_type, conversation_id):
    # Some questions have constraints on them as well
    response = {}
    response["answer"] = {}
    if answer_type == 'generic':
        response["answer"] = {
        "type": "generic",
        "input": {
        "include": chosen_ids,
        "exclude": not_chosen_ids
        }
        }
    elif answer_type in ["symptom","symptoms","health_background","factor","autocomplete"]:
        response["answer"] = {
            "type": answer_type,
            "selection": chosen_ids,
        }
    response["conversation"] = {
            "id": conversation_id
        }
    return response
async def main():
    query = {"answer": {
            "type": "entry",
            "name": "Tim",
            "gender": "male",
            "year_of_birth": 1978,
            "initial_symptom": "shaking and coughing",
            "other": False
    		}}
    answer = query["answer"]
    stringified = answer["name"] + answer["gender"] + str(answer["year_of_birth"]) + answer["initial_symptom"]
    stringified_hash = create_hash(stringified)
    access_token = await get_access_token(stringified_hash)
    response = await initial_query(access_token, query=query)
    print(json.dumps(response,indent=4))
    print("#############################")
    conversation_id = response["conversation"]["id"]
    while response["question"] and response["question"]["type"] in ["generic","symptom","symptoms","health_background","factor"]:
        choices_type = response["question"]["type"]
        choices = [choice["label"] for choice in response["question"]["choices"]]
        choice_ids = [choice["id"] for choice in response["question"]["choices"]]
        request = generate_answer_object(choice_ids,[],choices_type,conversation_id)
        response = await send_response_query(request,access_token)
        print(json.dumps(response,indent=4))
        print("#############################")
    if response["question"] and response["question"]["type"] == "autocomplete":
        request = generate_answer_object([],[],choices_type,conversation_id)
        response = await send_response_query(request,access_token)
    print(json.dumps(response,indent=4))

if __name__ == "__main__":
    asyncio.run(main())