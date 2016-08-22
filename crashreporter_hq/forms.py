from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email


class LoginForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class PasswordChangeform(Form):
    old_password = PasswordField('old_password', validators=[DataRequired()])
    new_password = PasswordField('new_password', validators=[DataRequired()])
    confirm = PasswordField('confirm', validators=[DataRequired(), EqualTo('new_password', message='New Passwords must match')])


class SignUpForm(Form):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm = PasswordField('confirm', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
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
                                         ('error_message', 'Error Message'), ('error_type', 'Error Type'),
                                          ('date', 'Date')])
    value = StringField('Value')


class CreateAliasForm(Form):
    alias = StringField('alias', validators=[DataRequired()])
    uuid = StringField('uuid', validators=[DataRequired()])
    submit = SubmitField('Create')


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