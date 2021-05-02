#programa para escanear facturas del mercadona
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

import cv2

# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# noise removal
def remove_noise(image):
    return cv2.medianBlur(image,5)
 
#thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def get_parsed_text(image_path):
    image = cv2.imread(image_path)

    gray = get_grayscale(image)
    thresh = thresholding(gray)

    text = pytesseract.image_to_string(thresh, config= r'--oem 1 --psm 6')
    return text.split('\n')