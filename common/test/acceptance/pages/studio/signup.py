"""
Signup page for studio
"""
from bok_choy.page_object import PageObject

from common.test.acceptance.pages.common.utils import click_css
from common.test.acceptance.pages.studio import BASE_URL
from common.test.acceptance.pages.studio.utils import HelpMixin, set_input_value


class SignupPage(PageObject, HelpMixin):
    """
    Signup page for Studio.
    """

    url = BASE_URL + "/signup"

    def is_browser_on_page(self):
        return self.q(css='body.view-signup').visible

    def input_password(self, password):
        """Inputs a password and then returns the password input"""
        return set_input_value(self, '#password', password)

    def sign_up_user(self, registration_dictionary):
        """
        Register the user.
        """
        for css, value in registration_dictionary.iteritems():
            set_input_value(self, css, value)

        click_css(page=self, css='#tos', require_notification=False)
        click_css(page=self, css='#submit', require_notification=False)
        self.wait_for_element_absence('#submit', 'Submit button is gone.')
