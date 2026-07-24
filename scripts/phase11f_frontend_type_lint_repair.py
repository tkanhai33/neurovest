#!/usr/bin/env python3
from pathlib import Path
import re

p = Path("frontend/app/page.tsx")
text = p.read_text()

# Ensure client + hooks import
if not text.startswith('"use client";'):
    text = '"use client";\n\n' + text

text = text.replace(
    'import { useState, useEffect } from "react";',
    'import { useCallback, useEffect, useState } from "react";'
)
text = text.replace(
    'import { useEffect, useState } from "react";',
    'import { useCallback, useEffect, useState } from "react";'
)

if 'type LiveQuote =' not in text:
    text = text.replace(
        'function LivePriceCard()',
        '''type LiveQuote = {
  status?: string;
  symbol?: string;
  price?: number | null;
  provider?: string;
  error?: string;
};

type AnalyticsSummary = {
  total_trades_logged?: number;
  buy_signals_count?: number;
  sell_signals_count?: number;
  execution_success_percentage?: number;
};

function LivePriceCard()'''
    )

text = text.replace('useState<any>(null)', 'useState<LiveQuote | null>(null)')

# Fix analytics never type
text = re.sub(
    r'const\s+\[analytics,\s*setAnalytics\]\s*=\s*useState\(null\)',
    'const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null)',
    text
)

# Convert LivePriceCard loadPrice function to useCallback
text = text.replace(
    '  async function loadPrice(nextSymbol = symbol) {',
    '  const loadPrice = useCallback(async (nextSymbol = symbol) => {'
)

text = text.replace(
    '''  }

  useEffect(() => {
    loadPrice(symbol);

    const timer = setInterval(() => {
      loadPrice(symbol);
    }, 30000);

    return () => clearInterval(timer);
  }, [symbol]);''',
    '''  }, [symbol]);

  useEffect(() => {
    const firstLoad = setTimeout(() => {
      void loadPrice(symbol);
    }, 0);

    const timer = setInterval(() => {
      void loadPrice(symbol);
    }, 30000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [loadPrice, symbol]);'''
)

# Fix older dashboard load() effect lint by deferring first call
text = text.replace(
    '''  useEffect(() => {
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);''',
    '''  useEffect(() => {
    const firstLoad = setTimeout(() => {
      void load();
    }, 0);

    const t = setInterval(() => {
      void load();
    }, 5000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(t);
    };
  }, []);'''
)

p.write_text(text)
print("patched Phase 11F frontend type/lint repair")
