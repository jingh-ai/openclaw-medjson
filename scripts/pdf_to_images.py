#!/usr/bin/env python3
"""
PDF to Images Converter for Medical Report Skill.

Converts each page of a PDF file into a separate PNG image.
Uses PyMuPDF (pymupdf) for rendering — no system dependencies required.

Usage:
    python3 pdf_to_images.py <pdf_path> <output_directory>

Output:
    Creates files like: <output_directory>/page_01.png, page_02.png, ...
    Prints the list of generated file paths to stdout (one per line).

Dependencies:
    pip3 install pymupdf
"""

import sys
import os

def check_dependencies():
    """Check if pymupdf is installed, provide installation hint if not."""
    try:
        import pymupdf  # noqa: F401
        return True
    except ImportError:
        print(
            "ERROR: pymupdf is not installed.\n"
            "Install it with: pip3 install pymupdf",
            file=sys.stderr,
        )
        return False


def convert_pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 200) -> list[str]:
    """
    Convert a PDF file to PNG images, one per page.

    Args:
        pdf_path: Path to the input PDF file.
        output_dir: Directory to save the output PNG files.
        dpi: Resolution for rendering (default: 200 DPI, good balance of
             quality vs file size for medical reports).

    Returns:
        List of paths to the generated PNG files.
    """
    import pymupdf

    if not os.path.isfile(pdf_path):
        print(f"ERROR: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    doc = pymupdf.open(pdf_path)
    generated_files = []

    zoom = dpi / 72  # 72 is the default PDF DPI
    matrix = pymupdf.Matrix(zoom, zoom)

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=matrix)

        filename = f"page_{page_num + 1:02d}.png"
        filepath = os.path.join(output_dir, filename)
        pix.save(filepath)
        generated_files.append(filepath)

    doc.close()

    return generated_files


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python3 pdf_to_images.py <pdf_path> <output_directory>",
            file=sys.stderr,
        )
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not check_dependencies():
        sys.exit(1)

    generated = convert_pdf_to_images(pdf_path, output_dir)

    # Print results to stdout for the agent to capture
    print(f"Converted {len(generated)} page(s):")
    for path in generated:
        print(path)


if __name__ == "__main__":
    main()
