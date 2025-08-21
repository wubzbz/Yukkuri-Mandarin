# 基于全局规则生成假名音声。
# 用于快速构建数据库。

from pathlib import Path
import csv
from typing import List

from yukkurimandarin.generate_gana import generate_hiragana, YINJIE

# 可选组件
try:
    import openpyxl
    _HAS_OPENPYXL = True
except ImportError:
    _HAS_OPENPYXL = False


def fill_xlsx(file_path: str = "gr_yinjie_table.xlsx") -> None:
    """利用统一规则填充可供数据库导入的excel工作表。"""
    if not _HAS_OPENPYXL:
        print("未安装openpyxl，该功能不可用。\n请尝试通过 pip install openpyxl 进行安装。 或使用fill_csv方法代替。")
        return
    try:
        filepath = Path(file_path)
        # 检查后缀
        if filepath.suffix.lower() != ".xlsx":
            filepath = filepath.with_suffix(".xlsx")
        # 检查相对路径
        if not filepath.is_absolute():
            filepath = Path.cwd() / filepath
        # 加载活动工作簿
        workbook = openpyxl.Workbook()
        sheet = workbook.active 
        if not sheet:
            sheet = workbook.create_sheet(title="拼音数据")
            workbook.active = sheet
        # 生成表头
        sheet["A1"] = "拼音"
        sheet["B1"] = "声调"
        sheet["C1"] = "平假名"
        # 生成合法声调列表
        tones = generate_valid_numbers()
        # 跳过表头
        row_num = 2
        for yinjie in YINJIE:
            for tone in tones:
                hiragana = generate_hiragana(yinjie, tone)
                # 填充数据到本行的A、B、C列
                sheet[f"A{row_num}"] = yinjie
                sheet[f"B{row_num}"] = tone
                sheet[f"C{row_num}"] = hiragana
                row_num += 1
        # 保存工作簿
        workbook.save(filepath)
        print(f"成功导出 {row_num-1} 行数据到 {filepath}")
        
    except FileNotFoundError:
        print(f"错误：未找到文件 '{filepath}'")
    except Exception as e:
        print(f"发生错误：{e}")


def fill_csv(file_path: str = "gr_yinjie_table.csv") -> None:
    """利用统一规则填充可供数据库导入的csv文档。"""
    try:
        filepath = Path(file_path)
        # 检查后缀
        if filepath.suffix.lower() != ".csv":
            filepath = filepath.with_suffix(".csv")
        # 检查相对路径
        if not filepath.is_absolute():
            filepath = Path.cwd() / filepath
        # 生成合法声调列表
        tones = generate_valid_numbers()
        # 表头
        rows = [["拼音", "声调", "平假名"]]
        for yinjie in YINJIE:
            for tone in tones:
                hiragana = generate_hiragana(yinjie, tone)
                # 填充数据到本行
                rows.append([yinjie, tone, hiragana])
        # 写入csv文件
        with open(filepath, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerows(rows)
            print(f"成功导出 {len(rows)} 行数据到 {filepath}")
        
    except FileNotFoundError:
        print(f"错误：未找到文件 '{filepath}'")
    except Exception as e:
        print(f"发生错误：{e}")


def generate_valid_numbers() -> List[str]:
    """生成所有符合条件的3位声调组合"""
    valid_tones = []
    digits = ["0", "1", "2", "3", "4", "5"]
    middle_digits = ["1", "2", "3", "4", "5"]  # 第2位不能是0
    
    for d1 in digits:
        for d2 in middle_digits:
            for d3 in digits:
                valid_tones.append(f"{d1}{d2}{d3}")
    
    return valid_tones
    
