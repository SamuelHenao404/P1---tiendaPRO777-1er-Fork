import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from django.utils import timezone

def generar_recibo_pdf(pedido):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, f"Recibo de Pedido #{pedido.id}")
    y -= 30
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Cliente: {pedido.nombre_cliente}")
    y -= 20
    p.drawString(50, y, f"Dirección de envío: {pedido.direccion_envio}")
    y -= 20
    p.drawString(50, y, f"Fecha: {pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M') if pedido.fecha_creacion else timezone.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 20
    p.drawString(50, y, f"Empresa encargada: {pedido.empresa_encargada}")
    y -= 30
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y, "Productos:")
    y -= 20
    p.setFont("Helvetica", 12)
    for item in pedido.pedidoitem_set.all():
        p.drawString(60, y, f"- {item.item.title} x{item.cantidad}")
        y -= 18
        if y < 80:
            p.showPage()
            y = height - 50
    y -= 10
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Estado del pedido: {pedido.get_estado_display()}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return ContentFile(buffer.read(), name=f"recibo_pedido_{pedido.id}.pdf")
