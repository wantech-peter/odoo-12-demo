
from odoo import models
import datetime
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter
import io


class CustomerNumberPartnerLedger(models.AbstractModel):
    _inherit = "account.report"

    def get_xlsx(self, options, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self._get_report_name()[:31])

        date_default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666',
             'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666',
             'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666',
             'indent': 2})
        default_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'bottom': 2})
        super_col_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'align': 'center'})
        level_0_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6,
             'font_color': '#666666'})
        level_1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1,
             'font_color': '#666666'})
        level_2_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12,
             'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12,
             'font_color': '#666666'})
        level_2_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12,
             'font_color': '#666666'})
        level_3_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666',
             'indent': 2})
        level_3_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12,
             'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})

        # Set the first column width to 50
        sheet.set_column(0, 0, 50)

        super_columns = self._get_super_columns(options)
        y_offset = bool(super_columns.get('columns')) and 1 or 0

        sheet.write(y_offset, 0, '', title_style)

        # Todo in master: Try to put this logic elsewhere
        x = super_columns.get('x_offset', 0)
        for super_col in super_columns.get('columns', []):
            cell_content = super_col.get('string', '').replace('<br/>',
                                                               ' ').replace(
                '&nbsp;', ' ')
            x_merge = super_columns.get('merge')
            if x_merge and x_merge > 1:
                sheet.merge_range(0, x, 0, x + (x_merge - 1), cell_content,
                                  super_col_style)
                x += x_merge
            else:
                sheet.write(0, x, cell_content, super_col_style)
                x += 1
        for row in self.get_header(options):
            x = 0
            for column in row:
                colspan = column.get('colspan', 1)
                header_label = column.get('name', '').replace('<br/>',
                                                              ' ').replace(
                    '&nbsp;', ' ')
                if colspan == 1:
                    sheet.write(y_offset, x, header_label, title_style)
                else:
                    sheet.merge_range(y_offset, x, y_offset, x + colspan - 1,
                                      header_label, title_style)
                x += colspan
            y_offset += 1
        ctx = self._set_context(options)
        ctx.update(
            {'no_format': True, 'print_mode': True, 'prefetch_fields': False})
        # deactivating the prefetching saves ~35% on get_lines running time
        lines = self.with_context(ctx)._get_lines(options)

        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines)

        # write all data rows
        for y in range(0, len(lines)):
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            if 'date' in lines[y].get('class', ''):
                # write the dates with a specific format to avoid them being casted as floats in the XLSX
                if isinstance(lines[y]['name'],
                              (datetime.date, datetime.datetime)):
                    sheet.write_datetime(y + y_offset, 0, lines[y]['name'],
                                         date_default_col1_style)
                else:
                    sheet.write(y + y_offset, 0, lines[y]['name'],
                                date_default_col1_style)
            else:
                # write the first column, with a specific style to manage the indentation
                if lines[y].get('partner_number'):
                    number = str(lines[y].get('partner_number')) + '-'
                else:
                    number = ''
                name_number = number + lines[y]['name']
                sheet.write(y + y_offset, 0, name_number, col1_style)

            # write all the remaining cells
            for x in range(1, len(lines[y]['columns']) + 1):
                this_cell_style = style
                if 'date' in lines[y]['columns'][x - 1].get('class', ''):
                    # write the dates with a specific format to avoid them being casted as floats in the XLSX
                    this_cell_style = date_default_style
                    if isinstance(lines[y]['columns'][x - 1].get('name', ''),
                                  (datetime.date, datetime.datetime)):
                        sheet.write_datetime(y + y_offset,
                                             x + lines[y].get('colspan',
                                                              1) - 1,
                                             lines[y]['columns'][x - 1].get(
                                                 'name', ''), this_cell_style)
                    else:
                        sheet.write(y + y_offset,
                                    x + lines[y].get('colspan', 1) - 1,
                                    lines[y]['columns'][x - 1].get('name', ''),
                                    this_cell_style)
                else:
                    sheet.write(y + y_offset,
                                x + lines[y].get('colspan', 1) - 1,
                                lines[y]['columns'][x - 1].get('name', ''),
                                this_cell_style)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()