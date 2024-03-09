from backend import login
from ui import layout
import json

def main():
    # Call functions from each module in the desired order
    auth_details = login.login()
    #print(auth_details)
    auth_data = json.loads(auth_details)
    #print(auth_data["access_token"])


if __name__ == "__main__":
    main()

