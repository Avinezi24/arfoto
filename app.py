from flask import Flask, render_template, request, redirect, url_for, flash
import os
import cv2
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Ganti dengan kunci rahasia yang lebih aman
UPLOAD_FOLDER = 'static/uploads'
QR_FOLDER = 'qr_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

def generate_qr_code(message):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(message)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    return img_qr

def add_watermark_to_image(image_path, message, output_path):
    image = cv2.imread(image_path)
    qr_image = generate_qr_code(message)
    qr_path = os.path.join(QR_FOLDER, "qr_code.png")
    qr_image.save(qr_path)
    qr_code = cv2.imread(qr_path)
    height, width, _ = image.shape
    qr_code_resized = cv2.resize(qr_code, (100, 100))
    y_offset = height - 100
    x_offset = width - 100
    image[y_offset:y_offset + 100, x_offset:x_offset + 100] = qr_code_resized
    cv2.imwrite(output_path, image)

def decode_qr_from_image(image_path):
    image = cv2.imread(image_path)
    decoded_objects = decode(image)
    for obj in decoded_objects:
        return obj.data.decode('utf-8')
    return "Tidak ada QR code yang terdeteksi."

@app.route('/')
def index():
    images = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', images=images)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'image' not in request.files or request.form['message'] == '':
            flash('Harap unggah gambar dan masukkan pesan.')
            return redirect(request.url)

        image_file = request.files['image']
        message = request.form['message']
        if image_file.filename == '':
            flash('Tidak ada gambar yang dipilih.')
            return redirect(request.url)

        image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(image_path)
        output_path = os.path.join(UPLOAD_FOLDER, f"watermarked_{image_file.filename}")
        add_watermark_to_image(image_path, message, output_path)

        flash('Gambar berhasil diunggah dengan QR code.')
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if request.method == 'POST':
        image_file = request.files.get('image')

        # Pastikan file terunggah
        if not image_file or image_file.filename == '':
            flash('Harap unggah gambar atau ambil gambar dengan kamera.')
            return redirect(request.url)

        # Simpan file ke folder unggahan
        image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(image_path)

        # Decode QR dari gambar yang diunggah
        message = decode_qr_from_image(image_path)

        # Tampilkan hasil deteksi QR
        return render_template('detect.html', message=message, image_file=image_file.filename)

    return render_template('detect.html', message=None)


if __name__ == "__main__":
    app.run(debug=True)
