from bokeh.models import Div, Button, FileInput, CheckboxButtonGroup
from bokeh.plotting import curdoc, figure
from bokeh.layouts import row, column
from bokeh.models import TextInput
from PIL import Image
import numpy as np
import io
import base64
import cv2

global img1
global img2
global yimg

def display_image(image_data):
    try:
        img = Image.open(io.BytesIO(image_data))
        img = img.convert("RGBA")
        imarray = np.array(img)
        imarray_flipped = imarray[::-1, :, :]
        p = figure(x_range=(0, imarray.shape[1]), y_range=(0, imarray.shape[0]), width=int(imarray.shape[1]),
                   height=int(imarray.shape[0]), active_scroll ="wheel_zoom")
        p.axis.visible = False
        p.grid.visible = False
        p.image_rgba(image=[imarray_flipped.view("uint32").reshape(imarray.shape[:2])], x=0, y=0, dw=imarray.shape[1],
                     dh=imarray.shape[0])
        return p
    except Exception as e:
        error_message = f"Error loading image: {str(e)}"
        error_div = Div(text=error_message)
        return error_div

def upload_handler1(attr, old, new):
    global img1
    try:
        uploaded_file_contents = base64.b64decode(new)
        img1 = uploaded_file_contents
    except Exception as e:
        error_message = f"Error processing uploaded image: {str(e)}"
        error_div = Div(text=error_message)
        layout.children[1] = error_div

def upload_handler2(attr, old, new):
    global img2
    try:
        uploaded_file_contents = base64.b64decode(new)
        img2 = uploaded_file_contents
    except Exception as e:
        error_message = f"Error processing uploaded image: {str(e)}"
        error_div = Div(text=error_message)
        layout.children[1] = error_div

def view1():
    p = display_image(img1)
    layout.children[1] = p

def view2():
    p = display_image(img2)
    layout.children[1] = p

def resize_image(image, target_shape):
    img = Image.fromarray(image)
    target_shape = (target_shape[1], target_shape[0])
    img = img.resize(target_shape, Image.BILINEAR)
    return np.array(img)

def rgba_to_rgb(image, background=(255, 255, 255)):
    rgba = image[:, :, :3]
    alpha = image[:, :, 3]
    bg_color = np.array(background, dtype=np.uint8)
    rgb = (1 - alpha[..., None] / 255) * bg_color + (alpha[..., None] / 255) * rgba
    return np.uint8(rgb)

def edit_button_callback(buttons, i1, i2, i3):
    active_index = buttons.active
    inv1 = False
    inv2 = False
    inv3 = False
    if 0 in active_index:
        inv1 = True
    if 1 in active_index:
        inv2 = True
    if 2 in active_index:
        inv3 = True

    Yimgl = Image.open(io.BytesIO(Yimg))
    Yimgl = Yimgl.convert("RGB")
    Yimarray = np.array(Yimgl)

    imgl1 = Image.open(io.BytesIO(img1))
    imgl1 = imgl1.convert("RGB")
    imarray1 = np.array(imgl1)

    imgl2 = Image.open(io.BytesIO(img2))
    imgl2 = imgl2.convert("RGB")
    imarray2 = np.array(imgl2)

    min_shape = max(Yimarray.shape, imarray1.shape, imarray2.shape)
    Yimarray = resize_image(Yimarray, min_shape[:2])
    imarray1 = resize_image(imarray1, min_shape[:2])
    imarray2 = resize_image(imarray2, min_shape[:2])

    if Yimarray.shape[2] == 4:
        Yimarray = rgba_to_rgb(Yimarray)
    imgYCrCB1 = cv2.cvtColor(Yimarray, cv2.COLOR_RGB2YCrCb)

    if imarray1.shape[2] == 4:
        imarray1 = rgba_to_rgb(imarray1)
    imgYCrCB2 = cv2.cvtColor(imarray1, cv2.COLOR_RGB2YCrCb)

    if imarray2.shape[2] == 4:
        imarray2 = rgba_to_rgb(imarray2)
    imgYCrCB3 = cv2.cvtColor(imarray2, cv2.COLOR_RGB2YCrCb)

    Y1, Cr1, Cb1 = cv2.split(imgYCrCB1)
    Y2, Cr2, Cb2 = cv2.split(imgYCrCB2)
    Y3, Cr3, Cb3 = cv2.split(imgYCrCB3)

    mult1 = 1
    mult2 = 1
    mult3 = 1

    if i1.value != "":
        mult1 = int(float(i1.value))
    if i2.value != "":
        mult2 = int(float(i2.value))
    if i3.value != "":
        mult3 = int(float(i3.value))

    if inv1:
        Y1 = cv2.bitwise_not(Y1)
    if inv2:
        Cr2 = cv2.bitwise_not(Cr2)
    if inv3:
        Cb3 = cv2.bitwise_not(Cb3)

    fin = cv2.merge([Y1 * mult1, Cr2 * mult2, Cb3 * mult3])
    RGB = cv2.cvtColor(fin, cv2.COLOR_YCrCb2BGR)
    RGBA = cv2.cvtColor(RGB, cv2.COLOR_BGR2RGBA)

    imarray_flipped = RGBA[::-1, :, :]
    p = figure(x_range=(0, RGBA.shape[1]), y_range=(0, RGBA.shape[0]), width=int(RGBA.shape[1]),
               height=int(RGBA.shape[0]), active_scroll ="wheel_zoom")
    p.axis.visible = False
    p.grid.visible = False
    p.image_rgba(image=[imarray_flipped.view("uint32").reshape(RGBA.shape[:2])], x=0, y=0, dw=RGBA.shape[1],
                 dh=RGBA.shape[0])
    layout.children[1] = p

initY = "photos/moda.png"
init2 = "photos/mountains.png"
init1 = "photos/house.jpg"

Yimg = open(initY, "rb").read()
p = display_image(Yimg)

img1 = open(init1, "rb").read()

img2 = open(init2, "rb").read()

input1 = TextInput(value="", title="MULT1", placeholder="")
input2 = TextInput(value="", title="MULT2", placeholder="")
input3 = TextInput(value="", title="MULT3", placeholder="")

def validate_input(attr, old, new):
    try:
        float(new)
    except ValueError:
        input1.value = ""

input1.on_change("value", lambda attr, old, new: validate_input(attr, old, new))
input2.on_change("value", lambda attr, old, new: validate_input(attr, old, new))
input3.on_change("value", lambda attr, old, new: validate_input(attr, old, new))

LABELS = ["INVERT Y", "INVERT CB", "INVERT CR"]
checkbox_button_group = CheckboxButtonGroup(labels=LABELS, active=[])

edit_button = Button(label="DISPLAY")
edit_button.on_click(lambda: edit_button_callback(checkbox_button_group, input1, input2, input3))

viewer1 = Button(label="VIEW IMAGE 1")
viewer1.on_click(view1)

viewer2 = Button(label="VIEW IMAGE 2")
viewer2.on_click(view2)

file_input1 = FileInput(accept=".jpg,.jpeg,.png,.webp", title="UPLOAD IMAGE 1")
file_input1.on_change('value', upload_handler1)

file_input2 = FileInput(accept=".jpg,.jpeg,.png,.webp", title="UPLOAD IMAGE 2")
file_input2.on_change('value', upload_handler2)

upload1 = column(file_input1, viewer1)
upload2 = column(file_input2, viewer2)
title = Div(text='<h1 style="text-align: center">CHANNEL BLASTER</h1>')

entries = column(title, upload1, upload2, input1, input2, input3, checkbox_button_group, edit_button)
layout = row(entries, p)

curdoc().add_root(layout)
