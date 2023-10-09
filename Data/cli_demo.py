import os
import torch
import platform
import subprocess
from colorama import Fore, Style
from tempfile import NamedTemporaryFile
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.utils import GenerationConfig
import openpyxl
import time

# 本地测试路径
cur_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
orgin_data_path = os.path.join(cur_path,"电销会话明细2_2.xlsx")

#def init_model():
#    print("init model ...")
#    model = AutoModelForCausalLM.from_pretrained(
#        "/data1/duxinfeng/YxProjects/yxLLM/Baichuan/Baichuan2-7B-Chat",
#        torch_dtype=torch.float16,
#        device_map="auto",
#        trust_remote_code=True
#    )
#    model.generation_config = GenerationConfig.from_pretrained(
#        "/data1/duxinfeng/YxProjects/yxLLM/Baichuan/Baichuan2-7B-Chat"
#    )
#    tokenizer = AutoTokenizer.from_pretrained(
#        "/data1/duxinfeng/YxProjects/yxLLM/Baichuan/Baichuan2-7B-Chat",
#        use_fast=False,
#        trust_remote_code=True
#    )
#    return model, tokenizer
#'''

#'''
# 10-07 微调模型
#/data1/duxinfeng/YxProjects/yxLLM/Baichuan/Baichuan2/fine-tune/output/Baichuan2-7B-Chat

def init_model():
    print("init model ...")
    model = AutoModelForCausalLM.from_pretrained(
        "/data1/duxinfeng/YxProjects/yxLLM/Baichuan/Baichuan2/fine-tune/output_10_08/Baichuan2-7B-Chat",
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    model.generation_config = GenerationConfig.from_pretrained(
        "/data1/duxinfeng/YxProjects/yxLLM/Baichuan/Baichuan2/fine-tune/output_10_08/Baichuan2-7B-Chat"
    )
    tokenizer = AutoTokenizer.from_pretrained(
        "/data1/duxinfeng/YxProjects/yxLLM/Baichuan/Baichuan2/fine-tune/output_10_08/Baichuan2-7B-Chat",
        use_fast=False,
        trust_remote_code=True
    )
    return model, tokenizer

# '''

#'''
#def init_model():
#    print("init model ...")
#    model = AutoModelForCausalLM.from_pretrained(
#        "baichuan-inc/Baichuan2-13B-Chat",
#        torch_dtype=torch.float16,
#        device_map="auto",
#        trust_remote_code=True
#    )
#    model.generation_config = GenerationConfig.from_pretrained(
#        "baichuan-inc/Baichuan2-13B-Chat"
#    )
#    tokenizer = AutoTokenizer.from_pretrained(
#        "baichuan-inc/Baichuan2-13B-Chat",
#        use_fast=False,
#        trust_remote_code=True
#    )
#    return model, tokenizer
#'''

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    print(Fore.YELLOW + Style.BRIGHT + "欢迎使用百川大模型，输入进行对话，vim 多行输入，clear 清空历史，CTRL+C 中断生成，stream 开关流式生成，exit 结束。")
    return []


def vim_input():
    with NamedTemporaryFile() as tempfile:
        tempfile.close()
        subprocess.call(['vim', '+star', tempfile.name])
        text = open(tempfile.name).read()
    return text

prompt_list = []

def main(stream=False):
    
    print(orgin_data_path)
    
    # 选择工作表
    workbook = openpyxl.load_workbook(orgin_data_path)
    sheet = workbook['Sheet1']

    for row_line in sheet.iter_rows(min_row=2, max_row=108,values_only=True):
        #print(row_line[0])
        prompt_str = f"以下是一段机器人（bot）和客户（user）的电销通话记录：\n'''\n{row_line[0]}\n''''\n仔细阅读上述对话，判断客户是否有车辆融资业务需求意向，你的回答应该为 有意向/无意向/意向不明 中的一种，只给结论不用解释，请全程用中文回答问题。"
        print(prompt_str)
        prompt_list.append(prompt_str)
        print("-----")
    print(len(prompt_list))

    
    model, tokenizer = init_model()
    messages = clear_screen()
    
    # 获取当前时间戳
    start_time = time.time()    

    for idx, prompt in enumerate(prompt_list):
        messages.append({"role": "user", "content": prompt})
        if stream:
            position = 0
            try:
                #print(f"idx:{idx+2}")
                for response in model.chat(tokenizer, messages, stream=True):
                    print(response[position:], end='', flush=True)
                    position = len(response)
                    if torch.backends.mps.is_available():
                        torch.mps.empty_cache()
            except KeyboardInterrupt:
                pass
            print()
        else:
            response = model.chat(tokenizer, messages)
            print(response)
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
        messages.append({"role": "assistant", "content": response})
    # 获取循环结束后的时间戳
    end_time = time.time()
    print(Style.RESET_ALL)
    print(end_time - start_time)
    '''
    while True:
        prompt = input(Fore.GREEN + Style.BRIGHT + "\n用户：" + Style.NORMAL)
        if prompt.strip() == "exit":
            break
        if prompt.strip() == "clear":
            messages = clear_screen()
            continue
        if prompt.strip() == 'vim':
            prompt = vim_input()
            print(prompt)
        print(Fore.CYAN + Style.BRIGHT + "\nBaichuan 2：" + Style.NORMAL, end='')
        if prompt.strip() == "stream":
            stream = not stream
            print(Fore.YELLOW + "({}流式生成)\n".format("开启" if stream else "关闭"), end='')
            continue
        messages.append({"role": "user", "content": prompt})
        if stream:
            position = 0
            try:
                for response in model.chat(tokenizer, messages, stream=True):
                    print(response[position:], end='', flush=True)
                    position = len(response)
                    if torch.backends.mps.is_available():
                        torch.mps.empty_cache()
            except KeyboardInterrupt:
                pass
            print()
        else:
            response = model.chat(tokenizer, messages)
            print(response)
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
        messages.append({"role": "assistant", "content": response})
    '''
    print(Style.RESET_ALL)
    

if __name__ == "__main__":
    main()
