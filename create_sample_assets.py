"""
Script to create sample test images for Food Verse AI:
- sample_images/salmon_bowl.jpg
- sample_images/avocado_toast.jpg
- sample_images/vegetable_biryani.jpg
- sample_images/laptop_non_food.jpg (to test non-food detection)
"""

import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("sample_images", exist_ok=True)

def create_salmon_bowl():
    w, h = 800, 600
    img = Image.new("RGB", (w, h), color="#1E293B")
    draw = ImageDraw.Draw(img)
    
    # Wooden table background
    for y in range(h):
        shade = int(35 + 10 * ((y % 40) / 40.0))
        draw.line([(0, y), (w, y)], fill=(shade, shade - 10, shade - 15))
        
    # Ceramic Bowl
    draw.ellipse([120, 60, 680, 540], fill="#0F172A", outline="#CBD5E1", width=6)
    draw.ellipse([140, 80, 660, 520], fill="#334155")
    
    # Quinoa base
    draw.ellipse([160, 100, 640, 500], fill="#D97706")
    
    # Salmon fillet (Pink-Orange)
    draw.polygon([(260, 220), (520, 170), (550, 310), (280, 370)], fill="#F97316", outline="#EA580C")
    # Grill marks
    for x_offset in range(0, 240, 45):
        draw.line([(300 + x_offset, 210), (320 + x_offset, 340)], fill="#7C2D12", width=5)
        
    # Greens / Spinach
    draw.pieslice([180, 120, 340, 280], start=45, end=180, fill="#15803D")
    
    # Cherry Tomatoes (Red dots)
    for cx, cy in [(480, 130), (530, 160), (450, 180), (570, 220)]:
        draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill="#DC2626", outline="#991B1B")
        
    # Cucumbers (Green slices)
    for cx, cy in [(200, 340), (250, 400), (200, 440), (260, 460)]:
        draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill="#86EFAC", outline="#16A34A", width=3)
        
    # Kalamata Olives (Purple-black dots)
    for cx, cy in [(380, 420), (440, 450), (490, 410), (420, 470)]:
        draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill="#312E81")
        
    # Tahini cream drizzle
    draw.arc([240, 150, 560, 450], start=20, end=190, fill="#FEF08A", width=5)
    draw.arc([260, 180, 520, 400], start=210, end=340, fill="#FEF08A", width=4)

    # Label overlay
    draw.rectangle([20, 20, 340, 60], fill="#0F172A")
    draw.text((35, 30), "Mediterranean Salmon Bowl", fill="#38BDF8")
    
    img.save("sample_images/salmon_bowl.jpg", quality=92)
    print("Created salmon_bowl.jpg")

def create_avocado_toast():
    w, h = 800, 600
    img = Image.new("RGB", (w, h), color="#F1F5F9")
    draw = ImageDraw.Draw(img)
    
    # Marble countertop texture
    for i in range(0, w, 60):
        draw.line([(i, 0), (i + 100, h)], fill="#E2E8F0", width=2)
        
    # Wooden Cutting Board
    draw.rounded_rectangle([100, 70, 700, 530], radius=30, fill="#78350F", outline="#451A03", width=6)
    
    # Sourdough Slice 1
    draw.rounded_rectangle([150, 130, 410, 470], radius=25, fill="#D97706", outline="#92400E", width=5)
    # Avocado Mash
    draw.rounded_rectangle([170, 150, 390, 450], radius=15, fill="#65A30D")
    
    # Sourdough Slice 2
    draw.rounded_rectangle([430, 130, 660, 470], radius=25, fill="#D97706", outline="#92400E", width=5)
    # Avocado Mash
    draw.rounded_rectangle([450, 150, 640, 450], radius=15, fill="#65A30D")
    
    # Poached Egg on Slice 1
    draw.ellipse([210, 230, 350, 370], fill="#F8FAFC", outline="#E2E8F0", width=2)
    draw.ellipse([250, 270, 310, 330], fill="#FBBF24")  # Runny yolk
    
    # Chili flakes & microgreens
    for cx, cy in [(230, 260), (320, 250), (280, 340), (490, 200), (550, 300), (510, 400), (580, 230)]:
        draw.rectangle([cx, cy, cx + 5, cy + 5], fill="#EF4444")
    for cx, cy in [(500, 220), (530, 330), (600, 380), (470, 360)]:
        draw.ellipse([cx, cy, cx + 8, cy + 16], fill="#15803D")

    # Label overlay
    draw.rectangle([20, 20, 300, 60], fill="#0F172A")
    draw.text((35, 30), "Avocado Sourdough Toast", fill="#4ADE80")

    img.save("sample_images/avocado_toast.jpg", quality=92)
    print("Created avocado_toast.jpg")

