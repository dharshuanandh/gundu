from PIL import Image, ImageDraw
import random
import os

# Ensure directory exists
os.makedirs('data/images', exist_ok=True)

# Create test images
for i in range(3):
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some random shapes to simulate face features
    for _ in range(10):
        x = random.randint(20, 180)
        y = random.randint(20, 180)
        draw.ellipse([x, y, x+30, y+30], fill=(random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)))
    
    img.save(f'test_face_{i}.jpg')
    print(f'Created test_face_{i}.jpg')
