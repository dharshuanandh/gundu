import struct
import zlib

def create_simple_png(filename, width=200, height=200):
    """Create a minimal PNG without PIL"""
    # PNG header
    png_header = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk (width, height, bit depth, color type, etc.)
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    # IDAT chunk (image data)
    idat_data = b''
    for y in range(height):
        idat_data += b'\x00'  # Filter type (no filter)
        for x in range(width):
            # Simple pattern: gradient-like colors
            r = (x * 255) // width
            g = (y * 255) // height
            b = 128
            idat_data += bytes([r, g, b])
    
    idat_compressed = zlib.compress(idat_data)
    idat_crc = zlib.crc32(b'IDAT' + idat_compressed) & 0xffffffff
    idat_chunk = struct.pack('>I', len(idat_compressed)) + b'IDAT' + idat_compressed + struct.pack('>I', idat_crc)
    
    # IEND chunk
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    
    # Write PNG file
    with open(filename, 'wb') as f:
        f.write(png_header + ihdr_chunk + idat_chunk + iend_chunk)

# Create test images
for i in range(3):
    create_simple_png(f'test_face_{i}.png')
    print(f'Created test_face_{i}.png')
