"""
Victors 全流程一键执行脚本
执行顺序：
1. 原始数据处理与RPKM计算
2. 按病原体(Pathogen)分类汇总
3. 按病原体属(Genus)分类汇总
"""

from pathlib import Path

import pandas as pd

from config.default_paths import VICTORS_DIR, VICTORS_FILES, READS_FILE, READS_16S_FILE
from modules.victors import rpkm, aggregators
from modules.utils import setup_logging
import logging


def run_victors_pipeline():
    """执行Victors全流程分析"""
    try:
        logger = logging.getLogger("VICTORS_Pipeline")

        logger.info("=" * 60)
        logger.info("开始 Victors 全流程处理")
        logger.info(f"工作目录: {VICTORS_DIR}")
        input_path = str(VICTORS_FILES["input"])
        df = pd.read_excel(input_path)
        logging.info(f"读取文件: {input_path}")
        logging.debug(f"数据形状: {df.shape}")
        logging.info("=" * 60)

        # 删除以下日志配置代码：
        # setup_logging()
        # logging.basicConfig(...)

        # 1. 处理原始数据并计算RPKM
        logging.info("步骤1: 处理原始数据并计算RPKM...")
        rpkm.process_victors_data(
            input_path=VICTORS_FILES["input"],
            output_path=VICTORS_FILES["output"],
            reads_path=READS_FILE,
            reads_16s_path=READS_16S_FILE
        )

        # 2. 按病原体分类汇总
        logging.info("步骤2: 按病原体(Pathogen)分类汇总...")
        aggregators.generate_pathogen_classification(
            input_path=VICTORS_FILES["output"],
            output_path=VICTORS_FILES["output"]
        )

        # 3. 按病原体属分类汇总
        logging.info("步骤3: 按病原体属(Genus)分类汇总...")
        aggregators.generate_genus_classification(
            input_path=VICTORS_FILES["output"],
            output_path=VICTORS_FILES["output"]
        )

        logging.info("\n" + "=" * 60)
        logging.info(f"✅ Victors全流程完成! 结果保存在: {VICTORS_FILES['output']}")
        logging.info("=" * 60)

    except Exception as e:  # 添加异常处理
        logger.error(f"❌ 流程执行失败: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    run_victors_pipeline()