# -*- coding: utf-8 -*-
"""
Created on Thu Jul  3 11:13:04 2025

@author: ZBaker
"""

def getPnl(BLOTTER_FILE):

    import os, re
    import pandas as pd
    
    from xlsxwriter.utility import xl_rowcol_to_cell

    # ─── CONFIGURABLES ─────────────────────────────────────────────────────────────
    
    # BLOTTER_FILE = r"C:\Users\zbaker\OneDrive - NINE MASTS CAPITAL LIMITED\Jason PnL File\JS_blotter_15290403_20250626.xlsx"
    TRADER_NAME  = "JASONSINGH88"
    OUTPUT_FILE = r"C:\Users\zbaker\OneDrive - NINE MASTS CAPITAL LIMITED\Jason PnL File\JS_PnL_TEST.xlsx"
    
    # Blotter Column Names
    COL_ORDER    = "Order Number"
    COL_SIDE     = "Side"
    COL_QTY      = "Exec Last Fill"
    COL_PX       = "Exec Last Fill Px"
    COL_EXCH     = "Exchange"
    COL_BBG      = "Ticker"
    COL_TRADER   = "Trader Name"
    COL_SEQ      = "Exec Seq Number"
    
    # Map root tickers
    
    CATEGORIES = {
        "Steel": ["HRC", "ROC"],
        "Copper": ["HG", "LMCADS03"],
        "Oil": ["CL", "HO"]
        # add others as you go...
    }
    
    # CAPITAL = {
    #     "HRCV5 Comdty": 500000,
    #     "HRCN5 Comdty": 500000,
    #     # add others as you go...    
    # }
    
    # CONTRACT_MULT = {
    #     "HRC": 1000,
    #     # add others as you go...
    # }
    
    # ─── 1) LOAD & FILTER ──────────────────────────────────────────────────────────
    
    df = pd.read_excel(BLOTTER_FILE)
    df = df[df[COL_TRADER] == TRADER_NAME].copy()
    
    # ─── 2) DEDUPE FILLS ──────────────────────────────────────────────────────────
    
    df.drop_duplicates(subset=[COL_ORDER, COL_SEQ], inplace=True)
    
    # ─── 3) SIGN QUANTITY ─────────────────────────────────────────────────────────
    
    # Normalize column names
    df.rename(columns={COL_QTY: "Amount", COL_PX: "EntryPx"}, inplace=True)
    
    # Define a simple BUY/SELL sign rule; adjust if your blotter codes differ:
    def sign_qty(side):
        side = side.strip().upper()
        if side.startswith("B"):   return "BUY"
        if side.startswith("S"):   return "SELL"
    df[COL_SIDE] = df.apply(lambda r: sign_qty(r[COL_SIDE]), axis=1)
    
    # df["SignedQty"] = df.apply(lambda r: sign_qty(r[COL_SIDE], r["Quantity"]), axis=1)
    df.drop(columns={
        # "Broker",
        "Is Leg Level",
        "Trader Name",
        # "Asset Class",
        "Exec Type"
    }, inplace=True)
    
    # ─── 4) EXTRACT ROOT TICKER ───────────────────────────────────────────────────
    
    # e.g. "HRCV5 Comdty"  →  "HRC"
    
    def extract_roots(code_str):
        code = code_str.split()[0]
        parts = re.findall(r'([A-Z]+[FGHJKMNQUVXZ]\d)', code)
        if parts:
            return [p[:-2] for p in parts]
        else:
            return [code]
    
    # df["Mul"] = df["Root"].map(CONTRACT_MULT).fillna(1)
    
    # ─── 5) PREPARE FOR EXCEL OUTPUT ───────────────────────────────────────────────
    
    group_cols = [COL_BBG, COL_ORDER, COL_SIDE, COL_EXCH, "Broker"]
    
    agg = (
        df
        .groupby(group_cols, as_index=False)
        .agg({
            "Amount": "sum",
            "EntryPx": "mean"
        })
    )
    
    
    # df = agg
    df["Last Price"] = ""
    
    
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Raw", index=False)
        wb = writer.book
        ws = writer.sheets["Raw"]
        
        # Write header in row-1
        for col, header in enumerate(df.columns):
            ws.write(0, col, header)
            
        idxs = {c: i for i, c in enumerate(df.columns)}
        cb = idxs[COL_BBG]
        ce = idxs["EntryPx"]
        cq = idxs["Amount"]
        # cm = idxs["Mul"]
        cmtm = idxs["Last Price"]
        # cpnl = idxs["PnL"]
        
        for r, row in enumerate(df.itertuples(), start=1):
            tkr = getattr(row, COL_BBG)
            px_f = f'=BDP("{tkr} Comdty", "PX_LAST")'
            ws.write_formula(r, cmtm, px_f)
            
            cell_m = xl_rowcol_to_cell(r, cmtm)
            cell_e = xl_rowcol_to_cell(r, ce)
            cell_q = xl_rowcol_to_cell(r, cq)
            # cell_u = xl_rowcol_to_cell(r, cm)
            # pnl_f = f'={cell_q}*({cell_m}-{cell_e})' # * cell_u (if adding multiplyer)
            # ws.write_formula(r, cpnl, pnl_f)
    
        for cat_name, triggers in CATEGORIES.items():
            ws_cat = writer.book.add_worksheet(cat_name)
            ws_cat.write(0, 0, cat_name)
            for c, k in enumerate(CATEGORIES.get(cat_name)):
                ws_cat.write(c+2, 0, k)
            headers = [
                "Exchange", "BBG Ticker", "Direction", "Enter Position", "POSITION", "PRICE", "MtM Price", "PnL"
            ]
            for c, h in enumerate(headers):
                ws_cat.write(len(CATEGORIES.get(cat_name))+3, c, h)
            
            mask = df[COL_BBG].apply(
                lambda full: any(rt in triggers
                                 for rt in extract_roots(full))    
            )
            sub = df[mask]
            
            grp = (
                sub
                .groupby(group_cols, as_index=False)
                .agg({
                    "Amount": "sum",
                    "EntryPx": "mean"
                    })
                )
            for r, row in enumerate(grp.itertuples(), start=len(CATEGORIES.get(cat_name))+4):
                exch = getattr(row, COL_EXCH)
                tkr = getattr(row, COL_BBG)
                side = getattr(row, COL_SIDE)
                ent = getattr(row, "Amount")
                px = getattr(row, "EntryPx")
                # cap = CAPITAL.get(tkr, "")
                
                ws_cat.write(r, 0, exch)
                ws_cat.write(r, 1 , f"{tkr} Comdty")
                ws_cat.write(r, 2, side)
                ws_cat.write(r, 3, ent)
                if side == "SELL":
                    ws_cat.write(r, 4, -ent)
                else:
                    ws_cat.write(r, 4, ent)
                ws_cat.write(r, 5, px)
                
                f_mtm = f'=BDP("{tkr} Comdty", "PX_LAST")'
                ws_cat.write_formula(r, 6, f_mtm)
                
                mcell = xl_rowcol_to_cell(r, 6)
                ecell = xl_rowcol_to_cell(r, 5)
                qcell = xl_rowcol_to_cell(r, 4)
                
                root = tkr[:-2]
                f_pnl = f'={qcell}*({mcell}-{ecell})'
                ws_cat.write_formula(r, 7, f_pnl)
                
                
    return OUTPUT_FILE
