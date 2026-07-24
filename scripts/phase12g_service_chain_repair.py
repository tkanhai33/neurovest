#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

main = ROOT / "backend/app/main.py"
text = main.read_text()

text = text.replace(
    "from backend.app.stacks.market_data.feed import get_live_price_quote\n",
    ""
)

if "from backend.app.stacks.market_data.market_data_service import get_live_market_price_for_api" not in text:
    text = "from backend.app.stacks.market_data.market_data_service import get_live_market_price_for_api\n" + text

text = text.replace(
    "return await get_live_price_quote(symbol)",
    "return await get_live_market_price_for_api(symbol)"
)

main.write_text(text)

phase11 = ROOT / "scripts/phase11_live_market_price_api_bridge.py"
p11 = phase11.read_text()

p11 = p11.replace(
    '''if "get_live_price_quote" not in main_text:
    main_text = main_text.replace(
        "from fastapi import FastAPI",
        "from fastapi import FastAPI"
    )

    import_line = "from backend.app.stacks.market_data.feed import get_live_price_quote\\n"

    if import_line not in main_text:
        main_text = import_line + main_text
''',
    '''if "get_live_market_price_for_api" not in main_text:
    import_line = "from backend.app.stacks.market_data.market_data_service import get_live_market_price_for_api\\n"

    if import_line not in main_text:
        main_text = import_line + main_text
'''
)

p11 = p11.replace(
    "return await get_live_price_quote(symbol)",
    "return await get_live_market_price_for_api(symbol)"
)

phase11.write_text(p11)

cert = ROOT / "scripts/phase11_live_market_price_api_bridge_certification.py"
c = cert.read_text()

c = c.replace(
    '"main_import_exists": "get_live_price_quote" in main_text,',
    '"main_import_exists": "get_live_market_price_for_api" in main_text,'
)

cert.write_text(c)

print("patched Phase 12G service-chain repair")
