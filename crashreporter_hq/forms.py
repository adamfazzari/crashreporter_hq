from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField
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
    submit = SubmitField('Search')


class CreateGroupForm(Form):
    name = StringField('name')
    description = TextAreaField('desc')
    submit = SubmitField('Create')


class SearchReportsForm(Form):
    field = SelectField('Field', choices=[('user_identifier', 'User'), ('application_name', 'Application Name'),
                                          ('application_version', 'Application Version'), ('id', 'Report Number'),
                                         ('error_message', 'Error Message'), ('error_type', 'Error Type')])
    value = StringField('Value')


class YoutrackSubmitForm(Form):
    server = StringField('YouTrack Server', validators=[DataRequired()])
    project = StringField('Project', validators=[DataRequired()])
    assignee = StringField('Assignee', validators=[DataRequired()])
    summary = StringField('Summary', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    priority = StringField('Priority')
    type = StringField('Type')
    subsystem = StringField('Subsystem')
    state = StringField('State')
    affects_versions = StringField('Affects_versions')
    permitted_group = StringField('Permitted Group')
    submit = SubmitField("Submit")