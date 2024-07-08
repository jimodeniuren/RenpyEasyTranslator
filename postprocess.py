import os

import re


def process_text(text):
    # 去掉包含中文的大括号，只保留内容
    text = re.sub(r'\{[^{}]*[\u4e00-\u9fff]+[^{}]*\}', lambda m: m.group(0)[1:-1], text)

    # 特殊控制符号成对出现的处理
    def remove_unpaired_tags(text, tag):
        open_tag = f'{{{tag}}}'
        close_tag = f'{{/{tag}}}'
        open_count = text.count(open_tag)
        close_count = text.count(close_tag)

        if open_count != close_count:
            text = text.replace(open_tag, '')
            text = text.replace(close_tag, '')

        return text

    for tag in ['b', 'i', 'q', 'size']:
        text = remove_unpaired_tags(text, tag)

    # 去掉落单的大括号
    def remove_unpaired_braces(text):
        stack = []
        result = []
        for char in text:
            if char == '{':
                stack.append(len(result))
            elif char == '}':
                if stack:
                    stack.pop()
                else:
                    continue
            result.append(char)

        for index in reversed(stack):
            del result[index]

        return ''.join(result)

    text = remove_unpaired_braces(text)

    return text

def find_rpy_files(path):
    rpy_files = []
    # 遍历给定路径及其子目录中的所有文件和目录
    for root, dirs, files in os.walk(path):
        for file in files:
            # 检查文件扩展名是否为 .rpy
            if file.endswith('.rpy'):
                # 将符合条件的文件路径添加到列表中
                rpy_files.append(os.path.join(root, file))

    return rpy_files

def process_line(line):
    # 找到第一个和最后一个双引号的位置
    first_quote_index = line.find('"')
    last_quote_index = line.rfind('"')

    # 如果没有找到双引号，直接返回原行
    if first_quote_index == -1 or last_quote_index == -1 or first_quote_index == last_quote_index:
        return line

    # 保留第一个和最后一个双引号，其余替换成单引号
    new_line = (
        line[:first_quote_index + 1] +  # 保留第一个双引号及其之前的部分
        line[first_quote_index + 1:last_quote_index].replace('"', "'") +  # 替换中间部分的双引号
        line[last_quote_index:]  # 保留最后一个双引号及其之后的部分
    )

    return new_line

path = "E:/Downloads/StudentTransfer-8.0-pc/game/tl/schinese/story"

rpy_files = find_rpy_files(path)

for file_name in rpy_files:
    if os.path.isfile(file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(file_name, 'w', encoding='utf-8') as file:
            for line in lines:
                processed_line = process_line(line)
                processed_line = process_text(processed_line)
                file.write(processed_line)
    else:
        print(f"文件 {file_name} 不存在")
