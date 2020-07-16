import pyimgur

def upload_graph(path):
    im = pyimgur.Imgur(client_id)
    uploaded_image = im.upload_image(path, title="Uploaded with PyImgur")
    return uploaded_image.link