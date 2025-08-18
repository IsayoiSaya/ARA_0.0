"""
BacMet 全流程分析脚本
"""

import logging
from pathlib import Path
from config.default_paths import BACMET_DIR, BACMET_FILES, READS_FILE, READS_16S_FILE
from modules.bacmet import preprocess, rpkm, aggregators
from modules.utils import setup_logging
import pandas as pd


def run_bacmet_pipeline():
    """执行BacMet全流程分析"""
    try:
        logger = logging.getLogger("BACMET_Pipeline")

        logger.info("=" * 50)
        logger.info("开始 BacMet 分析流程")
        logger.info(f"工作目录: {BACMET_DIR}")
        input_path = str(BACMET_FILES["input"])
        df = pd.read_excel(input_path)
        logging.info(f"读取文件: {input_path}")
        logging.debug(f"数据形状: {df.shape}")
        logging.info("=" * 50)

        # 删除以下日志配置代码：
        # setup_logging()
        # logging.basicConfig(...)

        # 1. 数据预处理
        logging.info("步骤1: 执行BacMet数据预处理...")
        preprocess.preprocess_bacmet(
            input_path=BACMET_FILES["input"],
            bacmet_mapping_file=BACMET_FILES["mapping"],
            output_path = BACMET_DIR / "BacMet_mapped.xlsx"
        )

        # 2. RPKM计算
        logging.info("步骤2: 执行RPKM标准化计算...")
        rpkm.process_sarg_data(
            file_path=BACMET_FILES["output"].with_name("BacMet_mapped.xlsx"),
            output_path=BACMET_FILES["output"],
            reads_path=READS_FILE,
            reads_16s_path=READS_16S_FILE
        )

        # 3. 分类汇总
        logging.info("步骤3: 执行分类汇总操作...")

        # 读取处理后的数据
        df_rpkm = pd.read_excel(BACMET_FILES["output"], sheet_name='RPKM')
        df_16s = pd.read_excel(BACMET_FILES["output"], sheet_name='16SRPKM')

        with pd.ExcelWriter(BACMET_FILES["output"], engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            # 化合物分类
            logging.info("- 化合物分类汇总")
            compound_rpkm = aggregators.generate_compound_classification(df_rpkm)
            compound_16s = aggregators.generate_compound_classification(df_16s)
            compound_rpkm.to_excel(writer, index=False, sheet_name='Compound_RPKM')
            compound_16s.to_excel(writer, index=False, sheet_name='Compound_16SRPKM')

            # 基因分类
            logging.info("- 基因分类汇总")
            gene_rpkm = aggregators.generate_gene_classification(df_rpkm)
            gene_16s = aggregators.generate_gene_classification(df_16s)
            gene_rpkm.to_excel(writer, index=False, sheet_name='Gene_RPKM')
            gene_16s.to_excel(writer, index=False, sheet_name='Gene_16SRPKM')

            # 位置分类
            logging.info("- 位置分类汇总")
            location_rpkm = aggregators.generate_location_classification(df_rpkm)
            location_16s = aggregators.generate_location_classification(df_16s)
            location_rpkm.to_excel(writer, index=False, sheet_name='Location_RPKM')
            location_16s.to_excel(writer, index=False, sheet_name='Location_16SRPKM')

            # 生物体分类
            logging.info("- 生物体分类汇总")
            organism_rpkm = aggregators.generate_organism_classification(df_rpkm)
            organism_16s = aggregators.generate_organism_classification(df_16s)
            organism_rpkm.to_excel(writer, index=False, sheet_name='Organism_RPKM')
            organism_16s.to_excel(writer, index=False, sheet_name='Organism_16SRPKM')


        logging.info("\n" + "=" * 50)
        logging.info(f"✅ BacMet分析流程完成! 结果保存在: {BACMET_FILES['output']}")
        logging.info("=" * 50)

    except Exception as e:  # 添加异常处理
        logger.error(f"❌ 流程执行失败: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    run_bacmet_pipeline()