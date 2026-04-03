"""
Generate sample images for cv-09 Emotion Detection System.
Run: pip install Pillow && python generate_samples.py
Output: 6 images — happy, sad, angry, surprised, neutral, fearful faces.
"""
from PIL import Image, ImageDraw
import os

OUT = os.path.dirname(__file__)


def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  created: {name}")


def base_face(bg=(230, 230, 230), skin=(220, 180, 140)):
    img = Image.new("RGB", (300, 300), bg)
    d = ImageDraw.Draw(img)
    # hair
    d.ellipse([50, 40, 250, 180], fill=(80, 50, 20))
    # head
    d.ellipse([55, 60, 245, 250], fill=skin)
    # eyes (whites)
    d.ellipse([85, 110, 125, 145], fill=(255, 255, 255))
    d.ellipse([175, 110, 215, 145], fill=(255, 255, 255))
    return img, d


def happy():
    img, d = base_face((255, 250, 220))
    # pupils
    d.ellipse([97, 118, 113, 137], fill=(40, 30, 20))
    d.ellipse([187, 118, 203, 137], fill=(40, 30, 20))
    # smile
    d.arc([100, 160, 200, 220], start=0, end=180, fill=(180, 60, 60), width=5)
    # cheeks
    d.ellipse([65, 165, 105, 195], fill=(255, 180, 180, 120))
    d.ellipse([195, 165, 235, 195], fill=(255, 180, 180, 120))
    d.text((110, 265), "Happy", fill=(80, 60, 20))
    return img


def sad():
    img, d = base_face((210, 220, 240))
    # droopy eyes
    d.ellipse([97, 118, 113, 137], fill=(40, 30, 20))
    d.ellipse([187, 118, 203, 137], fill=(40, 30, 20))
    # downward eyebrows
    d.line([85, 100, 125, 112], fill=(60, 40, 20), width=4)
    d.line([175, 112, 215, 100], fill=(60, 40, 20), width=4)
    # frown
    d.arc([100, 185, 200, 235], start=180, end=360, fill=(120, 60, 60), width=4)
    # tear
    d.ellipse([95, 148, 103, 165], fill=(150, 180, 220))
    d.text((115, 265), "Sad", fill=(40, 60, 100))
    return img


def angry():
    img, d = base_face((255, 220, 210))
    # angry pupils
    d.ellipse([97, 120, 113, 140], fill=(40, 20, 20))
    d.ellipse([187, 120, 203, 140], fill=(40, 20, 20))
    # angled eyebrows (angry)
    d.line([85, 112, 125, 100], fill=(60, 30, 20), width=5)
    d.line([175, 100, 215, 112], fill=(60, 30, 20), width=5)
    # tight mouth
    d.line([110, 200, 190, 200], fill=(160, 50, 50), width=4)
    # red flush
    d.ellipse([60, 150, 110, 190], fill=(255, 150, 130, 80))
    d.ellipse([190, 150, 240, 190], fill=(255, 150, 130, 80))
    d.text((110, 265), "Angry", fill=(160, 40, 40))
    return img


def surprised():
    img, d = base_face((240, 240, 255))
    # wide eyes
    d.ellipse([82, 108, 128, 150], fill=(255, 255, 255))
    d.ellipse([172, 108, 218, 150], fill=(255, 255, 255))
    d.ellipse([97, 118, 113, 140], fill=(40, 30, 20))
    d.ellipse([187, 118, 203, 140], fill=(40, 30, 20))
    # raised eyebrows
    d.arc([82, 88, 128, 112], start=180, end=360, fill=(60, 40, 20), width=4)
    d.arc([172, 88, 218, 112], start=180, end=360, fill=(60, 40, 20), width=4)
    # open mouth (O shape)
    d.ellipse([120, 175, 180, 225], fill=(100, 40, 40))
    d.ellipse([128, 183, 172, 217], fill=(200, 100, 100))
    d.text((100, 265), "Surprised", fill=(60, 60, 120))
    return img


def neutral():
    img, d = base_face((235, 235, 235))
    d.ellipse([97, 118, 113, 137], fill=(40, 30, 20))
    d.ellipse([187, 118, 203, 137], fill=(40, 30, 20))
    d.line([85, 105, 125, 105], fill=(60, 40, 20), width=3)
    d.line([175, 105, 215, 105], fill=(60, 40, 20), width=3)
    d.line([110, 200, 190, 200], fill=(140, 80, 80), width=3)
    d.text((105, 265), "Neutral", fill=(60, 60, 60))
    return img


def fearful():
    img, d = base_face((230, 240, 230))
    # wide fearful eyes
    d.ellipse([82, 108, 128, 150], fill=(255, 255, 255))
    d.ellipse([172, 108, 218, 150], fill=(255, 255, 255))
    d.ellipse([100, 120, 110, 138], fill=(40, 30, 20))
    d.ellipse([190, 120, 200, 138], fill=(40, 30, 20))
    # raised inner brows
    d.line([85, 108, 105, 98], fill=(60, 40, 20), width=4)
    d.line([195, 98, 215, 108], fill=(60, 40, 20), width=4)
    # trembling mouth
    d.arc([105, 185, 195, 225], start=180, end=360, fill=(140, 60, 60), width=3)
    d.text((105, 265), "Fearful", fill=(40, 100, 40))
    return img


if __name__ == "__main__":
    print("Generating cv-09 samples...")
    save(happy(), "sample_happy.jpg")
    save(sad(), "sample_sad.jpg")
    save(angry(), "sample_angry.jpg")
    save(surprised(), "sample_surprised.jpg")
    save(neutral(), "sample_neutral.jpg")
    save(fearful(), "sample_fearful.jpg")
    print("Done — 6 images in samples/")
