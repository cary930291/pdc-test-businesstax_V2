# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.http import content_disposition
from datetime import datetime, timedelta
from io import BytesIO


class BusinessTaxExportTextFile(http.Controller):

    @http.route('/make/txt', auth='public', type='http')
    def make_txt(self, invoice_ids, **kw):

        content = ''
        invoice_ids = invoice_ids.split(",")
        ndate = datetime.today() + timedelta(hours=8)
        for line in invoice_ids:
            inv_rec = request.env['businesstax.invoice'].sudo().browse([int(line)])
            if inv_rec.year.name and inv_rec.period.name:
                content += inv_rec.year.name + inv_rec.period.name  # 發票年月(5)
            else:
                content += '00000'
            if inv_rec.vat_declare_code.code:
                content += str(inv_rec.vat_declare_code.code)  # 格式代號(2)
            else:
                content += '00'
            if inv_rec.type.id in [1, 2, 3]:
                 content += str(inv_rec.declare_deduction.code)  # 扣抵代號(1) 銷項沒有
            if inv_rec.name:
                content += inv_rec.name.zfill(10)  # 發票號碼(10)
            else:
                content += '0000000000'
            if inv_rec.vat_code_partner :
                content += str(inv_rec.vat_code_partner).zfill(8)  # 銷售人統編(8)
            else:
                content +='00000000'
            if inv_rec.tax_code_type.code:
                content += str(inv_rec.tax_code_type.code)  # 課稅別(1)
            else:
                content += '0'
            if inv_rec.sales_amount:
                content += str(int(inv_rec.sales_amount)).zfill(12)  # 發票金額(12)
            else:
                content += '000000000000'
            if inv_rec.tax_amount:
                content += str(inv_rec.tax_amount).zfill(10)  # 稅額(10)
            else:
                content += '0000000000'
            content += '\r\n'
        exportdate = ndate.strftime("%Y%m%d%H%M%S")
        FileName = 'BusinessTax_' + exportdate + '.txt'
        pdfhttpheaders = [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', content_disposition(FileName))
        ]
        return request.make_response(content, headers=pdfhttpheaders)
