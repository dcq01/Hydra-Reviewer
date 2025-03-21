from Agent import *
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

import re
import json_and_jsonl_handler as jh


def run_agent_with_retry(agent, patch, progress=None, max_retries=100, function_calling_flag=True):
    retries = 0
    while retries <= max_retries:
        try:
            if hasattr(agent, 'using_function_calling'):
                agent.using_function_calling(function_calling_flag)
            result = agent.run_graph(patch)
            if progress:
                progress.update(1)
            return result
        except Exception as e:
            error_message = str(e)
            if "context_length_exceeded" in error_message:
                print(f"Critical error in {agent.__name__}: {error_message}")
                raise

            print(f"\nAgent {agent.__name__} failed with error: {e}")
            retries += 1
            if retries > max_retries:
                raise
            print(f"\nRetrying {agent.__name__}... Attempt {retries}")


def renumber_suggestions(text):
    lines = text.split('\n')
    suggestion_count = 1

    for i in range(len(lines)):
        # Check if the line starts with a number followed by a dot and a space
        if re.match(r'^\d+\.', lines[i]):
            # Replace the starting number with the suggestion_count
            lines[i] = re.sub(r'^\d+\.', f'{suggestion_count}.', lines[i], 1)
            suggestion_count += 1

    return '\n'.join(lines)


def get_review_comment(patch_with_additional_information):
    with tqdm(total=17, desc="Processing Agents") as pbar:
        with ThreadPoolExecutor(max_workers=17) as executor:
            futures = [
                executor.submit(run_agent_with_retry, code_semantic_correctness_agent,
                                patch_with_additional_information, progress=pbar),
                executor.submit(run_agent_with_retry, code_syntax_correctness_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, security_compliance_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, programming_handling_conventions_agent,
                                patch_with_additional_information, progress=pbar),
                executor.submit(run_agent_with_retry, identifier_naming_style_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, code_formatting_style_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, comment_style_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, identifier_naming_readability_agent,
                                patch_with_additional_information, progress=pbar),
                executor.submit(run_agent_with_retry, code_logic_readability_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, comment_quality_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, redundancy_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, compatibility_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, name_and_logic_consistency_agent,
                                patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, fault_tolerance_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, code_testing_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, extensibility_agent, patch_with_additional_information,
                                progress=pbar),
                executor.submit(run_agent_with_retry, performance_agent,
                                patch_with_additional_information, progress=pbar)
            ]

            results = [future.result() for future in futures]
            input_comment = patch_with_additional_information
            count = 1
            for result in results:
                input_comment += "{comment" + str(count) + "}:\n" + result + "\n"
                count += 1
            print(input_comment)
            print("-" * 80)
            summary_comment = run_agent_with_retry(summarizer_agent, input_comment, None)
            summarizer_clean_up_input = patch_with_additional_information + '\n{comments}:\n' + summary_comment
            clean_up_comment = run_agent_with_retry(summarizer_clean_up_agent, summarizer_clean_up_input, None)
            rerank_comment = run_agent_with_retry(suggestions_rerank_agent, clean_up_comment, None)
            final_comment = renumber_suggestions(rerank_comment)
            return input_comment, summary_comment, clean_up_comment, final_comment


if __name__ == "__main__":
    # 1. Use`pip install -r requirements.txt` to install required libraries.
    # 2. Fill in OPENAI_API_KEY, OPENAI_API_BASE, and OPENAI_GPT_MODEL in Agent/__init__.py
    # 3. Specify the datas_path (jsonl)
    # 4. Run the function

    datas_path = r''
    datas = jh.read_jsonl_file(datas_path)
    data = datas[0]
    print('Data loaded successfully.')

    # Context Retrieval
    patch_with_additional_information = get_additional_information_agent.get_additional_information(data)

    # Comment Generation
    input_comment, summary_comment, clean_up_comment, final_comment = get_review_comment(
        patch_with_additional_information)
    print("-" * 80)
    print(final_comment)
