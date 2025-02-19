def recommendation_message(best_pool, pools_text, tokens_info):
    return f"""
🏆 *Investment pools found:*

{pools_text}

📊 *Best pool details:*
• Protocol: `{best_pool['protocol_name']}`
• APY: `{best_pool['apy']:.2f}%`
• Type: `{best_pool['type']}`
• Pool address: `{best_pool['token_address']}`
• Contract: `{best_pool['primary_address']}`

💰 *Pool tokens:*
{tokens_info}

💡 _Safety conditions:_
• Realistic APY (0.1% - 100%)
• All tokens have current price
• Active trading volume
• Regular price updates
"""
