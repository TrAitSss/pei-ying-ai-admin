from typing import Optional, Dict, Any
import os

class OCRService:
    """OCR 服务 - 用于文档数据录入 (M1)"""
    
    def __init__(self):
        self.engine = None
    
    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        """从文件中提取文本"""
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext in ['.pdf']:
                return await self._extract_from_pdf(file_path)
            elif ext in ['.png', '.jpg', '.jpeg', '.bmp']:
                return await self._extract_from_image(file_path)
            elif ext in ['.doc', '.docx']:
                return await self._extract_from_word(file_path)
            elif ext in ['.xls', '.xlsx']:
                return await self._extract_from_excel(file_path)
            else:
                return {"text": "", "error": f"不支持的文件格式: {ext}"}
        except Exception as e:
            return {"text": "", "error": str(e)}
    
    async def _extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """从 PDF 提取文本"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return {"text": text, "pages": len(reader.pages)}
        except Exception as e:
            return {"text": "", "error": f"PDF 解析失败: {str(e)}"}
    
    async def _extract_from_image(self, file_path: str) -> Dict[str, Any]:
        """从图片提取文本 (OCR)"""
        try:
            # 尝试使用 PaddleOCR
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            result = ocr.ocr(file_path, cls=True)
            
            texts = []
            for line in result[0]:
                if line:
                    texts.append(line[1][0])
            
            return {"text": "\n".join(texts), "engine": "PaddleOCR"}
        except Exception as e:
            # 降级到 pytesseract
            try:
                import pytesseract
                from PIL import Image
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                return {"text": text, "engine": "Tesseract"}
            except Exception as e2:
                return {"text": "", "error": f"OCR 失败: {str(e)}, {str(e2)}"}
    
    async def _extract_from_word(self, file_path: str) -> Dict[str, Any]:
        """从 Word 提取文本"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return {"text": text, "engine": "python-docx"}
        except Exception as e:
            return {"text": "", "error": f"Word 解析失败: {str(e)}"}
    
    async def _extract_from_excel(self, file_path: str) -> Dict[str, Any]:
        """从 Excel 提取文本"""
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            text = df.to_string()
            return {"text": text, "engine": "pandas", "rows": len(df)}
        except Exception as e:
            return {"text": "", "error": f"Excel 解析失败: {str(e)}"}

ocr_service = OCRService()
