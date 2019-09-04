# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import logging
import time
import tempfile
import binascii
import xlrd
import io
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class VendorPricelist(models.TransientModel):
    _name = "import.vendor.pricelist"

    file = fields.Binary('File')
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
    import_prod_option = fields.Selection([('name', 'Name'),('code', 'Code'),('barcode', 'Barcode')],string='Select Product By',default='name')        
    import_prod_variant_option = fields.Selection([('name', 'Name'),('code', 'Code'),('barcode', 'Barcode')],string='Select Product Variant BY',default='name')

    @api.multi
    def make_pricelist(self, values):

        prod_supplierinfo_obj = self.env['product.supplierinfo']

        if not values.get('vendor'):
            raise Warning(_("Vendor name is required."))
            return

        supplier_search = prod_supplierinfo_obj.search([
            ('name', '=', values.get('vendor'))
        ])

        if supplier_search:
            for sup in supplier_search:
                if sup.currency_id.name == values.get('currency'):
                    raise Warning(_('Pricelist already exist for "%s" ') % values.get('vendor'))
                    return sup
                else:
                    raise Warning(_('Currency is different for "%s" .\n Please define same.') % values.get('vendor'))
        else:

            product_templ_obj = self.env['product.template']
            product_variant_obj = self.env['product.product']
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            partner_id = self.find_partner(values.get('vendor'))
            currency_id = self.find_currency(values.get('currency'))
            product_template_search = False
            product_variant_search = False

            if values.get('date_start') and values.get('date_end'):
                set_start_date = self.find_start_date(values.get('date_start'))
                set_end_date = self.find_end_date(values.get('date_end'))

            # Product Template
            if self.import_prod_option == 'barcode':
                product_template_search = product_templ_obj.search([('barcode',  '=',values['product_template'])])

            elif self.import_prod_option == 'code':
                product_template_search = product_templ_obj.search([('default_code', '=',values['product_template'])])
                            
            else:
                product_template_search = product_templ_obj.search([('name', '=',values['product_template'])])
                

            # Product Variant
            if self.import_prod_variant_option == 'barcode':
                product_variant_search = product_variant_obj.search([('barcode',  '=',values['product_variant'])])
                
            elif self.import_prod_variant_option == 'code':
                product_variant_search = product_variant_obj.search([('default_code', '=',values['product_variant'])])
                
            else:
                product_variant_search = product_variant_obj.search([('name', '=',values['product_variant'])])

            vals = {}
            if currency_id:
                vals = {
                    'name' : partner_id.id,
                    'product_tmpl_id' : product_template_search.id,
                    'product_id' : product_variant_search[0].id,
                    'min_qty' : values.get('min_qty') or 1,
                    'price' : values.get('price') or 0,
                    'currency_id' : currency_id.id,
                    'date_start' : values.get('date_start') or False,
                    'date_end' : values.get('date_end') or False,
                    'delay' : values.get('delay') or 0,
                }
            else:
                vals = {
                    'name' : partner_id.id,
                    'product_tmpl_id' : product_template_search.id,
                    'product_id' : product_variant_search[0].id,
                    'min_qty' : values.get('min_qty') or 1,
                    'price' : values.get('price') or 0,
                    'date_start' : values.get('date_start') or False,
                    'date_end' : values.get('date_end') or False,
                    'delay' : values.get('delay') or 0,
                }
            
            sale_id = supplier_search.create(vals)            

            return sale_id

    @api.multi
    def find_start_date(self, start_date):
        DATETIME_FORMAT = "%Y-%m-%d"
        i_date = datetime.strptime(start_date, DATETIME_FORMAT)
        return i_date

    @api.multi
    def find_end_date(self, end_date):
        DATETIME_FORMAT = "%Y-%m-%d"
        i_date = datetime.strptime(end_date, DATETIME_FORMAT)
        return i_date

    @api.multi
    def find_currency(self, name):
        currency_obj = self.env['res.currency']
        currency_search = currency_obj.search([('name', '=', name)])
        if currency_search:
            return currency_search

    @api.multi
    def find_partner(self, name):
        partner_obj = self.env['res.partner']
        partner_search = partner_obj.search([('name', '=', name)])
        if partner_search:
            return partner_search
        else:
            partner_id = partner_obj.create({
                'name' : name
            })
            return partner_id

    @api.multi
    def import_vendor_pricelist(self):

        if self.import_option == 'csv':
            if self.file:
                keys = ['vendor', 'product_template', 'product_variant','min_qty', 'price', 'currency','date_start','date_end','delay']
                csv_data = base64.b64decode(self.file)
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
                            values.update({'option':self.import_option})

                            res = self.make_pricelist(values)
            else:
                raise Warning(_('Please Seelect a file.'))
        else:
            if self.file:
                fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file))
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
                        
                        start_date_string = False
                        end_dt_string = False
                        delay = line[8] or 1

                        if line[6] and line[7]:
                            start_dt = int(float(line[6]))
                            end_dt = int(float(line[7]))
                        
                            start_dt_datetime = datetime(*xlrd.xldate_as_tuple(start_dt, workbook.datemode))
                            end_dt_datetime = datetime(*xlrd.xldate_as_tuple(end_dt, workbook.datemode))

                            start_date_string = start_dt_datetime.date().strftime('%Y-%m-%d')
                            end_dt_string = end_dt_datetime.date().strftime('%Y-%m-%d')

                        values.update({
                            'vendor':line[0],
                            'product_template' : line[1].split('.')[0],
                            'product_variant' : line[2].split('.')[0],
                            'min_qty' : line[3] or 1,
                            'price' : line[4],
                            'currency' : line[5],
                            'date_start' : start_date_string,
                            'date_end' : end_dt_string,
                            'delay' : int(float(delay)),
                        })
                        res = self.make_pricelist(values)
            else:
                raise Warning(_('Please Seelect a file.'))

        return res

