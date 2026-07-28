-- ============================================================
-- 明细表：昨日拜访个人明细（对应样例表格）
-- 关联：stat_date + region_code → ads_sales_daily_brief
-- ============================================================

CREATE TABLE IF NOT EXISTS market_db.ads_sales_daily_brief_visit_person (
    stat_date           DATE           NOT NULL COMMENT '统计日',
    region_code         VARCHAR(64)    NOT NULL COMMENT '省区编码',
    region_name         VARCHAR(128)   NOT NULL COMMENT '省区名称',
    person_id           VARCHAR(64)    NOT NULL COMMENT '人员ID',
    person_name         VARCHAR(128)   NOT NULL COMMENT '姓名（样列表头：姓名）',
    visit_dealer_cnt    INT            NULL COMMENT '拜访经销数',
    visit_store_cnt     INT            NULL COMMENT '拜访门店数',
    is_leader           TINYINT        NULL DEFAULT '0' COMMENT '是否分区/销售组负责人：1是0否',
    org_name            VARCHAR(128)   NULL COMMENT '所属销售组/分区',
    etl_time            DATETIME       NULL COMMENT '写入时间'
)
DUPLICATE KEY(stat_date, region_code, person_id)
COMMENT '销售管理日简报-昨日拜访个人明细'
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


-- ============================================================
-- 明细表：昨日下单客户清单（样例「附：下单客户清单及下单量」）
-- ============================================================

CREATE TABLE IF NOT EXISTS market_db.ads_sales_daily_brief_order_customer (
    stat_date           DATE           NOT NULL COMMENT '统计日',
    region_code         VARCHAR(64)    NOT NULL COMMENT '省区编码',
    region_name         VARCHAR(128)   NOT NULL COMMENT '省区名称',
    customer_id         VARCHAR(64)    NOT NULL COMMENT '客户ID',
    customer_name       VARCHAR(256)   NOT NULL COMMENT '客户名称',
    org_name            VARCHAR(128)   NULL COMMENT '所属销售组/分区',
    channel_type        VARCHAR(32)    NULL COMMENT '渠道：经销/直营/其他',
    order_amt           DECIMAL(18,4)  NULL COMMENT '下单金额，单位：万元',
    order_qty           DECIMAL(18,4)  NULL COMMENT '下单件数',
    order_cnt           BIGINT         NULL COMMENT '订单数',
    etl_time            DATETIME       NULL COMMENT '写入时间'
)
DUPLICATE KEY(stat_date, region_code, customer_id)
COMMENT '销售管理日简报-昨日下单客户明细'
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


-- ============================================================
-- 明细表：当月仍未下单客户（预警附录）
-- ============================================================

CREATE TABLE IF NOT EXISTS market_db.ads_sales_daily_brief_no_order_customer (
    stat_date           DATE           NOT NULL COMMENT '统计日（快照日）',
    region_code         VARCHAR(64)    NOT NULL COMMENT '省区编码',
    region_name         VARCHAR(128)   NOT NULL COMMENT '省区名称',
    customer_id         VARCHAR(64)    NOT NULL COMMENT '客户ID',
    customer_name       VARCHAR(256)   NOT NULL COMMENT '客户名称',
    org_name            VARCHAR(128)   NULL COMMENT '所属销售组/分区',
    channel_type        VARCHAR(32)    NULL COMMENT '渠道：经销/直营/其他',
    last_order_date     DATE           NULL COMMENT '最近一次下单日，可空',
    etl_time            DATETIME       NULL COMMENT '写入时间'
)
DUPLICATE KEY(stat_date, region_code, customer_id)
COMMENT '销售管理日简报-当月未下单客户明细'
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
