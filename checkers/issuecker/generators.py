import random
import string

ALPHA = string.ascii_letters + string.digits


def gen_string(min_size=20, max_size=20, alpha=ALPHA):
    return ''.join(random.choice(alpha) for _ in range(random.randint(min_size, max_size)))


def gen_pseudo_word():
    return gen_string(3, 14)


def gen_description():
    res = []
    for _ in range(random.randint(10, 50)):
        res.append(gen_pseudo_word())
        if random.random() < 0.1:
            res.append('\n')
        else:
            res.append(' ')
    return ''.join(res)


def gen_int():
    return random.randint(0, 10000)


def gen_name(min_size=6, max_size=30, alpha=string.ascii_lowercase):
    s = gen_string(min_size, max_size, alpha)
    return s[0].upper() + s[1:]


def get_queue_hash(name):
    res = ord(name[0]) * 2 ** 0
    for i, c in enumerate(name):
        res += ((ord(c) * pow(2, (i % 10))) % (i % 100 + 1)) * 1749
    return res


def gen_queue_name():
    while True:
        queue_name = gen_string(3, 40)
        if get_queue_hash(queue_name) < 1000000:
            return queue_name
