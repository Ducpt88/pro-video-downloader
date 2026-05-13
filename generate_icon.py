from PIL import Image, ImageDraw
import os

def create_pro_icon():
    # Kích thước lớn để làm icon xịn
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. Vẽ nền tròn gradient (giả lập bằng 2 vòng tròn)
    draw.ellipse([10, 10, 246, 246], fill=(0, 184, 148)) # Màu xanh Emerald
    draw.ellipse([30, 30, 226, 226], fill=(0, 163, 129)) # Màu đậm hơn chút
    
    # 2. Vẽ biểu tượng mũi tên tải xuống (trắng) cách điệu
    # Thân mũi tên
    draw.rectangle([108, 60, 148, 160], fill="white")
    # Đầu mũi tên (tam giác)
    draw.polygon([(60, 150), (128, 220), (196, 150)], fill="white")
    
    # 3. Vẽ tia sét nhỏ trang trí màu vàng
    draw.polygon([(160, 40), (190, 80), (170, 80), (180, 120), (150, 70), (170, 70)], fill="#f1c40f")

    # Lưu thành file .ico với nhiều kích thước để Windows không bị "đen thui"
    icon_path = "icon.ico"
    # Di chuyển file cũ nếu có (backup)
    if os.path.exists(icon_path):
        try: 
            if os.path.exists("icon_old.ico"): os.remove("icon_old.ico")
            os.rename(icon_path, "icon_old.ico")
        except: 
            try: os.remove(icon_path)
            except: pass
        
    img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"✅ Đã tạo icon mới tại: {os.path.abspath(icon_path)}")

if __name__ == "__main__":
    create_pro_icon()
