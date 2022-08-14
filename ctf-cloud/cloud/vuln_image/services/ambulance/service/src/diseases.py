#!/usr/bin/env python3

import json
from typing import List


class Disease:
    pass


class MentalDisease(Disease):
    def __init__(self, name: str, phase: str) -> None:
        self.name = name
        self.phase = phase

    def __str__(self) -> str:
        return f'{self.name} (mental), {self.phase} phase'


class InfectiousDisease(Disease):
    def __init__(self, name: str, symptoms: List[str]) -> None:
        self.name = name
        self.symptoms = symptoms

    def __str__(self) -> str:
        symptoms = ', '.join(self.symptoms)

        return f'{self.name} (infectious); symptoms: {symptoms}'


class OtherDisease(Disease):
    def __init__(self, name: str, type: str) -> None:
        self.name = name
        self.type = type

    def __str__(self) -> str:
        return f'{self.name} ({self.type})'


NoDisease = Disease()


def serialize(disease: Disease) -> str:
    if isinstance(disease, MentalDisease):
        disease: MentalDisease

        return json.dumps(
            dict(
                type = 'mental',
                name = disease.name,
                phase = disease.phase,
            ),
        )
    elif isinstance(disease, InfectiousDisease):
        disease: InfectiousDisease

        return json.dumps(
            dict(
                type = 'infectious',
                name = disease.name,
                symptoms = disease.symptoms,
            ),
        )
    elif isinstance(disease, OtherDisease):
        disease: OtherDisease

        return json.dumps(
            dict(
                type = disease.type,
                name = disease.name,
            ),
        )
    else:
        raise TypeError(f'unknown disease type: {type(disease)}')


def deserialize(data: str) -> Disease:
    obj = json.loads(data)
    type = obj['type']

    if type == 'mental':
        return MentalDisease(
            name = obj['name'],
            phase = obj['phase'],
        )
    elif type == 'infectious':
        return InfectiousDisease(
            name = obj['name'],
            symptoms = obj['symptoms'],
        )
    else:
        return OtherDisease(
            name = obj['name'],
            type = obj['type'],
        )
