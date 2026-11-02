import threading
from pathlib import Path
import pymupdf
import pytest

from pdf_engine import (
    Cancelled, build_candidate, compress_pdf, file_info, make_output,
    merge_pdfs, parse_pages, rotate_pdf, split_pdf
)


@pytest.fixture
def simple_pdf(tmp_path):
    path = tmp_path / 'text.pdf'
    with pymupdf.open() as d:
        for i in range(3):
            p=d.new_page(width=595,height=842)
            p.insert_text((80,120), f'Test page {i+1} vector text', fontsize=16)
        d.save(path)
    return path


def test_pages():
    assert parse_pages('1-3,5', 5)==[0,1,2,4]
    assert parse_pages('все', 4)==[0,1,2,3]
    assert parse_pages('1,1,2', 3)==[0,1]
    with pytest.raises(ValueError):
        parse_pages('1-6', 5)
    with pytest.raises(ValueError):
        parse_pages('2-1', 5)


def test_lossless_text(tmp_path,simple_pdf):
    result=compress_pdf(simple_pdf,tmp_path / 'out', mode='target',target_mb=1)
    assert result.target_met is True
    with pymupdf.open(result.output) as doc:
        assert len(doc)==3
        assert 'vector text' in doc[0].get_text()


def test_split_merge_rotate(tmp_path,simple_pdf):
    outputs=split_pdf(simple_pdf,tmp_path / 'splits', '1-3', each_page=True)
    assert len(outputs)==3
    for out in outputs:
        assert file_info(out)[1]==1
    merged=merge_pdfs(outputs,tmp_path / 'merged')
    assert file_info(merged)[1]==3
    rotated=rotate_pdf(simple_pdf,tmp_path / 'rotate',90, '2-3')
    with pymupdf.open(rotated) as doc:
        assert [p.rotation for p in doc] == [0,90,90]
        assert 'vector text' in doc[1].get_text()
    one=split_pdf(simple_pdf,tmp_path / 'one', '1,3')
    assert file_info(one[0])[1] == 2


def test_cancel(tmp_path,simple_pdf):
    cancel=threading.Event();cancel.set()
    with pytest.raises(Cancelled):
        compress_pdf(simple_pdf,tmp_path/'out',cancel=cancel)
    with pytest.raises(Cancelled):
        merge_pdfs([simple_pdf,simple_pdf],tmp_path/'merged',cancel=cancel)
    with pytest.raises(Cancelled):
        split_pdf(simple_pdf,tmp_path/'split',cancel=cancel)


def test_collision(tmp_path,simple_pdf):
    first=compress_pdf(simple_pdf,tmp_path/'out',name_template='test',mode='balanced')
    second=compress_pdf(simple_pdf,tmp_path/'out',name_template='test',mode='balanced')
    assert first.output != second.output
    assert Path(first.output).exists() and Path(second.output).exists()


def test_image_and_selectable_text_survive(tmp_path):
    from io import BytesIO
    from PIL import Image
    image=Image.new('RGB',(1100,800))
    # Nonuniform test image so JPEG compression actually matters.
    pixels=image.load()
    for y in range(800):
        for x in range(1100):
            pixels[x,y]=(x*11%256,y*17%256,(x+y)*7%256)
    data=BytesIO()
    image.save(data,format='PNG')
    src=tmp_path/'mixed.pdf'
    with pymupdf.open() as doc:
        p=doc.new_page(width=595,height=842)
        p.insert_text((72,78),'Selectable vector title',fontsize=18)
        p.insert_image(pymupdf.Rect(50,100,500,500),stream=data.getvalue())
        doc.save(src)
    result=compress_pdf(src,tmp_path/'out', mode='balanced')
    with pymupdf.open(result.output) as doc:
        assert len(doc)==1
        assert 'Selectable vector title' in doc[0].get_text()
        images=doc[0].get_images()
        assert images
        assert images[0][2:4]==(1100,800)
        assert doc[0].get_pixmap().samples
