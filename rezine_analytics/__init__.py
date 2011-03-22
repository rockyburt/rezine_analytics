import os
from rezine.api import _, get_application, url_for
from rezine.utils import forms
from rezine.privileges import BLOG_ADMIN, require_privilege
from rezine.views.admin import flash, render_admin_response
from rezine.utils.validators import ValidationError, check
from rezine.utils.http import redirect_to

CONFIG_ENDPOINT = 'analytics/config'

here = os.path.dirname(__file__)
SHARED = os.path.join(here, 'shared')
TEMPLATES = os.path.join(here, 'templates')

HTML = u'''\
<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', '%s']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>'''


def add_analytics_to_metadata(metadata):
    metadata += (HTML % {'account': get_analytics_account()}).split('\n')


class ConfigurationForm(forms.Form):
    """The configuration form."""
    account = forms.TextField()


@require_privilege(BLOG_ADMIN)
def show_analytics_config(req):
    """Show the analytics control panel."""
    form = ConfigurationForm(initial=dict(
        account=req.app.cfg['analytics/account']
    ))

    if req.method == 'POST' and form.validate(req.form):
        if form.has_changed:
            req.app.cfg.change_single('analytics/account',
                                      form['account'])
            if form['account']:
                flash(_('Google Analytics has been '
                        'successfully enabled.'), 'ok')
            else:
                flash(_('Google Analytics disabled.'), 'ok')
        return redirect_to(CONFIG_ENDPOINT)
    return render_admin_response('admin/google-analytics.html',
                                 'options.analytics',
                                 form=form.as_widget())

_verified_accounts = set()


def is_valid_account_id(message=None, memorize=False):
    if message is None:
        message = _('The key is invalid.')

    def validate(form, account):
        # TODO: cache the account id by querying google analytics itself
        # to make sure account is valid

        blog_url = get_application().cfg['blog_url']
        cachekey = (account, blog_url)
        if cachekey in _verified_accounts:
            return

        if not account:
            raise ValidationError(message)
        if memorize:
            _verified_accounts.add(cachekey)
    return validate


def get_analytics_account():
    """Return the Google Analytics account id for the current application or
    `None` if there is no key or the key is invalid.
    """
    app = get_application()
    key = app.cfg['analytics/account']
    if key and check(is_valid_account_id, key, memorize=True):
        return key


class ConfigLink(object):
    def __init__(self, category, link_id, endpoint, text, perm=BLOG_ADMIN):
        self.category = category
        self.link_id = link_id
        self.endpoint = endpoint
        self.text = text
        self.perm = perm

    def __call__(self, req, navigation_bar):
        if req.user.has_privilege(self.perm):
            for link_id, url, title, children in navigation_bar:
                if link_id == self.category:
                    link = url_for(self.endpoint)
                    children.append((self.link_id, link, self.text))


def setup(app, plugin):
    print "setup(): enter"
    app.add_config_var('analytics/account',
                       forms.TextField(default=u''))
    app.connect_event('before-metadata-assembled',
                      add_analytics_to_metadata)
    app.add_template_searchpath(TEMPLATES)
    app.add_url_rule('/options/analytics',
                     prefix='admin',
                     endpoint=CONFIG_ENDPOINT,
                     view=show_analytics_config)
    app.connect_event('modify-admin-navigation-bar',
                      ConfigLink('options', 'analytics',
                                 CONFIG_ENDPOINT,
                                 'Google Analytics'))
