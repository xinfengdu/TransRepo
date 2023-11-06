import pandas as pd
import json
import time
import os
import datetime

# 获取当前日期和时间
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d")
print(current_datetime)

# 读取、存储路径
cur_path = os.path.abspath(os.path.dirname(__file__))
cur_path = './'
# origin_file_path = r"合并文本摘要数据清洗.xlsx"
origin_file_path = r"./gpt.xlsx"
save_path = os.path.join(cur_path, current_datetime+"_tune.json")

def generate_fine_tune_json(origin_file_path,save_path):
    """
    根据提取的摘要数据生成微调数据
    :param origin_file_path:
    :param save_path:
    :return:
    """

    tune_list = []
    conversations = []

    # 读取电销对话意向识别文件
    df = pd.read_excel(origin_file_path, sheet_name='Sheet1', engine='openpyxl')
    # 获取对话列和一致列以及意向列
    dialogs = df['对话内容'].tolist()
    # problemDescs = df['问题描述清洗'].tolist()
    problemDescs = df['GPT结果'].tolist()

    # 循环一致列，如果一致列中值不等于0，提取对话列中的对话
    with open('tune.json', mode="w", encoding='utf-8') as f:
        for index, dialog in enumerate(dialogs):
            print(index,dialogs[index])
            prompt = f"""你是金牌坐席，你的任务是与用户通话完毕后写一个会话摘要，要求最多120字。\n以下三个反引号之间的是通话记录，请对这通对话进行概括，重点关注会话内容、客户诉求，如通话中涉及具体金额、期数、日期等数据在概括中写明。\n通话记录: ```
            {dialogs[index]}
            ```
            """
            conversations = {"prompt": prompt, "response": problemDescs[index]}
            tune_list.append(conversations)

    # 将tune_list写入json文件
    with open(save_path, mode="w", encoding='utf-8') as f:
        f.write(json.dumps(tune_list, ensure_ascii=False, indent=4) + "\n")


if __name__ == "__main__":
    generate_fine_tune_json(origin_file_path,save_path)
