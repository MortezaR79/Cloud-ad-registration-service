import requests


def send_message(email, text):
    return requests.post(
        "https://api.mailgun.net/v3/sandboxb51aec0a6b914365b6ea5038a98661a5.mailgun.org/messages",
        auth=("api", "c948a2124c2e1e0eb808dc5f9f697870-8845d1b1-17a2cc4f"),
        data={"from": "mailgun@sandboxb51aec0a6b914365b6ea5038a98661a5.mailgun.org",
              "to": [email],
              "subject": "request result",
              "text": text})



