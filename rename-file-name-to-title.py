import os
import shutil
from fontTools.ttLib import TTFont

# 仅匹配区分大小写的字体文件扩展名
FONT_EXTENSIONS = {".ttf", ".otf", ".ttc", ".fon"}


def get_font_name(file_path):
    """获取字体文件的名称（元数据中的标题）"""
    try:
        font = TTFont(file_path)
        for record in font["name"].names:
            if record.nameID == 4 and record.platformID == 3:  # Windows 平台
                name = record.string.decode("utf-16-be")

                # 处理 ";" 号分隔的情况，取分号后面的名称
                if ";" in name:
                    name = name.split(";")[-1].strip()

                return name
        return None
    except Exception as e:
        print(f"❌ 读取字体元数据失败: {e} ({file_path})")
        return None


def move_failed_font(file_path, failed_dir):
    """移动无法识别的字体文件到 `failed_fonts/` 目录"""
    if not os.path.exists(failed_dir):
        os.makedirs(failed_dir)  # 如果目录不存在，则创建
    new_path = os.path.join(failed_dir, os.path.basename(file_path))

    # 如果目标文件已存在，避免覆盖，添加编号
    counter = 1
    while os.path.exists(new_path):
        base, ext = os.path.splitext(file_path)
        new_path = os.path.join(failed_dir, f"{os.path.basename(base)}_{counter}{ext}")
        counter += 1

    shutil.move(file_path, new_path)
    print(f"🚨 无法读取元数据，已移动到失败目录: {new_path}")


def rename_font_files_in_directory(directory):
    """遍历目录中的所有字体文件，并重命名（严格区分大小写），无法解析的移动到 `failed_fonts/`"""
    failed_dir = os.path.join(directory, "failed_fonts")  # 失败文件存放路径

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        # 确保大小写敏感匹配字体扩展名
        ext = os.path.splitext(file_name)[1]  # 获取扩展名
        if os.path.isfile(file_path) and ext in FONT_EXTENSIONS:
            font_name = get_font_name(file_path)
            if font_name:
                new_file_name = f"{font_name}{ext}"
                new_file_path = os.path.join(directory, new_file_name)

                # **强制重命名，即使大小写不同**
                if new_file_name != file_name:
                    os.rename(file_path, new_file_path)
                    print(f"✅ 已重命名: {file_name} → {new_file_name}")
                else:
                    print(f"🔹 文件已正确命名: {file_name}，无需修改")
            else:
                move_failed_font(file_path, failed_dir)  # 移动无法读取的字体文件


# 运行重命名
current_directory = os.getcwd()  # 获取当前目录
rename_font_files_in_directory(current_directory)
