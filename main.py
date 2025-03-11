from refer import login_with_invite_code

if __name__ == "__main__":
    while True:
        invite_code = input("Input your StatusAI invite code: ")
        status_code, response_body = login_with_invite_code(invite_code)

        print("Status Code:", status_code)