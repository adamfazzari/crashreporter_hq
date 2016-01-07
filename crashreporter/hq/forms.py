from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class SignUpForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    name = StringField('name')
    company = StringField('name')


class SearchForm(Form):
    name = StringField('name')
    submit = SubmitField('Create')


class CreateGroupForm(Form):
    name = StringField('name')
    description = TextAreaField('desc')
    submit = SubmitField('Create')


class YoutrackSubmitForm(Form):
    server = StringField('YouTrack Server', validators=[DataRequired()])
    project = StringField('Project', validators=[DataRequired()])
    assignee = StringField('Assignee', validators=[DataRequired()])
    summary = StringField('Summary', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    priority = StringField('Ppriority')
    type = StringField('Type')
    subsystem = StringField('Subsystem')
    state = StringField('State')
    affects_versions = StringField('Affects_versions')
    permitted_group = StringField('Permitted Group')
    submit = SubmitField("Submit")