from django.core.management.commands.makemessages import Command as StockMakeMessages


class Command(StockMakeMessages):
    msgmerge_options = StockMakeMessages.msgmerge_options + [
        '--no-fuzzy-matching',
    ]
