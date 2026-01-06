import re
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.filters.hp_filter import hpfilter
import datetime as _dt


def _is_quarter_str(x) -> bool:
    if pd.isna(x):
        return False
    return bool(re.match(r"^\s*\d{4}\s*Q\s*[1-4]\s*$", str(x), flags=re.IGNORECASE))


def _parse_period(x, quarterly: bool) -> pd.Period | None:
    if pd.isna(x):
        return None

    if isinstance(x, (pd.Timestamp, _dt.datetime, _dt.date, np.datetime64)):
        ts = pd.Timestamp(x)
        if quarterly:
            return pd.Period(ts, freq="Q")
        return pd.Period(ts.year, freq="Y-DEC")

    s = str(x).strip().upper().replace(" ", "")
    if quarterly:
        m = re.match(r"^(\d{4})Q([1-4])$", s)
        return pd.Period(f"{m.group(1)}Q{m.group(2)}", freq="Q") if m else None
    m = re.match(r"^(\d{4})$", s)
    return pd.Period(int(m.group(1)), freq="Y-DEC") if m else None



def _find_xlsx(script_dir: Path, candidates: list[str]) -> Path:
    for name in candidates:
        p = script_dir / name
        if p.exists():
            return p
    lower = {p.name.lower(): p for p in script_dir.glob("*.xlsx")}
    for name in candidates:
        p = lower.get(name.lower())
        if p is not None:
            return p
    raise FileNotFoundError(f"Could not find any of: {candidates} in {script_dir}")


# Helper to read any Excel sheet containing 'Year' header or fallback.
def _read_excel_any_sheet(xlsx_path: Path, preferred: str = "Data") -> pd.DataFrame:
    xls = pd.ExcelFile(xlsx_path)
    if preferred in xls.sheet_names:
        return pd.read_excel(xlsx_path, sheet_name=preferred, header=None)

    def _has_year(df: pd.DataFrame) -> bool:
        for r in range(min(len(df), 200)):
            row = df.iloc[r].astype(str).str.strip().str.lower()
            if (row == "year").any():
                return True
            if row.str.contains(r"\bquarter\b", regex=True).any():
                return True
        return False

    for sh in xls.sheet_names:
        df = pd.read_excel(xlsx_path, sheet_name=sh, header=None)
        if _has_year(df):
            return df

    return pd.read_excel(xlsx_path, sheet_name=xls.sheet_names[0], header=None)


def load_gdp_from_excel(xlsx_path: Path) -> dict[str, pd.Series]:
    raw = _read_excel_any_sheet(xlsx_path, preferred="Data")

    header_row = None
    for r in range(len(raw)):
        row = raw.iloc[r].astype(str).str.strip().str.lower()
        if (row == "year").any():
            header_row = r
            break
    if header_row is None:
        raise ValueError("Could not find a header row containing 'Year'.")

    country_row = header_row - 1

    year_col = None
    for c in range(raw.shape[1]):
        v = raw.iat[header_row, c]
        if isinstance(v, str) and v.strip().lower() == "year":
            year_col = c
            break
    if year_col is None:
        raise ValueError("Could not locate the 'Year' column.")

    quarterly = False
    for r in range(header_row + 1, len(raw)):
        v = raw.iat[r, year_col]
        if pd.isna(v):
            continue
        quarterly = _is_quarter_str(v)
        break

    alias = {
        "usa": "USA",
        "uk": "UK",
        "unitedkingdom": "UK",
        "sweden": "Sweden",
        "sverige": "Sweden",
        "svergie": "Sweden",
        "denmark": "Denmark",
        "danmark": "Denmark",
    }

    gdp_cols: dict[str, int] = {}
    for c in range(raw.shape[1]):
        lab = raw.iat[header_row, c]
        ctry = raw.iat[country_row, c]
        if not (isinstance(lab, str) and lab.strip().lower() == "gdp"):
            continue
        if not isinstance(ctry, str):
            continue
        key = alias.get(ctry.strip().lower().replace(" ", ""))
        if key:
            gdp_cols[key] = c

    need = ["USA", "UK", "Sweden", "Denmark"]
    miss = [k for k in need if k not in gdp_cols]
    if miss:
        raise ValueError(f"Missing GDP columns for: {miss}. Found: {gdp_cols}")

    periods: list[pd.Period] = []
    for r in range(header_row + 1, len(raw)):
        p = _parse_period(raw.iat[r, year_col], quarterly=quarterly)
        if p is None:
            break
        periods.append(p)
    if not periods:
        raise ValueError("No dates found under 'Year'.")

    idx = pd.PeriodIndex(periods, freq=("Q" if quarterly else "Y-DEC"))

    out: dict[str, pd.Series] = {}
    for name in need:
        col = gdp_cols[name]
        vals = pd.to_numeric(
            raw.iloc[header_row + 1 : header_row + 1 + len(idx), col],
            errors="coerce",
        ).to_numpy()
        out[name] = pd.Series(vals, index=idx, name=name).dropna()

    return out


