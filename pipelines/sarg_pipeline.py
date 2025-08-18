"""
SARG 全流程一键执行脚本
"""

from pathlib import Path

import pandas as pd
from config.default_paths import SARG_DIR, SARG_FILES, READS_FILE, READS_16S_FILE
from modules.sarg import (
    process_sarg_data,
    add_risk_rank,
    generate_types_classification,
    generate_gene_classification,
    generate_rank_classification
)
from modules.utils import setup_logging
import logging


def run_sarg_pipeline():
    """执行SARG全流程"""
    # 使用主流程的日志配置
    logger = logging.getLogger("SARG_Pipeline")

    logger.info("=" * 60)
    logger.info("开始 SARG 全流程处理")
    logger.info(f"工作目录: {SARG_DIR}")
    input_path = str(SARG_FILES["input"])  # 添加这行定义input_path
    df = pd.read_excel(input_path)  # 添加这行读取数据并定义df
    logging.info(f"读取文件: {input_path}")
    logging.debug(f"数据形状: {df.shape}")
    logging.info("=" * 60)

    # 1. RPKM计算
    logging.info("① 计算 RPKM 与 16S RPKM ...")
    process_sarg_data(
        file_path=SARG_FILES["input"],
        output_path=SARG_FILES["output"],
        reads_path=READS_FILE,
        reads_16s_path=READS_16S_FILE
    )

    # 2. 添加风险等级
    logging.info("② 添加 ARGs 风险等级(Rank)...")
    add_risk_rank(
        risk_file=SARG_FILES["risk"],
        target_file=SARG_FILES["output"]
    )

    # 3. 分类汇总
    logging.info("③ 汇总 ARGs 类型(Types)...")
    generate_types_classification(
        SARG_FILES["output"],
        SARG_FILES["output"]
    )

    logging.info("④ 汇总 ARGs 基因(Gene)...")
    generate_gene_classification(
        SARG_FILES["output"],
        SARG_FILES["output"]
    )

    logging.info("⑤ 汇总 风险等级(Rank)...")
    generate_rank_classification(
        SARG_FILES["output"],
        SARG_FILES["output"]
    )

    logging.info("\n" + "=" * 60)
    logging.info(f"✅ SARG全流程完成! 结果保存在: {SARG_FILES['output']}")
    logging.info("=" * 60)


if __name__ == "__main__":
    run_sarg_pipeline()