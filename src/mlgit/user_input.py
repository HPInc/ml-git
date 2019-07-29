"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from colorama import Fore, Back, Style
from colorama import init
init()


def confirm(message, confirm_answer="Y", decline_answer="N", enforce_options=True):
    while True:
        answer = input("%s (%s/%s): " % (message, confirm_answer, decline_answer))
        if enforce_options and answer not in {confirm_answer, decline_answer}:
            print(Fore.RED + 'You must answer with %s for confirm or %s for decline' % (confirm_answer, decline_answer)
                  + Fore.RESET)
        else:
            return answer == confirm_answer

