# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import io, base64, os

app = Flask(__name__)

@app.route('/add_text', methods=['POST'])
def add_text():
    if 'image' not in request.files or 'text' not in request.form:
        return jsonify({'error': 'Missing image or text'}), 400

    file = request.files['image']
    text = request.form['text']
    image_data = file.read()

    try:
        img = Image.open(io.BytesIO(image_data)).convert("RGBA")
    except Exception as e:
        return jsonify({'error': f'Cannot open image: {str(e)}'}), 400

    draw = ImageDraw.Draw(img)

    # เปลี่ยนตรงนี้เป็นฟอนต์ที่คุณใช้
    font_path = os.path.join(os.path.dirname(__file__), "NotoSansThai.ttf")
    font_size = int(request.form.get('font_size', 48))
    bottom_margin = int(request.form.get('bottom_margin', 150))
    padding = 20

    try:
        font = ImageFont.truetype(font_path, font_size)  # ไม่ต้องใช้ LAYOUT_RAQM
    except Exception as e:
        return jsonify({'error': f'Font loading failed: {str(e)}'}), 500

    # คำนวณขนาดข้อความ
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (img.width - text_w) // 2
    y = img.height - text_h - bottom_margin

    # วาดกล่องดำหลังข้อความ
    draw.rectangle(
        [x + bbox[0] - padding, y + bbox[1] - padding,
         x + bbox[2] + padding, y + bbox[3] + padding],
        fill="black"
    )

    # วางข้อความสีขาว
    draw.text((x, y), text, font=font, fill="white")

    # แปลงกลับเป็น base64
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    result_img = base64.b64encode(buf.getvalue()).decode()

    return jsonify({'image_base64': f"data:image/png;base64,{result_img}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
