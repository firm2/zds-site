#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""The global lettuce functions.

Defined here are a set of functions that allow the use of lettuce
(http://lettuce.it) to perform BDD.

You are able to use the Django test Client to test template rendering and the
response codes from requests etc. etc. or use Selenium to test the interface
and expected behaviour.

   :py:func:`access_reverse_url`
   :py:func:`access_url`
   :py:func:`check_the_field_`
   :py:func:`click_on_button`
   :py:func:`expect_redirect`
   :py:func:`fill_the_field_with`
   :py:func:`finished_selenium`
   :py:func:`given_i_am_not_logged_in`
   :py:func:`hit_template`
   :py:func:`if_it_passes_then_should_see_text`
   :py:func:`import_forms`
   :py:func:`i_see_that_the_form_required_fields_are_present`
   :py:func:`kill_selenium`
   :py:func:`result_of_form_submission_should_be`
   :py:func:`see_header`
   :py:func:`set_browser`
   :py:func:`set_sel_timeout`
   :py:func:`silence_debug`
   :py:func:`sleep_for`
   :py:func:`start_selenium`
   :py:func:`that_its_id_is`
   :py:func:`using_selenium`
"""
import logging
import hashlib
import time

from datetime import datetime
from lxml import html
from selenium import selenium
from nose.tools import assert_equals

from django.test.client import Client
from django.core.urlresolvers import reverse

from lettuce import *
from lettuce.django import django_url


########## SET UP ###################################################


@after.all
def kill_selenium(total):
    """Called after all tests to kill selenium.

    Should not be used directly

    """
    world.sel.stop()
#    pass  # comment above and uncomment this if you want to see last sel. page


@before.all
def start_selenium():
    """Called before all tests to start selenium.

    Should not be used directly

    """
    world.using_selenium = False
    world.timeout = 5000
    world.sel = selenium(
        'localhost',
        4444,
        '*firefox',
        'http://localhost:8000')
    world.sel.start()


@before.all
def set_browser():
    world.browser = Client()


@before.all
def silence_debug():
    print "Silencing debug logs"
    logging.disable(logging.INFO)


@before.each_feature
def import_forms(feature):
    """Finds the app for these tests and loads the forms, if any.

    Should not be called directly

    """
    app = feature.described_at.file.split("/")[-3]
    world.app = app
    try:
        forms_app = __import__(app, fromlist='forms')
        world.forms = forms_app.forms
    except:
        print "Couldn't find any forms for %s" % app


#####################################################################

######### SELENIUM BITS #############################################

@step(u'Utiliser selenium')
def using_selenium(step):
    """Setup our selenium instance and tell the world to use it.

    Note that Django client tests are more rigorously checked -- this is the
    place to check things like template matching and redirects.

    Selenium use should be limited to JS/integration testing.

    """
    world.using_selenium = True


@step(u'Ne plus utiliser selenium')
def finished_selenium(step):
    """Stop using selenium - go back to Django's Client."""
    world.using_selenium = False


@step(ru'un timeout de "(\d+)" sec')
def set_sel_timeout(step, timeout):
    """Set the page timeout for selenium tests.

    :param integer timeout: number of seconds to wait.

    """
    world.timeout = int(timeout)

#####################################################################

######## PAGE ACCESS ################################################


@step(ru'Je vais sur le lien "(.*)"')
def access_url(step, url):
    """Go to the url check for a 200 response.

    The :py:data:`world.dom` and :py:data:`world.templates` variables are set.
    A 200 is checked for.

    If using Selenium will also try the url and wait for the page to load for
    :py:data:`world.timeout` which can be set with :py:func:`set_sel_timeout`.

    """
    if world.using_selenium:
        world.sel.open(url)
        world.sel.wait_for_page_to_load(world.timeout)
    response = world.browser.get(url)
    assert response.status_code == 200, \
        "Failed to get a 200 for {}, got {}".format(url, response.status_code)
    world.dom = html.fromstring(response.content)
    world.templates = [t.name for t in response.template]


@step(ru'Je vais sur le lien inversé "(.*)"')
def access_reverse_url(step, url):
    """Reverse the named url and visit it check for a 200 response.

    The same as :py:func:`access_url` except using a django-named url.

    """
    rev_url = reverse(url)
    if world.using_selenium:
        world.sel.open(rev_url)
        world.sel.wait_for_page_to_load(world.timeout)
    response = world.browser.get(rev_url)
    assert response.status_code == 200, \
        "Failed to get a 200 for {}, got {}".format(rev_url, response.status_code)
    world.dom = html.fromstring(response.content)
    world.templates = [t.name for t in response.template]


@step(ru'Je pense être redirigé de "([^"]*)" à "([^"]*)"')
def expect_redirect(step, from_url, to_url):
    """Go to a url and expect a 302, check the DOM returned == expected DOM.

    Bit weird this one, and might not be useful. The :py:data:`to_url` you are
    expecting to eventually reach (via the :py:data:`from_url`) is first hit
    in the normal fashion and the DOM is saved to a string. The
    :py:data:`from_url` is then hit, checked for a 302 and the eventual DOM is
    compared to the stored one.

    If Selenium is used, the :py:data:`from_url` is hit, and waited for as per
    :py:func:`access_url`.

    """
    step.given('Je vais sur le lien "{}"'.format(to_url))
    expected_dom_str = html.tostring(world.dom)
    response = world.browser.get(from_url)
    code = response.status_code
    assert code == 302, \
        u"Failed to get a 302 for {}, got {}".format(from_url, code)

    response = world.browser.get(from_url, follow=True)
    world.dom = html.fromstring(response.content)
    world.templates = [t.name for t in response.template]

    assert html.tostring(world.dom) == expected_dom_str, \
        u"Expected DOM doesn't match redirected DOM"

    if world.using_selenium:
        world.sel.open(from_url)
        world.sel.wait_for_page_to_load(world.timeout)


@step(ru'Je suis sur le template "(.*)"')
def hit_template(step, template):
    """Using Django's Client, check that a template was rendered.

    This expects one of the url access functions to have been used, which will
    set the :py:data:`world.templates` variable. Appropriate url access funcs
    are: :py:func:`access_url`, :py:func:`access_reverse_url` and
    :py:func:`expect_redirect`.

    """
    assert world.templates and template in world.templates, \
        u"{} not in {}".format(template, world.templates)

#####################################################################

######### DOM #######################################################


@step(ru'Je vois dans le titre(\d+) "(.*)"')
def see_header(step, header, text):
    """Check page for some text in a particular header type.

    Slight mis-match here between selenium and Django tests as we get the 0th
    element with lxml and any with selenium.

    """
    # this should work however we accessed the page (i.e. with or without
    # selenium), and so the world.element is set.
    header = world.dom.cssselect(u'h{}'.format(str(header)))[0]
    world.element = header
    if world.using_selenium:
        assert world.sel.get_text(u"css=h{}".format(str(header))) == text
    else:
        assert header.text == text


@step(ru'Son id est "(.*)"')
def that_its_id_is(step, id):
    """Check the element's id stored in :py:data:`world.element`.

    The :py:data:`world.element` is an :py:class:`lxml.html` element. It can
    be set by using methods :py:func:`see_header`...

    """
    assert_equals(world.element.attrib['id'], id)


@step(u'If the result "(.*)" is pass then I see the text "(.*)"')
def if_it_passes_then_should_see_text(step, result, text):
    """If the result is "pass" then check for the text.

    Typically used in a tabular scenario where some are expected to pass and
    some fail, whatever pass and fail means in that context.

    """
    if not result == "pass":
        return  # not relevant test.

    if world.using_selenium:
        assert world.sel.is_text_present(text)
    else:
        assert False, 'Cette étape doit être implentée'

#####################################################################

######### GLOBAL FUNCS ##############################################


@step(u'Je ne suis pas connecté')
def given_i_am_not_logged_in(step):
    """Do a logout with Django or Selenium.

    Note that selenium use is inferred here by the call to
    :py:func:`expect_redirect`.

    """
    auth_logout = reverse("auth_logout")
    step.given('I expect to be redirected from "{}" to "/"'.format(auth_logout))
    # what can I assert here?!


@step(u'I see that the form "(.*)" required fields are present')
def i_see_that_the_form_required_fields_are_present(step, friendly_form_name):
    """Load the django form and check all its required fields are present.

    """
    assert world.forms, "No forms for {}!".format(world.app)
    form_name = friendly_form_name.title().replace(' ', '')
    form = getattr(world.forms, form_name, None)
    assert form, "No form named {} in {}".format(form_name, world.app)
    form = form()
    for field in filter(lambda x: x.field.required, form):
        if world.using_selenium:
            assert world.sel.is_element_present("css=#id_{}".format(field.name)), \
                "No field with id id_{}".format(field.name)
        else:
            assert False, "implement me!"


@step(u'Rempli le champ "(.*)" avec "(.*)"')
def fill_the_field_with(step, id, value):
    """Fill in the field.

    Selenium only.

    :param string id: an id string without the #.

    """
    val = value
    if "<<rnd>>" in value:  # to avoid where we need unique input
        hash = hashlib.new("md5")
        hash.update(str(datetime.now()))
        rnd = hash.hexdigest()
        val = value.replace("<<rnd>>", rnd)

    if world.using_selenium:
        world.sel.type("css=#%s" % id, val)
    else:
        assert False, 'Cette étape doit être implentée'


@step(u'Pause de "(\d+)" sec')
def sleep_for(step, secs):
    """Delay for a while.

    Useful for selenium tests to see input (when debugging at least).

    """
    time.sleep(int(secs))


@step(u'Clique sur le bouton "(.*)"')
def click_on_button(step, selector):
    """Click a button, with selenium.

    :param string selector: a css selector.

    """
    if world.using_selenium:
        world.sel.click("css={}".format(selector))
        world.sel.wait_for_page_to_load(world.timeout)
    else:
        assert False, 'Cette étape doit être implentée'


@step(u'Coche le champ "(.*)" avec "(checked|unchecked)"')
def check_the_field_(step, id, checked):
    """Check or uncheck a field, if needed.

    Selenium only.

    :param string id: id string, excluding the #.

    """
    if world.using_selenium:
        if checked == "checked":
            if not world.sel.is_checked("css=#{}".format(id)):
                world.sel.click("css=#{}".format(id))
        elif checked == "unchecked":
            if world.sel.is_checked("css=#{}".format(id)):
                world.sel.click("css=#{}".format(id))
    else:
        assert False, 'Cette étape doit être implentée'


@step(u'Résultat de la soumission du formulaire doit être "(.*)"')
def result_of_form_submission_should_be(step, result):
    """Check for an errorlist, and compare that to expectation of presence.

    If we want this to be "pass" there should be no errorlist.
    If we want this to be "fail" there should be an errorlist.

    :param string result: should be either "pass" or "fail".

    """
    if world.using_selenium:
        if result == "pass":
            assert not world.sel.is_element_present('css=div.alert')
        elif result == "fail":
            assert world.sel.is_element_present('css=div.alert')
    else:
        assert False, 'Cette étape doit être implentée'
