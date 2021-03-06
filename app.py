# web-app for API image manipulation

from flask import Flask, request, render_template, send_from_directory
import os
import sys
from PIL import Image, ImageEnhance, ImageTk, ImageFilter

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


# default access page
@app.route("/")
def main():
    return render_template('index.html')


# upload selected image and forward to processing page
@app.route("/upload", methods=["POST"])
def upload():
    target = os.path.join(APP_ROOT, 'static/images/')

    # create image directory if not found
    if not os.path.isdir(target):
        os.mkdir(target)

    # retrieve file from html file-picker
    upload = request.files.getlist("file")[0]
    print("File name: {}".format(upload.filename))
    filename = upload.filename

    # file support verification
    ext = os.path.splitext(filename)[1]
    if (ext == ".jpg") or (ext == ".png") or (ext == ".bmp"):
        print("File accepted")
    else:
        return render_template("error.html", message="The selected file is not supported"), 400

    # save file
    destination = "/".join([target, filename])
    print("File saved to to:", destination)
    upload.save(destination)

    # forward to processing page
    return render_template("processing.html", image_name=filename)


# rotate filename the specified degrees
@app.route("/rotate", methods=["POST"])
def rotate():
    # retrieve parameters from html form
    angle = request.form['angle']
    filename = request.form['image']

    # open and process image
    target = os.path.join(APP_ROOT, 'static/images')
    destination = "/".join([target, filename])

    img = Image.open(destination)
    img = img.rotate(-1*int(angle))

    # save and return image
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return send_image('temp.png')


# flip filename 'vertical' or 'horizontal'
@app.route("/flip", methods=["POST"])
def flip():

    # retrieve parameters from html form
    if 'horizontal' in request.form['mode']:
        mode = 'horizontal'
    elif 'vertical' in request.form['mode']:
        mode = 'vertical'
    else:
        return render_template("error.html", message="Mode not supported (vertical - horizontal)"), 400
    filename = request.form['image']

    # open and process image
    target = os.path.join(APP_ROOT, 'static/images')
    destination = "/".join([target, filename])

    img = Image.open(destination)

    if mode == 'horizontal':
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    else:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # save and return image
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return send_image('temp.png')


# crop filename from (x1,y1) to (x2,y2)
@app.route("/crop", methods=["POST"])
def crop():
    # retrieve parameters from html form
    x1 = int(request.form['x1'])
    y1 = int(request.form['y1'])
    x2 = int(request.form['x2'])
    y2 = int(request.form['y2'])
    filename = request.form['image']

    # open image
    target = os.path.join(APP_ROOT, 'static/images')
    destination = "/".join([target, filename])

    img = Image.open(destination)

    # check for valid crop parameters
    width = img.size[0]
    height = img.size[1]

    crop_possible = True
    if not 0 <= x1 < width:
        crop_possible = False
    if not 0 < x2 <= width:
        crop_possible = False
    if not 0 <= y1 < height:
        crop_possible = False
    if not 0 < y2 <= height:
        crop_possible = False
    if not x1 < x2:
        crop_possible = False
    if not y1 < y2:
        crop_possible = False

    # crop image and show
    if crop_possible:
        img = img.crop((x1, y1, x2, y2))

        # save and return image
        destination = "/".join([target, 'temp.png'])
        if os.path.isfile(destination):
            os.remove(destination)
        img.save(destination)
        return send_image('temp.png')
    else:
        return render_template("error.html", message="Crop dimensions not valid"), 400
    return '', 204


# blend filename with stock photo and alpha parameter
@app.route("/blend", methods=["POST"])
def blend():
    # retrieve parameters from html form
    alpha = request.form['alpha']
    filename1 = request.form['image']

    # open images
    target = os.path.join(APP_ROOT, 'static/images')
    filename2 = 'blend.jpg'
    destination1 = "/".join([target, filename1])
    destination2 = "/".join([target, filename2])

    img1 = Image.open(destination1)
    img2 = Image.open(destination2)

    # resize images to max dimensions
    width = max(img1.size[0], img2.size[0])
    height = max(img1.size[1], img2.size[1])

    img1 = img1.resize((width, height), Image.ANTIALIAS)
    img2 = img2.resize((width, height), Image.ANTIALIAS)

    # if image in gray scale, convert stock image to monochrome
    if len(img1.mode) < 3:
        img2 = img2.convert('L')

    # blend and show image
    img = Image.blend(img1, img2, float(alpha)/100)

    # save and return image
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return send_image('temp.png')