def create_vegetable_biryani():
    w, h = 800, 600
    img = Image.new("RGB", (w, h), color="#1E293B")
    draw = ImageDraw.Draw(img)
    
    # Dark slate background
    # Brass Handi / Plate
    draw.ellipse([140, 70, 660, 530], fill="#B45309", outline="#D97706", width=8)
    draw.ellipse([160, 90, 640, 510], fill="#FDE68A")
    
    # Spiced Basmati Rice & Saffron strands
    for cx in range(200, 600, 40):
        for cy in range(140, 460, 35):
            draw.line([(cx, cy), (cx + 15, cy + 6)], fill="#D97706", width=3)
            draw.line([(cx - 10, cy + 12), (cx + 5, cy + 15)], fill="#EA580C", width=2)

    # Vegetables (green peas, carrots, mint leaves)
    for cx, cy in [(260, 180), (380, 220), (460, 190), (310, 320), (480, 340), (390, 420), (250, 400)]:
        draw.ellipse([cx, cy, cx + 18, cy + 18], fill="#16A34A")  # Peas
    for cx, cy in [(320, 160), (420, 260), (490, 270), (280, 260), (430, 380)]:
        draw.rectangle([cx, cy, cx + 22, cy + 14], fill="#EA580C")  # Carrots
        
    # Caramelized onions (Birista)
    for cx, cy in [(330, 220), (370, 300), (420, 180), (310, 360), (460, 390)]:
        draw.arc([cx, cy, cx + 40, cy + 25], start=0, end=160, fill="#78350F", width=4)

    # Raita bowl on the side
    draw.ellipse([570, 390, 760, 560], fill="#0F172A", outline="#CBD5E1", width=4)
    draw.ellipse([585, 405, 745, 545], fill="#F8FAFC")
    draw.ellipse([645, 455, 685, 495], fill="#86EFAC")  # Cucumber in raita

    # Label overlay
    draw.rectangle([20, 20, 260, 60], fill="#0F172A")
    draw.text((35, 30), "Dum Vegetable Biryani", fill="#FBBF24")

    img.save("sample_images/vegetable_biryani.jpg", quality=92)
    print("Created vegetable_biryani.jpg")

def create_non_food_laptop():
    w, h = 800, 600
    img = Image.new("RGB", (w, h), color="#0F172A")
    draw = ImageDraw.Draw(img)
    
    # Desk
    draw.rectangle([0, 380, w, h], fill="#334155")
    
    # Laptop Screen
    draw.rounded_rectangle([200, 100, 600, 380], radius=12, fill="#1E293B", outline="#94A3B8", width=4)
    draw.rectangle([220, 120, 580, 360], fill="#0284C7")
    draw.text((320, 220), "ANTIGRAVITY IDE", fill="#F8FAFC")
    draw.text((310, 260), "def main(): return 42", fill="#BAE6FD")
    
    # Laptop Keyboard base
    draw.polygon([(140, 380), (660, 380), (710, 480), (90, 480)], fill="#64748B", outline="#475569")
    draw.polygon([(180, 395), (620, 395), (645, 445), (155, 445)], fill="#1E293B")
    # Trackpad
    draw.rectangle([340, 450, 460, 475], fill="#475569")
    
    # Label overlay
    draw.rectangle([20, 20, 320, 60], fill="#DC2626")
    draw.text((35, 30), "NON-FOOD TEST: Laptop Computer", fill="#FFFFFF")

    img.save("sample_images/laptop_non_food.jpg", quality=92)
    print("Created laptop_non_food.jpg")

if __name__ == "__main__":
    create_salmon_bowl()
    create_avocado_toast()
    create_vegetable_biryani()
    create_non_food_laptop()
    print("All sample images generated successfully!")
