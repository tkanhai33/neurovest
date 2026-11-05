export const CAD_TICKER_SYMBOLS = [
  "CNR.TO", "CPKC.TO", "ENB.TO", "TRP.TO",
  "SU.TO", "CNQ.TO", "IMO.TO", "CVE.TO",
  "VFV.TO", "VUN.TO", "RY.TO", "TD.TO",
  "BNS.TO", "BMO.TO", "CM.TO", "NA.TO",
  "MFC.TO", "SLF.TO", "BCE.TO", "T.TO",
  "SHOP.TO", "BAM.TO", "ATD.TO", "WCN.TO",
  "FTS.TO", "EMA.TO", "FNV.TO", "DOL.TO",
  "L.TO", "GWO.TO", "NTR.TO", "CCO.TO",
  "CSU.TO", "CJT.TO", "CAE.TO", "WSP.TO",
  "QSR.TO", "IFC.TO", "POW.TO", "PPL.TO",
  "KEY.TO", "K.TO", "MRU.TO", "LSPD.TO",
  "GIL.TO", "WN.TO", "TOU.TO", "FRU.TO",
  "TVE.TO", "H.TO", "AQN.TO", "BIR.TO",
] as const;

export const US_TICKER_SYMBOLS = [
  "AAPL", "MSFT", "NVDA", "TSLA", "AMD",
  "META", "GOOGL", "AMZN", "AVGO", "NFLX",
  "ORCL", "CRM", "ADBE", "PLTR", "JPM",
  "V", "MA", "WMT", "COST", "XOM",
  "JNJ", "PG", "KO", "DIS", "NKE",
  "QCOM", "INTC", "SPY", "QQQ", "IWM",
  "BRK-B", "HD", "MCD", "SBUX", "BA",
  "GE", "CAT", "DE", "LIN", "ABBV",
  "MRK", "PFE", "TMO", "LLY", "UNH",
  "CVX", "COP", "OXY", "GS", "MS",
  "BAC", "C", "SCHW", "BLK", "AMGN",
  "TXN", "MU", "NOW", "PANW", "UBER",
] as const;

export const CRYPTO_TICKER_SYMBOLS = [
  "BTC-CAD", "ETH-CAD", "SOL-CAD", "XRP-CAD",
  "DOGE-CAD", "ADA-CAD", "AVAX-CAD", "LINK-CAD",
  "DOT-CAD", "LTC-CAD",
  "BCH-CAD", "XLM-CAD", "UNI7083-CAD",
  "AAVE-CAD", "ATOM-CAD", "ETC-CAD",
  "FIL-CAD", "SHIB-CAD", "ALGO-CAD",
  "XTZ-CAD",
] as const;

export const MARKET_TICKER_SYMBOLS = [
  ...CAD_TICKER_SYMBOLS,
  ...US_TICKER_SYMBOLS,
  ...CRYPTO_TICKER_SYMBOLS,
] as const;

export const TICKER_REFRESH_BATCH_SIZE = 10;
