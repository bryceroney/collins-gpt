from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class DixerForm(FlaskForm):
  """WTForms form for the Government Question (Dixer) writer.

  This form is used for server-side validation and to provide a CSRF token
  to the frontend JavaScript when making AJAX requests.
  """
  word_count = IntegerField('Answer Length', default=200, validators=[NumberRange(min=100, max=400)])
  topic = TextAreaField('Topic / Announcement', validators=[DataRequired()])
  member_name = StringField('Member Asking', validators=[Optional()])
  electorate = StringField("Member's Electorate", validators=[Optional()])
  strategy = SelectField('Strategy', choices=[('option_a', 'Option A: Good News'), ('option_b', 'Option B: Contrast')], default='option_a')
  model = SelectField('AI Model', choices=[
    ('anthropic/claude-sonnet-4.5', 'Claude Sonnet 4.5'),
    ('google/gemini-2.5-flash', 'Gemini 2.5 Flash'),
    ('openai/gpt-5-mini', 'GPT-5 Mini'),
    ('openai/gpt-5.1', 'GPT-5.1'),
  ], default='anthropic/claude-sonnet-4.5')
  submit = SubmitField('Generate Dixer')
