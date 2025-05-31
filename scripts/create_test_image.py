#!/usr/bin/env python3
"""
Create a simple test image with digits for testing the classification API.
"""

from PIL import Image, ImageDraw, ImageFont
import sys

def create_test_image():
    """Create a simple test image with digits."""
    # Create a white background image
    width, height = 200, 50
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fallback to basic if not available
    try:
        # Try to load a larger font
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # Draw some test digits
    text = "12345"
    
    # Calculate text position to center it
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        # Rough estimate for default font
        text_width = len(text) * 10
        text_height = 15
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw the text in a color that should be detected by the filter
    # Using a color within the range (160, 154, 157) to (255, 255, 255)
    # This matches the color range used in eval_forest.py
    text_color = (200, 200, 200)  # Light gray that should be detected
    
    if font:
        draw.text((x, y), text, fill=text_color, font=font)
    else:
        draw.text((x, y), text, fill=text_color)
    
    # Save the image
    image.save('image.png')
    print(f"Created test image 'image.png' with text: {text}")
    print(f"Image size: {width}x{height}")
    print(f"Text color: {text_color}")

if __name__ == "__main__":
    create_test_image()
