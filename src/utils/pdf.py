from typing import Any, List, Optional,Union
import numpy as np
import pypdfium2 as pdfium
from pathlib import Path


__all__ = ["Point2D", "BoundingBox", "Polygon4P", "Polygon", "Bbox","read_pdf"]



AbstractPath = Union[str, Path]
AbstractFile = Union[AbstractPath, bytes]


def read_pdf(
    file: AbstractFile,
    scale: float = 2,
    rgb_mode: bool = True,
    password: Optional[str] = None,
    **kwargs: Any,
) -> List[np.ndarray]:
    """Read a PDF file and convert it into an image in numpy format

    >>> from doctr.io import read_pdf
    >>> doc = read_pdf("path/to/your/doc.pdf")

    Args:
    ----
        file: the path to the PDF file
        scale: rendering scale (1 corresponds to 72dpi)
        rgb_mode: if True, the output will be RGB, otherwise BGR
        password: a password to unlock the document, if encrypted
        **kwargs: additional parameters to :meth:`pypdfium2.PdfPage.render`

    Returns:
    -------
        the list of pages decoded as numpy ndarray of shape H x W x C
    """
    # Rasterise pages to numpy ndarrays with pypdfium2
    pdf = pdfium.PdfDocument(file, password=password)
    try:
        return [page.render(scale=scale, rev_byteorder=rgb_mode, **kwargs).to_numpy() for page in pdf]
    finally:
        pdf.close()

class DocumentFile:
    """Read a document from multiple extensions"""

    @classmethod
    def from_pdf(cls, file: AbstractFile, **kwargs) -> List[np.ndarray]:
        """Read a PDF file

        >>> from doctr.io import DocumentFile
        >>> doc = DocumentFile.from_pdf("path/to/your/doc.pdf")

        Args:
        ----
            file: the path to the PDF file or a binary stream
            **kwargs: additional parameters to :meth:`pypdfium2.PdfPage.render`

        Returns:
        -------
            the list of pages decoded as numpy ndarray of shape H x W x 3
        """
        return read_pdf(file, **kwargs)        