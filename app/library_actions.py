"""Atomic library changes, with a connection owned by the worker thread."""

from contextlib import closing

from .library import Library


def change(directory, operation, identities, *, with_receipt=False, expected_deleted=None):
    if operation not in {'trash', 'restore', 'purge'}:
        raise ValueError('Thao tác thư viện không hợp lệ.')
    with closing(Library(directory)) as library:
        if operation == 'trash' and with_receipt:
            return library.trash_lessons(identities, with_receipt=True)
        if operation == 'restore' and expected_deleted is not None:
            return library.restore_lessons(identities, expected_deleted=expected_deleted)
        return getattr(library, operation + '_lessons')(identities)
