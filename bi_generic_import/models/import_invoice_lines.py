# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import Warning
import binascii
import tempfile
from tempfile import TemporaryFile
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
import io

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class import_invoice_wizard(models.TransientModel):

    _name='import.invoice.wizard'

    invoice_file = fields.Binary(string="Select File")
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
    import_prod_option = fields.Selection([('barcode', 'Barcode'),('code', 'Code'),('name', 'Name')],string='Import Product By ',default='name')
    product_details_option = fields.Selection([('from_product','Take Details From The Product'),('from_xls','Take Details From The XLS File')],default='from_xls')

    @api.multi
    def import_inv(self):
        if self.import_option == 'csv':
            keys = ['product', 'quantity', 'uom','description', 'price', 'tax']
            csv_data = base64.b64decode(self.invoice_file)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=',')
            try:
                file_reader.extend(csv_reader)
            except Exception:
                raise exceptions.Warning(_("Invalid file!"))
            values = {}
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        res = self.create_inv_line(values)
        else:
            fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.invoice_file))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    if self.product_details_option == 'from_product':
                                            values.update({
                                            'product' : line[0].split('.')[0],
                                            'quantity' : line[1]
                                        })
                    else:
                        values.update({
                                'product':line[0].split('.')[0],
                                'quantity':line[1],
                                'uom':line[2],
                                'description':line[3],
                                'price':line[4],
                                'tax':line[5],
                            })
                    res = self.create_inv_line(values)
        return res

    @api.multi
    def create_inv_line(self,values):
        account_inv_brw=self.env['account.invoice'].browse(self._context.get('active_id'))
        product=values.get('product')
        if self.product_details_option == 'from_product':
            if self.import_prod_option == 'barcode':
                product_obj_search=self.env['product.product'].search([('barcode',  '=',values['product'])])
            elif self.import_prod_option == 'code':
                product_obj_search=self.env['product.product'].search([('default_code', '=',values['product'])])
            else:
                product_obj_search=self.env['product.product'].search([('name', '=',values['product'])])

            if product_obj_search:
                product_id=product_obj_search
            else:
                raise Warning(_('%s product is not found".') % values.get('product'))
        
            if account_inv_brw.type == "out_invoice" and account_inv_brw.state == 'draft':
                cust_account_id = product_id.property_account_income_id.id
                if cust_account_id:
                    account_id = cust_account_id
                else:
                    account_id = product_id.categ_id.property_account_income_categ_id.id    

                    inv_lines=self.env['account.invoice.line'].create({
                                                        'account_id':account_id,
                                                        'invoice_id':account_inv_brw.id,
                                                        'product_id':product_id.id,
                                                        'name':product_id.name,
                                                        'quantity':values.get('quantity'),
                                                        'uom_id':product_id.uom_id.id,
                                                        'price_unit':product_id.lst_price,
                                                        })
                    return True
            
            elif account_inv_brw.type =="in_invoice" and account_inv_brw.state == 'draft':
                vendor_account_id = product_id.property_account_expense_id.id
                if vendor_account_id:
                    account_id = vendor_account_id
                else:
                    account_id = product_id.categ_id.property_account_expense_categ_id.id


                inv_lines=self.env['account.invoice.line'].create({
                                                    'account_id':account_id,
                                                    'invoice_id':account_inv_brw.id,
                                                    'product_id':product_id.id,
                                                    'name':product_id.name,
                                                    'quantity':values.get('quantity'),
                                                    'uom_id':product_id.uom_id.id,
                                                    'price_unit':product_id.lst_price,
                                                    })  
                return True 
            
            elif account_inv_brw.state != 'draft':
                raise UserError(_('We cannot import data in validated or confirmed Invoice.')) 

        else:
            uom=values.get('uom')
            if self.import_prod_option == 'barcode':
                product_obj_search=self.env['product.product'].search([('barcode',  '=',values['product'])])
            elif self.import_prod_option == 'code':
                product_obj_search=self.env['product.product'].search([('default_code', '=',values['product'])])
            else:
                product_obj_search=self.env['product.product'].search([('name', '=',values['product'])])
            
            uom_obj_search=self.env['uom.uom'].search([('name','=',uom)])
    
            if not uom_obj_search:
                raise Warning(_('UOM "%s" is Not Available') % uom)

            if product_obj_search:
                product_id=product_obj_search
            else:
                if self.import_prod_option == 'name':
                    product_id=self.env['product.product'].create({'name':product,'lst_price':values.get('price')})
                else:
                    raise Warning(_('%s product is not found" .\n If you want to create product then first select Import Product By Name option .') % values.get('product'))

            if account_inv_brw.type == "out_invoice" and account_inv_brw.state == 'draft':
                tax_id_lst=[]
                if values.get('tax'):
                    if ';' in  values.get('tax'):
                        tax_names = values.get('tax').split(';')
                        for name in tax_names:
                            tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','sale')])
                            if not tax:
                                raise Warning(_('"%s" Tax not in your system') % name)
                            tax_id_lst.append(tax.id)
                    elif ',' in  values.get('tax'):
                        tax_names = values.get('tax').split(',')
                        for name in tax_names:
                            tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','sale')])
                            if not tax:
                                raise Warning(_('"%s" Tax not in your system') % name)
                            tax_id_lst.append(tax.id)
                    else:
                        tax_names = values.get('tax').split(',')
                        tax= self.env['account.tax'].search([('name', '=', tax_names),('type_tax_use','=','sale')])
                        if not tax:
                            raise Warning(_('"%s" Tax not in your system') % tax_names)
                        tax_id_lst.append(tax.id)

                cust_account_id = product_id.property_account_income_id.id
                if cust_account_id:
                    account_id = cust_account_id
                else:
                    account_id = product_id.categ_id.property_account_income_categ_id.id    

                inv_lines=self.env['account.invoice.line'].create({
                                                    'account_id':account_id,
                                                    'invoice_id':account_inv_brw.id,
                                                    'product_id':product_id.id,
                                                    'name':values.get('description'),
                                                    'quantity':values.get('quantity'),
                                                    'uom_id':uom_obj_search.id,
                                                    'price_unit':values.get('price'),
                                                    })
                if tax_id_lst:
                    inv_lines.write({'invoice_line_tax_ids':([(6,0,tax_id_lst)])})
                account_inv_brw.compute_taxes()
                return True

            elif account_inv_brw.type =="in_invoice" and account_inv_brw.state == 'draft':
                tax_id_lst=[]
                if values.get('tax'):
                    if ';' in  values.get('tax'):
                        tax_names = values.get('tax').split(';')
                        for name in tax_names:
                            tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','purchase')])
                            if not tax:
                                raise Warning(_('"%s" Tax not in your system') % name)
                            tax_id_lst.append(tax.id)
                    elif ',' in  values.get('tax'):
                        tax_names = values.get('tax').split(',')
                        for name in tax_names:
                            tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','purchase')])
                            if not tax:
                                raise Warning(_('"%s" Tax not in your system') % name)
                            tax_id_lst.append(tax.id)
                    else:
                        tax_names = values.get('tax').split(',')
                        tax= self.env['account.tax'].search([('name', '=', tax_names),('type_tax_use','=','purchase')])
                        if not tax:
                            raise Warning(_('"%s" Tax not in your system') % tax_names)
                        tax_id_lst.append(tax.id)
                        
                vendor_account_id = product_id.property_account_expense_id.id
                if vendor_account_id:
                    account_id = vendor_account_id
                else:
                    account_id = product_id.categ_id.property_account_expense_categ_id.id


                inv_lines=self.env['account.invoice.line'].create({
                                                    'account_id':account_id,
                                                    'invoice_id':account_inv_brw.id,
                                                    'product_id':product_id.id,
                                                    'name':values.get('description'),
                                                    'quantity':values.get('quantity'),
                                                    'uom_id':uom_obj_search.id,
                                                    'price_unit':values.get('price'),
                                                    })
                if tax_id_lst:
                    inv_lines.write({'invoice_line_tax_ids':([(6,0,tax_id_lst)])})
                account_inv_brw.compute_taxes()
                return True
        
            elif account_inv_brw.state != 'draft':
                raise UserError(_('We cannot import data in validated or confirmed Invoice.'))
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
