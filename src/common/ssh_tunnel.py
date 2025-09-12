from fabric import Connection
from contextlib import contextmanager


SSH_HOST = "130.238.7.110"
SSH_PORT = 22
SSH_USER = "support"


@contextmanager
def diva_ssh_connection():
    with Connection(host=SSH_HOST, port=SSH_PORT, user=SSH_USER) as connection:
        yield connection