def load_yci_from_excel(xlsx_path: Path) -> dict[str, pd.Series]:
    raw = _read_excel_any_sheet(xlsx_path, preferred="Data")

    header_row = None
    for r in range(min(len(raw), 300)):
        row = raw.iloc[r].astype(str).str.strip().str.lower()
        if row.str.contains(r"\byear\b", regex=True).any() or row.str.contains(r"\bquarter\b", regex=True).any():
            header_row = r
            break
    if header_row is None:
        raise ValueError("Could not find a header row containing 'Year' or 'Quarter'.")

    year_col = None
    for c in range(raw.shape[1]):
        v = raw.iat[header_row, c]
        if isinstance(v, str):
            vv = v.strip().lower()
            if vv == "year" or "quarter" in vv or vv.startswith("quarter") or vv.startswith("date"):
                year_col = c
                break
    if year_col is None:
        year_col = 0

    quarterly = False
    h = raw.iat[header_row, year_col]
    if isinstance(h, str) and "quarter" in h.strip().lower():
        quarterly = True
    else:
        for r in range(header_row + 1, len(raw)):
            v = raw.iat[r, year_col]
            if pd.isna(v):
                continue
            if isinstance(v, (pd.Timestamp, _dt.datetime, _dt.date, np.datetime64)):
                quarterly = True
            else:
                quarterly = _is_quarter_str(v)
            break

    def labkey(v) -> str:
        if not isinstance(v, str):
            return ""
        s = v.strip().lower()
        s = re.sub(r"\s+", " ", s)
        return s

    cols: dict[str, int] = {}
    for c in range(raw.shape[1]):
        s = labkey(raw.iat[header_row, c])
        if not s:
            continue

        if ("gdp" in s) or ("bnp" in s) or re.search(r"[,\s]y\b", s):
            cols.setdefault("Y", c)
        elif ("consumption" in s) or ("forbrug" in s) or re.search(r"[,\s]c\b", s):
            cols.setdefault("C", c)
        elif ("investment" in s) or ("investering" in s) or re.search(r"[,\s]i\b", s):
            cols.setdefault("I", c)

    need = ["Y", "C", "I"]
    miss = [k for k in need if k not in cols]
    if miss:
        raise ValueError(f"Missing columns for {miss}. Found: {cols}")

    periods: list[pd.Period] = []
    for r in range(header_row + 1, len(raw)):
        p = _parse_period(raw.iat[r, year_col], quarterly=quarterly)
        if p is None:
            break
        periods.append(p)
    if not periods:
        raise ValueError("No dates found under 'Year'.")

    idx = pd.PeriodIndex(periods, freq=("Q" if quarterly else "Y-DEC"))

    out: dict[str, pd.Series] = {}
    for k in need:
        col = cols[k]
        vals = pd.to_numeric(
            raw.iloc[header_row + 1 : header_row + 1 + len(idx), col],
            errors="coerce",
        ).to_numpy()
        out[k] = pd.Series(vals, index=idx, name=k).dropna()

    return out


def period_to_ts(idx: pd.PeriodIndex) -> pd.DatetimeIndex:
    if idx.freqstr.startswith("Q"):
        return idx.to_timestamp("Q", how="end")
    return idx.to_timestamp(how="end")


def xlims_from_series(y_log: pd.Series) -> tuple[pd.Timestamp, pd.Timestamp]:
    idx = y_log.index
    if not isinstance(idx, pd.PeriodIndex):
        raise ValueError("Expected PeriodIndex.")
    if idx.freqstr.startswith("Q"):
        start = max(pd.Period("1950Q1", freq="Q"), idx.min())
    else:
        start = max(pd.Period("1950", freq="Y-DEC"), idx.min())
    end = idx.max()
    x0 = period_to_ts(pd.PeriodIndex([start]))[0]
    x1 = period_to_ts(pd.PeriodIndex([end]))[0]
    return x0, x1


