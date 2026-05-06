import csv
import os
import random
import time
from loader import load_data
from btree import BTree
from bplustree import BPlusTree
from bstartree import BStarTree
DATA_PATH = "data/student.csv"
RESULT_DIR = "results"
RESULT_PATH = "results/results.csv"
ADDITIONAL_RESULT_PATH = "results/additional_results.csv"

def main():
    records, key_to_rid = load_data(DATA_PATH)
    print("========== Data Loaded ==========")
    print("number of records:", len(records))
    print("number of keys:", len(key_to_rid))
    ids = [record["student_id"] for record in records]
    print(f"min id ~ max id: {min(ids)} ~ {max(ids)}")

    ensure_result_dir()
    write_header()
    write_additional_header()

    tree_classes = [
        ("B-tree", BTree),
        ("B+-tree", BPlusTree),
        ("B*-tree", BStarTree),
    ]

    for tree_type, TreeClass in tree_classes:
        for d in [3, 5, 10, 20, 50]:
            run_experiments(
                tree_type,
                TreeClass,
                records,
                key_to_rid,
                d
            )
    for tree_type, TreeClass in tree_classes:
        for d in [10]:
            run_additional_experiment(
                tree_type,
                TreeClass,
                records,
                d
            )
    
    print(f"\nResults saved to \"{RESULT_PATH}\"")
    print(f"Additional results saved to \"{ADDITIONAL_RESULT_PATH}\"")

def run_experiments(tree_type, TreeClass, records, key_to_rid, d):
    print(f"\n========== {tree_type}, d={d} ==========")
    tree, insert_time, utilization, height = insertion(
        TreeClass,
        records,
        d
    )
    search_query_count, avg_search_time = point_search(
        tree,
        records,
        key_to_rid,
        query_count=20000
    )
    range_count, range_time, avg_gpa = range_query(
        tree,
        records,
        start_key=202200000,
        end_key=202299999
    )
    delete_count, delete_time, is_valid = deletion(
        tree,
        records,
        delete_count=5000,
        sample_count=10000
    )
    redistribution_count = getattr(tree, "redistribution_count", 0)
    split_2to3_count = getattr(tree, "split_2to3_count", 0)

    save_results([
        tree_type, d, len(records),
        #insertion
        insert_time,
        tree.split_count,
        tree.node_count,
        utilization,
        height,
        #search
        search_query_count,
        avg_search_time,
        #range query
        range_count,
        range_time,
        avg_gpa,
        #deletion
        delete_count,
        delete_time,
        is_valid,
        #b*-tree specific
        redistribution_count,
        split_2to3_count
    ])

def insertion(TreeClass, records, d):
    print(f"-------- Insertion Experiment --------")
    tree = TreeClass(d=d)
    
    start = time.perf_counter()
    for rid, record in enumerate(records):
        tree.insert(record["student_id"], rid)
    end = time.perf_counter()
    insert_time = end - start

    utilization = tree.calculate_utilization()
    height = tree.calculate_height()

    print("insertion_time:", insert_time)
    print("split_count:", tree.split_count)
    print("node_count:", tree.node_count)
    print("utilization:", utilization)
    print("height:", height)
    print()
    return tree, insert_time, utilization, height

def point_search(tree, records, key_to_rid, query_count):
    print("-------- Point Search Experiment --------")
    query_count = min(query_count, len(records))
    sampled_records = random.sample(records, query_count)
    start = time.perf_counter()
    search_error_count = 0

    for record in sampled_records:
        key = record["student_id"]
        expected_rid = key_to_rid[key]
        result_rid = tree.search(key)

        if result_rid != expected_rid:
            search_error_count += 1
            print(f"ERROR: key={key}, result={result_rid}, expected={expected_rid}")
    end = time.perf_counter()
    avg_search_time = (end-start) / query_count

    print("query_count:", query_count)
    print("avg_search_time:", avg_search_time)
    print("search_error_count:", search_error_count)
    print()
    return query_count, avg_search_time

def range_query(tree, records, start_key, end_key):
    print("-------- Range Query Experiment --------")
    start = time.perf_counter()
    rids = tree.range_query(start_key, end_key)
    selected = [
        records[rid]
        for rid in rids
        if (records[rid]["gender"] == "Male" and 
            records[rid]["height"] <= 170 and 
            records[rid]["weight"] >= 80)
    ]

    if len(selected) == 0:
        avg_gpa = 0
    else:
        avg_gpa = sum(r["gpa"] for r in selected) / len(selected)
    end = time.perf_counter()
    range_time = end - start
    range_count = len(selected)

    print("range:", start_key, "~", end_key)
    print("result_count:", range_count)
    print("range_time:", range_time)
    print("avg_gpa:", avg_gpa)
    print()
    return range_count, range_time, avg_gpa

