from odoo import http
from odoo.http import request



class MyRedirectWarning(Exception):
    """ Warning with a possibility to redirect the user instead of simply
    diplaying the warning message.

    Should receive as parameters:
      :param int action_id: id of the action where to perform the redirection
      :param string button_text: text to put on the button that will trigger
          the redirection.
    """

    # using this RedirectWarning won't crash if used as an except_orm
    @property
    def name(self):
        return self.args[0]



