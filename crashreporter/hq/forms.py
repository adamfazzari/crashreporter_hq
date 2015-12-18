from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class YoutrackSubmitForm(Form):
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