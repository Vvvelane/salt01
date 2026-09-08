"""评估口径。

改这里就能改整个排名的行为，别把常数散到各处。

锚点不是拍脑袋定的：先在全候选池上把原始指标算出来，看实际分位，再把 lo 放在
"这一项已经差到会妨碍研究"的位置、hi 放在"再好也没有额外意义"的位置。用绝对锚点
而不是横截面分位，是为了换了候选池之后分数还能比。
"""

from __future__ import annotations

from dataclasses import dataclass, field

# 评估窗口：只看最近这么多年。技术指标研究吃的是当下的微观结构，
# 十年前的成交分布对"现在能不能做"没有发言权，所以数据质量和活跃度都只在窗口内算，
# 全历史只用来量"够不够长"。
WINDOW_YEARS = 3

# 相邻两根 1min bar 之间超过这么多分钟，就不当作连续。
# 用来一刀切开"盘中连续"和"跨节"，前者拿去算停滞和 Amihud，后者拿去算跳空。
CONTIGUOUS_MINUTES = 5

# 历史长度到这里就封顶：满 5 年之后，再长也不额外加分。
HISTORY_SATURATION_YEARS = 5.0

# 窗口内至少要有这么多个交易日，才进主榜。不到的单独列，注明原因。
MIN_DAYS_FOR_RANKING = 250


@dataclass(frozen=True, slots=True)
class Anchor:
    """把一个原始指标线性映到 0~1。lo 拿 0 分，hi 拿满分；lo > hi 表示越小越好。"""

    lo: float
    hi: float

    def score(self, value: float | None) -> float:
        if value is None or value != value:  # NaN
            return 0.0
        span = self.hi - self.lo
        if span == 0:
            return 0.0
        return max(0.0, min(1.0, (value - self.lo) / span))

    @property
    def lower_is_better(self) -> bool:
        return self.lo > self.hi


@dataclass(frozen=True, slots=True)
class Component:
    key: str
    label: str
    weight: float
    anchor: Anchor
    unit: str = ""
    note: str = ""


# 权重按"技术指标研究者的痛点"排：
# 序列有洞 > 序列不动 > 单子进不去 > 历史不够长。
# 一根不存在的 bar 和一根价格没变的 bar，会让 MA/RSI/MACD 直接失真，而且没法补救；
# 成交额小只是限制容量，策略逻辑照样能验；历史短只影响样本量。
DENSITY_WEIGHT = 45.0
LIQUIDITY_WEIGHT = 40.0
HISTORY_WEIGHT = 15.0

