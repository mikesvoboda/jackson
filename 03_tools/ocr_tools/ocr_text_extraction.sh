#!/bin/bash

# OCR Text Extraction Script
# Extracts text from images using Tesseract OCR
# Created for legal document processing - Butts County case
# Usage: ./ocr_text_extraction.sh [options]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default settings
OUTPUT_DIR="extracted_text"
COMBINED_FILE="extracted_text_combined.txt"
PREPROCESS=false
VERBOSE=false
IMAGE_EXTENSIONS="png jpg jpeg tiff tif bmp"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
OCR Text Extraction Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    -o, --output DIR    Output directory (default: extracted_text)
    -c, --combined FILE Combined output file (default: extracted_text_combined.txt)
    -p, --preprocess    Apply image preprocessing for better OCR
    -v, --verbose       Verbose output
    -e, --extensions    Image file extensions to process (default: "png jpg jpeg tiff tif bmp")

EXAMPLES:
    # Basic extraction of all images
    $0

    # Extract with preprocessing for better accuracy
    $0 --preprocess

    # Extract specific file types to custom output
    $0 --output my_text --extensions "png jpg" --verbose

    # Single file extraction
    tesseract image.png output.txt

DEPENDENCIES:
    - tesseract (brew install tesseract)
    - imagemagick (brew install imagemagick) [for preprocessing]

EOF
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v tesseract &> /dev/null; then
        print_error "Tesseract is not installed. Install with: brew install tesseract"
        exit 1
    fi
    
    if [[ "$PREPROCESS" == true ]] && ! command -v convert &> /dev/null; then
        print_error "ImageMagick is required for preprocessing. Install with: brew install imagemagick"
        exit 1
    fi
    
    print_success "All dependencies are available"
}

# Function to preprocess image
preprocess_image() {
    local input_file="$1"
    local output_file="$2"
    
    if [[ "$VERBOSE" == true ]]; then
        print_status "Preprocessing $input_file"
    fi
    
    # Apply image enhancements for better OCR
    convert "$input_file" \
        -resize 200% \
        -contrast \
        -normalize \
        -sharpen 0x1 \
        -density 300 \
        "$output_file" 2>/dev/null
}

# Function to extract text from single image
extract_text_from_image() {
    local image_file="$1"
    local output_file="$2"
    local temp_image="$image_file"
    
    # Apply preprocessing if enabled
    if [[ "$PREPROCESS" == true ]]; then
        temp_image="${image_file%.*}_processed.${image_file##*.}"
        preprocess_image "$image_file" "$temp_image"
    fi
    
    # Extract text using tesseract
    if tesseract "$temp_image" stdout 2>/dev/null > "$output_file"; then
        if [[ "$VERBOSE" == true ]]; then
            local word_count=$(wc -w < "$output_file")
            print_success "Extracted $word_count words from $(basename "$image_file")"
        fi
    else
        print_error "Failed to extract text from $image_file"
        return 1
    fi
    
    # Clean up temporary preprocessed image
    if [[ "$PREPROCESS" == true ]] && [[ -f "$temp_image" ]]; then
        rm "$temp_image"
    fi
}

# Function to process all images
process_all_images() {
    local image_count=0
    local success_count=0
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Initialize combined file
    echo "# OCR Text Extraction Results" > "$COMBINED_FILE"
    echo "# Generated on: $(date)" >> "$COMBINED_FILE"
    echo "# Script: $0" >> "$COMBINED_FILE"
    echo "" >> "$COMBINED_FILE"
    
    print_status "Starting OCR extraction..."
    
    # Process each image type
    for ext in $IMAGE_EXTENSIONS; do
        for image_file in *."$ext" *."${ext^^}"; do
            # Skip if file doesn't exist (glob didn't match)
            [[ -f "$image_file" ]] || continue
            
            image_count=$((image_count + 1))
            
            # Generate output filename
            local base_name="${image_file%.*}"
            local text_file="$OUTPUT_DIR/${base_name}.txt"
            
            print_status "Processing: $image_file"
            
            # Extract text
            if extract_text_from_image "$image_file" "$text_file"; then
                success_count=$((success_count + 1))
                
                # Add to combined file
                echo "=== Processing $image_file ===" >> "$COMBINED_FILE"
                cat "$text_file" >> "$COMBINED_FILE"
                echo "" >> "$COMBINED_FILE"
                echo "" >> "$COMBINED_FILE"
            fi
        done
    done
    
    if [[ $image_count -eq 0 ]]; then
        print_warning "No image files found with extensions: $IMAGE_EXTENSIONS"
        return 1
    fi
    
    print_success "Processed $success_count/$image_count images successfully"
    print_success "Individual files saved to: $OUTPUT_DIR/"
    print_success "Combined output saved to: $COMBINED_FILE"
    
    # Show file sizes
    if [[ -f "$COMBINED_FILE" ]]; then
        local file_size=$(wc -c < "$COMBINED_FILE" | awk '{print int($1/1024)}')
        local word_count=$(wc -w < "$COMBINED_FILE")
        print_status "Combined file: ${file_size}KB, ${word_count} words"
    fi
}

# Function to show quick commands
show_quick_commands() {
    cat << EOF

QUICK REFERENCE COMMANDS:

Single file extraction:
    tesseract image.png output.txt

Batch processing:
    for file in *.png; do tesseract "\$file" "\${file%.*}.txt"; done

With preprocessing:
    convert image.png -resize 200% -contrast -normalize processed.png
    tesseract processed.png output.txt

Combine all text files:
    cat *.txt > combined_output.txt

Check tesseract languages:
    tesseract --list-langs

Install additional languages:
    brew install tesseract-lang

Alternative OCR tools:
    brew install ocrmypdf  # For PDFs
    brew install gocr      # Alternative OCR engine

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            show_quick_commands
            exit 0
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -c|--combined)
            COMBINED_FILE="$2"
            shift 2
            ;;
        -p|--preprocess)
            PREPROCESS=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -e|--extensions)
            IMAGE_EXTENSIONS="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_status "OCR Text Extraction Script"
    print_status "Working directory: $(pwd)"
    
    check_dependencies
    process_all_images
    
    print_success "OCR extraction completed!"
    
    if [[ "$VERBOSE" == true ]]; then
        show_quick_commands
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 