class SalePricelist(models.TransientModel):

    _name = "import.sale.pricelist"

    file = fields.Binary('File')
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
    import_prod_option = fields.Selection([('name', 'Name'),('code', 'Code'),('barcode', 'Barcode')],string='Select Product By',default='name')        
    import_prod_variant_option = fields.Selection([('name', 'Name'),('code', 'Code'),('barcode', 'Barcode')],string='Select Product Variant By',default='name')
    compute_type = fields.Selection([('both', 'Fixed/Percentage'),('formula', 'Formula')],string='Compute Type',default='both')

    @api.multi
    def make_pricelist(self, values):

        prod_pricelist_obj = self.env['product.pricelist']

        if not values.get('name'):
            raise Warning(_("Name is required."))
            return           

        search_pricelist = prod_pricelist_obj.search([
            ('name', '=', values.get('name'))
        ])

        if search_pricelist:
            for sup in search_pricelist:
                if sup.currency_id.name == values.get('currency'):
                    lines = self.make_pricelist_line(values, sup)
                    if lines:
                        sup.write({
                            'item_ids' : [(4,lines.id)],  
                        })
                    return sup
                else:
                    raise Warning(_('Currency is different for "%s" . Please define same.') % values.get('name'))
        else:

            currency_id = self.find_currency(values.get('currency'))
            
            if currency_id:
                vals = {
                    'name' : values.get('name'),
                    'currency_id' : currency_id.id,
                }
            else:
                vals = {
                    'name' : values.get('name'),
                }
            
            pricelist_id = search_pricelist.create(vals)

            apply_on = values.get('apply_on')
            min_qty = values.get('min_qty') or 1
            st_dt = values.get('start_dt')
            ed_dt = values.get('end_dt')
            check_type = self.compute_type

            if(apply_on or min_qty or st_dt or ed_dt or check_type):
                lines = self.make_pricelist_line(values, pricelist_id)
                if lines:
                    pricelist_id.write({
                        'item_ids' : [(4,lines.id)],  
                    })

            return pricelist_id

    @api.multi
    def make_pricelist_line(self, values, pricelist_id):
        
        product_obj = self.env['product.product']
        product_templ_obj = self.env['product.template']
        product_categ_obj = self.env['product.category']
        pricelist_obj = self.env['product.pricelist']
        pricelist_line_obj = self.env['product.pricelist.item']

        DATETIME_FORMAT = "%Y-%m-%d"
        current_time=datetime.now().strftime('%Y-%m-%d')
        product_categ = product_categ_obj.search([('name','=',values.get('check_apply_on'))])
                
        set_product_template = False
        set_product_variant = False

        apply_on = values.get('apply_on') or 'global'
        min_qty = values.get('min_qty') or 1

        st_date = values.get('start_dt') or current_time
        ed_date = values.get('end_dt') or current_time

        st_dt = datetime.strptime(st_date, DATETIME_FORMAT) 
        ed_dt = datetime.strptime(ed_date, DATETIME_FORMAT)
        compute_type = self.compute_type
        fixed = 0.00
        percentage = 0.00
        other_pricelist_column = False
        
        if_formula_then_add = {} 
            

        if compute_type == 'both':
            if values['compute_price'].lower() == 'percentage':
                compute_type = 'percentage'
                percentage = values['amount']
            elif values['compute_price'].lower() == 'fix':
                compute_type = 'fixed'
                fixed = values['amount']
            else:
                compute_type = 'fixed'
                fixed = values['amount']

        elif compute_type == 'formula':
            compute_type = 'formula'
            based_on = False
            
            if values.get('based_on'):

                if values['based_on'].lower() == 'public pricelist':
                    based_on = 'list_price'

                if values['based_on'].lower() == 'cost':
                    based_on = 'standard_price'

                if values['based_on'].lower() == 'other pricelist':
                    based_on = 'pricelist'
                    if values['other_pricelist']:
                        other_pricelist_column = values['other_pricelist'].lower()
                    else:
                        raise Warning(_("Please fill 'Other Pricelist' column in CSV or XLS file."))
                        return


                discount = values['discount']
                surcharge = values['surcharge']
                rounding = values['rounding']
                min_margin = values['min_margin']
                max_margin = values['max_margin']

                if based_on and discount and surcharge and rounding and min_margin and max_margin:

                    if_formula_then_add.update({
                        'based_on': based_on,
                        'discount': discount,
                        'surcharge': surcharge,
                        'rounding': rounding,
                        'min_margin': min_margin,
                        'max_margin': max_margin,   
                    })
            else:

                raise Warning(_("Please fill the 'Based On' column in CSV or XLS file, if you want to import pricelist using formula." ))


        if(apply_on.lower() == 'global'):
            
            vals={
                'applied_on':'3_global',
                'min_quantity':min_qty,
                'date_start': st_dt,
                'date_end': ed_dt,
                'compute_price': compute_type,
                'fixed_price' : fixed,
                'percent_price' : percentage,
            }

            if if_formula_then_add:

                vals.update({
                    'base': if_formula_then_add['based_on'],
                    'price_discount':if_formula_then_add['discount'],
                    'price_surcharge': if_formula_then_add['surcharge'],
                    'price_round': if_formula_then_add['rounding'],
                    'price_min_margin': if_formula_then_add['min_margin'],
                    'price_max_margin' : if_formula_then_add['max_margin'],
                })

                if other_pricelist_column:    
                    other_pricelist_m2o = pricelist_obj.search([('name','=ilike',other_pricelist_column)])                    
                    vals.update({
                        'base_pricelist_id': other_pricelist_m2o.id,
                    })

            return_line_obj = pricelist_line_obj.create(vals)

            return return_line_obj

        elif(apply_on.lower() == 'product category'):

            if product_categ:
                
                vals={
                    'applied_on':'2_product_category',
                    'categ_id' : product_categ.id,
                    'min_quantity':min_qty,
                    'date_start': st_dt,
                    'date_end': ed_dt,
                    'compute_price': compute_type,
                    'fixed_price' : fixed,
                    'percent_price' : percentage,
                }

                if if_formula_then_add:

                    vals.update({
                        'base': if_formula_then_add['based_on'],
                        'price_discount':if_formula_then_add['discount'],
                        'price_surcharge': if_formula_then_add['surcharge'],
                        'price_round': if_formula_then_add['rounding'],
                        'price_min_margin': if_formula_then_add['min_margin'],
                        'price_max_margin' : if_formula_then_add['max_margin'],
                    })

                if other_pricelist_column:    
                    other_pricelist_m2o = pricelist_obj.search([('name','=ilike',other_pricelist_column)])                    
                    vals.update({
                        'base_pricelist_id': other_pricelist_m2o.id,
                    })

                return_line_obj = pricelist_line_obj.create(vals)

                return return_line_obj
            else:

                raise Warning(_(' "%s" is not a category.') % values['check_apply_on'])

        elif(apply_on.lower() == 'product'):

            if self.import_prod_option == 'barcode':
                set_product_template = product_templ_obj.search([('barcode',  '=',values['check_apply_on'])])
                
                if not set_product_template:
                    raise Warning(_(' "%s" Product is not available.') % values['check_apply_on'])
            
            elif self.import_prod_option == 'code':
                set_product_template = product_templ_obj.search([('default_code', '=',values['check_apply_on'])])
                if not set_product_template:
                    raise Warning(_(' "%s" Product is not available.') % values['check_apply_on'])
            
            else:
                
                set_product_template = product_templ_obj.search([('name', '=',values['check_apply_on'])])
                if not set_product_template:
                    raise Warning(_(' "%s" Product is not available.') % values['check_apply_on'])

            if set_product_template:

                vals={
                    'applied_on':'1_product',
                    'product_tmpl_id' : set_product_template.id,
                    'min_quantity':min_qty,
                    'date_start': st_dt,
                    'date_end': ed_dt,
                    'compute_price': compute_type,
                    'fixed_price' : fixed,
                    'percent_price' : percentage,
                }

                if if_formula_then_add:

                    vals.update({
                        'base': if_formula_then_add['based_on'],
                        'price_discount':if_formula_then_add['discount'],
                        'price_surcharge': if_formula_then_add['surcharge'],
                        'price_round': if_formula_then_add['rounding'],
                        'price_min_margin': if_formula_then_add['min_margin'],
                        'price_max_margin' : if_formula_then_add['max_margin'],
                    })
                
                if other_pricelist_column:
                    other_pricelist_m2o = pricelist_obj.search([('name','=ilike',other_pricelist_column)])                    
                    vals.update({
                        'base_pricelist_id': other_pricelist_m2o.id,
                    })

                return_line_obj = pricelist_line_obj.create(vals)

                return return_line_obj

        elif(apply_on.lower() == 'product variant'):

            if self.import_prod_variant_option == 'barcode':
                
                set_product_variant = product_obj.search([('barcode',  '=',values['check_apply_on'])])
                
                if not set_product_variant:
                    raise Warning(_(' "%s" Product variant is not available.') % values['check_apply_on'])
            
            elif self.import_prod_variant_option == 'code':
                
                set_product_variant = product_obj.search([('default_code', '=',values['check_apply_on'])])
                
                if not set_product_variant:
                    raise Warning(_(' "%s" Product varinat is not available.') % values['check_apply_on'])
            
            else:
                
                set_product_variant = product_obj.search([('name', '=',values['check_apply_on'])])
                if not set_product_variant:
                    raise Warning(_(' "%s" Product variant is not available.') % values['check_apply_on'])

            if set_product_variant:

                vals={
                    'applied_on':'0_product_variant',
                    'product_id' : set_product_variant[0].id,
                    'min_quantity':min_qty,
                    'date_start': st_dt,
                    'date_end': ed_dt,
                    'compute_price': compute_type,
                    'fixed_price' : fixed,
                    'percent_price' : percentage,
                }

                if if_formula_then_add:
                    vals.update({
                        'base': if_formula_then_add['based_on'],
                        'price_discount':if_formula_then_add['discount'],
                        'price_surcharge': if_formula_then_add['surcharge'],
                        'price_round': if_formula_then_add['rounding'],
                        'price_min_margin': if_formula_then_add['min_margin'],
                        'price_max_margin' : if_formula_then_add['max_margin'],
                    })

                if other_pricelist_column:    
                    other_pricelist_m2o = pricelist_obj.search([('name','=ilike',other_pricelist_column)])                    
                    vals.update({
                        'base_pricelist_id': other_pricelist_m2o.id,
                    })

                return_line_obj = pricelist_line_obj.create(vals)

                return return_line_obj


    @api.multi
    def find_currency(self, name):
        
        currency_obj = self.env['res.currency']
        currency_search = currency_obj.search([('name', '=', name)])

        if currency_search:
            return currency_search

    @api.multi
    def import_sale_pricelist(self):
            
        if self.import_option == 'csv':
            
            if(self.file):
                if self.compute_type == 'both':
                    keys = ['name', 'currency','apply_on','check_apply_on','min_qty','start_dt','end_dt','compute_price','amount']
                else:
                    keys = ['name', 'currency','apply_on','check_apply_on','min_qty','start_dt','end_dt','based_on','discount','surcharge','rounding','min_margin','max_margin','other_pricelist']


                csv_data = base64.b64decode(self.file)
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
                            values.update({'option':self.import_option})
                            res = self.make_pricelist(values)
            else:
                raise Warning(_('Please Seelect a file.'))
        else:
            
            if(self.file):
                
                fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file))
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
                        
                        start_date_string = False
                        end_dt_string = False
                        amount = line[8] or 0

                        if line[5] and line[6]:
                            start_dt = int(float(line[5]))
                            end_dt = int(float(line[6]))
                            
                            start_dt_datetime = datetime(*xlrd.xldate_as_tuple(start_dt, workbook.datemode))
                            end_dt_datetime = datetime(*xlrd.xldate_as_tuple(end_dt, workbook.datemode))

                            start_date_string = start_dt_datetime.date().strftime('%Y-%m-%d')
                            end_dt_string = end_dt_datetime.date().strftime('%Y-%m-%d')

                        min_qty = 1
                        if line[4]:
                            min_qty = int(float(line[4]))

                        if self.compute_type == 'both':

                            values.update({
                                'name':line[0],
                                'currency' : line[1],
                                'apply_on' : line[2].strip(),
                                'check_apply_on' : line[3],
                                'min_qty' : min_qty,
                                'start_dt' : start_date_string,
                                'end_dt' : end_dt_string,
                                'compute_price' : line[7],
                                'amount' : float(amount),
                            })

                            res = self.make_pricelist(values)

                        else:

                            if not len(line) > 9:
                                raise Warning(_("Please select proper file when you select 'Formula' option."))
                                return
                            discount = line[8] or 0
                            surcharge = line[9] or 0
                            rounding = line[10] or 0
                            min_margin = line[11] or 0
                            max_margin = line[12] or 0
                            values.update({
                                'name':line[0],
                                'currency' : line[1],
                                'apply_on' : line[2].strip(),
                                'check_apply_on' : line[3],
                                'min_qty' : min_qty,
                                'start_dt' : start_date_string,
                                'end_dt' : end_dt_string,
                                'based_on' : line[7],
                                'discount' : float(discount),
                                'surcharge' : float(surcharge),
                                'rounding' : float(rounding),
                                'min_margin' : float(min_margin),
                                'max_margin' : float(max_margin),
                            })

                            if line[7].lower() == 'other pricelist' and line[13]:
                                values.update({
                                    'other_pricelist': line[13]    
                                })

                            res = self.make_pricelist(values)
            else:

                raise Warning(_('Please Seelect a file.'))


