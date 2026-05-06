from btree import BTree

class BStarTree(BTree):
    def __init__(self, d):
        super().__init__(d)
        self.redistribution_count = 0
        self.split_2to3_count = 0

    def _max_keys(self):
        return 2 * self.d - 1

    # def _min_keys_bstar(self):
    #     # for B*-tree, min keys is 2/3 of max keys
    #     return (2 * self._max_keys()) // 3

    def insert(self, key, rid):
        if self.search(key) is not None:
            return

        if len(self.root.keys) >= self._max_keys(): # root split은 일반 B-tree split 사용
            old_root = self.root
            new_root = type(old_root)(leaf=False)
            new_root.child.append(old_root)
            self.root = new_root
            self.node_count += 1
            self._split_children(new_root, 0) 

        self._insert_non_full(self.root, key, rid)

    def _insert_non_full(self, node, key, rid):
        if node.leaf:
            i = len(node.keys)
            node.keys.append(None)
            node.rids.append(None)
            while i > 0 and key < node.keys[i - 1]:
                node.keys[i] = node.keys[i - 1]
                node.rids[i] = node.rids[i - 1]
                i -= 1
            node.keys[i] = key
            node.rids[i] = rid
            return
        i = len(node.keys)
        while i > 0 and key < node.keys[i - 1]:
            i -= 1
        if len(node.child[i].keys) >= self._max_keys():
            if self._try_redistribute(node, i):
                self.redistribution_count += 1
            else:
                self._split_2to3(node, i)

            i = len(node.keys) 
            while i > 0 and key < node.keys[i - 1]: # redistribution 또는 split 후 다시 내려갈 child 계산
                i -= 1

            if len(node.child[i].keys) >= self._max_keys(): # 재계산된 child가 아직 full이면 안전하게 일반 split
                self._split_children(node, i)
                if key > node.keys[i]:
                    i += 1

        self._insert_non_full(node.child[i], key, rid)

    def _try_redistribute(self, parent, child_index):
        if child_index > 0:
            if len(parent.child[child_index - 1].keys) < self._max_keys():
                self._redistribute(parent, child_index - 1)
                return True

        if child_index + 1 < len(parent.child):
            if len(parent.child[child_index + 1].keys) < self._max_keys():
                self._redistribute(parent, child_index)
                return True

        return False

    def _redistribute(self, parent, left_idx):
        left = parent.child[left_idx]
        right = parent.child[left_idx + 1]

        all_keys = left.keys + [parent.keys[left_idx]] + right.keys
        all_rids = left.rids + [parent.rids[left_idx]] + right.rids

        split_idx = len(all_keys) // 2

        left.keys = all_keys[:split_idx]
        left.rids = all_rids[:split_idx]

        parent.keys[left_idx] = all_keys[split_idx]
        parent.rids[left_idx] = all_rids[split_idx]

        right.keys = all_keys[split_idx + 1:]
        right.rids = all_rids[split_idx + 1:]

        if not left.leaf:
            all_children = left.child + right.child
            left.child = all_children[:len(left.keys) + 1]
            right.child = all_children[len(left.keys) + 1:]

    def _split_2to3(self, parent, child_index):
        if child_index + 1 < len(parent.child):
            left_idx = child_index
            right_idx = child_index + 1
        else:
            left_idx = child_index - 1
            right_idx = child_index

        left = parent.child[left_idx]
        right = parent.child[right_idx]
        new_node = type(left)(leaf=left.leaf)

        if left.leaf:
            self._split_2to3_leaf(parent, left_idx, left, right, new_node)
        else:
            self._split_2to3_internal(parent, left_idx, left, right, new_node)

        parent.child.insert(right_idx + 1, new_node)

        self.node_count += 1
        self.split_count += 1
        self.split_2to3_count += 1

    def _split_2to3_leaf(self, parent, left_idx, left, right, new_node):
        all_keys = left.keys + [parent.keys[left_idx]] + right.keys
        all_rids = left.rids + [parent.rids[left_idx]] + right.rids

        sep1_idx = len(all_keys) // 3
        sep2_idx = (2 * len(all_keys)) // 3

        left.keys = all_keys[:sep1_idx]
        left.rids = all_rids[:sep1_idx]

        parent.keys[left_idx] = all_keys[sep1_idx]
        parent.rids[left_idx] = all_rids[sep1_idx]

        right.keys = all_keys[sep1_idx + 1:sep2_idx]
        right.rids = all_rids[sep1_idx + 1:sep2_idx]

        parent.keys.insert(left_idx + 1, all_keys[sep2_idx])
        parent.rids.insert(left_idx + 1, all_rids[sep2_idx])

        new_node.keys = all_keys[sep2_idx + 1:]
        new_node.rids = all_rids[sep2_idx + 1:]

    def _split_2to3_internal(self, parent, left_idx, left, right, new_node):
        all_keys = left.keys + [parent.keys[left_idx]] + right.keys
        all_rids = left.rids + [parent.rids[left_idx]] + right.rids
        all_children = left.child + right.child

        sep1_idx = len(all_keys) // 3
        sep2_idx = (2 * len(all_keys)) // 3

        left.keys = all_keys[:sep1_idx]
        left.rids = all_rids[:sep1_idx]
        left.child = all_children[:sep1_idx + 1]

        parent.keys[left_idx] = all_keys[sep1_idx]
        parent.rids[left_idx] = all_rids[sep1_idx]

        right.keys = all_keys[sep1_idx + 1:sep2_idx]
        right.rids = all_rids[sep1_idx + 1:sep2_idx]
        right.child = all_children[sep1_idx + 1:sep2_idx + 1]

        parent.keys.insert(left_idx + 1, all_keys[sep2_idx])
        parent.rids.insert(left_idx + 1, all_rids[sep2_idx])

        new_node.keys = all_keys[sep2_idx + 1:]
        new_node.rids = all_rids[sep2_idx + 1:]
        new_node.child = all_children[sep2_idx + 1:]

    def delete(self, key): # delete는 B-tree deletion 사용
        return super().delete(key)

    def validate(self):
        return super().validate()