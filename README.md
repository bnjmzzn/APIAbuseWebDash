# APIAbuseWebDash

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Socket.io](https://img.shields.io/badge/Socket.io-black?style=for-the-badge&logo=socket.io&badgeColor=010101)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![jQuery](https://img.shields.io/badge/jquery-%230769AD.svg?style=for-the-badge&logo=jquery&logoColor=white)

A web-based dashboard for managing multiple *******.com accounts using their API.  
It can perform actions such as getting, claiming, and transferring coins in bulk.  

I made the accounts by hand with the assistance of another program. (I hate hCaptcha)

### Video Demonstration:

https://github.com/user-attachments/assets/48c98b68-5e82-468f-b207-88dbd030a44d

### Instructions:

1. Install dependencies first:

    ```sh
    pip install -r requirements.txt
    ```

2. Supply the data  

    Place your account details in the `/data` directory as YAML files.  
    Each file should contain a LIST of account objects.  

    Yaml file example:
    ```
    - api_key: abcd             # API key, string
      discord_id: '1234'        # Discord ID, string
      tag: random               # "special" or "random"
      username: hcaptcha_hater  # Username, string
    - api_key: zyxw             # Another account starts here
      discord_id: '9876'
      tag: random
      username: hcaptcha_basher
    ```

3. Run the program:

    ```sh
    python app.y
    ```

### Notes

> Q: Why redact it?
> - Skids
> - Developers might add security patches once they find out about this

> Q: Hints?
> - It's not Discord's API
> - It may require a Discord account
> - I hate hCaptcha
