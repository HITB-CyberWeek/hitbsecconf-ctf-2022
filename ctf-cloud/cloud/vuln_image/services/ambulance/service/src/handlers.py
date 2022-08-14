#!/usr/bin/env python3

import string
from typing import Optional

import db
import crypto
import diseases


def validate_username(username: str) -> bool:
    return 1 <= len(username) < 128 and all(
        symbol in string.ascii_letters + string.digits
        for symbol in username
    )


def login() -> Optional[db.User]:
    print('[*] Please, enter username:')
    username = input('> ')

    if not validate_username(username):
        print('[-] Sorry, username is not valid.')
        return

    user = db.load_user(username)

    if user is None:
        print('[-] Sorry, user does not exist.')
        return

    print('[*] Please, enter password:')
    password = input('> ')

    try:
        verify_result = crypto.verify(
            user.username.encode(), user.public_key, password,
        )
    except Exception:
        verify_result = False

    if not verify_result:
        print('[-] Sorry, password is incorrect.')
        return

    print(f'[+] Welcome, {user.username}!')

    return user


def register() -> Optional[db.User]:
    print('[*] Please, enter username:')
    username = input('> ')

    if not validate_username(username):
        print('[-] Sorry, username is not valid.')
        return

    if db.user_exists(username):
        print('[-] Sorry, user already exists.')
        return

    private_key, public_key = crypto.generate_keypair()

    user = db.User(username, public_key)
    db.save_user(user)

    print(f'[+] Success! Nice to meet you, {username}!')

    print('[!] Here is your password:')
    password = crypto.sign(username.encode(), private_key)
    print(password)

    print('[!] Here is your recovery key:')
    print(private_key)

    return user


def print_user_info(user: db.User) -> None:
    print(f'[*] Name: {user.username}')

    if db.disease_exists(user.username):
        print(f'[*] Disease: {user.disease}')
    else:
        print(f'[*] No disease')


def change_recovery_key(user: db.User) -> None:
    print('[*] Please, enter password:')
    password = input('> ')

    try:
        verify_result = crypto.verify(
            user.username.encode(), user.public_key, password,
        )
    except Exception:
        verify_result = False

    if not verify_result:
        print('[-] Sorry, password is incorrect.')
        return

    print('[*] Please, enter new recovery key:')
    private_key = input('> ')

    try:
        public_key = crypto.get_public_key(private_key)
    except Exception:
        print('[-] Sorry, recovery key is not valid.')
        return

    user.public_key = public_key
    db.save_public_key(user.username, user.public_key)

    print('[+] Success, recovery key has been changed.')


def update_disease(user: db.User) -> None:
    print('[*] Please, enter disease type:')
    type = input('> ')

    print('[*] Please, enter disease name:')
    name = input('> ')

    if type == 'mental':
        print('[*] Please, enter disease phase:')
        phase = input('> ')

        disease = diseases.MentalDisease(name, phase)
    elif type == 'infectious':
        print('[*] Please, enter disease symptoms:')
        symptoms = input('> ').split(' ')

        disease = diseases.InfectiousDisease(name, symptoms)
    else:
        disease = diseases.OtherDisease(name, type)

    user.disease = disease
    db.save_disease(user.username, user.disease)

    print('[+] Success, disease has been updated.')


def exit() -> None:
    print('[*] Bye.')

    raise SystemExit()
