from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import AdminUserForm
from .models import CustomUser
from sportassociation import settings
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.contrib import messages
from smtplib import SMTPException

class AdminUserCreateView(View):
    initial = {'form': AdminUserForm()}
    template_name = 'users/create.html'

    def get(self, request):
        return render(request, self.template_name, self.initial)

    def post(self, request):
        form = AdminUserForm(request.POST, request.FILES)
        if form.is_valid():
            password = User.objects.make_random_password()
            user = User(username=form.cleaned_data['email'],
                        email=form.cleaned_data['email'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'])
            user.set_password(password)
            #TODO: Catch exceptions and if occuring, rollback the transactions
            #below.
            user.save()
            customUser = CustomUser(user=user, id_photo=request.FILES['id_photo'])
            customUser.save()

            #Create the email content and send it.
            content = {'username': user.username, 'first_name': user.first_name,
                        'password': password}
            mail_content_txt = render_to_string('users/mail_new.txt', content)
            mail_content_html = render_to_string('users/mail_new.html', content)
            try:
                send_mail(_('Welcome to BDS !'),
                            mail_content_txt,
                            settings.EMAIL_HOST_USER,
                            [user.email],
                            html_message=mail_content_html)
            except SMTPException:
                messages.add_message(request, messages.ERROR, _('Failed to send \
                                    credentials by mail.'))
            return HttpResponseRedirect('/admin/users/customuser/%s' % (customUser.id))
        return render(request, self.template_name, {'form': form})

    @method_decorator(permission_required('users.add_customuser'))
    def dispatch(self, *args, **kwargs):
        return super(AdminUserCreateView, self).dispatch(*args, **kwargs)
