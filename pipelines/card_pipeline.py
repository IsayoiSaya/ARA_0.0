# pipelines/card_pipeline.py
"""
CARD 全流程一键执行脚本
执行顺序：
1. 原始数据预处理（转置与合并）
2. RPKM计算（含16S RPKM）
3. 多种分类汇总（基因家族、类别、类型、机制、ARGs）
"""

import logging
from pathlib import Path
import pandas as pd
from modules.card import (
    preprocess,
    rpkm,
    aggregators
)
from config.default_paths import CARD_DIR, CARD_FILES, READS_FILE, READS_16S_FILE


def run_card_pipeline():
    """执行CARD全流程分析"""
    try:
        # 使用主流程的日志配置（删除原日志配置代码）
        logger = logging.getLogger("CARD_Pipeline")

        logger.info("=" * 60)
        logger.info("开始 CARD 抗性基因分析流程")
        logger.info(f"工作目录: {CARD_DIR}")
        logger.info("=" * 60)

        # 删除以下日志文件配置代码：
        # log_file = CARD_DIR / "card_pipeline.log"
        # file_handler = logging.FileHandler(log_file)
        # stream_handler = logging.StreamHandler()
        # logger.addHandler(file_handler)
        # logger.addHandler(stream_handler)

        # 确保目录存在
        CARD_DIR.mkdir(parents=True, exist_ok=True)

        # 配置日志（只在函数内部）
        logger = logging.getLogger("CARD_Pipeline")
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # 文件处理器
        log_file = CARD_DIR / "card_pipeline.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        # 控制台处理器
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # 清除可能存在的旧处理器
        if logger.hasHandlers():
            logger.handlers.clear()

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        logger.info("=" * 60)
        logger.info("开始 CARD 抗性基因分析流程")
        logger.info(f"工作目录: {CARD_DIR}")
        logger.info("=" * 60)

        # 1. 数据预处理
        logger.info("\n" + "=" * 60)
        logger.info("步骤1: 数据预处理")
        logger.info("=" * 60)

        logger.info("① 转置原始CARD映射数据...")
        preprocess.process_and_transpose_card_mapping(
            file_path=CARD_FILES["input"],
            output_path=CARD_FILES["output"],
            sheet_name='CARD_mapping'
        )

        logger.info("② 合并AMR元数据信息...")
        preprocess.merge_amr_info(
            card_path=CARD_FILES["output"],
            amr_meta_path=CARD_FILES["mapping"],
            sheet_name='Merged'
        )

        # 2. RPKM计算
        logger.info("\n" + "=" * 60)
        logger.info("步骤2: RPKM计算")
        logger.info("=" * 60)

        logger.info("③ 计算RPKM与16S RPKM...")
        rpkm.process_sarg_data(
            file_path=CARD_FILES["output"],
            output_path=CARD_FILES["output"],
            reads_path=READS_FILE,
            reads_16s_path=READS_16S_FILE
        )

        # 3. 分类汇总
        logger.info("\n" + "=" * 60)
        logger.info("步骤3: 分类汇总")
        logger.info("=" * 60)

        logger.info("④ AMR基因家族分类汇总...")
        aggregators.generate_gene_family_classification(
            CARD_FILES["output"],
            CARD_FILES["output"]
        )

        logger.info("⑤ 抗性类别分类汇总...")
        aggregators.generate_class_classification(
            CARD_FILES["output"],
            CARD_FILES["output"]
        )

        logger.info("⑥ Class-Types分类汇总...")
        aggregators.generate_class_types_classification(
            CARD_FILES["output"],
            CARD_FILES["output"],
            CARD_FILES["types_class"]
        )

        logger.info("⑦ 抗性机制分类汇总...")
        aggregators.generate_mechanism_classification(
            CARD_FILES["output"],
            CARD_FILES["output"]
        )

        logger.info("⑧ ARGs分类汇总(含高频ARGs筛选)...")
        aggregators.generate_arg_classification(
            CARD_FILES["output"],
            CARD_FILES["output"]
        )

        logger.info("\n" + "=" * 60)
        logger.info(f"[完成] CARD分析流程成功完成! 结果文件: {CARD_FILES['output']}")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error(f"[错误] 流程执行失败: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    run_card_pipeline()