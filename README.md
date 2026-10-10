# Flowbit page for vistaarwebx.com

`flowbit.html` is the built, self-contained page (inline CSS/JS, assets as data URIs).

- `page/flowbit.src.html`: the page source with `@@PLACEHOLDER@@` slots.
- `page/vistaar-shell.css`: the Vistaar header/footer CSS and Geist fonts, copied verbatim from the About page.
- `page/assets/`: Flowbit brand files from the flowbit-main zip (logo, mark, ribbons, check-in widget).
- `build.py`: fills the slots and writes `flowbit.html`. Run `python3 build.py` after editing the source.

Placeholders to replace before launch: the signup URL (`https://flowbit.com/signup?trial=15`), the `₹XX` prices, and the stat tiles marked "Placeholder".
