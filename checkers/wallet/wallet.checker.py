#!/usr/bin/env python3

import json
import logging
import random
import re
import string
from typing import Optional
from bs4 import BeautifulSoup

import checklib.http
import checklib.random


def get_random_domain():
    word = checklib.random.english_word().lower()
    while len(word) < 2:
        word = checklib.random.english_word().lower()
    return word


class WalletChecker(checklib.http.HttpChecker):
    port = 443
    proto = 'https'

    def info(self):
        print("vulns: 1")
        print("public_flag_description: Flag ID is just a transaction ID, flag is transaction's comment")

    def check(self, address):

        # check create
        to_user = self.create_user()
        self.logout()
        # check transaction

        from_user = self.create_user()
        transfer_comment = ""
        for i in range(random.randint(10, 15)):
            transfer_comment += f"{checklib.random.english_word().lower()} "
        transfer_sum = str(random.randint(100, 499))
        self.create_transfer(from_user, to_user, transfer_sum, transfer_comment)
        comment = ""
        for i in range(random.randint(10, 15)):
            comment += f"{checklib.random.english_word().lower()} "
        from_user_sum_donate = str(random.randint(100, 300))
        self.create_donate(from_user, from_user_sum_donate, comment)

        self.logout()
        self.check_donators(from_user, from_user_sum_donate, comment)

        self.login(to_user)

        to_user_sum_donate = str(random.randint(100, 300))
        self.create_donate(to_user, to_user_sum_donate, comment)
        self.logout()
        self.check_donators(to_user, to_user_sum_donate, comment)
        user_with_recovery = self.recovery(to_user)
        self.check_donators(user_with_recovery, to_user_sum_donate, comment)
        self.exit(checklib.StatusCode.OK)

    def put(self, address, flag_id, flag, vuln):

        from_user = self.create_user()
        user_sum_donate = str(random.randint(100, 300))
        self.logout()

        if random.randint(0, 1):
            self.login(from_user)
            transaction_id = self.create_donate(from_user, user_sum_donate, flag)
        else:
            to_user = self.create_user()
            self.logout()
            self.login(from_user)
            transaction_id = self.create_transfer(from_user, to_user, user_sum_donate, flag)
        self.logout()

        print(json.dumps({
            "public_flag_id": transaction_id,
            "user": from_user,
            "user_sum_donate": user_sum_donate
        }))

        self.exit(checklib.StatusCode.OK)

    def get(self, address, flag_id, flag, vuln):
        info = json.loads(flag_id)
        user = info["user"]
        r = self.try_http_post(
            "/signin",
            data={"email": user['email'], "password": user['password']}
        )
        self.corrupt_if_false(f"Welcome {user['username']}" in r.text, f"Login for {user['username']} is corrupted")
        check_donate_2 = self.try_http_get("/transactions")
        self.corrupt_if_false(
            flag in check_donate_2.text,
            "Could not find flag in the transactions for user " + user["email"]
        )
        self.logout()

    def recovery(self, user):
        recovery_start = self.try_http_get("/recovery")
        self.mumble_if_false("<h1>Recovery</h1>" in recovery_start.text, "Invalid format of response on GET /recovery")
        recovery_step_1 = self.try_http_post(
            "/recovery",
            data={"email": user['email'], "step": 1}
        )
        self.mumble_if_false("value=\"code\"" in recovery_step_1.text,
                             "Invalid format of response on POST /recovery step 1")
        recovery_step_2 = self.try_http_post(
            "/recovery",
            data={"recovery_type": "code", "step": 2}
        )
        self.mumble_if_false("Secret code #" in recovery_step_2.text,
                             "Invalid format of response on POST /recovery step 2")
        soup_2 = BeautifulSoup(recovery_step_2.content, "html.parser")
        input_label = soup_2.find(attrs={"for": "code"})
        secret_code_number = str(re.search(r'\d+', input_label.text).group())
        user['password'] = checklib.random.string(string.ascii_letters + string.digits, random.randint(8, 12))
        recovery_step_3 = self.try_http_post(
            "/recovery",
            data={
                "step": "3",
                "code": user['secret_codes'][secret_code_number],
                "password": user['password']
            }
        )

        self.mumble_if_false("<p>Set new password </p>" in recovery_step_3.text,
                             "Invalid format of response on POST /recovery step 3")
        return user

    def login(self, user):
        r = self.try_http_post(
            "/signin",
            data={"email": user['email'], "password": user['password']}
        )
        self.mumble_if_false(f"Welcome {user['username']}" in r.text, "Invalid format of response on POST /signin")

    def logout(self):
        r = self.try_http_post("/exit")
        self.mumble_if_false("Welcome!" in r.text, "Invalid format of response on /exit")

    def create_user(self) -> dict:
        username = f"{checklib.random.firstname().lower()}_{checklib.random.firstname().lower()}"
        email = f"{username}@{get_random_domain()}.{get_random_domain()}"
        password = checklib.random.string(string.ascii_letters + string.digits, random.randint(8, 12))
        logging.info(f"Creating user {username} with password {password}")
        r = self.try_http_post(
            "/signup",
            data={"username": username, "email": email, "password": password, "confirm_password": password}
        )
        self.mumble_if_false("Save the secret codes" in r.text, "Invalid format of response on POST /signup")

        secret_codes = {}
        soup = BeautifulSoup(r.content, "html.parser")
        number = ""

        for td in soup.find("table").find_all('td'):
            if not number:
                number = td.text
            else:
                secret_codes[number] = td.text
                number = ""
        self.mumble_if_false(50 == len(secret_codes), "Invalid format of response on POST /signup")
        logging.info(f"Created user with username {username}")
        return {
            "username": username,
            "email": email,
            "password": password,
            "secret_codes": secret_codes
        }

    def create_donate(self, from_user: dict, donate_sum: str, comment: str):

        step_donate_1 = self.try_http_post(
            "/transfer",
            data={
                "action": "donate",
                "step": "1",
                "sum": donate_sum,
                "comment": comment
            }
        )
        self.mumble_if_false("Wallet platform" in step_donate_1.text,
                             "Invalid format of response on POST /transfer step 1")
        step_donate_2 = self.try_http_post(
            "/transfer",
            data={
                "step": "2",
            }
        )
        self.mumble_if_false("Secret code #" in step_donate_2.text,
                             "Invalid format of response on POST /transfer step 2")
        soup_2 = BeautifulSoup(step_donate_2.content, "html.parser")
        input_label = soup_2.find(attrs={"for": "code"})
        secret_code_number = str(re.search(r'\d+', input_label.text).group())
        step_donate_3 = self.try_http_post(
            "/transfer",
            data={
                "step": "3",
                "code": from_user['secret_codes'][secret_code_number]
            }
        )

        self.mumble_if_false("Transfer done!" in step_donate_3.text,
                             "Invalid format of response on POST /transfer step 3")
        return self.get_transaction_id(comment)

    def check_donators(self, user: dict, donate_sum: str, comment: str):
        check_donate = self.try_http_get(
            "/donators"
        )
        self.mumble_if_false(user['email'] in check_donate.text, "Invalid format of response on GET /donators")

        self.login(user)
        check_donate_2 = self.try_http_get(
            "/transactions"
        )
        self.mumble_if_false(donate_sum in check_donate_2.text and comment in check_donate_2.text,
                             "Invalid format of response on GET /transactions")
        self.logout()

    def create_transfer(self, from_user: dict, to_user: dict, transfer_sum: str, comment: str):

        start_transfer = self.try_http_get("/transfer")
        self.mumble_if_false(to_user["email"] in start_transfer.text, "Invalid format of response on GET /transfer")

        soup = BeautifulSoup(start_transfer.content, "html.parser")
        to_id = 0
        for option in soup.findAll('option'):
            if option.text == to_user["email"]:
                to_id = option['value']
        self.mumble_if_false(to_id != 0, "Invalid format of response on GET /transfer")

        step_transfer_1 = self.try_http_post(
            "/transfer",
            data={
                "action": "transfer",
                "step": "1",
                "sum": transfer_sum,
                "to_user_id": to_id,
                "comment": comment
            }
        )
        self.mumble_if_false(to_user["username"] in step_transfer_1.text,
                             "Invalid format of response on POST /transfer step 1")
        step_transfer_2 = self.try_http_post(
            "/transfer",
            data={
                "step": "2",
            }
        )
        self.mumble_if_false("Secret code #" in step_transfer_2.text,
                             "Invalid format of response on POST /transfer step 2")
        soup_2 = BeautifulSoup(step_transfer_2.content, "html.parser")
        input_label = soup_2.find(attrs={"for": "code"})
        secret_code_number = str(re.search(r'\d+', input_label.text).group())
        step_transfer_3 = self.try_http_post(
            "/transfer",
            data={
                "step": "3",
                "code": from_user['secret_codes'][secret_code_number]
            }
        )

        self.mumble_if_false("Transfer done!" in step_transfer_3.text,
                             "Invalid format of response on POST /transfer step 3")
        check_transfer = self.try_http_get(
            "/transactions"
        )
        self.mumble_if_false(transfer_sum in check_transfer.text and comment in check_transfer.text,
                             "Invalid format of response on GET /transactions")
        return self.get_transaction_id(comment)

    def get_transaction_id(self, comment):
        get_transaction = self.try_http_get(
            "/transactions"
        )
        soap = BeautifulSoup(get_transaction.content, "html.parser")
        transaction_id = 0
        for tr in soap.findAll('tr'):
            if 'td' in str(tr):
                transaction_comment = tr.findAll("td")[3].text
                if transaction_comment == comment:
                    transaction_id = tr.findAll("td")[0].text
                    break
        self.mumble_if_false(transaction_id != 0,
                             "Not found donate transaction on GET /transactions")
        return transaction_id


if __name__ == "__main__":
    WalletChecker().run()
