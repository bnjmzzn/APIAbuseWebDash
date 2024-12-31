from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import api

app = Flask(__name__)
app.config["SECRET_KEY"] = "i hate hcaptcha"
app.debug = True
socketio = SocketIO(app)

PUBLIC_IP_ADDRESS = api.get_public_ip() # "***.***.***.***"
JSON_PATH = "data"
TAGS_MAX_MEMBERS = 11

account_list = api.assign_tags(api.load_account_yaml(JSON_PATH), TAGS_MAX_MEMBERS)
program = api.ProgramBase()

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    print("client has connected")
    data = {
        "account_list": account_list,
        "ip_address": PUBLIC_IP_ADDRESS,
        "program_state": program.state
    }
    emit("receive_data", data)

@socketio.on("disconnect")
def handle_disconnect():
    print("client has disconnected")

@socketio.on("ping")
def handle_ping():
    emit("pong")

@socketio.on("HALT")
def handle_stop():
    program.set_state("HALT")

@socketio.on("CONTINUE")
def handle_continue():
    program.set_state("IDLE")

@socketio.on("get_coins")
def handle_get_coins(data):
    if not program.is_safe_to_run():
        return
    
    for account_data in data["accounts_list"]:
        if program.is_halt():
            return
        
        program.set_state("GET_COINS")
        account = api.Account(account_data)
        account.exec_get_coins()
    
    program.set_state("IDLE")
    
@socketio.on("claim_coins")
def handle_claim_coins(data):
    if not program.is_safe_to_run():
        return
    
    for account_data in data["accounts_list"]:
        if program.is_halt():
            return
        
        program.set_state("CLAIM_COINS")
        account = api.Account(account_data)
        account.exec_claim_coins()
    
    program.set_state("IDLE")

@socketio.on("transfer_coins")
def handle_transfer_coins(data):
    if not program.is_safe_to_run():
        return
    
    for account_data in data["accounts_list"]:
        if program.is_halt():
            return
        
        program.set_state("TRANSFER")
        account = api.Account(account_data)
        account.exec_transfer_coins(data["target_id"], data["amount"])
    
    program.set_state("IDLE")

@socketio.on("check_coins")
def handle_check_coins(data):
    if not program.is_safe_to_run():
        return
    
    print("hey")
    account_data = data["accounts_list"][0]
    account = api.Account(account_data)
    account.exec_get_coins(data["target_id"])

if __name__ == "__main__":
    socketio.run(app)