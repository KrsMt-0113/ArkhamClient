"""
ArkhamClient — Arkham Intel API 完整 Python SDK

支持两种认证方式：
  1. API Key 认证（推荐）：
     client = ArkhamClient(api_key="your-api-key")
  2. 邮箱密码登录（Session Cookie 认证）：
     client = ArkhamClient(email="...", password="...")

API 文档：https://intel.arkm.com/api/docs
OpenAPI Spec：https://intel.arkm.com/openapi.json
Base URL：https://api.arkm.com

涵盖全部官方 API 端点（v1.1.0），包括：
  - Intelligence（地址/实体/合约/Token 情报）
  - Transfers & Swaps（转账/交换记录）
  - Balances & Loans（余额/借贷）
  - Portfolio & History（组合/历史）
  - Counterparties & Flow & Volume（交易对手/资金流/交易量）
  - Token（Token 数据/持有者/价格/趋势）
  - Tags & Clusters（标签/聚类）
  - User（用户标签/私有实体）
  - Market Data & Networks（市场数据/网络状态）
  - WebSocket（实时推送）
  - Misc（ARKM 供应量/链列表）
"""

from __future__ import annotations

from typing import Any

import requests


class ArkhamClient:
    LOGIN_URL = "https://arkm.com/api/auth/login"
    AUTH_URL = "https://api.arkm.com/authenticate"
    BASE_API = "https://api.arkm.com"

    def __init__(
        self,
        api_key: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ):
        self.api_key = api_key
        self.email = email
        self.password = password
        self.session = requests.Session()
        headers: dict[str, str] = {
            "Accept": "application/json, text/plain, */*",
        }
        if api_key:
            headers["API-Key"] = api_key
        else:
            headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/133.0.0.0 Safari/537.36"
                ),
                "Origin": "https://intel.arkm.com",
                "Referer": "https://intel.arkm.com/",
            })
        self.session.headers.update(headers)
        self._logged_in = bool(api_key)

    # ── 通用请求方法 ──────────────────────────────────────────

    def login(self) -> dict:
        """邮箱密码登录并交换 token，返回登录响应 JSON"""
        if not self.email or not self.password:
            raise RuntimeError("需要提供 email 和 password 才能登录")
        login_resp = self.session.post(self.LOGIN_URL, json={
            "email": self.email,
            "password": self.password,
            "redirectDomain": "https://intel.arkm.com",
            "redirectPath": "/",
            "turnstile": "",
            "invisibleTurnstile": "",
        })
        login_resp.raise_for_status()
        data = login_resp.json()
        token = data.get("tradeInToken")
        if not token:
            raise RuntimeError(
                f"登录未返回 tradeInToken (requireMFA={data.get('requireMFA')})"
            )
        auth_resp = self.session.post(self.AUTH_URL, json={
            "tradeInToken": token,
            "redirectPath": "/",
        })
        auth_resp.raise_for_status()
        self._logged_in = True
        return data

    def get(self, path: str, **kwargs) -> requests.Response:
        """GET api.arkm.com/{path}"""
        self._ensure_login()
        return self.session.get(self._url(path), **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        """POST api.arkm.com/{path}"""
        self._ensure_login()
        return self.session.post(self._url(path), **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        """PUT api.arkm.com/{path}"""
        self._ensure_login()
        return self.session.put(self._url(path), **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        """DELETE api.arkm.com/{path}"""
        self._ensure_login()
        return self.session.delete(self._url(path), **kwargs)

    # ══════════════════════════════════════════════════════════
    #  Intelligence — 地址/实体/合约/Token 情报
    # ══════════════════════════════════════════════════════════

    def intelligence_address(self, address: str, *, chain: str | None = None) -> dict:
        """GET /intelligence/address/{address} — 获取地址情报"""
        params = self._clean(chain=chain)
        return self.get(f"/intelligence/address/{address}", params=params).json()

    def intelligence_address_all(self, address: str) -> dict:
        """GET /intelligence/address/{address}/all — 获取地址在所有链上的情报"""
        return self.get(f"/intelligence/address/{address}/all").json()

    def intelligence_address_enriched(
        self, address: str, *, chain: str | None = None,
        includeTags: bool | None = None, includeClusters: bool | None = None,
        includeEntityPredictions: bool | None = None,
    ) -> dict:
        """GET /intelligence/address_enriched/{address} — 获取地址增强情报"""
        params = self._clean(
            chain=chain, includeTags=includeTags, includeClusters=includeClusters,
            includeEntityPredictions=includeEntityPredictions,
        )
        return self.get(f"/intelligence/address_enriched/{address}", params=params).json()

    def intelligence_address_enriched_all(
        self, address: str, *, includeTags: bool | None = None,
        includeClusters: bool | None = None, includeEntityPredictions: bool | None = None,
    ) -> dict:
        """GET /intelligence/address_enriched/{address}/all — 获取地址在所有链上的增强情报"""
        params = self._clean(
            includeTags=includeTags, includeClusters=includeClusters,
            includeEntityPredictions=includeEntityPredictions,
        )
        return self.get(f"/intelligence/address_enriched/{address}/all", params=params).json()

    def intelligence_address_batch(
        self, addresses: list[str], *, chains: str | None = None, chain: str | None = None,
    ) -> dict:
        """POST /intelligence/address/batch — 批量查询地址情报（最多 1000 个）"""
        params = self._clean(chains=chains, chain=chain)
        return self.post("/intelligence/address/batch", json={"addresses": addresses}, params=params).json()

    def intelligence_address_batch_all(
        self, addresses: list[str], *, chains: str | None = None, chain: str | None = None,
    ) -> dict:
        """POST /intelligence/address/batch/all — 批量查询地址在所有链上的情报"""
        params = self._clean(chains=chains, chain=chain)
        return self.post("/intelligence/address/batch/all", json={"addresses": addresses}, params=params).json()

    def intelligence_address_enriched_batch(
        self, addresses: list[str], *, chains: str | None = None,
        includeTags: bool | None = None, includeClusters: bool | None = None,
        includeEntityPredictions: bool | None = None,
    ) -> dict:
        """POST /intelligence/address_enriched/batch — 批量查询地址增强情报"""
        params = self._clean(
            chains=chains, includeTags=includeTags, includeClusters=includeClusters,
            includeEntityPredictions=includeEntityPredictions,
        )
        return self.post("/intelligence/address_enriched/batch", json={"addresses": addresses}, params=params).json()

    def intelligence_address_enriched_batch_all(
        self, addresses: list[str], *, chains: str | None = None,
        includeTags: bool | None = None, includeClusters: bool | None = None,
        includeEntityPredictions: bool | None = None,
    ) -> dict:
        """POST /intelligence/address_enriched/batch/all — 批量查询地址在所有链上的增强情报"""
        params = self._clean(
            chains=chains, includeTags=includeTags, includeClusters=includeClusters,
            includeEntityPredictions=includeEntityPredictions,
        )
        return self.post("/intelligence/address_enriched/batch/all", json={"addresses": addresses}, params=params).json()

    def intelligence_entity(self, entity: str) -> dict:
        """GET /intelligence/entity/{entity} — 获取实体情报"""
        return self.get(f"/intelligence/entity/{entity}").json()

    def intelligence_entity_summary(self, entity: str) -> dict:
        """GET /intelligence/entity/{entity}/summary — 获取实体摘要统计"""
        return self.get(f"/intelligence/entity/{entity}/summary").json()

    def intelligence_entity_predictions(self, entity: str) -> dict:
        """GET /intelligence/entity_predictions/{entity} — 获取实体预测"""
        return self.get(f"/intelligence/entity_predictions/{entity}").json()

    def intelligence_entity_balance_changes(
        self, *, chains: str | None = None, entityTypes: str | None = None,
        entityIds: str | None = None, entityTags: str | None = None,
    ) -> dict:
        """GET /intelligence/entity_balance_changes — 获取实体余额变动"""
        params = self._clean(chains=chains, entityTypes=entityTypes, entityIds=entityIds, entityTags=entityTags)
        return self.get("/intelligence/entity_balance_changes", params=params).json()

    def intelligence_entity_types(self) -> list:
        """GET /intelligence/entity_types — 获取所有实体类型"""
        return self.get("/intelligence/entity_types").json()

    def intelligence_contract(self, chain: str, address: str) -> dict:
        """GET /intelligence/contract/{chain}/{address} — 获取合约情报"""
        return self.get(f"/intelligence/contract/{chain}/{address}").json()

    def intelligence_token_by_id(self, token_id: str) -> dict:
        """GET /intelligence/token/{id} — 按 CoinGecko ID 获取 Token 情报"""
        return self.get(f"/intelligence/token/{token_id}").json()

    def intelligence_token_by_chain(self, chain: str, address: str) -> dict:
        """GET /intelligence/token/{chain}/{address} — 按链和地址获取 Token 情报"""
        return self.get(f"/intelligence/token/{chain}/{address}").json()

    def intelligence_search(self, query: str, *, filterLimits: str | None = None) -> dict:
        """GET /intelligence/search — 搜索地址、实体和 Token"""
        params = self._clean(query=query, filterLimits=filterLimits)
        return self.get("/intelligence/search", params=params).json()

    # ── Intelligence 更新流 ───────────────────────────────────

    def intelligence_addresses_updates(self, *, since: str | None = None, **kwargs) -> dict:
        """GET /intelligence/addresses/updates — 获取地址情报更新"""
        params = self._clean(since=since, **kwargs)
        return self.get("/intelligence/addresses/updates", params=params).json()

    def intelligence_entities_updates(self, *, since: str | None = None, **kwargs) -> dict:
        """GET /intelligence/entities/updates — 获取实体情报更新"""
        params = self._clean(since=since, **kwargs)
        return self.get("/intelligence/entities/updates", params=params).json()

    def intelligence_tags_updates(self, *, since: str | None = None, **kwargs) -> dict:
        """GET /intelligence/tags/updates — 获取标签定义更新"""
        params = self._clean(since=since, **kwargs)
        return self.get("/intelligence/tags/updates", params=params).json()

    def intelligence_address_tags_updates(self, *, since: str | None = None, **kwargs) -> dict:
        """GET /intelligence/address_tags/updates — 获取地址-标签关联更新"""
        params = self._clean(since=since, **kwargs)
        return self.get("/intelligence/address_tags/updates", params=params).json()

    # ══════════════════════════════════════════════════════════
    #  Transfers & Swaps — 转账和交换
    # ══════════════════════════════════════════════════════════

    def transfers(self, *, base: str | None = None, chains: str | None = None,
                  flow: str | None = None, limit: int | None = None,
                  offset: int | None = None, **kwargs) -> dict:
        """GET /transfers — 获取转账记录

        常用参数：base, chains, flow, from_, to, tokens, timeGte, timeLte,
        timeLast, usdGte, usdLte, sortKey, sortDir, limit, offset, counterparties
        """
        params = self._clean(base=base, chains=chains, flow=flow, limit=limit, offset=offset, **kwargs)
        return self.get("/transfers", params=params).json()

    def transfers_tx(self, tx_hash: str, *, transferType: str | None = None,
                     chain: str | None = None) -> dict:
        """GET /transfers/tx/{hash} — 获取指定交易的转账记录"""
        params = self._clean(transferType=transferType, chain=chain)
        return self.get(f"/transfers/tx/{tx_hash}", params=params).json()

    def transfers_histogram(self, *, base: str | None = None, chains: str | None = None,
                            flow: str | None = None, **kwargs) -> dict:
        """GET /transfers/histogram — 获取转账详细直方图（API Only）"""
        params = self._clean(base=base, chains=chains, flow=flow, **kwargs)
        return self.get("/transfers/histogram", params=params).json()

    def transfers_histogram_simple(self, *, base: str | None = None, chains: str | None = None,
                                   flow: str | None = None, **kwargs) -> dict:
        """GET /transfers/histogram/simple — 获取转账简单直方图（Public）"""
        params = self._clean(base=base, chains=chains, flow=flow, **kwargs)
        return self.get("/transfers/histogram/simple", params=params).json()

    def tx(self, tx_hash: str) -> dict:
        """GET /tx/{hash} — 获取交易详情"""
        return self.get(f"/tx/{tx_hash}").json()

    def swaps(self, *, base: str | None = None, chains: str | None = None,
              flow: str | None = None, limit: int | None = None,
              offset: int | None = None, **kwargs) -> dict:
        """GET /swaps — 获取 DEX 交换记录

        常用参数：base, chains, flow, tokens, from_, to, timeGte, timeLte,
        timeLast, usdGte, usdLte, sortKey, sortDir, limit, offset,
        counterparties, senders, receivers, protocols
        """
        params = self._clean(base=base, chains=chains, flow=flow, limit=limit, offset=offset, **kwargs)
        return self.get("/swaps", params=params).json()

    # ══════════════════════════════════════════════════════════
    #  Balances & Loans — 余额和借贷
    # ══════════════════════════════════════════════════════════

    def balances_address(self, address: str, *, chains: str | None = None) -> dict:
        """GET /balances/address/{address} — 获取地址 Token 余额"""
        params = self._clean(chains=chains)
        return self.get(f"/balances/address/{address}", params=params).json()

    def balances_entity(self, entity: str, *, chains: str | None = None,
                        cheap: str | None = None) -> dict:
        """GET /balances/entity/{entity} — 获取实体 Token 余额"""
        params = self._clean(chains=chains, cheap=cheap)
        return self.get(f"/balances/entity/{entity}", params=params).json()

    def balances_solana_subaccounts_address(
        self, addresses: str, *, pricingID: str | None = None, limit: int | None = None,
    ) -> list:
        """GET /balances/solana/subaccounts/address/{addresses} — 获取 Solana 子账户地址余额"""
        params = self._clean(pricingID=pricingID, limit=limit)
        return self.get(f"/balances/solana/subaccounts/address/{addresses}", params=params).json()

    def balances_solana_subaccounts_entity(
        self, entities: str, *, pricingID: str | None = None, limit: int | None = None,
    ) -> list:
        """GET /balances/solana/subaccounts/entity/{entities} — 获取 Solana 子账户实体余额"""
        params = self._clean(pricingID=pricingID, limit=limit)
        return self.get(f"/balances/solana/subaccounts/entity/{entities}", params=params).json()

    def loans_address(self, address: str, *, chains: str | None = None) -> dict:
        """GET /loans/address/{address} — 获取地址借贷仓位"""
        params = self._clean(chains=chains)
        return self.get(f"/loans/address/{address}", params=params).json()

    def loans_entity(self, entity: str, *, chains: str | None = None) -> dict:
        """GET /loans/entity/{entity} — 获取实体借贷仓位"""
        params = self._clean(chains=chains)
        return self.get(f"/loans/entity/{entity}", params=params).json()

    # ══════════════════════════════════════════════════════════
    #  Portfolio & History — 组合和历史
    # ══════════════════════════════════════════════════════════

    def portfolio_address(self, address: str, *, time: str | None = None,
                          chains: str | None = None) -> dict:
        """GET /portfolio/address/{address} — 获取地址组合历史"""
        params = self._clean(time=time, chains=chains)
        return self.get(f"/portfolio/address/{address}", params=params).json()

    def portfolio_entity(self, entity: str, *, time: str | None = None,
                         chains: str | None = None) -> dict:
        """GET /portfolio/entity/{entity} — 获取实体组合历史"""
        params = self._clean(time=time, chains=chains)
        return self.get(f"/portfolio/entity/{entity}", params=params).json()

    def portfolio_timeseries_address(
        self, address: str, *, pricingId: str | None = None, chains: str | None = None,
    ) -> dict:
        """GET /portfolio/timeSeries/address/{address} — 获取地址 Token 每日时间序列"""
        params = self._clean(pricingId=pricingId, chains=chains)
        return self.get(f"/portfolio/timeSeries/address/{address}", params=params).json()

    def portfolio_timeseries_entity(
        self, entity: str, *, pricingId: str | None = None, chains: str | None = None,
    ) -> dict:
        """GET /portfolio/timeSeries/entity/{entity} — 获取实体 Token 每日时间序列"""
        params = self._clean(pricingId=pricingId, chains=chains)
        return self.get(f"/portfolio/timeSeries/entity/{entity}", params=params).json()

    def history_address(self, address: str, *, chains: str | None = None) -> dict:
        """GET /history/address/{address} — 获取地址历史数据"""
        params = self._clean(chains=chains)
        return self.get(f"/history/address/{address}", params=params).json()

    def history_entity(self, entity: str, *, chains: str | None = None) -> dict:
        """GET /history/entity/{entity} — 获取实体历史数据"""
        params = self._clean(chains=chains)
        return self.get(f"/history/entity/{entity}", params=params).json()

    # ══════════════════════════════════════════════════════════
    #  Counterparties, Flow & Volume — 交易对手/资金流/交易量
    # ══════════════════════════════════════════════════════════

    def counterparties_address(self, address: str, *, chains: str | None = None,
                               flow: str | None = None, limit: int | None = None,
                               offset: int | None = None, **kwargs) -> dict:
        """GET /counterparties/address/{address} — 获取地址交易对手（限速 1 req/s）

        常用参数：base, chains, flow, from_, to, tokens, timeGte, timeLte,
        timeLast, usdGte, usdLte, sortKey, sortDir, limit, offset, counterparties, tags
        """
        params = self._clean(chains=chains, flow=flow, limit=limit, offset=offset, **kwargs)
        return self.get(f"/counterparties/address/{address}", params=params).json()

    def counterparties_entity(self, entity: str, *, chains: str | None = None,
                              flow: str | None = None, limit: int | None = None,
                              offset: int | None = None, **kwargs) -> dict:
        """GET /counterparties/entity/{entity} — 获取实体交易对手（限速 1 req/s）"""
        params = self._clean(chains=chains, flow=flow, limit=limit, offset=offset, **kwargs)
        return self.get(f"/counterparties/entity/{entity}", params=params).json()

    def flow_address(self, address: str, *, chains: str | None = None) -> dict:
        """GET /flow/address/{address} — 获取地址历史 USD 资金流"""
        params = self._clean(chains=chains)
        return self.get(f"/flow/address/{address}", params=params).json()

    def flow_entity(self, entity: str, *, chains: str | None = None) -> dict:
        """GET /flow/entity/{entity} — 获取实体历史 USD 资金流"""
        params = self._clean(chains=chains)
        return self.get(f"/flow/entity/{entity}", params=params).json()

    def volume_address(self, address: str, *, chains: str | None = None) -> dict:
        """GET /volume/address/{address} — 获取地址转账量"""
        params = self._clean(chains=chains)
        return self.get(f"/volume/address/{address}", params=params).json()

    def volume_entity(self, entity: str, *, chains: str | None = None) -> dict:
        """GET /volume/entity/{entity} — 获取实体转账量"""
        params = self._clean(chains=chains)
        return self.get(f"/volume/entity/{entity}", params=params).json()

    # ══════════════════════════════════════════════════════════
    #  Token — Token 数据
    # ══════════════════════════════════════════════════════════

    def token_top(self, *, timeframe: str | None = None, orderByAgg: str | None = None,
                  orderByDesc: bool | None = None, orderByPercent: bool | None = None) -> dict:
        """GET /token/top — 获取交易所活跃度最高的 Token"""
        params = self._clean(timeframe=timeframe, orderByAgg=orderByAgg,
                             orderByDesc=orderByDesc, orderByPercent=orderByPercent)
        return self.get("/token/top", params=params).json()

    def token_trending(self) -> dict:
        """GET /token/trending — 获取趋势 Token"""
        return self.get("/token/trending").json()

    def token_trending_by_id(self, token_id: str) -> dict:
        """GET /token/trending/{id} — 获取单个趋势 Token"""
        return self.get(f"/token/trending/{token_id}").json()

    def token_holders_by_id(self, token_id: str, *, groupByEntity: bool | None = None) -> dict:
        """GET /token/holders/{id} — 按 pricing ID 获取 Token 持有者排名"""
        params = self._clean(groupByEntity=groupByEntity)
        return self.get(f"/token/holders/{token_id}", params=params).json()

    def token_holders_by_chain(self, chain: str, address: str, *,
                               groupByEntity: bool | None = None) -> dict:
        """GET /token/holders/{chain}/{address} — 按链和地址获取 Token 持有者排名"""
        params = self._clean(groupByEntity=groupByEntity)
        return self.get(f"/token/holders/{chain}/{address}", params=params).json()

    def token_top_flow_by_id(self, token_id: str, *, timeLast: str | None = None,
                             chains: str | None = None) -> dict:
        """GET /token/top_flow/{id} — 按 pricing ID 获取 Token 最大资金流"""
        params = self._clean(timeLast=timeLast, chains=chains)
        return self.get(f"/token/top_flow/{token_id}", params=params).json()

    def token_top_flow_by_chain(self, chain: str, address: str, *,
                                timeLast: str | None = None, chains: str | None = None) -> dict:
        """GET /token/top_flow/{chain}/{address} — 按链和地址获取 Token 最大资金流"""
        params = self._clean(timeLast=timeLast, chains=chains)
        return self.get(f"/token/top_flow/{chain}/{address}", params=params).json()

    def token_volume_by_id(self, token_id: str, *, timeLast: str | None = None,
                           granularity: str | None = None) -> dict:
        """GET /token/volume/{id} — 按 pricing ID 获取 Token 交易量"""
        params = self._clean(timeLast=timeLast, granularity=granularity)
        return self.get(f"/token/volume/{token_id}", params=params).json()

    def token_volume_by_chain(self, chain: str, address: str, *,
                              timeLast: str | None = None, granularity: str | None = None) -> dict:
        """GET /token/volume/{chain}/{address} — 按链和地址获取 Token 交易量"""
        params = self._clean(timeLast=timeLast, granularity=granularity)
        return self.get(f"/token/volume/{chain}/{address}", params=params).json()

    def token_balance_by_id(self, token_id: str, *, entityID: str | None = None,
                            address: str | None = None) -> dict:
        """GET /token/balance/{id} — 按 pricing ID 获取 Token 余额（所有链）"""
        params = self._clean(entityID=entityID, address=address)
        return self.get(f"/token/balance/{token_id}", params=params).json()

    def token_balance_by_chain(self, chain: str, token_address: str, *,
                               entityID: str | None = None, address: str | None = None) -> dict:
        """GET /token/balance/{chain}/{address} — 按链和地址获取 Token 余额"""
        params = self._clean(entityID=entityID, address=address)
        return self.get(f"/token/balance/{chain}/{token_address}", params=params).json()

    def token_market(self, token_id: str) -> dict:
        """GET /token/market/{id} — 获取 Token 当前市场数据"""
        return self.get(f"/token/market/{token_id}").json()

    def token_price_history_by_id(self, token_id: str, *, daily: bool | None = None) -> dict:
        """GET /token/price/history/{id} — 按 pricing ID 获取 Token 价格历史"""
        params = self._clean(daily=daily)
        return self.get(f"/token/price/history/{token_id}", params=params).json()

    def token_price_history_by_chain(self, chain: str, address: str, *,
                                     daily: bool | None = None) -> dict:
        """GET /token/price/history/{chain}/{address} — 按链和地址获取 Token 价格历史"""
        params = self._clean(daily=daily)
        return self.get(f"/token/price/history/{chain}/{address}", params=params).json()

    def token_price_change(self, token_id: str, *, pastTime: str | None = None) -> dict:
        """GET /token/price_change/{id} — 获取 Token 自某时间戳以来的价格变化"""
        params = self._clean(pastTime=pastTime)
        return self.get(f"/token/price_change/{token_id}", params=params).json()

    def token_addresses(self, token_id: str) -> dict:
        """GET /token/addresses/{id} — 获取 Token 在各链上的合约地址"""
        return self.get(f"/token/addresses/{token_id}").json()

    def token_arkham_exchange_tokens(self) -> dict:
        """GET /token/arkham_exchange_tokens — 获取 Arkham 交易所支持的 Token"""
        return self.get("/token/arkham_exchange_tokens").json()

    # ══════════════════════════════════════════════════════════
    #  Tags & Clusters — 标签和聚类
    # ══════════════════════════════════════════════════════════

    def tag_params(self, tag_id: str, *, limit: int | None = None,
                   offset: int | None = None) -> dict:
        """GET /tag/{id}/params — 获取标签参数"""
        params = self._clean(limit=limit, offset=offset)
        return self.get(f"/tag/{tag_id}/params", params=params).json()

    def tag_summary(self, tag_id: str) -> dict:
        """GET /tag/{id}/summary — 获取标签摘要统计"""
        return self.get(f"/tag/{tag_id}/summary").json()

    def cluster_summary(self, cluster_id: str) -> dict:
        """GET /cluster/{id}/summary — 获取聚类摘要统计"""
        return self.get(f"/cluster/{cluster_id}/summary").json()

    # ══════════════════════════════════════════════════════════
    #  User — 用户标签和私有实体
    # ══════════════════════════════════════════════════════════

    def user_profile(self) -> dict:
        """获取当前用户信息"""
        return self.get("/user").json()

    def user_alerts(self) -> list:
        """获取用户告警列表"""
        return self.get("/user/alerts").json()

    def user_labels(self) -> dict:
        """GET /user/labels — 获取用户标签"""
        return self.get("/user/labels").json()

    def user_labels_create(self, labels: list[dict]) -> dict:
        """POST /user/labels — 创建标签

        labels: [{"address": "0x...", "chainType": "ethereum", "name": "My Label", "note": "..."}]
        """
        return self.post("/user/labels", json=labels).json()

    def user_entities(self, *, includeAddresses: bool | None = None) -> dict:
        """GET /user/entities — 获取所有私有实体"""
        params = self._clean(includeAddresses=includeAddresses)
        return self.get("/user/entities", params=params).json()

    def user_entity(self, entity_id: str) -> dict:
        """GET /user/entities/{id} — 获取单个私有实体"""
        return self.get(f"/user/entities/{entity_id}").json()

    def user_entity_update(self, entity_id: str, body: dict) -> dict:
        """PUT /user/entities/only_add/{id} — 更新私有实体

        body 必须包含: id, name, note, type, service, addresses
        """
        return self.put(f"/user/entities/only_add/{entity_id}", json=body).json()

    # ══════════════════════════════════════════════════════════
    #  Market Data & Networks — 市场数据和网络状态
    # ══════════════════════════════════════════════════════════

    def marketdata_altcoin_index(self) -> dict:
        """GET /marketdata/altcoin_index — 获取 Altcoin 指数"""
        return self.get("/marketdata/altcoin_index").json()

    def networks_status(self) -> dict:
        """GET /networks/status — 获取所有区块链网络当前状态"""
        return self.get("/networks/status").json()

    def networks_history(self, chain: str) -> dict:
        """GET /networks/history/{chain} — 获取区块链网络历史数据"""
        return self.get(f"/networks/history/{chain}").json()

    def chains(self) -> list:
        """GET /chains — 获取支持的链列表"""
        return self.get("/chains").json()

    # ══════════════════════════════════════════════════════════
    #  Misc — ARKM 供应量
    # ══════════════════════════════════════════════════════════

    def arkm_circulating(self) -> dict:
        """GET /arkm/circulating — 获取 ARKM 流通供应量"""
        return self.get("/arkm/circulating").json()

    # ══════════════════════════════════════════════════════════
    #  WebSocket — 实时推送管理
    # ══════════════════════════════════════════════════════════

    def ws_session_info(self) -> dict:
        """GET /ws/session-info — 获取 WebSocket 定价信息"""
        return self.get("/ws/session-info").json()

    def ws_sessions(self) -> dict:
        """GET /ws/sessions — 列出 WebSocket 会话"""
        return self.get("/ws/sessions").json()

    def ws_session_create(self) -> dict:
        """POST /ws/sessions — 创建 WebSocket 会话"""
        return self.post("/ws/sessions", json={}).json()

    def ws_session_status(self, session_id: str) -> dict:
        """GET /ws/sessions/{id} — 获取 WebSocket 会话状态"""
        return self.get(f"/ws/sessions/{session_id}").json()

    def ws_session_delete(self, session_id: str) -> dict:
        """DELETE /ws/sessions/{id} — 删除 WebSocket 会话"""
        return self.delete(f"/ws/sessions/{session_id}").json()

    def ws_active_connections(self) -> dict:
        """GET /ws/active_connections — 获取活跃 WebSocket 连接"""
        return self.get("/ws/active_connections").json()

    # ══════════════════════════════════════════════════════════
    #  便捷方法
    # ══════════════════════════════════════════════════════════

    def tag(self, address: str) -> tuple[str | None, str | None]:
        """查询地址标签，返回 (entity_name, label_name)。

        entity_name: arkhamEntity.name  — 实体名称，如 "Binance"
        label_name:  arkhamLabel.name   — 地址标签，如 "Cold Wallet"
        无标签时返回 (None, None)。
        """
        try:
            data = self.intelligence_address(address)
        except Exception:
            return None, None
        entity = data.get("arkhamEntity")
        label = data.get("arkhamLabel")
        entity_name = entity.get("name") if entity else None
        label_name = label.get("name") if label else None
        return entity_name, label_name

    # ── 向后兼容别名 ─────────────────────────────────────────

    def address_balances(self, address: str) -> dict:
        """获取地址余额（兼容旧接口）"""
        return self.balances_address(address)

    def address_transfers(self, address: str, limit: int = 20) -> dict:
        """获取地址转账记录（兼容旧接口）"""
        return self.transfers(base=address, limit=limit)

    def address_intelligence(self, address: str) -> dict:
        """获取地址情报标签（兼容旧接口）"""
        return self.intelligence_address(address)

    # ── 内部 ─────────────────────────────────────────────────

    def _ensure_login(self):
        if not self._logged_in:
            self.login()

    def _url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{self.BASE_API}/{path.lstrip('/')}"

    @staticmethod
    def _clean(**kwargs) -> dict[str, Any]:
        """移除值为 None 的参数，将 bool 转为小写字符串"""
        result = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            # 处理 from_ -> from 的参数名映射
            key = k.rstrip("_") if k.endswith("_") else k
            if isinstance(v, bool):
                result[key] = str(v).lower()
            else:
                result[key] = v
        return result
