#!/bin/bash

# Audio Converter Menu - Interactive CLI for macOS

# Colors for terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display header
show_header() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║       Audio Converter Tool - macOS         ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to convert single file
convert_file() {
    echo -e "${YELLOW}Convert Single Audio File${NC}"
    echo "------------------------"

    read -p "Enter input file path (or drag file here): " input_file
    # Remove quotes if present (from drag and drop)
    input_file="${input_file%\'}"
    input_file="${input_file#\'}"

    if [ ! -f "$input_file" ]; then
        echo -e "${RED}Error: File not found!${NC}"
        read -p "Press Enter to continue..."
        return
    fi

    echo ""
    echo "Select output format:"
    echo "1) MP3"
    echo "2) WAV"
    echo "3) FLAC"
    echo "4) AAC"
    echo "5) OGG"
    read -p "Choice (1-5): " format_choice

    case $format_choice in
        1) format="mp3"; codec="libmp3lame" ;;
        2) format="wav"; codec="pcm_s16le" ;;
        3) format="flac"; codec="flac" ;;
        4) format="aac"; codec="aac" ;;
        5) format="ogg"; codec="libvorbis" ;;
        *) echo -e "${RED}Invalid choice!${NC}"; return ;;
    esac

    if [ "$format" = "mp3" ] || [ "$format" = "aac" ]; then
        echo ""
        echo "Select bitrate:"
        echo "1) 128k"
        echo "2) 192k (recommended)"
        echo "3) 256k"
        echo "4) 320k"
        read -p "Choice (1-4): " bitrate_choice

        case $bitrate_choice in
            1) bitrate="128k" ;;
            2) bitrate="192k" ;;
            3) bitrate="256k" ;;
            4) bitrate="320k" ;;
            *) bitrate="192k" ;;
        esac
    fi

    # Generate output filename
    dir=$(dirname "$input_file")
    base=$(basename "$input_file" | sed 's/\.[^.]*$//')
    output_file="$dir/${base}_converted.$format"

    echo ""
    echo -e "${BLUE}Converting...${NC}"

    if [ "$format" = "mp3" ] || [ "$format" = "aac" ]; then
        ffmpeg -i "$input_file" -acodec $codec -b:a $bitrate "$output_file" -y 2>/dev/null
    else
        ffmpeg -i "$input_file" -acodec $codec "$output_file" -y 2>/dev/null
    fi

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Conversion successful!${NC}"
        echo "Output: $output_file"

        # Show file sizes
        input_size=$(du -h "$input_file" | cut -f1)
        output_size=$(du -h "$output_file" | cut -f1)
        echo "Input size: $input_size → Output size: $output_size"
    else
        echo -e "${RED}✗ Conversion failed!${NC}"
    fi

    read -p "Press Enter to continue..."
}

# Function for batch conversion
batch_convert() {
    echo -e "${YELLOW}Batch Convert Audio Files${NC}"
    echo "-------------------------"

    read -p "Enter folder path (or drag folder here): " folder
    # Remove quotes if present
    folder="${folder%\'}"
    folder="${folder#\'}"

    if [ ! -d "$folder" ]; then
        echo -e "${RED}Error: Folder not found!${NC}"
        read -p "Press Enter to continue..."
        return
    fi

    echo ""
    echo "Select output format:"
    echo "1) MP3"
    echo "2) WAV"
    echo "3) FLAC"
    read -p "Choice (1-3): " format_choice

    case $format_choice in
        1) format="mp3"; codec="libmp3lame"; bitrate="192k" ;;
        2) format="wav"; codec="pcm_s16le" ;;
        3) format="flac"; codec="flac" ;;
        *) echo -e "${RED}Invalid choice!${NC}"; return ;;
    esac

    # Create output folder
    output_folder="$folder/converted_$format"
    mkdir -p "$output_folder"

    echo ""
    echo -e "${BLUE}Converting files...${NC}"

    count=0
    total=$(find "$folder" -maxdepth 1 -type f \( -iname "*.mp3" -o -iname "*.wav" -o -iname "*.flac" -o -iname "*.aac" -o -iname "*.m4a" \) | wc -l)

    find "$folder" -maxdepth 1 -type f \( -iname "*.mp3" -o -iname "*.wav" -o -iname "*.flac" -o -iname "*.aac" -o -iname "*.m4a" \) | while read -r file; do
        ((count++))
        base=$(basename "$file" | sed 's/\.[^.]*$//')
        output_file="$output_folder/${base}.$format"

        echo -n "[$count/$total] Converting $(basename "$file")... "

        if [ "$format" = "mp3" ]; then
            ffmpeg -i "$file" -acodec $codec -b:a $bitrate "$output_file" -y 2>/dev/null
        else
            ffmpeg -i "$file" -acodec $codec "$output_file" -y 2>/dev/null
        fi

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
        fi
    done

    echo ""
    echo -e "${GREEN}Batch conversion complete!${NC}"
    echo "Output folder: $output_folder"

    read -p "Press Enter to continue..."
}

# Function to normalize audio
normalize_audio() {
    echo -e "${YELLOW}Normalize Audio Volume${NC}"
    echo "----------------------"

    read -p "Enter file or folder path: " input_path
    # Remove quotes if present
    input_path="${input_path%\'}"
    input_path="${input_path#\'}"

    if [ -f "$input_path" ]; then
        # Single file
        echo -e "${BLUE}Normalizing file...${NC}"
        python3 audio_processor.py normalize "$input_path" -o "normalized"
    elif [ -d "$input_path" ]; then
        # Folder
        echo -e "${BLUE}Normalizing all files in folder...${NC}"
        python3 audio_processor.py normalize "$input_path" -o "$input_path/normalized"
    else
        echo -e "${RED}Error: Path not found!${NC}"
    fi

    read -p "Press Enter to continue..."
}

# Function to split audio
split_audio() {
    echo -e "${YELLOW}Split Large Audio Files${NC}"
    echo "-----------------------"

    read -p "Enter file or folder path: " input_path
    # Remove quotes if present
    input_path="${input_path%\'}"
    input_path="${input_path#\'}"

    if [ ! -e "$input_path" ]; then
        echo -e "${RED}Error: Path not found!${NC}"
        read -p "Press Enter to continue..."
        return
    fi

    echo -e "${BLUE}Processing...${NC}"
    python3 split_videos.py "$input_path"

    echo -e "${GREEN}Split complete!${NC}"
    read -p "Press Enter to continue..."
}

# Main menu
while true; do
    show_header
    echo "Main Menu:"
    echo "----------"
    echo "1) Convert single audio file"
    echo "2) Batch convert folder"
    echo "3) Normalize audio volume"
    echo "4) Split large audio files"
    echo "5) Launch GUI version"
    echo "6) Exit"
    echo ""
    read -p "Select option (1-6): " choice

    case $choice in
        1) show_header; convert_file ;;
        2) show_header; batch_convert ;;
        3) show_header; normalize_audio ;;
        4) show_header; split_audio ;;
        5) python3 audio_converter_gui.py & ;;
        6) echo -e "${GREEN}Goodbye!${NC}"; exit 0 ;;
        *) echo -e "${RED}Invalid option!${NC}"; sleep 1 ;;
    esac
done