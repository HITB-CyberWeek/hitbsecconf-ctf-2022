#!/usr/bin/env python3

import os
import dataclasses
from typing import Optional

import diseases


@dataclasses.dataclass
class User:
    username: str
    public_key: str
    disease: diseases.Disease = diseases.NoDisease


USER_FILE_TPL = 'users/%s.txt'
DISEASE_FILE_TPL = 'diseases/%s.txt'


def user_exists(username: str) -> bool:
    return os.path.isfile(USER_FILE_TPL % username)


def disease_exists(username: str) -> bool:
    return os.path.isfile(DISEASE_FILE_TPL % username)


def load_public_key(username: str) -> Optional[str]:
    if not user_exists(username):
        return None

    with open(USER_FILE_TPL % username, 'r') as file:
        return file.read()


def save_public_key(username: str, public_key: str) -> None:
    with open(USER_FILE_TPL % username, 'w') as file:
        file.write(public_key)


def load_disease(username: str) -> diseases.Disease:
    if not disease_exists(username):
        return diseases.NoDisease

    with open(DISEASE_FILE_TPL % username, 'r') as file:
        return diseases.deserialize(file.read())


def save_disease(username: str, disease: diseases.Disease) -> None:
    if disease is diseases.NoDisease:
        return

    with open(DISEASE_FILE_TPL % username, 'w') as file:
        file.write(diseases.serialize(disease))


def load_user(username: str) -> Optional[User]:
    if not user_exists(username):
        return None

    return User(
        username = username,
        public_key = load_public_key(username),
        disease = load_disease(username),
    )


def save_user(user: User) -> None:
    save_public_key(user.username, user.public_key)
    save_disease(user.username, user.disease)
