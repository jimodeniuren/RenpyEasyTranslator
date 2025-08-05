from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
from tqdm import tqdm
import re

def split_into_chunks(file_content, chunk_size):
    # 使用正则表达式匹配翻译块
    # translation_block_start = re.compile(r'^# game.*\ntranslate schinese .*:\n$')

    lines = file_content.split("# game")
    lines = [lines[0]] + ["# game" + line.replace(r'\n', '') for line in lines[1:]]
    merged_list = []

    # 使用步长为3的切片遍历列表
    for i in range(0, len(lines), chunk_size):
        # 取出当前的三个元素
        chunk = lines[i:i + chunk_size]
        # 用换行符合并这三个元素，并添加到结果列表中
        merged_list.append('\n'.join(chunk))
    return merged_list


def deal_file(raw_file_path):
    try:
        with open("./finished_file_list.txt", 'r', encoding="utf-8") as finif:
            finished_file_list = finif.readlines()
            finished_file_list = [f.strip() for f in finished_file_list]
            if raw_file_path in finished_file_list:
                print(f"{raw_file_path}" + "已经被标记为完成，跳过")
                return
    except:
        pass
    error_cnt = 0
    cnt = 0
    # 读取本地文件的内容
    with open(raw_file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # 分块
    chunks = split_into_chunks(file_content, 5)
    results = []
    last_result = ""

    for chunk in tqdm(chunks):
        js_script = f"""
                var inputBox = document.querySelector('div[contenteditable="true"][role="textbox"]');
                var outputBox = document.querySelector('d-textarea[name="target"] div[contenteditable="true"]');
                var textToCopy = `{chunk}`;

                // 设置输入框的内容
                inputBox.innerHTML = textToCopy;

                // 创建并触发input事件以确保网站检测到变化
                var event = new Event('input', {{ bubbles: true }});
                inputBox.dispatchEvent(event);

                // setTimeout(function() {{
                // var result = outputBox.innerHTML;
                // console.log("输出结果: " + result);
                // }}, 60000);
                """
        global browser
        browser.get(url)
        browser.refresh()
        if cnt%150 == 0:
            browser = webdriver.Chrome(options=options)
            browser.get(url)
            browser.refresh()
        try:
            browser.execute_script(index_content)
            browser.execute_script(js_script)
        except:
            browser = webdriver.Chrome(options=options)
            browser.get(url)
            browser.refresh()
            browser.execute_script(index_content)
            browser.execute_script(js_script)

        output_box = None
        result = ""
        start_time = time.time()
        while not output_box or not '#' in result[:5] or result == last_result:
            try:
                output_box = browser.find_element("css selector", 'd-textarea[name="target"] div[contenteditable="true"]')
                result = output_box.get_attribute('innerHTML')
            except:
                pass
            finally:
                time.sleep(0.05)
                if time.time() - start_time > 20:
                    result = chunk
                    error_cnt +=1
                    break
        if error_cnt > max(len(chunks) // 20, 4):
            with open("./error_file_list.txt", 'a', encoding="utf-8") as errf:
                print(raw_file_path + "处理失败，可能已经被限速，请稍后重试")
                errf.write(f"{raw_file_path}\n")
                return
        last_result = result
        results.append(result)
        cnt +=1

    # 合并所有结果并写入文件
    final_result = '\n'.join(results)
    lines = final_result.split('\n')
    # 保留不包含连续两个双引号的行
    filtered_lines = [line for line in lines if '""' not in line]
    # 将过滤后的行重新组合成字符串
    final_result = '\n'.join(filtered_lines)
    with open(raw_file_path, "w", encoding='utf-8') as f:
        print(raw_file_path + " 处理完成！")
        f.write(final_result)
    with open("./finished_file_list.txt", 'a', encoding="utf-8") as finif:
        finif.write(f"{raw_file_path}\n")

    # print("避免速率过快，暂停一会儿。。。")
    # time.sleep(300)

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

if __name__ == "__main__":
    path = "C:XXXXXXXXXXXX/aa"	# 替换为要翻译的文件所在的路径
    url = 'https://www.deepl.com/zh/translator#en/zh/'	# 默认英翻中，想翻别的语言可以把这里改一下
    with open('index.js', 'r', encoding='utf-8') as file:
        index_content = file.read()

    options = Options()
    options.add_argument("headless")
    # options.add_argument("--lang=zh-CN")
    finished = False
    while not finished:
        try:
            browser = webdriver.Chrome(options=options)
            rpy_files = find_rpy_files(path)

            for rpy_file in rpy_files:
                rpy_file = rpy_file.replace("\\", "/")
                print("开始处理：" + rpy_file)
                deal_file(rpy_file)
            finished = True
            browser.quit()
        except Exception as e:
            print(e)