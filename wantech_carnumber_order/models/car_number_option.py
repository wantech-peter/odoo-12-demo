""" Inheriting Car Number Option Model to add number_int field"""
from odoo import models, fields, api


class CarNumberOption(models.Model):
    """ Inheriting Car Number Option Model to add number_int field"""
    _inherit = 'car.number.option'

    number_int = fields.Integer(string="Car Number")

    def init(self):
        """ Calculates the value of number_int"""
        env_cr = self._cr
        print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
        try:
            env_cr.execute("""
                    UPDATE car_number_option SET number_int = number::int
                    """)
        except Exception as cursor_exception:
            print(str(cursor_exception))

    @api.onchange('number')
    def on_number_changed(self):
        """ Calculates the value of number_int"""
        env_cr = self._cr
        try:
            env_cr.execute("""
            UPDATE car_number_option SET number_int = number::int
            """)
        except Exception as cursor_exception:
            print(str(cursor_exception))
