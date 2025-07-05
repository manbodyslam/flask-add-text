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
    img = Image.open(io.BytesIO(image_data)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # ใช้ Prompt-Regular.ttf เพื่อรองรับภาษาไทย+วรรณยุกต์ไม่ลอย
    font_path = os.path.join(os.path.dirname(__file__), "Prompt-Regular.ttf")
    font_size = int(request.form.get('font_size', 48))
    bottom_margin = int(request.form.get('bottom_margin', 150))

    try:
        # ถ้าติดตั้ง libraqm ใน environment แล้ว จะ render สระ/วรรณยุกต์ได้ดีที่สุด
        font = ImageFont.truetype(font_path, font_size, layout_engine=ImageFont.LAYOUT_RAQM)
    except Exception as e:
        # ถ้าไม่รองรับ layout_engine ก็ fallback เป็นปกติ
        font = ImageFont.truetype(font_path, font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (img.width - text_w) // 2
    y = img.height - text_h - bottom_margin
    padding = 10
    draw.rectangle([x - padding, y - padding, x + text_w + padding, y + text_h + padding], fill="black")
    draw.text((x, y), text, font=font, fill="white")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    result_img = base64.b64encode(buf.getvalue()).decode()
    return jsonify({'image_base64': f"data:image/png;base64,{result_img}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