# White to Trasnparent


@app.route("/whitetotransparent", methods=["POST"])
def whitetotransparent():
    filename = request.form['image']
    # open and process image
    target = os.path.join(APP_ROOT, 'static/images')
    destination = "/".join([target, filename])

    img = Image.open(destination)
    img.convert('RGBA')
    datas = img.getdata()
    newData = []
    for item in datas:
	    if item[0] == 255 and item[1] == 255 and item[2] == 255:
	        newData.append((255, 255, 255, 0))
	    else:
	        newData.append(item)
    img.putdata(newData)
    # save and return image
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return send_image('temp.png')

@app.route("/simplegeometry", methods=["POST"])
def simplegeometry():
    filename = request.form['image']
    x1 = int(request.form['x1'])
    x2 = int(request.form['x2'])
    target = os.path.join(APP_ROOT,'static/images')
    destination = "/".join([target,filename])
    img = Image.open(destination)
    size = (x1, x2)
    img.thumbnail(size)
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return send_image('temp.png')
@app.route("/colorbalance", methods=["POST"])
def colorbalance():
    filename = request.form['image']
    target = os.path.join(APP_ROOT,'static/images')
    destination = "/".join([target,filename])
    img = Image.open(destination)
    enhancer = ImageEnhance.Color(img)
    for i in range(8):
        factor = i / 4.0
        enhancer.enhance(factor) 
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return send_image('temp.png')
@app.route("/enhancesharpness", methods=["POST"])
def enhancesharpness():
    filename = request.form['image']
    target = os.path.join(APP_ROOT,'static/images')
    destination = "/".join([target,filename])
    img = Image.open(destination)
    enhancer = ImageEnhance.Sharpness(img)
    for i in range(8):
        factor = i / 4.0
        enhancer.enhance(factor) 
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return send_image('temp.png')
@app.route("/enhancecontrast", methods=["POST"])
def enhancecontrast():
    filename = request.form['image']
    target = os.path.join(APP_ROOT,'static/images')
    destination = "/".join([target,filename])
    img = Image.open(destination)
    enhancer = ImageEnhance.Contrast(img)
    for i in range(30):
        factor = i / 4.0
        enhancer.enhance(factor) 
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return send_image('temp.png')
@app.route("/enhancebrightness", methods=["POST"])
def enhancebrightness():
    filename = request.form['image']
    target = os.path.join(APP_ROOT,'static/images')
    destination = "/".join([target,filename])
    img = Image.open(destination)
    enhancer = ImageEnhance.Brightness(img)
    for i in range(8):
        factor = i / 4.0
        enhancer.enhance(factor) 
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return send_image('temp.png')
@app.route("/blackandwhite", methods=["POST"])
def blackandwhite():
    filename = request.form['image']
    target = os.path.join(APP_ROOT,'static/images')
    destination = "/".join([target,filename])
    img = Image.open(destination)
    thresh = 200
    fn = lambda x : 255 if x > thresh else 0
    r = img.convert('L').point(fn, mode='1') 
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    r.save(destination)

    return send_image('temp.png')
@app.route("/negative", methods=["POST"])
def negative():
    filename = request.form['image']
    target = os.path.join(APP_ROOT,'static/images')
    destination = "/".join([target,filename])
    img = Image.open(destination)
    for i in range(0, img.size[0]-1):

        for j in range(0, img.size[1]-1):

        # Get pixel value at (x,y) position of the image

            pixelColorVals = img.getpixel((i,j));

       

        # Invert color

            redPixel    = 255 - pixelColorVals[0]; # Negate red pixel

            greenPixel  = 255 - pixelColorVals[1]; # Negate green pixel

            bluePixel   = 255 - pixelColorVals[2]; # Negate blue pixel

                   

        # Modify the image with the inverted pixel values

            img.putpixel((i,j),(redPixel, greenPixel, bluePixel))
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return send_image('temp.png')
@app.route("/grayscale", methods=["POST"])
def grayscale():
    filename = request.form['image']
    target = os.path.join(APP_ROOT,'static/images')
    destination = "/".join([target,filename])
    img = Image.open(destination)
    grayscale = img.convert("L")
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    grayscale.save(destination)

    return send_image('temp.png')
# retrieve file from 'static/images' directory
@app.route('/static/images/<filename>')
def send_image(filename):
    return send_from_directory("static/images", filename)


if __name__ == "__main__":
    app.run(host='192.168.200.41')
