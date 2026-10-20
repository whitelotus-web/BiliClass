"""Atomic library changes, with a connection owned by the worker thread."""

from contextlib import closing

from .library import Library


def change(directory, operation, identities):
    if operation not in {'trash', 'restore', 'purge'}:
        raise ValueError('Thao tác thư viện không hợp lệ.')
    with closing(Library(directory)) as library:
        return getattr(library, operation + '_lessons')(identities)
