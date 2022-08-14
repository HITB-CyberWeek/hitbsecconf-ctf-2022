#!/usr/bin/env python3

import sys
from typing import Optional

import db
import handlers


def show_banner() -> None:
    with open('banner.txt', 'rb') as file:
        sys.stdout.buffer.write(file.read())

    print('=== Ambulance Database ===')


def anonymous_menu() -> None:
    return '\n'.join([
        '',
        '1) login',
        '2) register',
        '3) exit',
    ])


def user_menu() -> None:
    return '\n'.join([
        '',
        '1) print info',
        '2) change recovery key',
        '3) update disease',
        '4) logout',
        '5) exit',
    ])


def get_choice() -> int:
    choice = input('> ')

    try:
        return int(choice)
    except (ValueError, TypeError):
        return -1


def handler(user: Optional[db.User]) -> Optional[db.User]:
    if user is None:
        print(anonymous_menu())
        choice = get_choice()

        if choice == 1:
            user = handlers.login()
        elif choice == 2:
            user = handlers.register()
        elif choice == 3:
            handlers.exit()
        else:
            print('[-] Unknown command.')
    else:
        print(user_menu())
        choice = get_choice()

        if choice == 1:
            handlers.print_user_info(user)
        elif choice == 2:
            handlers.change_recovery_key(user)
        elif choice == 3:
            handlers.update_disease(user)
        elif choice == 4:
            user = None
        elif choice == 5:
            handlers.exit()
        else:
            print('[-] Unknown command.')

    return user


def main():
    show_banner()

    user = None

    while True:
        try:
            user = handler(user)
        except Exception as e:
            print(f'[!] Error: {e}')


if __name__ == '__main__':
    main()
