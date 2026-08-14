import io
from datetime import datetime
from typing import Dict, Any

def generate_invoice_pdf(invoice_data: Dict[str, Any]) -> bytes:
    """Generates professional PDF invoice bytes for TravelMind AI.
    
    Formula Verification:
    Room Cost = Room Price * Nights * Rooms
    Subtotal = Room Cost
    Final Amount = Subtotal + Tax + Service Fee - Discount
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#06b6d4')  # Cyan 500
        )
        tagline_style = ParagraphStyle(
            'Tagline',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=10,
            leading=12,
            textColor=colors.HexColor('#64748b')  # Slate 500
        )
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=14,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=6
        )
        cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=12)
        cell_normal = ParagraphStyle('CellNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=12)
        cell_right = ParagraphStyle('CellRight', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=12, alignment=2)
        cell_right_bold = ParagraphStyle('CellRightBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=12, alignment=2)

        story = []

        # Header Banner
        header_table_data = [
            [
                Paragraph("<b>TRAVELMIND AI</b>", title_style),
                Paragraph(f"<b>INVOICE</b><br/><font size=9 color='#64748b'>#{invoice_data.get('invoice_number', 'TMAI-INV-2026-000001')}</font>", cell_right_bold)
            ],
            [
                Paragraph("Predict. Personalize. Plan.", tagline_style),
                Paragraph(f"<font size=9 color='#64748b'>Date: {invoice_data.get('created_at', datetime.now().strftime('%Y-%m-%d'))}</font>", cell_right)
            ]
        ]
        header_table = Table(header_table_data, colWidths=[4.0 * inch, 3.2 * inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=15))

        # Customer & Booking Details Section
        cust_info = [
            [Paragraph("<b>CUSTOMER DETAILS</b>", heading_style), Paragraph("<b>BOOKING DETAILS</b>", heading_style)],
            [
                Paragraph(f"<b>Guest:</b> {invoice_data.get('guest_name', 'Customer')}<br/>"
                          f"<b>Email:</b> {invoice_data.get('guest_email', 'guest@travelmind.ai')}<br/>"
                          f"<b>Phone:</b> {invoice_data.get('guest_phone', '+91 98765 43210')}", cell_normal),
                Paragraph(f"<b>Booking Reference:</b> {invoice_data.get('booking_reference', 'TMAI-2026-000123')}<br/>"
                          f"<b>Hotel:</b> {invoice_data.get('hotel_name', 'Ocean Pearl Resort')}<br/>"
                          f"<b>Room Type:</b> {invoice_data.get('room_type', 'Deluxe Room')}<br/>"
                          f"<b>Check-In:</b> {invoice_data.get('check_in', '2026-08-20')} | <b>Check-Out:</b> {invoice_data.get('check_out', '2026-08-23')}<br/>"
                          f"<b>Nights:</b> {invoice_data.get('nights', 3)} | <b>Rooms:</b> {invoice_data.get('rooms', 1)}", cell_normal)
            ]
        ]
        info_table = Table(cust_info, colWidths=[3.6 * inch, 3.6 * inch])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f1f5f9')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))

        # Price Breakdown Table
        subtotal = float(invoice_data.get('subtotal', 10500))
        tax = float(invoice_data.get('tax', 1890))
        service_fee = float(invoice_data.get('service_fee', 300))
        discount = float(invoice_data.get('discount', 500))
        total_amount = float(invoice_data.get('total_amount', 12190))
        curr = invoice_data.get('currency', 'INR')
        curr_symbol = '₹' if curr == 'INR' else '$'

        breakdown_data = [
            [Paragraph("<b>Description</b>", cell_bold), Paragraph("<b>Nights / Qty</b>", cell_bold), Paragraph("<b>Rate</b>", cell_right_bold), Paragraph("<b>Amount</b>", cell_right_bold)],
            [
                Paragraph(f"Room Charges ({invoice_data.get('room_type', 'Deluxe Room')})", cell_normal),
                Paragraph(f"{invoice_data.get('nights', 3)} Nights × {invoice_data.get('rooms', 1)} Room(s)", cell_normal),
                Paragraph(f"{curr_symbol}{invoice_data.get('room_price', 3500):,.2f}", cell_right),
                Paragraph(f"{curr_symbol}{subtotal:,.2f}", cell_right)
            ],
            [Paragraph("Subtotal", cell_bold), "", "", Paragraph(f"{curr_symbol}{subtotal:,.2f}", cell_right_bold)],
            [Paragraph("Tax (18% GST)", cell_normal), "", "", Paragraph(f"{curr_symbol}{tax:,.2f}", cell_right)],
            [Paragraph("Service Fee", cell_normal), "", "", Paragraph(f"{curr_symbol}{service_fee:,.2f}", cell_right)],
            [Paragraph("Discount", cell_normal), "", "", Paragraph(f"-{curr_symbol}{discount:,.2f}", cell_right)],
            [Paragraph("<b>TOTAL AMOUNT</b>", ParagraphStyle('TLabel', parent=cell_bold, fontSize=12)), "", "", Paragraph(f"<b>{curr_symbol}{total_amount:,.2f}</b>", ParagraphStyle('TVal', parent=cell_right_bold, fontSize=12, textColor=colors.HexColor('#0284c7')))]
        ]

        breakdown_table = Table(breakdown_data, colWidths=[3.2 * inch, 1.8 * inch, 1.1 * inch, 1.1 * inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0fdf4')),
        ]))
        story.append(breakdown_table)
        story.append(Spacer(1, 20))

        # Status Badges Section
        pay_status = invoice_data.get('payment_status', 'Pending')
        status_color = colors.HexColor('#16a34a') if pay_status == 'Paid' else (colors.HexColor('#dc2626') if pay_status == 'Failed' else colors.HexColor('#d97706'))

        status_text = (
            f"<b>Payment Status:</b> <font color='{status_color.hexval()}'><b>{pay_status.upper()}</b></font><br/>"
            f"<b>Booking Status:</b> Confirmed<br/>"
            f"<font size=8 color='#64748b'>Demo Payment — No real money was charged.</font>"
        )
        story.append(Paragraph(status_text, cell_normal))

        doc.build(story)
        return buffer.getvalue()

    except Exception:
        # Minimalistic PDF Generator Fallback if ReportLab fails
        buffer = io.BytesIO()
        inv_num = invoice_data.get('invoice_number', 'TMAI-INV-2026-000001')
        subtotal = float(invoice_data.get('subtotal', 10500))
        tax = float(invoice_data.get('tax', 1890))
        service_fee = float(invoice_data.get('service_fee', 300))
        discount = float(invoice_data.get('discount', 500))
        total_amount = float(invoice_data.get('total_amount', 12190))
        
        pdf_content = (
            f"%PDF-1.4\n"
            f"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
            f"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
            f"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
            f"4 0 obj << /Length 400 >> stream\n"
            f"BT /F1 18 Tf 50 740 TD (TRAVELMIND AI - INVOICE {inv_num}) Tj ET\n"
            f"BT /F1 12 Tf 50 710 TD (Guest: {invoice_data.get('guest_name', 'Customer')}) Tj ET\n"
            f"BT /F1 12 Tf 50 690 TD (Hotel: {invoice_data.get('hotel_name', 'Ocean Pearl Resort')}) Tj ET\n"
            f"BT /F1 12 Tf 50 670 TD (Room Charges: INR {subtotal:.2f}) Tj ET\n"
            f"BT /F1 12 Tf 50 650 TD (Tax 18%: INR {tax:.2f}) Tj ET\n"
            f"BT /F1 12 Tf 50 630 TD (Service Fee: INR {service_fee:.2f}) Tj ET\n"
            f"BT /F1 12 Tf 50 610 TD (Discount: -INR {discount:.2f}) Tj ET\n"
            f"BT /F1 14 Tf 50 580 TD (TOTAL AMOUNT: INR {total_amount:.2f}) Tj ET\n"
            f"BT /F1 10 Tf 50 550 TD (Payment Status: {invoice_data.get('payment_status', 'Pending')}) Tj ET\n"
            f"BT /F1 10 Tf 50 530 TD (Demo Payment - No real money was charged.) Tj ET\n"
            f"endstream endobj\n"
            f"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
            f"xref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000244 00000 n\n0000000700 00000 n\n"
            f"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n770\n%%EOF"
        )
        return pdf_content.encode('utf-8')
