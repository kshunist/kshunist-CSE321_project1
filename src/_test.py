#for debugging and testing

# def basic_test():
#     print("===== Basic Tree Test =====")
#     tree = BPlusTree(d=3)
#     data = [
#         (10, 0),
#         (20, 1),
#         (5, 2),
#         (6, 3),
#         (12, 4),
#         (30, 5),
#         (7, 6),
#         (17, 7),
#     ]
#     for key, rid in data:
#         tree.insert(key, rid)
#     for key, rid in data:
#         print(f"before delete|| key: {key}, search result: {tree.search(key)}, rid: {rid}")
#     print("before delete|| range query 6-17:", tree.range_query(6, 17))
#     tree.delete(6)
#     for key, rid in data:
#         print(f"after delete|| key: {key}, search result: {tree.search(key)}, rid: {rid}")
#     print("after delete|| range query 6-17:", tree.range_query(6, 17))
#     print("split_count:", tree.split_count)
#     print("node_count:", tree.node_count)
#     print("height:", tree.calculate_height())
#     print()

# def bstar_occupancy_test():
#     print("===== B*-Tree Occupancy Test =====")
#     tree = BStarTree(d=10)
#     keys = list(range(1, 1000))
#     random.shuffle(keys)
#     for key in keys:
#         tree.insert(key, key)

#     print("After insert")
#     print("Tree valid:", tree.validate())
#     print("split_count:", tree.split_count)
#     print("redistribution_count:", tree.redistribution_count)
#     print("node_count:", tree.node_count)
#     print("utilization:", tree.calculate_utilization())
#     print("height:", tree.calculate_height())

#     delete_keys = random.sample(keys, 100)
#     for key in delete_keys:
#         tree.delete(key)

#     print("After delete")
#     print("Tree valid:", tree.validate())
#     print("delete_redistribution_count:", getattr(tree, "delete_redistribution_count", 0))
#     print("merge_count:", getattr(tree, "merge_count", 0))
#     print("node_count:", tree.node_count)
#     print("utilization:", tree.calculate_utilization())
#     print("height:", tree.calculate_height())