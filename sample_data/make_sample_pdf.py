from __future__ import annotations

from pathlib import Path


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(lines: list[str], destination: Path) -> None:
    content_lines = ["BT", "/F1 12 Tf", "72 760 Td", "14 TL"]

    for index, line in enumerate(lines):
        prefix = "" if index == 0 else "T* "
        content_lines.append(f"{prefix}({escape_pdf_text(line)}) Tj")

    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1")

    objects: list[bytes] = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Count 1 /Kids [3 0 R] >> endobj\n")
    objects.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
    )
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    objects.append(
        f"5 0 obj << /Length {len(stream)} >> stream\n".encode("latin-1")
        + stream
        + b"\nendstream endobj\n"
    )

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

    pdf.extend(
        (
            f"trailer << /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("latin-1")
    )

    destination.write_bytes(pdf)


if __name__ == "__main__":
    output_path = Path(__file__).with_name("sample_company_handbook.pdf")
    lines = [
        "Acme Company Handbook",
        "Employees may work remotely up to three days per week with manager approval.",
        "Core collaboration hours are 10 AM to 3 PM Eastern Time.",
        "Travel expenses must be submitted within 30 days of the trip.",
        "The learning stipend is 1200 dollars per year for job-related courses and books.",
        "Security incidents must be reported to the engineering lead immediately.",
    ]
    make_pdf(lines, output_path)
    print(f"Created {output_path}")
