import os
import re
from PIL import Image, ImageDraw

def crop_circle(image):
    """ Crop the image into a circle and draw a 2px black circle as a border. """
    # Create a mask for the circle
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + image.size, fill=255)
    
    # Create a new image to paste the circle on
    result = Image.new('RGBA', image.size, (0, 0, 0, 0))
    result.paste(image, (0, 0), mask)
    
    # Draw a 2px black border around the circle
    draw = ImageDraw.Draw(result)
    draw.ellipse((0, 0) + image.size, outline="black", width=2)
    
    return result

def process_images(directory):
    os.makedirs(os.path.join(directory, 'cropped'), exist_ok=True)
    file_pattern = re.compile(r'_\d+in(_\d+ct)?\.(png|webp)$')
    size_in_inches_pattern = re.compile(r'_(\d+)in(?:_\d+ct)?\.(png|webp)')

    for filename in os.listdir(directory):
        if file_pattern.search(filename):
            try:
                size_in_inches_match = size_in_inches_pattern.search(filename)
                if size_in_inches_match:
                    size_in_inches = int(size_in_inches_match.group(1))
                    if size_in_inches in [1, 2, 3, 4]:  # Assuming these are the only valid sizes
                        image = Image.open(os.path.join(directory, filename))
                        size_in_pixels = size_in_inches * 300  # pixels per inch
                        image = image.resize((size_in_pixels, size_in_pixels))
                        image = crop_circle(image)

                        new_filename = re.sub(r'\.(png|webp)$', '_circle.\\1', filename)
                        image.save(os.path.join(directory, 'cropped', new_filename))
                        print(f"Processed {filename}")
                else:
                    print(f"Skipping {filename}: Does not match size pattern")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

process_images('.')  # Replace with your directory path