def deletion(tree, records, delete_count, sample_count):
    print("-------- Delete Experiment --------")
    delete_count = min(delete_count, len(records))
    delete_records = random.sample(records, delete_count)
    delete_keys = [record["student_id"] for record in delete_records]
    delete_set = set(delete_keys)

    start = time.perf_counter()
    for key in delete_keys:
        tree.delete(key)
    end = time.perf_counter()
    delete_time = end - start

    delete_error_count = 0
    # 1. 삭제한 key가 정말 사라졌는지 확인
    for key in delete_keys:
        if tree.search(key) is not None:
            delete_error_count += 1
            print(f"ERROR: deleted key still found: {key}")
    # 2. 삭제하지 않은 key들이 여전히 검색되는지 확인
    remaining_records = [
        record for record in records
        if record["student_id"] not in delete_set
    ]
    sample_count = min(sample_count, len(remaining_records))
    sampled = random.sample(remaining_records, sample_count)
    for record in sampled:
        key = record["student_id"]
        result = tree.search(key)
        if result is None:
            delete_error_count += 1
            print(f"ERROR: remaining key not found: {key}")
    is_valid = tree.validate()
    print("delete_count:", delete_count)
    print("delete_time:", delete_time)
    print("delete_error_count:", delete_error_count)
    print("tree_validation:", is_valid)
    
    return delete_count, delete_time, is_valid

def run_additional_experiment(tree_type, TreeClass, records, d):
    print(f"\n========== Additional Experiment: {tree_type}, d={d} ==========")
    print("-------- Insertion Order Sensitivity Experiment --------")
    ordered_record_sets = make_insertion_orders(records)
    for order_name, ordered_records in ordered_record_sets.items():
        tree = TreeClass(d=d)
        start = time.perf_counter()
        for rid, record in enumerate(ordered_records):
            tree.insert(record["student_id"], rid)
        end = time.perf_counter()
        insert_time = end - start

        split_count = tree.split_count
        node_count = tree.node_count
        utilization = tree.calculate_utilization()
        height = tree.calculate_height()
        redistribution_count = getattr(tree, "redistribution_count", 0)
        split_2to3_count = getattr(tree, "split_2to3_count", 0)
        is_valid = tree.validate()

        print("order:", order_name)
        print("insert_time:", insert_time)
        print("split_count:", split_count)
        print("node_count:", node_count)
        print("utilization:", utilization)
        print("height:", height)
        print("tree_validation:", is_valid)

        save_additional_results([
            tree_type,
            d,
            order_name,
            len(ordered_records),
            insert_time,
            split_count,
            node_count,
            utilization,
            height,
            redistribution_count,
            split_2to3_count,
            is_valid
        ])

def make_insertion_orders(records):
    sorted_records = sorted(records, key=lambda r: r["student_id"])
    reverse_sorted_records = list(reversed(sorted_records))
    random_records = records[:]
    random.shuffle(random_records)
    return {
        "sorted": sorted_records,
        "reverse_sorted": reverse_sorted_records,
        "random": random_records
    }

def ensure_result_dir():
    os.makedirs(RESULT_DIR, exist_ok=True)

def write_header():
        with open(RESULT_PATH, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "tree_type", "d", "num_records",
                #insertion
                "insert_time", "split_count", "node_count", "utilization", "height",
                #search
                "search_query_count", "avg_search_time",
                #range query
                "range_result_count", "range_time", "range_avg_gpa",
                #deletion
                "delete_count", "delete_time", "tree_validation",
                #b*-tree specific
                "redistribution_count", "split_2to3_count"
            ])

def write_additional_header():
    with open(ADDITIONAL_RESULT_PATH, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "tree_type",
            "d",
            "insertion_order",
            "num_records",
            "insert_time",
            "split_count",
            "node_count",
            "utilization",
            "height",
            "redistribution_count",
            "split_2to3_count",
            "tree_validation"
        ])

def save_results(row):
    with open(RESULT_PATH, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(row)

def save_additional_results(row):
    with open(ADDITIONAL_RESULT_PATH, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(row)

if __name__ == "__main__":
    main()