COMPONENTS: tuple[Component, ...] = (
    # ---------- 数据密集度 45 ----------
    Component(
        "fill_rate",
        "分钟填充率",
        18.0,
        Anchor(lo=0.80, hi=1.00),
        "",
        "每个交易日实际 bar 数 / 该品种当年日 bar 数的 P90，逐日取 min(·,1) 后平均。"
        "用逐年经验基准而不是交易时段规则，因为 catalog 的时段规则是按合约生命周期给的整段，"
        "不反映夜盘上线、时段调整这类历史变更。",
    ),
    Component(
        "zero_vol_share",
        "零成交分钟占比",
        12.0,
        Anchor(lo=0.20, hi=0.00),
        "",
        "时间戳存在但成交量为 0 的 bar 占比。这类 bar 让指标在原地空转，"
        "而且不会像缺失 bar 那样被察觉。",
    ),
    Component(
        "stale_share",
        "价格停滞占比",
        10.0,
        Anchor(lo=0.60, hi=0.05),
        "",
        "相邻连续 bar 收盘价完全相同的占比，Lesmond/Ogden/Trzcinka (1999) "
        "zero-return 测度的分钟版。停滞会把动量类指标压成噪声。",
    ),
    Component(
        "day_gap_share",
        "交易日内部缺口",
        5.0,
        Anchor(lo=0.05, hi=0.00),
        "",
        "品种自身首末日之间，全市场有交易而该品种一根 bar 都没有的日子占比。"
        "只算内部缺口，尾端停更不计——那是派生任务的排期问题，不是品种的数据质量。",
    ),
    # ---------- 流动性与交易摩擦 40 ----------
    Component(
        "log_adv",
        "日均成交额",
        14.0,
        Anchor(lo=8.0, hi=11.0),
        "log10(元)",
        "窗口内日均成交额取 log10。锚点 8~11 即 1 亿到 1000 亿元/日。",
    ),
    Component(
        "amihud",
        "Amihud 非流动性",
        8.0,
        Anchor(lo=-9.0, hi=-12.0),
        "log10",
        "Amihud (2002) ILLIQ 的分钟版：mean(|r| / 成交额)，只在连续 bar 上算，取 log10。"
        "衡量单位成交额能把价格推动多远。",
    ),
    Component(
        "roll_bp",
        "Roll 有效价差",
        8.0,
        Anchor(lo=12.0, hi=1.0),
        "bp",
        "Roll (1984) 估计量：买卖价差的来回跳动会在成交价里留下负的一阶自协方差，"
        "S = 2*sqrt(-cov)，在 1min 收益上算。这里没用 Corwin-Schultz——CS 依赖"
        "高低价来自买价和卖价成交的假设，对连续交易的期货会被波动率主导，"
        "铜算出来 30bp 而真实价差只有 1.25bp；Roll 给出 1.8bp，量级是对的。"
        "CS 仍作为诊断项一并列出。",
    ),
    Component(
        "gap_ratio",
        "跨节跳空占比",
        6.0,
        Anchor(lo=0.22, hi=0.06),
        "",
        "跨节跳空幅度均值 / 日均振幅。回答的是：一天的波动里，有多大一块是在没法交易的"
        "时候跳掉的。这个比例高，盘中指标的连续性就是假的。除以振幅是为了剥掉波动率，"
        "否则高波动品种会被误判成流动性差。",
    ),
    Component(
        "range_ticks",
        "价格分辨率",
        4.0,
        Anchor(lo=20.0, hi=120.0),
        "tick",
        "日均振幅 / 最小变动价位。一天只走几十个 tick 的品种，价格序列是粗颗粒的，"
        "均线、通道、形态类指标在上面会大量出现假的平台和假的突破。",
    ),
    # ---------- 历史长度 15 ----------
    Component(
        "history_years",
        "历史长度",
        15.0,
        Anchor(lo=0.0, hi=HISTORY_SATURATION_YEARS),
        "年",
        f"主连 1min 首末日跨度，满 {HISTORY_SATURATION_YEARS:.0f} 年封顶。"
        "封顶是因为技术指标的参数空间不大，五年的分钟样本已经足够做样本内外切分。",
    ),
)

GROUPS: dict[str, tuple[str, ...]] = {
    "数据密集度": ("fill_rate", "zero_vol_share", "stale_share", "day_gap_share"),
    "流动性与交易摩擦": ("log_adv", "amihud", "roll_bp", "gap_ratio", "range_ticks"),
    "历史长度": ("history_years",),
}

# 只报告、不计分：拿来解释排名，不参与打分
DIAGNOSTICS: tuple[str, ...] = (
    "n_days",
    "n_bars",
    "last_day",
    "adv",
    "cs_spread",
    "roll_cov",
    "jump_share",
    "jump_p99_ticks",
    "gap_session",
    "range_pct",
    "active_contracts",
    "tail_ratio",
)


@dataclass(frozen=True, slots=True)
class Settings:
    window_years: int = WINDOW_YEARS
    contiguous_minutes: int = CONTIGUOUS_MINUTES
    min_days: int = MIN_DAYS_FOR_RANKING
    components: tuple[Component, ...] = field(default=COMPONENTS)

    @property
    def total_weight(self) -> float:
        return sum(c.weight for c in self.components)

    def by_key(self, key: str) -> Component:
        for c in self.components:
            if c.key == key:
                return c
        raise KeyError(key)


SETTINGS = Settings()
