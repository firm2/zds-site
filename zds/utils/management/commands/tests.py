# -*- coding: utf-8 -*-

from datetime import datetime
from django.test import TestCase
from django.core.management import call_command

class FixturesTest(TestCase):

    def test_load_fixtures(self):
        call_command('load_fixtures', 
                     'size=low module=member,staff,gallery,'
                     'category_forum,category_content,forum,'
                     'tag,topic,post,article,note,tutorial,'
                     'reaction racine=user',
                     verbosity=0)
