import easyocr
# Initialize the EasyOCR Reader with desired languages
reader = easyocr.Reader(['en', 'fr']) # English and French
# Perform OCR on an image
result = reader.readtext("C:/Users/Varad Bhagat/Downloads/Extracting-handwritten-information-2.jpg")
# Print the detected text along with confidence levels
for detection in result:
   print(f"Text: {detection[1]}, Confidence: {detection[2]}")