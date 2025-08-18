"""
抗性基因分析总流程主入口
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
import logging
from pipelines import card_pipeline, sarg_pipeline, victors_pipeline, bacmet_pipeline, mge_pipeline
from pipelines.assign import organize_files, convert_to_xlsx
from modules.utils import setup_logging
from config.default_paths import PROJECT_ROOT

def main():
  try:
    setup_logging(PROJECT_ROOT)

    # 0. 确保目录存在
    from config.default_paths import CARD_DIR, SARG_DIR, VICTORS_DIR, BACMET_DIR, MGE_DIR
    for dir_path in [CARD_DIR, SARG_DIR, VICTORS_DIR, BACMET_DIR, MGE_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # 1. 执行文件自动归类
    logging.info("=" * 50)
    logging.info("步骤1: 执行文件自动归类")
    logging.info("=" * 50)
    organize_files(PROJECT_ROOT)

    # 2. 执行各分析流程
    logging.info("\n" + "=" * 50)
    logging.info("步骤2: 执行CARD分析流程")
    logging.info("=" * 50)
    card_pipeline.run_card_pipeline()


    logging.info("\n" + "=" * 50)
    logging.info("步骤3: 执行SARG分析流程")
    logging.info("=" * 50)
    sarg_pipeline.run_sarg_pipeline()

    logging.info("\n" + "=" * 50)
    logging.info("步骤4: 执行Victors分析流程")
    logging.info("=" * 50)
    victors_pipeline.run_victors_pipeline()

    logging.info("\n" + "=" * 50)
    logging.info("步骤5: 执行BacMet分析流程")
    logging.info("=" * 50)
    bacmet_pipeline.run_bacmet_pipeline()

    logging.info("\n" + "=" * 50)
    logging.info("步骤6: 执行MGE分析流程")
    logging.info("=" * 50)
    mge_pipeline.run_mge_pipeline()
    
    logging.info("\n" + "=" * 50)
    logging.info("✅ 所有分析流程成功完成!")
    logging.info("=" * 50)

  except Exception as e:
       logging.exception("主流程执行失败")
       sys.exit(1)

if __name__ == "__main__":
    main()