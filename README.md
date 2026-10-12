# Flowbit page for vistaarwebx.com

`flowbit.html` is the built page (inline CSS/JS, images as data URIs). Deploy it next to `wiki/` (the user-manual PDFs) and `vendor/pdf.worker.min.js` (the PDF.js 3.11.174 worker for the in-page reader); both are linked relatively.

- `page/flowbit.src.html`: the page source with `@@PLACEHOLDER@@` slots.
- `page/vistaar-shell.css`: the Vistaar header/footer CSS and Geist fonts, copied verbatim from the About page.
- `page/assets/`: Flowbit brand files from the flowbit-main zip (logo, mark, ribbons, check-in widget).
- `build.py`: fills the slots and writes `flowbit.html`. Run `python3 build.py` after editing the source.

Trial and demo buttons link to useflowbit.com. The support address (support@flowbit.app) still needs confirming.
