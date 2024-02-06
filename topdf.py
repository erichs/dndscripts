from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image
import os
import re

def add_image_to_pdf(image_path, pdf_canvas, x, y, diameter, filename, text_above):
    """Add an image to the PDF at the specified location and size, then add the filename text."""
    with Image.open(image_path) as img:
        # Composite with white background if RGBA
        if img.mode == 'RGBA':
            white_bg = Image.new('RGB', img.size, 'white')
            white_bg.paste(img, (0, 0), img.split()[3])
            img = white_bg

        img.save(image_path, 'PNG')
        pdf_canvas.drawInlineImage(image_path, x, y - diameter, width=diameter, height=diameter)

    # Modify filename to keep size category only
    modified_filename = re.sub(r'(tiny|small|medium|large|huge|gargantuan)(.*)', r'\1', filename)

    # Adjust text placement based on flag
    if text_above:
        text_y = y + 5  # Space above the image
    else:
        text_y = y - diameter - 15  # Space below the image

    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.drawString(x, text_y, modified_filename)

def layout_images(directory, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter

    x_margin = 1 * cm
    y_margin = 2 * cm
    spacing = 1 * cm

    x, y = x_margin, height - y_margin
    row_height = 0
    text_above_image = True  # Initialize flag for alternating text placement

    images = []
    for filename in sorted(os.listdir(directory)):
        size_match = re.search(r'_(\d+)in', filename)
        count_match = re.search(r'_(\d+)ct', filename)
        if size_match:
            size_in_inches = int(size_match.group(1))
            diameter = size_in_inches * 2.54 * cm
            count = int(count_match.group(1)) if count_match else 1
            images.extend([(filename, diameter)] * count)

    images.sort(key=lambda x: -x[1])

    for filename, diameter in images:
        if x + diameter + spacing > width - x_margin:
            x = x_margin
            y -= (row_height + spacing + (20 if text_above_image else 0))  # Adjust for text space
            row_height = 0
            text_above_image = not text_above_image  # Toggle for the new row

        if y - diameter - spacing - (20 if text_above_image else 0) < y_margin:
            c.showPage()
            x, y = x_margin, height - y_margin - diameter
            row_height = 0
            text_above_image = True  # Reset flag for new page

        add_image_to_pdf(os.path.join(directory, filename), c, x, y, diameter, filename, text_above_image)
        x += (diameter + spacing)
        row_height = max(row_height, diameter + (20 if text_above_image else 0))
        text_above_image = not text_above_image  # Toggle for the next image

    c.save()

layout_images('./cropped', 'circles_layout_us_letter_alternating_text.pdf')
