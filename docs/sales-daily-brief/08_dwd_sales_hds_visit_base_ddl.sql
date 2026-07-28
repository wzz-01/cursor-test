-- ============================================================
-- 拜访底表 DDL（字段对齐当前查询）
-- 建表人：xj
-- 说明：Doris DUPLICATE KEY 必须是建表字段的有序前缀
-- ============================================================

CREATE TABLE IF NOT EXISTS market_db.dwd_sales_hds_visit_base (
    -- KEY 前缀（顺序必须与 DUPLICATE KEY 一致）
    riqi                DATE           NOT NULL COMMENT '拜访业务日',
    c_shengqu           VARCHAR(128)   NULL COMMENT '省区',
    mendian_code        VARCHAR(64)    NULL COMMENT '门店编码',
    ry_code             VARCHAR(64)    NULL COMMENT '人员编码',

    -- 时间相关
    yuefen              VARCHAR(10)    NULL COMMENT '业务月（月初，yyyy-MM-01）',
    vs_visit_type       VARCHAR(64)    NULL COMMENT '拜访类型',

    -- 门店相关
    mendian_name        VARCHAR(256)   NULL COMMENT '门店名称',
    mendian_type        VARCHAR(64)    NULL COMMENT '门店类型',
    c_code              VARCHAR(64)    NULL COMMENT '经销客户编码（映射后）',

    -- 架构相关
    c_daqu              VARCHAR(128)   NULL COMMENT '大区',
    c_xiaoshouzu        VARCHAR(128)   NULL COMMENT '销售组',
    c_qudao             VARCHAR(64)    NULL COMMENT '直营经销',
    is_hexin1           VARCHAR(64)    NULL COMMENT '核心客户标签a',
    c_hexin1_type       VARCHAR(128)   NULL COMMENT '核心客户标签',
    c_kehu_type         VARCHAR(64)    NULL COMMENT '客户类型',

    -- 人员相关
    ry_name             VARCHAR(128)   NULL COMMENT '人员姓名',
    vs_emp_position     VARCHAR(128)   NULL COMMENT '拜访表岗位',
    org_name            VARCHAR(256)   NULL COMMENT '组织名称',
    ry_positiontype     VARCHAR(128)   NULL COMMENT '人员归属',
    ry_position_new     VARCHAR(128)   NULL COMMENT '岗位（合并）',
    vs_is_finished      TINYINT        NULL COMMENT '是否完成拜访：1是0否',

    etl_time            DATETIME       NULL COMMENT '写入时间'
)
DUPLICATE KEY(riqi, c_shengqu, mendian_code, ry_code)
COMMENT '拜访底表-有效已完成拜访；建表人:xj'
PARTITION BY RANGE(riqi) ()
DISTRIBUTED BY HASH(c_shengqu) BUCKETS 16
PROPERTIES (
    "replication_num" = "3",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.start" = "-400",
    "dynamic_partition.end" = "3",
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "16"
);
