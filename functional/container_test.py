from pathlib import Path
from typing import List

import pytest
from lxml import etree

from xml_dataclasses import dump, load, rename, xml_dataclass

from .utils import lmxl_dump

BASE = Path(__file__).resolve(strict=True).parent

CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"


@xml_dataclass
class RootFile:
    __ns__ = CONTAINER_NS
    full_path: str = rename(name="full-path")
    media_type: str = rename(name="media-type")


@xml_dataclass
class RootFiles:
    __ns__ = CONTAINER_NS
    rootfile: List[RootFile]


@xml_dataclass
class Container:
    __ns__ = CONTAINER_NS
    version: str
    rootfiles: RootFiles
    # WARNING: this is an incomplete implementation of an OPF container

    def xml_validate(self):
        if self.version != "1.0":
            raise ValueError(f"Unknown container version '{self.version}'")


@pytest.mark.parametrize("remove_blank_text", [True, False])
def test_functional_container_no_whitespace(remove_blank_text):
    parser = etree.XMLParser(remove_blank_text=remove_blank_text)
    el = etree.parse(str(BASE / "container.xml"), parser).getroot()
    original = lmxl_dump(el)
    container = load(Container, el, "container")
    assert container == Container(
        version="1.0",
        rootfiles=RootFiles(
            rootfile=[
                RootFile(
                    full_path="OEBPS/content.opf",
                    media_type="application/oebps-package+xml",
                ),
            ],
        ),
    )
    el = dump(container, "container", {None: CONTAINER_NS})
    roundtrip = lmxl_dump(el)
    assert original == roundtrip
