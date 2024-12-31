import yaml
import glob
import string
import time
from datetime import datetime

import requests
from flask_socketio import emit

BASE_URL = "https://*************" # i leaked it 3x
TRANSFER_URL = BASE_URL + "******"
CLAIM_URL = BASE_URL + "*********"
COINS_URL = BASE_URL + "*********"

class ProgramBase():
    def __init__(self):
        self.state = "HALT"

    def is_safe_to_run(self):
        if self.state != "IDLE":
            emit_log("WARN", f"Program is {self.state}. Skipping request.")
            return False
        else:
            return True
        
    def is_halt(self):
        if self.state == "HALT":
            emit_log("WARN", f"Program is {self.state}. Stopping all current request.")
            return True
        else:
            return False

    def set_state(self, state):
        if self.state == state:
            return
        
        self.state = state
        emit("update_program_state", {"program_state": self.state})
        emit_log("INFO", f"Program state changed to \"{self.state}\"")

class Account():
    def __init__(self, account_data):
        for key, value in account_data.items():
            setattr(self, key, value)

    def emit_update_all(self):
        data = self.__dict__
        emit("update_row", data)

    def emit_update_state(self, state):
        self.state = state
        self.emit_update_all()

    def emit_handle_error(self, error):
        emit_log("ERROR", f"{self.username}: {str(error)}")
        self.emit_update_state("ERROR")

    def exec_get_coins(self, target_id=None):
        try:
            self.emit_update_state("GET_COINS")
            response_data = req_get_coins(self.api_key, target_id or self.discord_id, data_only=True)
            coins = response_data["coins"]

            if (target_id):
                emit_log("INFO", f"{self.username}: Scout finished.\n {target_id} have {coins} coins")
            else:
                emit_log("INFO", f"{self.username}: Got coins ({coins})")

            self.coins = coins
            self.state = "IDLE"
            self.emit_update_all()

        except Exception as error:
            self.emit_handle_error(error)

    def exec_claim_coins(self, target_id=None):
        try:
            self.emit_update_state("CLAIM_COINS")
            response_data = req_claim_coins(self.api_key, target_id or self.discord_id, data_only=True)
            just_claimed = response_data["ready"]
            amount = response_data["amount"]
            remaining_time = convert_time(response_data["remaining_time"])

            if just_claimed:
                emit_log("INFO", f"{self.username}: claimed coins (+{amount})")
                coins_response_data = req_get_coins(self.api_key, target_id or self.discord_id, data_only=True)
                coins = coins_response_data["coins"]
                self.coins = coins
            else:
                emit_log("INFO", f"{self.username}: already claimed coins")

            self.claim_time = remaining_time
            self.state = "IDLE"
            self.emit_update_all()

        except Exception as error:
            self.emit_handle_error(error) 

    def exec_transfer_coins(self, target_id, target_amount):
        try:
            self.emit_update_state("TRANSFER")

            if self.discord_id == target_id:
                emit_log("WARN", f"{self.username}: Sending coins to self, skipping.")
                self.emit_update_state("WARN")
                return

            donator_coins_before = req_get_coins(self.api_key, self.discord_id, data_only=True)["coins"]
            receiver_coins_before = req_get_coins(self.api_key, target_id, data_only=True)["coins"]

            if target_amount == "*":
                send_amount = donator_coins_before - 1 if donator_coins_before > 1 else 0
            else:
                send_amount = int(target_amount)

            if send_amount <= 0 or send_amount > donator_coins_before:
                emit_log("WARN", (
                    f"{self.username}: Not enough coins\n" +
                    f"(Sending {send_amount}, only have {donator_coins_before})")
                )
                self.emit_update_state("WARN")
                return

            req_transfer_coins(self.api_key, self.discord_id, target_id, send_amount)

            donator_coins_after = req_get_coins(self.api_key, self.discord_id, data_only=True)["coins"]
            receiver_coins_after = req_get_coins(self.api_key, target_id, data_only=True)["coins"]

            log_message = (
                f"{self.username}: Transfer success (-{send_amount}) to {target_id}\n" +
                f"{self.username}: {donator_coins_before} -> {donator_coins_after}\n" +
                f"{target_id}: {receiver_coins_before} -> {receiver_coins_after}"
            )

            emit_log("INFO", log_message)

            self.coins = donator_coins_after
            self.state = "IDLE"
            self.emit_update_all()

        except Exception as error:
            self.emit_handle_error(error)

def get_public_ip():
    response = requests.get("https://api.ipify.org?format=json")
    return response.json()["ip"]

def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def convert_time(milliseconds):
    seconds = milliseconds // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{remaining_seconds:02}"

def emit_log(type, content):
    data = {
        "type": type,
        "time": get_current_time(),
        "content": content
    }
    emit("log_update", data)
    print(*data.values())
    return

def load_account_yaml(directory_path):
    account_list = []
    yaml_files = glob.glob(f"{directory_path}/*.yaml")
    for file_path in yaml_files:
        with open(file_path) as file:
            data_list = yaml.safe_load(file)
            for account_data in data_list:
                account_list.append(account_data)
    return account_list

def assign_tags(account_list, max_members):
    assigned_account_list = []
    tag_index = 0
    account_index = 0

    for account_data in account_list:
        if account_data["tag"] == "SPECIAL":
            account_data["tag"] = "ZZZ"
            assigned_account_list.append(account_data)
            continue

        if (account_index == max_members):
            tag_index += 1
            account_index = 0
        
        new_tag = string.ascii_uppercase[tag_index] + f"{account_index:02d}"
        account_data["tag"] = new_tag

        assigned_account_list.append(account_data)
        account_index += 1

    return assigned_account_list

def req_handler(url, headers, payload):
    retries = 0
    while retries < 5:
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            response_json = response.json()

            if not (response_json.get("success", False)):
                error_message = response_json.get("message", "Unknown error")
                raise ValueError(error_message)
            
            return response_json
        
        except requests.exceptions.Timeout:
            retries += 1
            emit_log("WARN", f"time out occured, retrying ({retries})")
            time.sleep(5)

        except requests.exceptions.RequestException as error:
            if response.state_code == 429:
                retries += 1
                emit_log("WARN", f"Rate limited, retrying ({retries})")
                time.sleep(5)
            else:
                raise Exception(f"Request failed: {str(error)}")

        except ValueError as error:
            raise ValueError(f"Request error: {str(error)}") 

def req_get_coins(api_key, discord_id, target_id=None, data_only=False) -> dict:
    headers = {"authorization": api_key}
    payload = {"user_id": target_id or discord_id}
    response = req_handler(COINS_URL, headers, payload)

    if data_only:
        return response["data"]
    else:
        return response

def req_claim_coins(api_key, discord_id, data_only=False) -> dict:
    headers = {"authorization": api_key}
    payload = {"user_id": discord_id}
    response = req_handler(CLAIM_URL, headers, payload)

    if data_only:
        return response["data"]
    else:
        return response
          
def req_transfer_coins(api_key, discord_id, reciever_id, coins) -> dict:
    headers = {"authorization": api_key}
    payload = {
        "user_donator": discord_id,
        "user_receiver": reciever_id,
        "coins": coins
    }
    return req_handler(TRANSFER_URL, headers, payload)