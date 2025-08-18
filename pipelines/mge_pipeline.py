"""
MGE 全流程一键执行脚本
执行顺序：
1. 原始数据处理与RPKM计算
2. 按基因(Genes)分类汇总
"""

from pathlib import Path

import pandas as pd

from config.default_paths import MGE_DIR, MGE_FILES, READS_FILE, READS_16S_FILE
from modules.mge import rpkm, aggregators
from modules.utils import setup_logging
import logging


def run_mge_pipeline():
    """执行MGE全流程"""
    try:
        logger = logging.getLogger("MGE_Pipeline")

        logger.info("=" * 50)
        logger.info("开始 MGE 全流程处理")
        logger.info(f"工作目录: {MGE_DIR}")
        input_path = str(MGE_FILES["input"])
        df = pd.read_excel(input_path)
        logger.info(f"读取文件: {input_path}")
        logger.debug(f"数据形状: {df.shape}")
        logging.info("=" * 50)

        # 1. 数据处理与RPKM计算
        logger.info("检查必需文件是否存在...")
        required_files = [
            MGE_FILES["input"],
            MGE_FILES["search"],
            READS_FILE,
            READS_16S_FILE
        ]
        for f in required_files:
            if not f.exists():
                logger.error(f"❌ 文件不存在: {f}")
                return False

        logger.info("已找到所有必需文件")

        # 增强数据处理流程
        logger.info("步骤1: 处理原始MGE数据并计算RPKM...")
        rpkm.process_mge_data(
            input_file=MGE_FILES["input"],
            output_file=MGE_FILES["output"],
            search_file=MGE_FILES["search"],
            reads_path=READS_FILE,
            reads_16s_path=READS_16S_FILE
        )

        # 2. 基因分类汇总
        logger.info("步骤2: 按基因(Genes)分类汇总...")
        aggregators.generate_gene_classification(
            input_path=MGE_FILES["output"],
            output_path=MGE_FILES["output"]
        )

        logger.info("\n" + "=" * 50)  # 修改为logger
        logger.info(f"✅ MGE全流程完成! 结果保存在: {MGE_FILES['output']}")  # 修改为logger
        logger.info("=" * 50)  # 修改为logger

    except Exception as e:  # 添加异常处理
        logger.error(f"❌ 流程执行失败: {str(e)}", exc_info=True)
        return False


def calculate_rpkm(df, reads_data, length_col):
    """标准RPKM计算公式实现"""
    return (df.select_dtypes(include='number') * 1e9) / (length_col.values.reshape(-1, 1) * reads_data.values)


if __name__ == "__main__":
    run_mge_pipeline()