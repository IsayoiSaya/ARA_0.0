"""
分析流程执行脚本
"""

# 导入所有流程
from .assign import organize_files
from .card_pipeline import run_card_pipeline
from .sarg_pipeline import run_sarg_pipeline
from .victors_pipeline import run_victors_pipeline
from .bacmet_pipeline import run_bacmet_pipeline
from .mge_pipeline import run_mge_pipeline

# 定义公共接口
__all__ = [
    'organize_files',
    'run_card_pipeline',
    'run_sarg_pipeline',
    'run_victors_pipeline',
    'run_bacmet_pipeline',
    'run_mge_pipeline'
]