def hp_trend_gap(y_log: pd.Series, lamb: float) -> tuple[pd.Series, pd.Series]:
    cycle, trend = hpfilter(y_log, lamb=lamb)
    gap_pct = 100.0 * cycle
    trend.name = "trend"
    gap_pct.name = "gap"
    return trend, gap_pct


def plot_lngdp_2x2(gdp: dict[str, pd.Series], outpath: Path, lamb: float = 100.0) -> None:
    countries = ["USA", "UK", "Sweden", "Denmark"]

    fig, axes = plt.subplots(2, 2, figsize=(7, 5), sharex=False, sharey=False)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.16, wspace=0.18, hspace=0.28)

    y_ref = np.log(gdp["USA"].dropna())
    x0, x1 = xlims_from_series(y_ref)

    leg_handle = None
    leg_label = None

    for k, name in enumerate(countries):
        ax = axes[k // 2, k % 2]

        y = np.log(gdp[name].dropna())
        trend, _ = hp_trend_gap(y, lamb=lamb)

        y_ts = pd.Series(y.values, index=period_to_ts(y.index))
        tr_ts = pd.Series(trend.values, index=period_to_ts(trend.index))

        ax.grid(True, linestyle=":", alpha=0.7)
        ax.set_xlim(x0, x1)

        ax.plot(y_ts.index, y_ts.values, linewidth=2.0)
        l_tr, = ax.plot(tr_ts.index, tr_ts.values, linewidth=2.0, label=rf"HP ($\lambda={int(lamb)}$)")

        ymin = float(np.nanmin([y_ts.values.min(), tr_ts.values.min()]))
        ymax = float(np.nanmax([y_ts.values.max(), tr_ts.values.max()]))
        ax.set_ylim(ymin - 0.15, ymax + 0.15)

        ax.set_title(name, fontsize=11)
        ax.set_ylabel("Log GDP" if (k % 2 == 0) else "")

        ax.xaxis.set_major_locator(mdates.YearLocator(10))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.tick_params(axis="x", labelsize=9)
        ax.tick_params(axis="y", labelsize=9)

        if leg_handle is None:
            leg_handle, leg_label = l_tr, l_tr.get_label()

    fig.legend([leg_handle], [leg_label], loc="lower center", ncol=1, frameon=False)
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_output_gap(gdp: dict[str, pd.Series], outpath: Path, lamb: float) -> None:
    plt.figure(figsize=(6, 4))
    plt.grid(True, linestyle=":", alpha=0.7)

    y_ref = np.log(gdp["USA"].dropna())
    x0, x1 = xlims_from_series(y_ref)

    all_vals = []
    for name in ["USA", "UK", "Sweden", "Denmark"]:
        y = np.log(gdp[name].dropna())
        _, gap = hp_trend_gap(y, lamb=lamb)
        gap_ts = pd.Series(gap.values, index=period_to_ts(gap.index))
        plt.plot(gap_ts.index, gap_ts.values, label=name)
        all_vals.append(gap_ts.values)

    all_vals = np.concatenate(all_vals)

    plt.axhline(0, linewidth=0.8)
    plt.xlim(x0, x1)
    plt.ylim(np.floor(np.nanmin(all_vals) - 1.0), np.ceil(np.nanmax(all_vals) + 1.0))
    plt.ylabel("Output gap (pct.)")
    plt.legend()
    plt.savefig(outpath, bbox_inches="tight")
    plt.close()


def _fmt_pct(x: float | None) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    return f"{x:.1f}" + r"\%"


def _fmt_corr(x: float | None) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    return f"{x:.2f}"


def write_table_tex(gdp: dict[str, pd.Series], outpath: Path) -> None:
    lamb = 100.0
    gaps: dict[str, pd.Series] = {}
    for name in ["USA", "UK", "Sweden", "Denmark"]:
        y = np.log(gdp[name].dropna())
        _, gap = hp_trend_gap(y, lamb=lamb)
        gaps[name] = gap

    def pick(s: pd.Series, y0: int, y1: int) -> pd.Series:
        idx = s.index
        m = (idx.year >= y0) & (idx.year <= y1)
        return s.loc[m].dropna()

    rows = [
        ("1955-1964", 1955, 1964),
        ("1965-1974", 1965, 1974),
        ("1975-1984", 1975, 1984),
        ("1985-1994", 1985, 1994),
        ("1995-2004", 1995, 2004),
        ("2005-2014", 2005, 2014),
        ("1955-2014", 1955, 2014),
    ]

    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\begin{tabular}{lcccccc}",
        r"\hline",
        r"& $\sigma_{DK}$ & $\sigma_{UK}$ & $\sigma_{SWE}$ & $\sigma_{DK}$ & $\rho_{DK,USA}$ & $\rho_{DK,SWE}$ \\",
        r"\hline",
    ]

    for label, y0, y1 in rows:
        sd_usa = pick(gaps["USA"], y0, y1).std(ddof=1)
        sd_uk = pick(gaps["UK"], y0, y1).std(ddof=1)
        sd_swe = pick(gaps["Sweden"], y0, y1).std(ddof=1)
        sd_dk = pick(gaps["Denmark"], y0, y1).std(ddof=1)

        c1 = ""
        c2 = ""
        if label == "1955-2014":
            dk = pick(gaps["Denmark"], y0, y1)
            usa = pick(gaps["USA"], y0, y1).reindex(dk.index).dropna()
            swe = pick(gaps["Sweden"], y0, y1).reindex(dk.index).dropna()

            dk_usa = dk.reindex(usa.index).dropna()
            dk_swe = dk.reindex(swe.index).dropna()

            c1 = _fmt_corr(dk_usa.corr(usa)) if len(dk_usa) and len(usa) else ""
            c2 = _fmt_corr(dk_swe.corr(swe)) if len(dk_swe) and len(swe) else ""

        lines.append(
            f"{label} & {_fmt_pct(sd_usa)} & {_fmt_pct(sd_uk)} & {_fmt_pct(sd_swe)} & {_fmt_pct(sd_dk)} & {c1} & {c2} \\\\"
        )

    lines += [r"\hline", r"\end{tabular}", r"\end{table}"]
    outpath.write_text("\n".join(lines), encoding="utf-8")


