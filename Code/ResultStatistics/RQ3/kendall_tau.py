import numpy as np
import json_and_jsonl_handler as jh

from scipy.stats import kendalltau

gpt_comments_path = r'D:\咳咳\Code Review\dataset\hydra_single_comments.jsonl'
variant3_comments_path = r'D:\咳咳\Code Review\dataset\variant3_single_comments.jsonl'
patches_path = r'D:\咳咳\Code Review\dataset\ablation_variants_comments.jsonl'

gpt_comments = jh.read_jsonl_file(gpt_comments_path)
variant3_comments = jh.read_jsonl_file(variant3_comments_path)
patches = jh.read_jsonl_file(patches_path)

priority = {
    'Fault Tolerance': 1,
    'Code Semantic Correctness': 2,
    'Compatibility': 3,
    'Performance': 4,
    'Security Compliance': 5,
    'Comment Quality': 6,
    'Identifier Naming Style': 7,
    'Code Formatting Style': 8,
}


def get_kendal_tau(actual_list):
    expected_list = sorted(actual_list)
    actual_ranks = np.argsort(actual_list).argsort() + 1
    expected_ranks = np.argsort(expected_list).argsort() + 1
    tau, p = kendalltau(actual_ranks, expected_ranks)
    return tau, p


# IDs of patches with inconsistent number of suggestions before and after processing by Ranker
inconformity_list = [8258, 7467, 15841, 12390, 15270, 12593, 3695, 12209, 17934]


def get_avg_tau(comments):
    tau_sum = 0
    p_sum = 0
    tmp_count = 0
    for i, patch in enumerate(patches):
        if i == 384:
            break
        patch_id = patch['id']
        if patch_id not in inconformity_list:
            dimension_list = []
            for comment in comments:
                if comment['id'] == patch_id:
                    dimensions = comment['dimension'].split('、')
                    max_dimension = 9
                    for dimension in dimensions:
                        if dimension in priority:
                            value = priority[dimension]
                            if value < max_dimension:
                                max_dimension = value
                    dimension_list.append(max_dimension)
            if len(dimension_list) != 0:
                tau, p = get_kendal_tau(dimension_list)
                tau_sum += tau
                p_sum += p
                if p < 0.05:
                    tmp_count += 1
    print(tmp_count)
    return tau_sum / (384 - len(inconformity_list)), p_sum / (384 - len(inconformity_list))


a, ap = get_avg_tau(gpt_comments)
b, bp = get_avg_tau(variant3_comments)
print('Hydra-Reviewer_kendal_tau:', round(a, 3))
print('variant3_kendal_tau:', round(b, 3))

count = 0
for i, patch in enumerate(patches):
    if i == 384:
        break
    gpt_dimension_list = []
    variant3_dimension_list = []
    for gpt_comment in gpt_comments:
        if gpt_comment['id'] == patch['id']:
            dimensions = gpt_comment['dimension'].split('、')
            max_dimension = 9
            for dimension in dimensions:
                if dimension in priority:
                    value = priority[dimension]
                    if value < max_dimension:
                        max_dimension = value
            gpt_dimension_list.append(max_dimension)
    for variant3_comment in variant3_comments:
        if variant3_comment['id'] == patch['id']:
            dimensions = variant3_comment['dimension'].split('、')
            max_dimension = 9
            for dimension in dimensions:
                if dimension in priority:
                    value = priority[dimension]
                    if value < max_dimension:
                        max_dimension = value
            variant3_dimension_list.append(max_dimension)
    if gpt_dimension_list != [] and variant3_dimension_list != []:
        tau1, p1 = get_kendal_tau(gpt_dimension_list)
        tau2, p2 = get_kendal_tau(variant3_dimension_list)
        if tau1 > tau2:
            count += 1

print('count:', count)
# Number of patches where Hydra-Reviewer has a higher Kendall Tau than variant3
