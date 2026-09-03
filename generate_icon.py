from PIL import Image, ImageDraw

sizes = [16, 24, 32, 48, 64, 128, 256]
images = []

for size in sizes:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = max(1, size // 12)
    draw.rounded_rectangle(
        (margin, margin, size - margin - 1, size - margin - 1),
        radius=max(2, size // 5),
        fill=(37, 99, 235, 255),
    )
    # White SMS bubble
    x1, y1 = size * 0.20, size * 0.24
    x2, y2 = size * 0.80, size * 0.68
    draw.rounded_rectangle((x1, y1, x2, y2), radius=max(2, size // 8), fill=(255, 255, 255, 255))
    tail = [(size * 0.36, y2 - 1), (size * 0.30, size * 0.80), (size * 0.48, y2 - 1)]
    draw.polygon(tail, fill=(255, 255, 255, 255))
    # Message dots
    r = max(1, size // 18)
    cy = size * 0.46
    for cx in (size * 0.40, size * 0.50, size * 0.60):
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(37, 99, 235, 255))
    images.append(img)

images[-1].save("app.ico", format="ICO", sizes=[(s, s) for s in sizes], append_images=images[:-1])
print("Created app.ico")
