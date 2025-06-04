async def build_message(data):
    """{
    "token_address": "J94jBu9K2zaMhuwjGAFmjzpj25LYGQmSNvsrcdzwpump",
    "creation_time": "2025-03-21 13:23:22.167850",
    "dex_tools_data": "base_coin_id=1 id=1 data={'address': 'J94jBu9K2zaMhuwjGAFmjzpj25LYGQmSNvsrcdzwpump', 'exchange': {'name': 'Pump.fun', 'factory': '6ef8rrecthr5dkzon8nwu78hrvfckubj14m5ubewf6p'}, 'mainToken': {'name': 'Stay Hydrated', 'symbol': 'Dalí', 'address': 'J94jBu9K2zaMhuwjGAFmjzpj25LYGQmSNvsrcdzwpump'}, 'sideToken': {'name': 'Wrapped SOL', 'symbol': 'SOL', 'address': 'So11111111111111111111111111111111111111112'}, 'creationTime': '2025-03-21T12:22:23.056Z', 'creationBlock': 328215952} updated_at=datetime.datetime(2025, 3, 21, 13, 23, 22, 173386)",
    "rug_check_data": {
    "mint": "J94jBu9K2zaMhuwjGAFmjzpj25LYGQmSNvsrcdzwpump",
    "tokenProgram": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "creator": "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM",
    "token": {
      "mintAuthority": null,
      "supply": 1000000000000000,
      "decimals": 6,
      "isInitialized": true,
      "freezeAuthority": null
    },
    "token_extensions": null,
    "tokenMeta": {
      "name": "Stay Hydrated",
      "symbol": "Dalí",
      "uri": "https://ipfs.io/ipfs/QmfRGPSLepMKCzNogYhEH75si2XKZVRGvRbQxfDwecKRKp",
      "mutable": false,
      "updateAuthority": "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM"
    },
    "topHolders": [
      {
        "address": "77wYiKUN68i5pGFGYocVHouXyzAYQcx5yhodZS2DLFnq",
        "amount": 965387096774194,
        "decimals": 6,
        "pct": 96.5387096774194,
        "uiAmount": 965387096.774194,
        "uiAmountString": "965387096.774194",
        "owner": "9G6HaM5uyjWvEPVjHwTvKeNokfycQ1o3YSbBAUJ4rjBD",
        "insider": false
      },
      {
        "address": "7NkVpnWszoL6sB9CPAaBTVbv26AK3bSx2aTq9vPAVYu",
        "amount": 34612903225806,
        "decimals": 6,
        "pct": 3.4612903225806,
        "uiAmount": 34612903.225806,
        "uiAmountString": "34612903.225806",
        "owner": "Ftd26h3Mda2EBsmSu9onWRxw6dVe96YQShH6JxNMzb6k",
        "insider": false
      },
      {
        "address": "B8wbGqmSF6U3d7iXndaLyunU37RJYFg8QhTdPQKNAwjX",
        "amount": 0,
        "decimals": 6,
        "pct": 0,
        "uiAmount": 0,
        "uiAmountString": "0",
        "owner": "6nhfhL3GvpZKVmwm9ji9J6RPTDRuXPD4V77i8JtkYb4y",
        "insider": false
      }
    ],
    "freezeAuthority": null,
    "mintAuthority": null,
    "risks": [],
    "score": 1,
    "score_normalised": 1,
    "fileMeta": {
      "description": "",
      "name": "Stay Hydrated",
      "symbol": "Dalí",
      "image": "https://ipfs.io/ipfs/QmeQLYxP8F5r5JYkdLyidTPZN8kN33xb2vV8GiyWMY7h59"
    },
    "lockerOwners": {},
    "lockers": {},
    "markets": [
      {
        "pubkey": "9G6HaM5u
    yjWvEPVjHwTvKeNokfycQ1o3YSbBAUJ4rjBD",
        "marketType": "pump_fun",
        "mintA": "J94jBu9K2zaMhuwjGAFmjzpj25LYGQmSNvsrcdzwpump",
        "mintB": "So11111111111111111111111111111111111111112",
        "mintLP": "11111111111111111111111111111111",
        "liquidityA": "77wYiKUN68i5pGFGYocVHouXyzAYQcx5yhodZS2DLFnq",
        "liquidityB": "9G6HaM5uyjWvEPVjHwTvKeNokfycQ1o3YSbBAUJ4rjBD",
        "mintAAccount": {
          "mintAuthority": null,
          "supply": 1000000000000000,
          "decimals": 6,
          "isInitialized": true,
          "freezeAuthority": null
        },
        "mintBAccount": {
          "mintAuthority": null,
          "supply": 0,
          "decimals": 9,
          "isInitialized": false,
          "freezeAuthority": null
        },
        "mintLPAccount": {
          "mintAuthority": null,
          "supply": 0,
          "decimals": 0,
          "isInitialized": false,
          "freezeAuthority": null
        },
        "liquidityAAccount": {
          "mint": "J94jBu9K2zaMhuwjGAFmjzpj25LYGQmSNvsrcdzwpump",
          "owner": "9G6HaM5uyjWvEPVjHwTvKeNokfycQ1o3YSbBAUJ4rjBD",
          "amount": 758487096774194,
          "delegate": null,
          "state": 0,
          "delegatedAmount": 0,
          "closeAuthority": null
        },
        "liquidityBAccount": {
          "mint": "So11111111111111111111111111111111111111112",
          "owner": "9G6HaM5uyjWvEPVjHwTvKeNokfycQ1o3YSbBAUJ4rjBD",
          "amount": 1000000002,
          "delegate": null,
          "state": 0,
          "delegatedAmount": 0,
          "closeAuthority": null
        },
        "lp": {
          "baseMint": "J94jBu9K2zaMhuwjGAFmjzpj25LYGQmSNvsrcdzwpump",
          "quoteMint": "So11111111111111111111111111111111111111112",
          "lpMint": "11111111111111111111111111111111",
          "quotePrice": 126.75685119162561,
          "basePrice": 3.788087962983359e-06,
          "base": 758487096.774194,
          "quote": 1.000000002,
          "reserveSupply": 1000000002,
          "currentSupply": 0,
          "quoteUSD": 126.7568514451393,
          "baseUSD": 2873.2158413685183,
          "pctReserve": 0,
          "pctSupply": 0,
          "holders": null,
          "totalTokensUnlocked": 0,
          "tokenSupply": 0,
          "lpLocked": 1000000002,
          "lpUnlocked": 0,
          "lpLockedPct": 100,
          "lpLockedUSD": 2999.9726928136574,
          "lpMaxSupply": 0,
          "lpCurrentSupply": 0,
          "lpTotalSupply": 1000000002
        }
      }
    ],
    "totalMarketLiquidity": 2999.9726928136574,
    "totalLPProviders": 0,
    "totalHolders": 1,
    "price": 3.788087962983359e-06,
    "rugged": false,
    "tokenType": "",
    "transferFee": {
      "pct": 0,
      "maxAmount": 0,
      "authority": "11111111111111111111111111111111"
    },
    "knownAccounts": {
      "77wYiKUN68i5pGFGYocVHouXyzAYQcx5yhodZS2DLFnq": {
        "name": "Pump Fun",
        "type": "AMM"
      },
      "9G6HaM5uyjWvEPVjHwTvKeNokfycQ1o3YSbBAUJ4rjBD": {
        "name": "Pump Fun",
        "type": "AMM"
      },
      "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM": {
        "name": "Creator",
        "type": "CREATOR"
      }
    },
    "events": [],
    "verification": null,
    "graphInsidersDetected": 0,
    "insiderNetworks": null,
    "detectedAt": "2025-03-21T12:22:21.724164989Z",
    "creatorTokens": null
    }
    }

    """
    rug_check_data = data.get("rug_check_data", {})
    if not rug_check_data:
        return "No rug check data available."

    token_meta = rug_check_data.get("tokenMeta", {})
    name = token_meta.get("name", "Unknown")
    symbol = token_meta.get("symbol", "Unknown")
    contract = rug_check_data.get("mint", "Unknown")
    creator = rug_check_data.get("creator", "Unknown")
    if creator is None:
        creator = "Unknown"
    price = rug_check_data.get("price", 0)
    market_cap = rug_check_data.get("totalMarketLiquidity", 0)

    top_holders = rug_check_data.get("topHolders", [])

    risks = rug_check_data.get("risks", [])
    risk_info = (
        "\n".join([f"⚠️ {risk['name']}: {risk['description']}" for risk in risks]) if risks else "No risks detected."
    )

    transfer_fee = rug_check_data.get("transferFee", {}).get("pct", 0)
    img = rug_check_data.get("fileMeta", {}).get("image", "")
    rugged = "🟢 No" if not rug_check_data.get("rugged", False) else "🔴 Yes"
    score_normalised = rug_check_data.get("score_normalised", 0)
    score_levels = {
        20: "🟢",  # Зеленый
        40: "🟡",  # Желтый
        60: "🟠",  # Оранжевый
        80: "🔴",  # Красный
    }

    emoji = next((emoji for threshold, emoji in score_levels.items() if score_normalised < threshold), "🔴")

    score_normalised = f"{emoji} {score_normalised}"
    message = f"""
📊 **{name} ({symbol})**
💰 **Price:** {price:.10f} USD
🏦 **Market Cap:** {market_cap:,.2f} USD

🛠 **Token Info:**
    ├ 🏦 **Contract:** {await build_sol_scan_links(contract)}
    ├ 👤 **Creator:** {await build_sol_scan_links(creator)}
    ├ 🔝 **Top Holders:** {await sort_holders(top_holders)}

🔎 **Security Check:**
    ├ ⚠️ **Rug Check:** {rugged}
    ├ 💸 **Transfer Fee:** {transfer_fee}%
    ├ 📊 **Score:** {score_normalised}
    ├ 🏛️ **Risks:**{risk_info}

[Dextools](https://www.dextools.io/app/solana/pair-explorer/{contract}) | [RugCheck](https://rugcheck.xyz/tokens/{contract}) | [DexScreener](https://dexscreener.com/solana/{contract})
"""

    return message, img


async def cut_string(string: str, start: int = 5, end: int = 5):
    if len(string) <= start + end:
        return string
    return string[:start] + "..." + string[-end:]


async def build_sol_scan_links(address):
    return f"[{await cut_string(address)}](https://solscan.io/account/{address})"


async def sort_holders(holders):
    # holders_info = "\n".join(
    #     [f"- `{holder['address']}` ({holder['pct']:.2f}%)" for holder in top_holders]
    # )
    if holders:
        holder_msg = ""
        for holder in holders:
            if float(holder["pct"]) > 1:
                holder_msg += f"\n- {await build_sol_scan_links(holder['address'])} ({holder['pct']:.2f}%)"
    else:
        holder_msg = "No holders detected."

    return holder_msg