class ProductPricelist(models.TransientModel):

    _name = "import.product.pricelist"

    file = fields.Binary('File')
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
    import_prod_option = fields.Selection([('name', 'Name'),('code', 'Code'),('barcode', 'Barcode')],string='Select Product By',default='name')        


    @api.multi
    def make_product_pricelist(self, values):

        prod_pricelist_obj = self.env['product.pricelist']
        product_templ_obj = self.env['product.template']

        DATETIME_FORMAT = "%Y-%m-%d"

        product = values['product']
        pricelist = values['pricelist'].lower()
        price = values['price'].lower()
        min_qty = values['min_qty'] or 1
        current_time=datetime.now().strftime('%Y-%m-%d')
        st_dt = datetime.strptime(values.get('start_dt') or current_time, DATETIME_FORMAT)
        ed_dt = datetime.strptime(values.get('end_dt') or current_time, DATETIME_FORMAT)
        find_product = False

        if pricelist and price:

            if self.import_prod_option == 'barcode':
            
                find_product = product_templ_obj.search([('barcode','=',product)])
                            
            elif self.import_prod_option == 'code':
                
                find_product = product_templ_obj.search([('default_code','=',product)])
            
            else:
                find_product = product_templ_obj.search([('name','=ilike',product.lower())])


            if find_product:
                pricelist_id = prod_pricelist_obj.search([('name','=ilike',pricelist)])

                if not pricelist:
                    
                    raise Warning(_('Please fill the pricelist column.') % pricelist)
                    return

                else:

                    get_pricelist = False

                    pricelist_exist = prod_pricelist_obj.search([('name','=ilike',pricelist)])

                    if pricelist_exist:
                        get_pricelist = pricelist_exist 
                    else:
                        product_pricelist = {
                            'name':values['pricelist'],
                            'product_id': find_product.id,
                        }

                        get_pricelist = prod_pricelist_obj.create(product_pricelist)

                    item_list ={
                        'pricelist_id': get_pricelist.id,
                        'fixed_price': price,
                        'min_quantity': min_qty,
                        'date_start': st_dt,
                        'date_end': ed_dt,
                    }

                    find_product.write({
                        'item_ids': [(0,0,item_list)]    
                    })

        else:
            raise Warning(_("Pricelist or price are required."))


    @api.multi
    def import_product_pricelist(self):
            
            if self.import_option == 'csv':
                
                if(self.file):
                    
                    keys = ['product', 'pricelist','price','min_qty','start_dt','end_dt']

                    csv_data = base64.b64decode(self.file)
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
                                values.update({'option':self.import_option})
                                res = self.make_product_pricelist(values)
                else:
                    raise Warning(_('Please Seelect a file.'))
            else:
                
                if(self.file):
                    
                    fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                    fp.write(binascii.a2b_base64(self.file))
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

                            start_date_string = False
                            end_dt_string = False

                            if line[4] and line[5]:
                                
                                start_dt = int(float(line[4]))
                                end_dt = int(float(line[5]))

                                start_dt_datetime = datetime(*xlrd.xldate_as_tuple(start_dt, workbook.datemode))
                                end_dt_datetime = datetime(*xlrd.xldate_as_tuple(end_dt, workbook.datemode))

                                start_date_string = start_dt_datetime.date().strftime('%Y-%m-%d')
                                end_dt_string = end_dt_datetime.date().strftime('%Y-%m-%d')
                            
                            min_qty = 1

                            if line[3]:
                                min_qty = int(float(line[3]))
                            

                            values.update({
                                'product':line[0],
                                'pricelist' : line[1],
                                'price' : line[2],
                                'min_qty' : min_qty,
                                'start_dt' : start_date_string,
                                'end_dt' : end_dt_string,
                            })

                            res = self.make_product_pricelist(values)

                else:

                    raise Warning(_('Please Seelect a file.'))
            
