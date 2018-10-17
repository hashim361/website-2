from flask import redirect, url_for, request
from flask_admin import Admin
from flask_admin.contrib import sqla

from .auth import current_user_is_roadie
from .headers import talisman
from .models import db
from .members.models import User, EmailAddress
from .projects.models import (Project, ProjectCredential, ProjectUpload,
                              ProjectMembership)


class JazzbandModelView(sqla.ModelView):

    def _run_view(self, fn, *args, **kwargs):
        """
            This method will run actual view function.
            While it is similar to _handle_view, can be used to change
            arguments that are passed to the view.
            :param fn:
                View function
            :param kwargs:
                Arguments
        """
        decorator = talisman(content_security_policy=None)
        return decorator(fn(self, *args, **kwargs))

    def is_accessible(self):
        return current_user_is_roadie()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('account.login', next=request.url))


class UserAdmin(JazzbandModelView):
    column_searchable_list = ('login',)
    column_filters = (
        'is_member',
        'is_roadie',
        'is_banned',
        'is_restricted',
        'has_2fa',
        'joined_at',
        'left_at',
        'consented_at',
        'profile_consent',
        'org_consent',
        'cookies_consent',
        'age_consent',
    )
    inline_models = (EmailAddress, ProjectMembership)


class EmailAddressAdmin(JazzbandModelView):
    column_searchable_list = ('email',)
    column_filters = ('verified', 'primary')


class ProjectAdmin(JazzbandModelView):
    column_searchable_list = ('name', 'description')
    column_filters = ('is_active', 'created_at', 'updated_at', 'pushed_at')
    inline_models = (ProjectCredential, ProjectUpload, ProjectMembership)


class ProjectUploadAdmin(JazzbandModelView):
    column_searchable_list = ('filename', 'sha256_digest')
    column_filters = ('uploaded_at', 'released_at')


def init_app(app):
    admin = Admin(app, name='jazzband', template_mode='bootstrap3')

    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(EmailAddressAdmin(EmailAddress, db.session))

    admin.add_view(ProjectAdmin(Project, db.session))
    admin.add_view(JazzbandModelView(ProjectMembership, db.session))
    admin.add_view(ProjectUploadAdmin(ProjectUpload, db.session))
    admin.add_view(JazzbandModelView(ProjectCredential, db.session))
