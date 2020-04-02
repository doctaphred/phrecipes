#!/usr/bin/env python
"""Generate a new secret key suitable for use with Django.

Uses the same procedure as django.core.management.utils:get_random_secret_key.
"""
from random import SystemRandom

random = SystemRandom()
chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
print(''.join(random.choice(chars) for _ in range(50)))
