"""openpyxl なしで xlsx の各シートを行の配列として読む（ふりがな rPh は除く）。
使い方: python3 -I xlsx_dump.py FILE [最大行数]
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_xlsx(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            parts = [t.text or "" for t in si.findall("m:t", NS)]
            parts += [t.text or "" for t in si.findall("m:r/m:t", NS)]
            shared.append("".join(parts))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap = {r.get("Id"): r.get("Target") for r in rels}
    sheets = []
    for sh in wb.find("m:sheets", NS):
        rid = sh.get("{%s}id" % NS["r"])
        target = relmap[rid].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        root = ET.fromstring(z.read(target))
        rows = []
        for row in root.iter("{%s}row" % NS["m"]):
            cells = {}
            for c in row.findall("m:c", NS):
                t = c.get("t")
                v = c.find("m:v", NS)
                if t == "s" and v is not None:
                    val = shared[int(v.text)]
                elif t == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
                elif v is not None:
                    val = v.text
                    try:
                        val = float(val)
                        if val.is_integer():
                            val = int(val)
                    except ValueError:
                        pass
                else:
                    continue
                cells[col_index(c.get("r"))] = val
            if cells:
                width = max(cells) + 1
                rows.append([cells.get(i) for i in range(width)])
            else:
                rows.append([])
        sheets.append((sh.get("name"), rows))
    return sheets


if __name__ == "__main__":
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    for name, rows in read_xlsx(sys.argv[1]):
        print("##", name, len(rows))
        for r in rows[:limit]:
            print([c for c in r if c not in (None, "")][:16])
