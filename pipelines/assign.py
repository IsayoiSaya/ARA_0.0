import os
import shutil
import pandas as pd
import re


def organize_files(source_dir):
    """
    自动归类文件到指定文件夹并处理文件
    参数：
        source_dir: 需要整理的文件夹目录路径
    """
    category_rules = {
        "CARD": "01 CARD",
        "SARG": "02 SARG",
        "victors": "03 victors",
        "BacMet": "04 BacMet",
        "count": "05 MGE"
    }

    print(f"整理目录: {source_dir}")
    others_dir = os.path.join(source_dir, "Others")
    os.makedirs(others_dir, exist_ok=True)

    # 第一步：处理普通规则文件
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)

        if os.path.isdir(file_path) or filename == __file__:
            continue

        moved = False
        for keyword, folder_name in category_rules.items():
            if keyword in filename:
                target_dir = os.path.join(source_dir, folder_name)
                os.makedirs(target_dir, exist_ok=True)

                new_filename = f"{keyword}.csv"
                target_path = os.path.join(target_dir, new_filename)

                try:
                    # 修改移动操作为复制操作
                    shutil.copy(file_path, target_path)  # 替换原来的shutil.move
                    print(f"[成功] 复制 '{filename}' -> {folder_name}/{new_filename}")
                    if os.path.exists(target_path):
                        print(f"  目标文件大小: {os.path.getsize(target_path) // 1024}KB")

                    # 处理文件（转换格式和分割列）
                    convert_to_xlsx(target_path)
                except FileExistsError:
                    print(f"[警告] 目标文件已存在，覆盖: {folder_name}/{new_filename}")
                    os.replace(file_path, target_path)  # 这里改为直接覆盖目标文件
                    convert_to_xlsx(target_path)
                except Exception as e:
                    print(f"[错误] 处理失败: {filename} -> {str(e)}")

                moved = True
                break

        if not moved:
            print(f"[忽略] 未匹配规则: {filename}")

    # 第二步：处理含16S的文件
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if os.path.isdir(file_path) or filename == __file__:
            continue

        if "16S" in filename.upper():
            target_dir = os.path.join(source_dir, "Others")
            os.makedirs(target_dir, exist_ok=True)
            new_filename = "16S_reads_number.txt"
            target_path = os.path.join(target_dir, new_filename)

            try:
                # 将文件复制到Others目录
                shutil.copy(file_path, target_path)
                print(f"[成功] 复制 '{filename}' -> Others/{new_filename}")
                if os.path.exists(target_path):
                    print(f"  目标文件大小: {os.path.getsize(target_path) // 1024}KB")
                # 注意：这里不调用convert_to_xlsx，因为我们不需要处理txt文件
            except FileExistsError:
                print(f"[警告] 目标文件已存在，覆盖: Others/{new_filename}")
                shutil.copy(file_path, target_path)
            except Exception as e:
                print(f"[错误] 处理16S文件失败: {filename} -> {str(e)}")

    # 第三步：处理含reads_number的文件
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if os.path.isdir(file_path) or filename == __file__:
            continue

        if "reads_number" in filename.lower() and "16S" not in filename.upper():
            target_dir = os.path.join(source_dir, "Others")
            os.makedirs(target_dir, exist_ok=True)
            new_filename = "reads_number.txt"
            target_path = os.path.join(target_dir, new_filename)

            try:
                # 复制文件到Others目录
                shutil.copy(file_path, target_path)
                print(f"[成功] 复制reads_number文件 '{filename}' -> Others/{new_filename}")
                convert_to_xlsx(target_path)  # ✅ 确保转换被调用
            except FileExistsError:
                shutil.copy(file_path, target_path)
                print(f"[警告] 目标文件已存在，覆盖: Others/{new_filename}")
            except Exception as e:
                print(f"[错误] 处理reads_number文件失败: {filename} -> {str(e)}")


def convert_to_xlsx(file_path):
    """强制转换CSV/TSV为XLSX（增强版）"""
    if not file_path.lower().endswith(('.csv', '.tsv')):
        print(f"[忽略] 不是CSV/TSV文件: {file_path}")
        return

    xlsx_path = os.path.splitext(file_path)[0] + '.xlsx'

    try:
        # 强制覆盖已存在的xlsx文件
        if os.path.exists(xlsx_path):
            os.remove(xlsx_path)

        # 自动检测分隔符并读取
        df = pd.read_csv(file_path, sep=None, engine='python', thousands=',')

        # 自动修正常见列名拼写错误
        df.columns = [col.replace('lentgh', 'length').strip() for col in df.columns]

        # 保存为Excel
        df.to_excel(xlsx_path, index=False, engine='openpyxl')
        print(f"[强制转换] {os.path.basename(file_path)} → {os.path.basename(xlsx_path)}")

    except Exception as e:
        print(f"[严重错误] 转换失败: {file_path}\n错误详情: {str(e)}")
        if os.path.exists(xlsx_path):
            os.remove(xlsx_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        # 使用更通用的示例路径
        target_dir = os.path.join(os.path.expanduser("~"), "Desktop", "analysis_data")
        print(f"警告: 使用默认目录 {target_dir}")

    print(f"开始整理目录: {target_dir}")
    organize_files(target_dir)
    print("文件整理完成！")
    print("文件整理完成！")