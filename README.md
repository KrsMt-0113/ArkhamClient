# ArkhamClient — Arkham Intel API Python SDK

> 基于 [Arkham Intel API v1.1.0](https://intel.arkm.com/api/docs) 的完整 Python SDK，覆盖全部 80+ 个官方 API 端点。

## 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [认证方式](#认证方式)
- [API 方法一览](#api-方法一览)
  - [Intelligence — 情报查询](#intelligence--情报查询)
  - [Transfers & Swaps — 转账和交换](#transfers--swaps--转账和交换)
  - [Balances & Loans — 余额和借贷](#balances--loans--余额和借贷)
  - [Portfolio & History — 组合和历史](#portfolio--history--组合和历史)
  - [Counterparties, Flow & Volume — 交易对手/资金流/交易量](#counterparties-flow--volume--交易对手资金流交易量)
  - [Token — Token 数据](#token--token-数据)
  - [Tags & Clusters — 标签和聚类](#tags--clusters--标签和聚类)
  - [User — 用户管理](#user--用户管理)
  - [Market Data & Networks — 市场数据和网络](#market-data--networks--市场数据和网络)
  - [WebSocket — 实时推送](#websocket--实时推送)
  - [便捷方法](#便捷方法)
- [高级用法](#高级用法)
  - [分页查询](#分页查询)
  - [时间范围过滤](#时间范围过滤)
  - [from/to 特殊过滤语法](#fromto-特殊过滤语法)
  - [速率限制与重试](#速率限制与重试)
  - [自定义请求](#自定义请求)
- [Credit 消耗参考](#credit-消耗参考)
- [相关链接](#相关链接)

---

## 安装

本 SDK 仅依赖 `requests`：

```bash
pip install requests
```

将 `arkham_client.py` 放入你的项目目录即可使用。

---

## 快速开始

```python
from arkham_client import ArkhamClient

# 方式一：使用 API Key（推荐）
client = ArkhamClient(api_key="your-api-key")

# 方式二：使用邮箱密码登录
client = ArkhamClient(email="your@email.com", password="your-password")

# 查询地址情报
info = client.intelligence_address("0x28C6c06298d514Db089934071355E5743bf21d60")
print(info.get("arkhamEntity", {}).get("name"))  # → "Binance"

# 查询地址标签（便捷方法）
entity_name, label_name = client.tag("0x28C6c06298d514Db089934071355E5743bf21d60")
print(f"实体: {entity_name}, 标签: {label_name}")

# 获取支持的链列表
supported_chains = client.chains()
print(supported_chains)  # → ["ethereum", "bsc", "polygon", ...]

# 获取地址最近转账
txs = client.transfers(base="0x28C6c06298d514Db089934071355E5743bf21d60", timeLast="1h", limit=10)
for t in txs.get("transfers", []):
    print(f"  {t['chain']} | ${t.get('historicalUSD', 0):,.0f} | {t['tokenSymbol']}")
```

---

## 认证方式

### API Key 认证（推荐）

通过 [intel.arkm.com/settings](https://intel.arkm.com/settings) 生成 API Key，所有请求自动附带 `API-Key` 请求头：

```python
client = ArkhamClient(api_key="your-api-key")
```

### 邮箱密码登录

使用 Session Cookie 认证，首次调用任何 API 时会自动登录：

```python
client = ArkhamClient(email="your@email.com", password="your-password")

# 也可以手动登录
client.login()
```

---

## API 方法一览

### Intelligence — 情报查询

#### 地址情报

```python
# 获取单个地址情报
info = client.intelligence_address("0x1234...", chain="ethereum")

# 获取地址在所有链上的情报
info = client.intelligence_address_all("0x1234...")

# 获取增强情报（含标签、聚类、实体预测）
info = client.intelligence_address_enriched(
    "0x1234...",
    chain="ethereum",
    includeTags=True,
    includeClusters=True,
    includeEntityPredictions=True,
)

# 增强情报 - 所有链
info = client.intelligence_address_enriched_all(
    "0x1234...",
    includeTags=True,
)
```

#### 批量地址查询

```python
addresses = ["0xaaa...", "0xbbb...", "0xccc..."]

# 批量查询（最多 1000 个地址）
results = client.intelligence_address_batch(addresses, chain="ethereum")

# 批量查询 - 所有链
results = client.intelligence_address_batch_all(addresses)

# 批量增强查询
results = client.intelligence_address_enriched_batch(
    addresses, includeTags=True, includeClusters=True
)

# 批量增强查询 - 所有链
results = client.intelligence_address_enriched_batch_all(
    addresses, includeTags=True
)
```

#### 实体情报

```python
# 获取实体情报（如 "binance", "coinbase"）
entity = client.intelligence_entity("binance")

# 实体摘要统计（地址数、余额、交易量等）
summary = client.intelligence_entity_summary("binance")

# 实体预测（预测关联的地址）
predictions = client.intelligence_entity_predictions("binance")

# 实体余额变动
changes = client.intelligence_entity_balance_changes(
    chains="ethereum", entityTypes="cex"
)

# 获取所有实体类型
types = client.intelligence_entity_types()
```

#### 合约 & Token 情报

```python
# 合约情报
contract = client.intelligence_contract("ethereum", "0xdAC17F958D2ee523a2206206994597C13D831ec7")

# Token 情报 - 按 CoinGecko ID
token = client.intelligence_token_by_id("ethereum")

# Token 情报 - 按链和合约地址
token = client.intelligence_token_by_chain("ethereum", "0xdAC17F958D2ee523a2206206994597C13D831ec7")
```

#### 搜索

```python
# 搜索地址、实体和 Token
results = client.intelligence_search("binance")
```

#### 情报更新流（用于增量同步）

```python
# 获取地址情报更新（since 为 ISO 时间戳）
updates = client.intelligence_addresses_updates(since="2025-01-01T00:00:00Z")

# 获取实体情报更新
updates = client.intelligence_entities_updates(since="2025-01-01T00:00:00Z")

# 获取标签定义更新
updates = client.intelligence_tags_updates(since="2025-01-01T00:00:00Z")

# 获取地址-标签关联更新
updates = client.intelligence_address_tags_updates(since="2025-01-01T00:00:00Z")
```

---

### Transfers & Swaps — 转账和交换

#### 转账查询

```python
# 基本查询 - 获取某地址的转账
txs = client.transfers(base="0x1234...", limit=50)

# 带丰富过滤条件
txs = client.transfers(
    base="binance",           # 地址或实体
    chains="ethereum",        # 限定链
    flow="out",               # 方向: in/out/self/all
    tokens="ethereum",        # Token 过滤
    timeLast="24h",           # 最近 24 小时
    usdGte=100000,            # USD 最小值
    sortKey="usd",            # 排序字段: time/value/usd
    sortDir="desc",           # 排序方向: asc/desc
    limit=100,
    offset=0,
)

# 通过 from/to 过滤
txs = client.transfers(
    from_="binance",          # 注意：from 是 Python 关键字，用 from_ 代替
    to="0x1234...",
    timeLast="7d",
)

# 获取指定交易的转账记录
tx_transfers = client.transfers_tx("0xabcdef...", chain="ethereum")

# 获取交易详情
tx_detail = client.tx("0xabcdef...")
```

#### 转账直方图

```python
# 详细直方图（API Only，需要 API 计划）
histogram = client.transfers_histogram(base="binance", timeLast="30d")

# 简单直方图（Public）
histogram = client.transfers_histogram_simple(base="binance", timeLast="30d")
```

#### DEX 交换查询

```python
swaps = client.swaps(
    base="0x1234...",
    chains="ethereum",
    timeLast="24h",
    usdGte=10000,
    limit=50,
)
```

---

### Balances & Loans — 余额和借贷

```python
# 地址余额
balances = client.balances_address("0x1234...", chains="ethereum,bsc")

# 实体余额
balances = client.balances_entity("binance", chains="ethereum")

# 实体余额（快速模式，数据可能不完整）
balances = client.balances_entity("binance", cheap="true")

# Solana 子账户余额（质押、借贷等）
sol_balances = client.balances_solana_subaccounts_address(
    "SolanaAddr1,SolanaAddr2",
    pricingID="solana",
)
sol_balances = client.balances_solana_subaccounts_entity(
    "binance",
    pricingID="solana",
)

# 借贷仓位
loans = client.loans_address("0x1234...", chains="ethereum")
loans = client.loans_entity("aave", chains="ethereum")
```

---

### Portfolio & History — 组合和历史

```python
# 地址组合历史
portfolio = client.portfolio_address("0x1234...", time="2025-01-01", chains="ethereum")

# 实体组合历史
portfolio = client.portfolio_entity("binance", chains="ethereum")

# 每日时间序列（某个 Token 的持仓变化）
ts = client.portfolio_timeseries_address("0x1234...", pricingId="ethereum")
ts = client.portfolio_timeseries_entity("binance", pricingId="ethereum")

# 历史数据
history = client.history_address("0x1234...", chains="ethereum")
history = client.history_entity("binance", chains="ethereum")
```

---

### Counterparties, Flow & Volume — 交易对手/资金流/交易量

> ⚠️ `counterparties` 端点限速 1 请求/秒

```python
# 地址交易对手
cp = client.counterparties_address(
    "0x1234...",
    chains="ethereum",
    flow="all",          # in/out/self/all
    timeLast="30d",
    usdGte=10000,
    limit=100,
)

# 实体交易对手
cp = client.counterparties_entity("binance", timeLast="7d", limit=50)

# 历史 USD 资金流
flow = client.flow_address("0x1234...", chains="ethereum")
flow = client.flow_entity("binance", chains="ethereum")

# 转账量
vol = client.volume_address("0x1234...", chains="ethereum")
vol = client.volume_entity("binance", chains="ethereum")
```

---

### Token — Token 数据

#### 排行与趋势

```python
# 交易所活跃度最高的 Token
top = client.token_top(timeframe="24h", orderByDesc=True)

# 趋势 Token
trending = client.token_trending()

# 单个趋势 Token
token = client.token_trending_by_id("ethereum")
```

#### 持有者

```python
# 按 CoinGecko pricing ID 查询持有者
holders = client.token_holders_by_id("ethereum", groupByEntity=True)

# 按链和合约地址查询持有者
holders = client.token_holders_by_chain(
    "ethereum",
    "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    groupByEntity=True,
)
```

#### 资金流 & 交易量

```python
# Token 最大资金流
flow = client.token_top_flow_by_id("ethereum", timeLast="24h")
flow = client.token_top_flow_by_chain("ethereum", "0x1234...", timeLast="7d")

# Token 交易量
vol = client.token_volume_by_id("ethereum", timeLast="24h", granularity="1h")
vol = client.token_volume_by_chain("ethereum", "0x1234...", timeLast="7d")
```

#### 余额

```python
# 按 pricing ID 获取某实体/地址的 Token 余额（所有链）
bal = client.token_balance_by_id("ethereum", entityID="binance")
bal = client.token_balance_by_id("ethereum", address="0x1234...")

# 按链和地址获取 Token 余额
bal = client.token_balance_by_chain("ethereum", "0xdAC17...", entityID="binance")
```

#### 价格 & 市场

```python
# 当前市场数据
market = client.token_market("ethereum")

# 价格历史
prices = client.token_price_history_by_id("ethereum", daily=True)
prices = client.token_price_history_by_chain("ethereum", "0x1234...", daily=True)

# 价格变化（自指定时间戳以来）
change = client.token_price_change("ethereum", pastTime="1706745600000")
```

#### 其他

```python
# Token 在各链上的合约地址
addresses = client.token_addresses("ethereum")

# Arkham 交易所支持的 Token
tokens = client.token_arkham_exchange_tokens()
```

---

### Tags & Clusters — 标签和聚类

```python
# 标签参数（标签下的地址列表）
params = client.tag_params("cex", limit=100, offset=0)

# 标签摘要统计
summary = client.tag_summary("cex")

# 聚类摘要统计（地址数、余额、交易量等）
summary = client.cluster_summary("cluster-id-here")
```

---

### User — 用户管理

```python
# 获取当前用户信息
profile = client.user_profile()

# 获取用户告警
alerts = client.user_alerts()

# 获取用户自定义标签
labels = client.user_labels()

# 创建标签
client.user_labels_create([
    {
        "address": "0x1234...",
        "chainType": "ethereum",
        "name": "我的钱包",
        "note": "主要交易钱包",
    }
])

# 获取私有实体列表
entities = client.user_entities(includeAddresses=True)

# 获取单个私有实体
entity = client.user_entity("my-entity-id")

# 更新私有实体（添加地址等）
client.user_entity_update("my-entity-id", {
    "id": "my-entity-id",
    "name": "My Entity",
    "note": "Updated entity",
    "type": "custom",
    "service": False,
    "addresses": {
        "ethereum": ["0xaaa...", "0xbbb..."],
    },
})
```

---

### Market Data & Networks — 市场数据和网络

```python
# Altcoin 指数
index = client.marketdata_altcoin_index()

# 所有区块链网络状态
status = client.networks_status()

# 单个链的历史数据
history = client.networks_history("ethereum")

# 支持的链列表（免费，不消耗 Credit）
chains = client.chains()

# ARKM 流通供应量（免费）
supply = client.arkm_circulating()
```

---

### WebSocket — 实时推送

SDK 提供 WebSocket 会话的 REST 管理接口。实际 WebSocket 连接需要使用 `websockets` 库。

```python
# 获取 WebSocket 定价信息
info = client.ws_session_info()

# 创建 WebSocket 会话
session = client.ws_session_create()
session_id = session["sessionId"]

# 列出所有会话
sessions = client.ws_sessions()

# 查看会话状态
status = client.ws_session_status(session_id)

# 获取活跃连接数
connections = client.ws_active_connections()

# 删除会话
client.ws_session_delete(session_id)
```

#### 使用 websockets 库连接实时推送

```python
import asyncio
import json
import websockets

async def stream_transfers(api_key: str):
    """实时接收 CEX 大额转账"""
    url = "wss://api.arkm.com/ws/transfers"
    headers = {"API-Key": api_key}

    async with websockets.connect(url, additional_headers=headers) as ws:
        # 订阅过滤条件
        await ws.send(json.dumps({
            "id": "1",
            "type": "subscribe",
            "payload": {
                "filters": {
                    "from": ["type:cex"],
                    "usdGte": 10000,
                }
            }
        }))

        # 等待确认
        ack = await ws.recv()
        print("已订阅:", json.loads(ack))

        # 接收推送
        async for message in ws:
            data = json.loads(message)
            if data.get("type") == "transfer":
                t = data["payload"]["transfer"]
                print(f"${t['historicalUSD']:,.0f} {t['tokenSymbol']} on {t['chain']}")

# asyncio.run(stream_transfers("your-api-key"))
```

> **WebSocket 过滤要求**：必须包含 `from`、`to`、`tokens` 中至少一个，或者 `usdGte >= 10,000,000`。

---

### 便捷方法

```python
# 快速查询地址标签 → 返回 (entity_name, label_name)
entity_name, label_name = client.tag("0x1234...")
# 例: ("Binance", "Hot Wallet 6") 或 (None, None)

# 向后兼容的旧接口别名
client.address_balances("0x1234...")        # → balances_address()
client.address_transfers("0x1234...", 20)   # → transfers(base=..., limit=20)
client.address_intelligence("0x1234...")    # → intelligence_address()
```

---

## 高级用法

### 分页查询

API 使用 `limit` + `offset` 分页：

```python
all_transfers = []
offset = 0

while True:
    resp = client.transfers(base="binance", timeLast="24h", limit=50, offset=offset)
    batch = resp.get("transfers", [])
    all_transfers.extend(batch)

    if len(batch) < 50:
        break
    offset += 50

print(f"共获取 {len(all_transfers)} 条转账")
```

#### 时间窗口滑动分页（适合频繁变动的数据）

```python
from datetime import datetime, timedelta

window_end = datetime.utcnow()
window_size = timedelta(hours=1)
all_results = []

while window_end > earliest_date:
    window_start = window_end - window_size
    resp = client.transfers(
        base="binance",
        timeGte=str(int(window_start.timestamp() * 1000)),
        timeLte=str(int(window_end.timestamp() * 1000)),
        limit=500,
    )
    all_results.extend(resp.get("transfers", []))
    window_end = window_start
```

---

### 时间范围过滤

三种方式（互斥，不能混用）：

```python
# 1. 相对时间
client.transfers(base="binance", timeLast="24h")   # 最近 24 小时
client.transfers(base="binance", timeLast="7d")     # 最近 7 天
client.transfers(base="binance", timeLast="1M")     # 最近 1 个月

# 2. 绝对时间戳（毫秒）
client.transfers(
    base="binance",
    timeGte="1696630274000",    # 起始时间
    timeLte="1696716674000",    # 结束时间
)

# 3. 排序
client.transfers(base="binance", sortKey="usd", sortDir="desc", timeLast="24h")
```

> ⚠️ `timeLast` 不能与 `timeGte`/`timeLte` 同时使用，否则返回 HTTP 400。

---

### from/to 特殊过滤语法

`transfers`、`counterparties`、`swaps` 等端点的 `from`/`to` 参数支持特殊语法：

```python
# 按实体类型过滤
client.transfers(from_="type:cex", timeLast="1h", limit=10)

# 按存款地址过滤
client.transfers(to="deposit:binance", timeLast="1h", limit=10)

# 多个过滤条件（逗号分隔）
client.transfers(from_="binance,coinbase", timeLast="24h", limit=50)
```

> **注意**：Python 中 `from` 是关键字，SDK 支持使用 `from_`（末尾加下划线），会自动映射为 `from` 参数。

---

### 速率限制与重试

| 端点类型 | 限速 |
|---------|------|
| 标准端点 | 20 请求/秒 |
| 重量级端点（transfers, counterparties, swaps 等） | 1 请求/秒 |

```python
import time
import random

def request_with_backoff(func, *args, max_retries=5, **kwargs):
    """带指数退避的重试"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("Retry-After", 2 ** attempt))
                jitter = random.uniform(0, 1)
                time.sleep(retry_after + jitter)
                continue
            raise
    raise Exception("超过最大重试次数")

# 使用示例
result = request_with_backoff(
    client.transfers,
    base="binance",
    timeLast="24h",
    limit=50,
)
```

---

### 自定义请求

如果 SDK 没有封装某个端点，可以直接使用底层方法：

```python
# GET 请求
resp = client.get("/some/new/endpoint", params={"key": "value"})
data = resp.json()

# POST 请求
resp = client.post("/some/new/endpoint", json={"key": "value"})
data = resp.json()

# PUT 请求
resp = client.put("/some/endpoint", json={...})

# DELETE 请求
resp = client.delete("/some/endpoint")
```

---

## Credit 消耗参考

每个 API 请求消耗 Credit，不同端点消耗不同。失败请求（4xx/5xx）不计费。

| 分类 | 端点 | Credit | 计费方式 |
|------|------|--------|---------|
| **免费** | `/chains`, `/networks/status`, `/arkm/circulating` | 0 | — |
| **Intelligence** | `/intelligence/address/{address}` | 1 | 每次调用 |
| | `/intelligence/address/{address}/all` | 2 | 每次调用 |
| | `/intelligence/address_enriched/{address}` | 2 | 每次调用 |
| | `/intelligence/address_enriched/{address}/all` | 4 | 每次调用 |
| | `POST /intelligence/address/batch` | 250 | 每次调用 |
| | `POST /intelligence/address_enriched/batch/all` | 1000 | 每次调用 |
| | `/intelligence/search` | 30 | 每次调用 |
| **Transfers** | `/transfers` | 2 | **每条记录** |
| | `/swaps` | 2 | **每条记录** |
| **Token** | `/token/holders/{id}` | 30 | 每次调用 |
| | `/token/top` | 10 | 每次调用 |
| **Counterparties** | `/counterparties/address/{address}` | 50 | 每次调用 |
| **WebSocket** | `POST /ws/sessions` | 500 | 每次调用 |

> ⚠️ `/transfers` 和 `/swaps` 按返回记录数计费！例如返回 50 条转账 = 50 × 2 = 100 Credit。请合理使用 `limit` 参数。

完整定价表请参考 [官方文档](https://intel.arkm.com/api/docs)。

---

## 相关链接

| 资源 | 链接 |
|------|------|
| API 文档 | https://intel.arkm.com/api/docs |
| OpenAPI Spec | https://intel.arkm.com/openapi.json |
| LLM 友好文档 | https://intel.arkm.com/llms-full.txt |
| 申请 API 访问 | https://intel.arkm.com/api |
| API Key 管理 | https://intel.arkm.com/settings |
| 技术支持 | api@arkm.com |
