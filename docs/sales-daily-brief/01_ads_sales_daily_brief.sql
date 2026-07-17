-- ============================================================
-- 销售管理日简报 - 每日基础宽表（Doris）
-- 用途：每天按「统计日 + 省区」落一行，供 PDF 模板直接取数
-- 更新频率：每日 T+1（建议早上跑完昨天完整日）
-- 说明：字段对齐《销售管理日简报》样例；源表映射待阶段2确认后补齐
-- ============================================================

CREATE DATABASE IF NOT EXISTS market_db;

-- 主表：省区日简报宽表
CREATE TABLE IF NOT EXISTS market_db.ads_sales_daily_brief (
    -- ---------- 主键 / 维度 ----------
    stat_date               DATE           NOT NULL COMMENT '统计日（昨天完整日）',
    region_code             VARCHAR(64)    NOT NULL COMMENT '省区编码',
    region_name             VARCHAR(128)   NOT NULL COMMENT '省区名称，如XX省区',

    -- ---------- 1）区域销售进度（截止昨日） ----------
    sales_amt               DECIMAL(18,4)  NULL COMMENT '截至统计日累计/当日口径销售额，单位：万元；以业务确认口径为准',
    yoy_amt_inc             DECIMAL(18,4)  NULL COMMENT '同比去年同日增额，单位：万元；= 本期额 - 去年同日额',
    yoy_sales_amt           DECIMAL(18,4)  NULL COMMENT '去年同日对照销售额，单位：万元（便于核对）',
    achieve_rate            DECIMAL(10,4)  NULL COMMENT '总达成率，单位：%（存数值，如 85.5 表示 85.5%）',
    keysku_achieve_rate     DECIMAL(10,4)  NULL COMMENT '大单品达成率，单位：%；缺数可空',
    growth_rate             DECIMAL(10,4)  NULL COMMENT '增长率，单位：%',
    achieve_rank            INT            NULL COMMENT '省区达成率排名（位）',
    growth_rank             INT            NULL COMMENT '省区增长率排名（位）',
    dealer_achieve_rate     DECIMAL(10,4)  NULL COMMENT '经销达成率，单位：%',
    dealer_growth_rate      DECIMAL(10,4)  NULL COMMENT '经销增长率，单位：%',
    direct_achieve_rate     DECIMAL(10,4)  NULL COMMENT '直营达成率，单位：%',
    direct_growth_rate      DECIMAL(10,4)  NULL COMMENT '直营增长率，单位：%',
    month_forecast_achieve  DECIMAL(10,4)  NULL COMMENT '结合当前进度及同期实际值预估本月达成，单位：%',
    top3_groups_text        VARCHAR(1000)  NULL COMMENT '达成率前三销售组/分区，文本，如：A组(98%),B组(95%),C组(92%)',
    bottom3_groups_text     VARCHAR(1000)  NULL COMMENT '达成率后三销售组/分区，文本',

    -- ---------- 2）昨日订单情况 ----------
    order_amt               DECIMAL(18,4)  NULL COMMENT '昨日下单金额，单位：万元',
    order_qty               DECIMAL(18,4)  NULL COMMENT '昨日下单件数，单位：件',
    order_cnt               BIGINT         NULL COMMENT '昨日订单数，单位：单',
    order_budget_pct        DECIMAL(10,4)  NULL COMMENT '昨日下单金额占全月预算比例，单位：%',
    month_order_budget_amt  DECIMAL(18,4)  NULL COMMENT '本月订单预算金额，单位：万元（便于核对占比）',
    no_order_5d_groups_text VARCHAR(2000)  NULL COMMENT '连续5日未下单的销售分区/销售组，逗号分隔文本',
    no_order_mtd_customers_text VARCHAR(4000) NULL COMMENT '当月仍未下单客户摘要（过长可只存数量+详见明细表）',
    no_order_mtd_customer_cnt INT          NULL COMMENT '当月仍未下单客户数',

    -- ---------- 3）费用使用情况（可空） ----------
    expense_amt             DECIMAL(18,4)  NULL COMMENT '费用使用额，单位：万元；无数据则空',
    expense_budget_amt      DECIMAL(18,4)  NULL COMMENT '费用预算，单位：万元',
    expense_use_rate        DECIMAL(10,4)  NULL COMMENT '费用使用率，单位：%',
    expense_remark          VARCHAR(1000)  NULL COMMENT '费用说明/异常；无数据时 PDF 写「本版暂无费用数据」',

    -- ---------- 4）昨日拜访情况（汇总） ----------
    visit_customer_cnt      INT            NULL COMMENT '昨日拜访客户数，单位：家',
    visit_customer_cover_rate DECIMAL(10,4) NULL COMMENT '拜访客户月累计覆盖率，单位：%',
    visit_store_cnt         INT            NULL COMMENT '昨日拜访门店数，单位：家',
    visit_store_cover_rate  DECIMAL(10,4)  NULL COMMENT '拜访门店月累计覆盖率，单位：%',
    visit_people_cnt        INT            NULL COMMENT '昨日参与拜访人数，单位：人',

    -- ---------- 5）业绩预警 / 市场问题 ----------
    decline_3m_cities_text  VARCHAR(2000)  NULL COMMENT '连续三个月下滑城市，逗号分隔',
    decline_3m_groups_text  VARCHAR(2000)  NULL COMMENT '连续三个月下滑销售组，逗号分隔',
    decline_3m_customers_text VARCHAR(4000) NULL COMMENT '连续三个月下滑客户摘要',
    bottom20_groups_3m_text VARCHAR(2000)  NULL COMMENT '近三月达成率处于全国后20%的销售组',

    -- ---------- 6）年度目标 ----------
    ytd_sales_amt           DECIMAL(18,4)  NULL COMMENT '年累计销售额，单位：万元',
    ytd_amt_inc             DECIMAL(18,4)  NULL COMMENT '年累计同比增额，单位：万元',
    ytd_progress            DECIMAL(10,4)  NULL COMMENT '当前累计进度，单位：%',
    ytd_progress_ly         DECIMAL(10,4)  NULL COMMENT '去年同期实际进度，单位：%',
    ytd_growth_rate         DECIMAL(10,4)  NULL COMMENT '年度同比增速，单位：%',
    ytd_progress_rank       INT            NULL COMMENT '省区进度排名（位）',
    ytd_growth_rank         INT            NULL COMMENT '省区增速排名（位）',

    -- ---------- 7）页脚 / 元数据 ----------
    contact_text            VARCHAR(500)   NULL COMMENT '页脚联系人，如：营销职能数据组 陶松华：...，刘颜杰：...',
    data_ready_flag         TINYINT        NULL DEFAULT '0' COMMENT '1=昨日数据已就绪可出PDF；0=未就绪',
    remark                  VARCHAR(1000)  NULL COMMENT '备注/口径说明',
    etl_time                DATETIME       NULL COMMENT '本行写入/更新时间'
)
UNIQUE KEY(stat_date, region_code)
COMMENT '销售管理日简报-省区日宽表；每天每省区一行'
PARTITION BY RANGE(stat_date) ()
DISTRIBUTED BY HASH(region_code) BUCKETS 8
PROPERTIES (
    "replication_num" = "3",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.start" = "-90",
    "dynamic_partition.end" = "3",
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "8"
);
