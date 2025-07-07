from flask import Flask, request, render_template_string, jsonify
from PIL import Image, ImageDraw, ImageFont
import io, base64, os

app = Flask(__name__)

HTML_PAGE = """
<!doctype html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>ทดสอบภาษาไทยบนภาพ</title>
</head>
<body style="font-family:sans-serif; padding: 20px;">
    <h2>🖼️ ทดสอบการใส่ข้อความภาษาไทยลงบนภาพ</h2>
    <form method="post" enctype="multipart/form-data">
        <p><label>เลือกรูปภาพ: <input type="file" name="image" required></label></p>
        <p><label>ข้อความภาษาไทย: <input type="text" name="text" value="สวัสดีครับ!" required></label></p>
        <p><label>ขนาดตัวอักษร: <input type="number" name="font_size" value="48"></label></p>
        <p><label>ระยะห่างจากล่างภาพ: <input type="number" name="bottom_margin" value="150"></label></p>
        <p><button type="submit">แสดงผลลัพธ์</button></p>
    </form>

    {% if image_base64 %}
        <hr>
        <h3>📸 ภาพผลลัพธ์:</h3>
        <img src="{{ image_base64 }}" style="max-width:100%;">
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    image_base64 = None

    if request.method == 'POST':
        if 'image' not in request.files or 'text' not in request.form:
            return "Missing image or text", 400

        file = request.files['image']
        text = request.form['text']
        image_data = file.read()
        img = Image.open(io.BytesIO(image_data)).convert("RGBA")
        draw = ImageDraw.Draw(img)

        font_path = os.path.join(os.path.dirname(__file__), "Prompt-Regular.ttf")  # ใช้ฟอนต์ไทย
        font_size = int(request.form.get('font_size', 48))
        bottom_margin = int(request.form.get('bottom_margin', 150))

        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            return f"Font loading failed: {str(e)}", 500

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
        image_base64 = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

    return render_template_string(HTML_PAGE, image_base64=image_base64)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
