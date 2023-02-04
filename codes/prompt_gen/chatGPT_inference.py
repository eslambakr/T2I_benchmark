"""
Generate the real text prompt which will be fed to text-2-image models based on the fed meta-prompt.
"""
from meta_prompt_gen import MetaPromptGen
import openai
import datetime
from tqdm import tqdm
import csv


def run_chatgpt(model, temp, meta_prompt, max_tokens):
    # Set your API key
    # openai.api_key = "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"
    openai.api_key = "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"
    # Define the parameters for the text generation
    prompt = "In one sentence, describe a real outdoor scene about transportations and people."
    completions = openai.Completion.create(engine=model, prompt=meta_prompt, max_tokens=max_tokens, n=1, stop=None,
                                           temperature=temp)
    gen_prompt = completions.choices[0].text.strip().lower()
    # Print the generated text
    print("The meta prompt is: ", meta_prompt)
    print("ChatGPT output is: ", gen_prompt)
    return gen_prompt


def save_lst_strings_to_txt(saving_txt, lst_str):
    file = open(saving_txt, 'w')
    for item in lst_str:
        file.write(item + "\n")
    file.close()


def save_prompts_in_csv(lst, saving_name):
    # Save output in csv:
    keys = lst[0].keys()
    with open(saving_name, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(lst)


def wait_one_n_mins(n_mins=1):
    endTime = datetime.datetime.now() + datetime.timedelta(minutes=n_mins)
    while True:
        if datetime.datetime.now() >= endTime:
            break


if __name__ == '__main__':
    meta_prompt_gen = MetaPromptGen(ann_path="../../data/metrics/det/lvis_v1/lvis_v1_train.json",
                                    label_space_path="../eval_metrics/detection/UniDet-master/datasets/label_spaces/learned_mAP+M.json",
                                    )
    num_prompts = 1500
    skill = "counting"
    generated_txt = []
    for i in tqdm(range(num_prompts)):
        template = meta_prompt_gen.gen_meta_prompts(level_id=int(i // (num_prompts / 3)), skill=skill)
        if int(i // (num_prompts / 3)) == 2 and skill == "fidelity":
            max_tokens = 50
        else:
            max_tokens = 40

        chatgpt_out = run_chatgpt(model="text-davinci-003", temp=0.5, meta_prompt=template, max_tokens=max_tokens)
        if skill == "writing":
            if int(i // (num_prompts / 3)) == 2:  # Hard level
                final_prompt = "a real scene of {place} with a sign written on it {chatgpt_out}".format(
                    place=meta_prompt_gen.select_rand_place(), chatgpt_out=chatgpt_out)
            else:  # Easy & Medium levels
                final_prompt = "a sign written on it {chatgpt_out}".format(
                    place=meta_prompt_gen.select_rand_place(), chatgpt_out=chatgpt_out)
        else:
            final_prompt = chatgpt_out
        generated_txt.append({"meta_prompt": template, "synthetic_prompt": final_prompt})

        if i % 15 == 0:
            wait_one_n_mins(n_mins=1)  # wait one minute to not exceed the openai limits

    # save_lst_strings_to_txt(saving_txt="synthetic_" + skill + "_prompts.txt", lst_str=generated_txt)
    save_prompts_in_csv(lst=generated_txt, saving_name="synthetic_" + skill + "_prompts.csv")
    print("Done")