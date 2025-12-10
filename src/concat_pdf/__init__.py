import argparse
import io
import math
import sys
from pathlib import Path
from typing import Tuple, Optional

import fitz
import numpy as np
from PIL import Image

# Set console encoding to UTF-8
if sys.platform == 'win32':
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'English_United States.1252')
        except:
            pass


def calculate_grid_size(total_pages: int, n: int, m: Optional[int] = None) -> Tuple[int, int]:
    """Calculate grid size"""
    if m is None:
        m = math.ceil(total_pages / n)
    return n, m


def process_pdf(
    input_path: Path,
    output_path: Path,
    n: int,
    m: Optional[int] = None,
    page_size: Optional[Tuple[float, float]] = None,  # None means auto-calculate
    orientation: str = "landscape",  # Default landscape for better multi-page display
    dpi: int = 150,
    gap: float = 3,  # Spacing between thumbnails (points), smaller to save space
    padding: float = 10,  # Page margins
) -> None:
    """
    Process PDF file to generate N×M grid merged thumbnail PDF

    Args:
        input_path: Input PDF file path
        output_path: Output PDF file path
        n: Number of grid columns
        m: Number of grid rows (optional, auto-calculated if not provided)
        page_size: Output PDF page size (width, height) in points, None means auto-calculate
        orientation: Page orientation "portrait" or "landscape"
        dpi: Thumbnail DPI
        gap: Spacing between thumbnails (points)
        padding: Page margins (points)
    """
    # Open input PDF
    doc = fitz.open(input_path)
    total_pages = len(doc)

    # Calculate grid size
    n, m = calculate_grid_size(total_pages, n, m)

    # Calculate total pages (how many output pages are needed)
    thumbnails_per_page = n * m
    output_pages = math.ceil(total_pages / thumbnails_per_page)

    # If no page size specified, automatically calculate the optimal page size based on content and layout
    if page_size is None:
        # Get the aspect ratio of the first page as reference
        first_page = doc[0]
        src_rect = first_page.rect
        aspect_ratio = src_rect.width / src_rect.height

        # Set appropriate thumbnail height (based on DPI)
        # Use larger size for better viewing, but avoid excessive size
        base_thumb_height = 300  # Base thumbnail height
        base_thumb_width = base_thumb_height * aspect_ratio

        # Calculate page size - use compact layout to reduce whitespace
        # Reduce spacing and margins to better utilize space
        effective_gap = gap * 0.5  # Use smaller spacing
        effective_padding = padding * 0.8  # Use smaller margins

        page_width = n * base_thumb_width + (n - 1) * effective_gap + 2 * effective_padding
        page_height = m * base_thumb_height + (m - 1) * effective_gap + 2 * effective_padding

        page_size = (page_width, page_height)
        print(f"Auto-calculated page size: {page_width:.2f} x {page_height:.2f} points")
        print(f"In inches: {page_width/72:.2f} x {page_height/72:.2f} inches")
    else:
        print(f"Using specified page size: {page_size}")
        # Adjust page orientation
        if orientation == "landscape":
            page_size = (page_size[1], page_size[0])

    # Calculate available space for each thumbnail
    # If auto-calculating page size, use actual effective spacing
    if page_size is None:
        effective_gap = gap * 0.5
        effective_padding = padding * 0.8
    else:
        effective_gap = gap
        effective_padding = padding

    available_width = page_size[0] - 2 * effective_padding - (n - 1) * effective_gap
    available_height = page_size[1] - 2 * effective_padding - (m - 1) * effective_gap
    thumbnail_width = available_width / n
    thumbnail_height = available_height / m

    # Create output PDF
    output_doc = fitz.open()

    for page_idx in range(output_pages):
        # Create new page
        page = output_doc.new_page(width=page_size[0], height=page_size[1])

        # Calculate thumbnail range for current page
        start_idx = page_idx * thumbnails_per_page
        end_idx = min(start_idx + thumbnails_per_page, total_pages)

        for idx in range(start_idx, end_idx):
            # Calculate position in grid
            grid_idx = idx - start_idx
            row = grid_idx // n
            col = grid_idx % n

            # Calculate thumbnail position on page
            x = effective_padding + col * (thumbnail_width + effective_gap)
            y = effective_padding + row * (thumbnail_height + effective_gap)

            # Get original page
            src_page = doc[idx]

            # Get original page aspect ratio
            src_rect = src_page.rect
            aspect_ratio = src_rect.width / src_rect.height

            # Calculate thumbnail rectangle, maintaining aspect ratio
            if aspect_ratio > thumbnail_width / thumbnail_height:
                # Width limited
                thumb_width_final = thumbnail_width
                thumb_height_final = thumbnail_width / aspect_ratio
                # Center align
                y_offset = (thumbnail_height - thumb_height_final) / 2
                img_rect = fitz.Rect(x, y + y_offset, x + thumb_width_final, y + y_offset + thumb_height_final)
            else:
                # Height limited
                thumb_height_final = thumbnail_height
                thumb_width_final = thumbnail_height * aspect_ratio
                # Center align
                x_offset = (thumbnail_width - thumb_width_final) / 2
                img_rect = fitz.Rect(x + x_offset, y, x + x_offset + thumb_width_final, y + thumb_height_final)

            # Draw page directly to new position (more efficient and maintains quality)
            page.show_pdf_page(img_rect, doc, idx)

            # Draw black border
            page.draw_rect(img_rect, color=fitz.utils.getColor("black"), width=0.5)

    # Save output PDF
    output_doc.save(output_path, garbage=4, deflate=True)
    output_doc.close()
    doc.close()


def main():
    parser = argparse.ArgumentParser(description="PDF Thumbnail Grid Tool - Auto-calculate page size")
    parser.add_argument("input", type=Path, help="Input PDF file path")
    parser.add_argument("output", type=Path, help="Output PDF file path")
    parser.add_argument("-n", "--columns", type=int, required=True, help="Number of grid columns")
    parser.add_argument("-m", "--rows", type=int, help="Number of grid rows (optional, auto-calculated)")
    parser.add_argument("--page-size", type=str, default="auto",
                       choices=["auto", "A4", "A3", "A5", "Letter"],
                       help="Output page size, 'auto' means auto-calculate based on content")
    parser.add_argument("--orientation", type=str, default="landscape",
                       choices=["portrait", "landscape"],
                       help="Page orientation (default: landscape)")
    parser.add_argument("--dpi", type=int, default=150, help="Thumbnail DPI")
    parser.add_argument("--gap", type=float, default=3, help="Spacing between thumbnails (points)")
    parser.add_argument("--padding", type=float, default=10, help="Page margins (points)")

    args = parser.parse_args()

    # Page size mapping
    page_sizes = {
        "auto": None,
        "A4": (595.276, 841.890),
        "A3": (841.890, 1190.551),
        "A5": (419.528, 595.276),
        "Letter": (612, 792)
    }

    process_pdf(
        input_path=args.input,
        output_path=args.output,
        n=args.columns,
        m=args.rows,
        page_size=page_sizes[args.page_size],
        orientation=args.orientation,
        dpi=args.dpi,
        gap=args.gap,
        padding=args.padding
    )

    print(f"Successfully generated thumbnail PDF: {args.output}")


if __name__ == "__main__":
    import io
    main()