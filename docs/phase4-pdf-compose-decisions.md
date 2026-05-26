# Phase 4 PDF Compose Decisions

PDF composition uses PyMuPDF `insert_pdf` and preserves source pages exactly. Pass slots are represented as blank pages so slot numbering and bookmarks stay aligned with the composition file.

Because `IndexEntry` does not yet store per-problem answer page ranges, v1 uses the problem page range against `answer_path` when an answer PDF exists. This is documented as a model limitation and should be replaced by explicit answer ranges in a later index model upgrade.

