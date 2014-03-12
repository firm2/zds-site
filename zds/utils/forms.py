# coding: utf-8

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Field, Div
from crispy_forms.bootstrap import StrictButton

class CommonLayoutEditor(Layout):
	def __init__(self, *args, **kwargs):
		super(CommonLayoutEditor, self).__init__(
			Div(
                Field('text', css_class = 'md-editor'),
                ButtonHolder(
                    StrictButton('Envoyer', type = 'submit', css_class = 'btn-submit', name = 'answer'),
                    StrictButton(u'Aperçu', type = 'submit', css_class = 'btn-submit', name = 'preview'),
                ),
            ),
		)