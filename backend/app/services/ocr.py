import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path

def preprocess_image(image: np.ndarray) -> np.ndarray:
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)
    thresh = cv2.adaptiveThreshold(
        filtered, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

def ocr_image(image_np: np.ndarray) -> str:
    config = "--oem 3 --psm 3"
    return pytesseract.image_to_string(image_np, config=config)

def extract_text_from_file(file_path: str) -> dict:
    results = {"status": "success", "total_pages": 0, "pages": []}
    
    try:
        if file_path.lower().endswith('.pdf'):
            images = convert_from_path(file_path)
            results["total_pages"] = len(images)
            
            for i, img in enumerate(images):
                open_cv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                processed = preprocess_image(open_cv_image)
                text = ocr_image(processed)
                
                results["pages"].append({
                    "page_number": i + 1,
                    "content": text.strip()
                })
                
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError("Could not read image file")
                
            processed = preprocess_image(img)
            text = ocr_image(processed)
            
            results["total_pages"] = 1
            results["pages"].append({
                "page_number": 1,
                "content": text.strip()
            })
        else:
            raise ValueError("Unsupported OCR file type")
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "total_pages": 0,
            "pages": []
        }
        
    return results