def plot_usa_gap_compare(gdp: dict[str, pd.Series], outpath: Path) -> None:
    y = np.log(gdp["USA"].dropna())
    _, gap100 = hp_trend_gap(y, lamb=100.0)
    _, gap1000 = hp_trend_gap(y, lamb=1000.0)

    gap100_ts = pd.Series(gap100.values, index=period_to_ts(gap100.index))
    gap1000_ts = pd.Series(gap1000.values, index=period_to_ts(gap1000.index))

    x0, x1 = xlims_from_series(y)

    plt.figure(figsize=(7, 5))
    plt.grid(True, linestyle=":", alpha=0.7)
    plt.plot(gap100_ts.index, gap100_ts.values, linewidth=1.5, label=r"Outputgap USA ($\lambda=100$)")
    plt.plot(gap1000_ts.index, gap1000_ts.values, linewidth=1.5, label=r"Outputgap USA ($\lambda=1000$)")
    allv = np.concatenate([gap100_ts.values, gap1000_ts.values])
    plt.ylim(np.floor(np.nanmin(allv) - 1.0), np.ceil(np.nanmax(allv) + 1.0))
    plt.axhline(0, linewidth=1.5, color="gray", linestyle="--")
    plt.xlim(x0, x1)
    plt.ylabel("Outputgap (%)")
    plt.legend(loc="lower right")
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.YearLocator(10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.savefig(outpath, bbox_inches="tight")
    plt.close()


def plot_denmark_gap_annotated(gdp: dict[str, pd.Series], outpath: Path) -> None:
    y = np.log(gdp["Denmark"].dropna())
    _, gap = hp_trend_gap(y, lamb=100.0)
    gap_ts = pd.Series(gap.values, index=period_to_ts(gap.index))
    x0, x1 = xlims_from_series(y)

    fig = plt.figure(figsize=(7, 5))
    ax = plt.gca()
    plt.grid(True, linestyle=":", alpha=0.7)
    plt.plot(gap_ts.index, gap_ts.values, linewidth=1.5, label=r"Outputgap DK ($\lambda=100$)")
    plt.axhline(0, linewidth=1.5, color="gray", linestyle="--")
    plt.xlim(x0, x1)

    plt.ylim(np.floor(np.nanmin(gap_ts.values) - 1.0), np.ceil(np.nanmax(gap_ts.values) + 1.0))

    ax.xaxis.set_major_locator(mdates.YearLocator(10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.legend(loc="lower right")
    plt.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def _slice_6621(s: pd.Series) -> pd.Series:
    idx = s.index
    if idx.freqstr.startswith("Q"):
        a = pd.Period("1966Q1", freq="Q")
        b = pd.Period("2021Q4", freq="Q")
    else:
        a = pd.Period("1966", freq="Y-DEC")
        b = pd.Period("2021", freq="Y-DEC")
    b = min(b, idx.max())
    return s.loc[(idx >= a) & (idx <= b)].dropna()


def plot_fig5_dk_log_levels_trends(yci: dict[str, pd.Series], outpath: Path) -> None:
    order = [("Y", "ln(Y)"), ("C", "ln(C)"), ("I", "ln(I)")]
    lambdas = [1600.0, 100.0]

    fig, axes = plt.subplots(2, 3, figsize=(12, 6), sharex=False, sharey=False)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.14, wspace=0.22, hspace=0.28)

    for r, lam in enumerate(lambdas):
        for c, (k, lab) in enumerate(order):
            ax = axes[r, c]
            s = _slice_6621(yci[k])
            y = np.log(s)
            tr, _ = hp_trend_gap(y, lamb=lam)

            y_ts = pd.Series(y.values, index=period_to_ts(y.index))
            tr_ts = pd.Series(tr.values, index=period_to_ts(tr.index))

            x0 = y_ts.index.min()
            x1 = y_ts.index.max()

            ax.grid(True, linestyle=":", alpha=0.7)
            ax.plot(y_ts.index, y_ts.values, linewidth=2.0, label=lab)
            ax.plot(tr_ts.index, tr_ts.values, linewidth=2.0, label=rf"{lab} trend ($\lambda={int(lam)}$)")

            ymin = float(np.nanmin([y_ts.values.min(), tr_ts.values.min()]))
            ymax = float(np.nanmax([y_ts.values.max(), tr_ts.values.max()]))
            ax.set_ylim(ymin - 0.15, ymax + 0.15)

            ax.set_ylabel(lab)
            ax.set_xlim(x0, x1)
            ax.margins(x=0)
            ax.xaxis.set_major_locator(mdates.YearLocator(10))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
            ax.tick_params(axis="x", rotation=0, labelsize=8)
            ax.tick_params(axis="y", labelsize=8)
            ax.legend(loc="lower right", fontsize=7, frameon=False)

    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_fig6_dk_outputgaps_yci(yci: dict[str, pd.Series], outpath: Path, lamb: float = 1600.0) -> None:
    y = np.log(_slice_6621(yci["Y"]))
    c = np.log(_slice_6621(yci["C"]))
    i = np.log(_slice_6621(yci["I"]))

    _, gy = hp_trend_gap(y, lamb=lamb)
    _, gc = hp_trend_gap(c, lamb=lamb)
    _, gi = hp_trend_gap(i, lamb=lamb)

    gy_ts = pd.Series(gy.values, index=period_to_ts(gy.index))
    gc_ts = pd.Series(gc.values, index=period_to_ts(gc.index))
    gi_ts = pd.Series(gi.values, index=period_to_ts(gi.index))

    plt.figure(figsize=(6, 4))
    plt.grid(True, linestyle=":", alpha=0.7)
    plt.plot(gy_ts.index, gy_ts.values, linewidth=1.5, label=rf"Outputgap ln(Y) ($\lambda={int(lamb)}$)")
    plt.plot(gc_ts.index, gc_ts.values, linewidth=1.5, label=rf"Outputgap ln(C) ($\lambda={int(lamb)}$)")
    plt.plot(gi_ts.index, gi_ts.values, linewidth=1.5, label=rf"Outputgap ln(I) ($\lambda={int(lamb)}$)")
    plt.axhline(0, linewidth=2.0, color="gray", linestyle="--")

    allv = np.concatenate([gy_ts.values, gc_ts.values, gi_ts.values])
    plt.ylim(np.floor(np.nanmin(allv) - 1.0), np.ceil(np.nanmax(allv) + 1.0))
    plt.xlim(min(gy_ts.index.min(), gc_ts.index.min(), gi_ts.index.min()),
             max(gy_ts.index.max(), gc_ts.index.max(), gi_ts.index.max()))
    plt.ylabel("Outputgap (%)")
    plt.legend(loc="lower right", fontsize=8, frameon=False)

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.YearLocator(10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.xticks(rotation=0, fontsize=8)

    sy = float(np.nanstd(gy_ts.values, ddof=1))
    sc = float(np.nanstd(gc_ts.values, ddof=1))
    si = float(np.nanstd(gi_ts.values, ddof=1))

    plt.savefig(outpath, bbox_inches="tight")
    plt.close()


def write_fig7_corr_table_tex(yci: dict[str, pd.Series], outpath: Path, lamb: float = 1600.0) -> None:
    from decimal import Decimal, ROUND_HALF_UP

    def _r2(x: float) -> str:
        return str(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    def _end_2017q4(s: pd.Series) -> pd.Series:
        idx = s.index
        if isinstance(idx, pd.PeriodIndex) and idx.freqstr.startswith("Q"):
            endp = pd.Period("2017Q3", freq="Q")
        else:
            endp = pd.Period("2017", freq="Y-DEC")
        return s.loc[idx <= endp].dropna()

    y = np.log(_end_2017q4(_slice_6621(yci["Y"])))
    c = np.log(_end_2017q4(_slice_6621(yci["C"])))
    i = np.log(_end_2017q4(_slice_6621(yci["I"])))

    _, gy = hp_trend_gap(y, lamb=lamb)
    _, gc = hp_trend_gap(c, lamb=lamb)
    _, gi = hp_trend_gap(i, lamb=lamb)

    def corr_at_lag(a: pd.Series, b: pd.Series, k: int) -> float:
        bb = b.shift(k)
        df = pd.concat([a, bb], axis=1).dropna()
        return float(df.iloc[:, 0].corr(df.iloc[:, 1]))

    ks = [-2, -1, 0, 1, 2]
    rows = [
        (r"$Y$", [corr_at_lag(gy, gy, k) for k in ks]),
        (r"$C$", [corr_at_lag(gc, gy, k) for k in ks]),
        (r"$I$", [corr_at_lag(gi, gy, k) for k in ks]),
    ]

    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\begin{tabular}{lccccc}",
        r"\hline",
        r"\multicolumn{6}{c}{$\rho$} \\",
        r"\hline",
        r"& -2 & -1 & 0 & 1 & 2 \\",
        r"\hline",
    ]
    for name, vals in rows:
        lines.append(f"{name} & " + " & ".join([_r2(v) for v in vals]) + r" \\")
    lines += [r"\hline", r"\end{tabular}", r"\end{table}"]
    outpath.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=None)
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    outdir = args.outdir if args.outdir is not None else script_dir
    outdir.mkdir(parents=True, exist_ok=True)

    data_132 = _find_xlsx(script_dir, ["exercise_13_2_data.xlsx", "Exercise_13_2_Data.xlsx"])
    gdp = load_gdp_from_excel(data_132)

    plot_lngdp_2x2(gdp, outdir / "lngdp.pdf", lamb=100.0)
    plot_output_gap(gdp, outdir / "output_gap_lambda100.pdf", lamb=100.0)
    plot_output_gap(gdp, outdir / "output_gap_lambda1000.pdf", lamb=1000.0)
    write_table_tex(gdp, outdir / "table1.tex")
    plot_usa_gap_compare(gdp, outdir / "usa_outputgap_comp.pdf")
    plot_denmark_gap_annotated(gdp, outdir / "dk_outputgap.pdf")

    data_133 = _find_xlsx(script_dir, [
        "exercise_13_3_data.xlsx",
        "Exercise_13_3_Data.xlsx",
        "Exercise_13_3_Data (2).xlsx",
        "Opgave 13.3_svar.xlsx",
    ])
    yci = load_yci_from_excel(data_133)

    plot_fig5_dk_log_levels_trends(yci, outdir / "dk_log_trends.pdf")
    plot_fig6_dk_outputgaps_yci(yci, outdir / "dk_outputgaps_yci.pdf", lamb=1600.0)
    write_fig7_corr_table_tex(yci, outdir / "corr_table.tex", lamb=1600.0)

    print(f"Saved outputs to: {outdir}")


if __name__ == "__main__":
    main()