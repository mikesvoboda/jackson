# OCR Text Extraction for Legal Documents

This directory contains tools for extracting text from scanned legal documents using Optical Character Recognition (OCR).

## 🔧 **Quick Start**

```bash
# Make script executable (if not already)
chmod +x ocr_text_extraction.sh

# Extract text from all images in current directory
./ocr_text_extraction.sh

# Extract with better quality (preprocessing)
./ocr_text_extraction.sh --preprocess --verbose
```

## 📁 **Files**

- `ocr_text_extraction.sh` - Main OCR extraction script
- `extracted_text_combined.txt` - Combined text from all screenshots
- `Screenshot *.png` - Original scanned document images

## 🛠️ **Script Features**

- **Batch Processing**: Processes all images at once
- **Multiple Formats**: Supports PNG, JPG, JPEG, TIFF, BMP
- **Preprocessing**: Optional image enhancement for better OCR
- **Organized Output**: Individual files + combined output
- **Error Handling**: Graceful failure handling
- **Verbose Mode**: Detailed processing information

## 📊 **Usage Examples**

```bash
# Basic usage - extract all images
./ocr_text_extraction.sh

# Custom output directory
./ocr_text_extraction.sh --output my_extracted_text

# Only process PNG files with verbose output
./ocr_text_extraction.sh --extensions "png" --verbose

# Apply image preprocessing for better accuracy
./ocr_text_extraction.sh --preprocess

# Get help and see all options
./ocr_text_extraction.sh --help
```

## 🎯 **Legal Case Context**

These screenshots contain **1984 Butts County plat documentation** showing:
- Professional surveying standards by **Georgia Registered Surveyor No. 1507**
- Detailed metes and bounds descriptions
- Precise coordinate recordings
- Official Plat Book references (Book 8, Pages 195-199)

This documentation demonstrates the **professional competency standards** that existed in 1984, creating a stark contrast with the surveying malpractice committed by Ironstone Surveying in 2021-2022.

## 🔗 **Dependencies**

- **Tesseract OCR**: `brew install tesseract`
- **ImageMagick** (optional, for preprocessing): `brew install imagemagick`

## 📝 **Output**

The script generates:
1. **Individual text files** in `extracted_text/` directory
2. **Combined file** with all text and clear separators
3. **File statistics** (word count, file sizes)

**Current Results**: 40KB of extracted text, 737 lines of detailed legal surveying descriptions. 