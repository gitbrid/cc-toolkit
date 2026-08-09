"""本地 OCR：不依赖视觉 API，使用便携 Tesseract 识别图片或扫描 PDF。

用法示例:
    uv tool run --python 3.12 --with pypdfium2 --with pillow python local_ocr.py "D:\\资料\\书页.png"
    uv tool run --python 3.12 --with pypdfium2 --with pillow python local_ocr.py "D:\\资料\\扫描书.pdf" --out "D:\\资料\\OCR结果"

默认语言 chi_sim+eng，可直接识别中文和英文；无需管理员安装，也无需视觉 API。
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TESSERACT_EXE = r"D:\program\CC 工具库\tools\tesseract-portable\tesseract.exe"
TESSDATA_DIR = r"D:\program\CC 工具库\tools\tesseract-portable\tessdata"


def run_tesseract(image: Path, lang: str, psm: str) -> str:
    env = os.environ.copy()
    env["TESSDATA_PREFIX"] = TESSDATA_DIR
    proc = subprocess.run(
        [TESSERACT_EXE, str(image), "stdout", "-l", lang, "--psm", psm],
        capture_output=True,
        env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Tesseract 运行失败: {proc.stderr.decode('utf-8', 'replace')[:500]}")
    return proc.stdout.decode("utf-8", "replace").strip()


def ocr_image(path: Path, lang: str, psm: str) -> str:
    return run_tesseract(path, lang, psm)


def ocr_pdf(path: Path, lang: str, psm: str, dpi: int, start: int, end: int) -> str:
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(str(path))
    total = len(pdf)
    page_numbers = [p for p in range(start, min(end, total) + 1) if 1 <= p <= total]
    parts: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for page_no in page_numbers:
            page = pdf[page_no - 1]
            bitmap = page.render(scale=dpi / 72.0)
            image_path = tmp_dir / f"page-{page_no:04d}.png"
            bitmap.to_pil().save(image_path)
            text = run_tesseract(image_path, lang, psm)
            parts.append(f"===== 第 {page_no}/{total} 页 =====\n{text}")
    return "\n\n".join(parts)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="本地 Tesseract OCR（图片/PDF）")
    parser.add_argument("paths", nargs="+", help="图片或 PDF 路径")
    parser.add_argument("--lang", default="chi_sim+eng", help="Tesseract 语言（默认 chi_sim+eng）")
    parser.add_argument("--psm", default="6", help="Tesseract 版面分析模式（默认 6）")
    parser.add_argument("--dpi", type=int, default=300, help="PDF 渲染 DPI（默认 300）")
    parser.add_argument("--start", type=int, default=1, help="PDF 起始页（1 起，默认 1）")
    parser.add_argument("--end", type=int, default=0, help="PDF 结束页（默认到最后）")
    parser.add_argument("--out", help="输出目录；默认只打印到 stdout")
    args = parser.parse_args()

    if not Path(TESSERACT_EXE).exists():
        print(f"未找到便携 Tesseract: {TESSERACT_EXE}", file=sys.stderr)
        return 1

    out_dir = Path(args.out) if args.out else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    failed = 0
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            print(f"文件不存在: {path}", file=sys.stderr)
            failed += 1
            continue
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                end_page = args.end if args.end else 1_000_000
                text = ocr_pdf(path, args.lang, args.psm, args.dpi, args.start, end_page)
            else:
                text = ocr_image(path, args.lang, args.psm)
        except Exception as exc:
            print(f"OCR 失败 {path}: {exc}", file=sys.stderr)
            failed += 1
            continue
        if out_dir:
            out_file = out_dir / f"{path.stem}.txt"
            out_file.write_text(text, encoding="utf-8")
            print(f"[OK] {path} -> {out_file}", file=sys.stderr)
        else:
            print(f"===== {path} =====")
            print(text)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
