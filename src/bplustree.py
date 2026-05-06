class BPlusTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.child = []
        self.rids = []
        self.next = None

class BPlusTree:
    def __init__(self, d):
        self.d = d
        self.root = BPlusTreeNode(leaf=True)
        self.split_count = 0
        self.node_count = 1

    def search(self, key):
        leaf = self._find_leaf(key)
        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.rids[i]
        return None

    def _find_leaf(self, key):
        node = self.root
        while not node.leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.child[i]
        return node
    
    def insert(self, key, rid):
        if self.search(key) is not None:
            return
        root = self.root

        if len(root.keys) == 2 * self.d - 1:
            new_root = BPlusTreeNode(leaf=False)
            new_root.child.append(root)
            self.root = new_root
            self.node_count += 1
            self._split_children(new_root, 0)
            self._insert_non_full(new_root, key, rid)
        else:
            self._insert_non_full(root, key, rid)

    def _insert_non_full(self, node, key, rid):
        if node.leaf:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            node.keys.insert(i, key)
            node.rids.insert(i, rid)

        else:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            child = node.child[i]
            if len(child.keys) == 2 * self.d - 1:
                self._split_children(node, i)
                if key >= node.keys[i]:
                    i += 1
            self._insert_non_full(node.child[i], key, rid)

    def _split_children(self, parent, child_index):
        child = parent.child[child_index]
        new_child = BPlusTreeNode(leaf=child.leaf)
        if child.leaf:
            mid = self.d
            new_child.keys = child.keys[mid:]
            new_child.rids = child.rids[mid:]
            child.keys = child.keys[:mid]
            child.rids = child.rids[:mid]

            new_child.next = child.next
            child.next = new_child
            promoted_key = new_child.keys[0]
            parent.keys.insert(child_index, promoted_key)
            parent.child.insert(child_index + 1, new_child)
        else:
            all_children = child.child
            child.child = all_children[:self.d]
            new_child.child = all_children[self.d:]
            self._refresh_keys(child)
            self._refresh_keys(new_child)
            promoted_key = self._get_min_key(new_child)
            parent.keys.insert(child_index, promoted_key)
            parent.child.insert(child_index + 1, new_child)
        self.split_count += 1
        self.node_count += 1

    def range_query(self, start_key, end_key):
        result_rids = []
        leaf = self._find_leaf(start_key)
        while leaf is not None:
            for key, rid in zip(leaf.keys, leaf.rids):
                if start_key <= key <= end_key:
                    result_rids.append(rid)
                elif key > end_key:
                    return result_rids
            leaf = leaf.next
        return result_rids

    def calculate_utilization(self):
        total_keys = 0
        total_capacity = 0
        def dfs(node):
            nonlocal total_keys, total_capacity
            total_keys += len(node.keys)
            total_capacity += 2 * self.d - 1
            if not node.leaf:
                for child in node.child:
                    dfs(child)
        dfs(self.root)
        if total_capacity == 0:
            return 0
        return total_keys / total_capacity

    def calculate_height(self):
        h = 0
        node = self.root
        while not node.leaf:
            h += 1
            node = node.child[0]
        return h

    def delete(self, key):
        deleted, xxx = self._delete_recursive(self.root, key, is_root=True)
        self._shrink_root()
        if not self.root.leaf:
            self._refresh_keys(self.root)
        return deleted
    
    def _delete_recursive(self, node, key, is_root=False):
        if node.leaf:
            for i, k in enumerate(node.keys):
                if k == key:
                    node.keys.pop(i)
                    node.rids.pop(i)
                    return True, self._is_underflow(node, is_root)
            return False, False
        idx = 0
        while idx < len(node.keys) and key >= node.keys[idx]:
            idx += 1
        deleted, child_underflow = self._delete_recursive(
            node.child[idx],
            key,
            is_root=False
        )

        if not deleted:
            return False, False
        if child_underflow:
            self._fix_underflow(node, idx)
        self._refresh_keys(node)
        underflow = self._is_underflow(node, is_root)
        return True, underflow

    def _refresh_keys(self, node):
        if node.leaf:
            return
        node.keys = []
        for i in range(1, len(node.child)):
            node.keys.append(self._get_min_key(node.child[i]))

    def _get_min_key(self, node):
        while not node.leaf:
            node = node.child[0]
        if len(node.keys) == 0:
            return None
        return node.keys[0]
    
    def _is_underflow(self, node, is_root=False):
        if is_root:
            return False
        min_keys = self.d - 1
        if node.leaf:
            return len(node.keys) < min_keys
        else:
            min_children = self.d
            return len(node.child) < min_children

    def _can_lend(self, node):
        if node.leaf:
            return len(node.keys) > self.d - 1
        else:
            return len(node.child) > self.d
    
    def _fix_underflow(self, parent, idx):
        if idx >= len(parent.child):
            idx = len(parent.child) - 1
        left = parent.child[idx - 1] if idx > 0 else None
        right = parent.child[idx + 1] if idx + 1 < len(parent.child) else None
        if left is not None and self._can_lend(left):
            self._borrow_from_left(parent, idx)
            return
        if right is not None and self._can_lend(right):
            self._borrow_from_right(parent, idx)
            return
        if left is not None:
            self._merge_nodes(parent, idx - 1)
        elif right is not None:
            self._merge_nodes(parent, idx)
        self._refresh_keys(parent)

    def _borrow_from_left(self, parent, idx):
        child = parent.child[idx]
        left = parent.child[idx - 1]
        if child.leaf:
            key = left.keys.pop()
            rid = left.rids.pop()
            child.keys.insert(0, key)
            child.rids.insert(0, rid)
        else:
            borrowed_child = left.child.pop()
            child.child.insert(0, borrowed_child)
            self._refresh_keys(left)
            self._refresh_keys(child)

        self._refresh_keys(parent)

    def _borrow_from_right(self, parent, idx):
        child = parent.child[idx]
        right = parent.child[idx + 1]
        if child.leaf:
            key = right.keys.pop(0)
            rid = right.rids.pop(0)
            child.keys.append(key)
            child.rids.append(rid)
        else:
            borrowed_child = right.child.pop(0)
            child.child.append(borrowed_child)
            self._refresh_keys(right)
            self._refresh_keys(child)
        self._refresh_keys(parent)

    def _merge_nodes(self, parent, left_idx):
        left = parent.child[left_idx]
        right = parent.child[left_idx + 1]
        if left.leaf:
            left.keys.extend(right.keys)
            left.rids.extend(right.rids)
            left.next = right.next
        else:
            left.child.extend(right.child)
            self._refresh_keys(left)
        parent.child.pop(left_idx + 1)
        self.node_count -= 1
        self._refresh_keys(parent)

    def _shrink_root(self):
        while not self.root.leaf and len(self.root.child) == 1:
            self.root = self.root.child[0]
            self.node_count -= 1

    def validate(self):
        leaf_depths = []
        def check(node, depth, is_root=False):
            # 1. key 정렬
            if any(node.keys[i - 1] >= node.keys[i] for i in range(1, len(node.keys))):
                return False
            # 2. max keys
            if len(node.keys) > 2 * self.d - 1:
                return False
            # 3. min 조건
            if not is_root:
                if node.leaf:
                    if len(node.keys) < self.d - 1:
                        return False
                else:
                    if len(node.child) < self.d:
                        return False
            # 4. leaf 처리
            if node.leaf:
                if len(node.keys) != len(node.rids):
                    return False
                leaf_depths.append(depth)
                return True
            # 5. internal node child 개수
            if len(node.child) != len(node.keys) + 1:
                return False
            # 6. separator key 확인
            for i in range(1, len(node.child)):
                if node.keys[i - 1] != self._get_min_key(node.child[i]):
                    return False
            # 7. 재귀
            return all(check(child, depth + 1) for child in node.child)
        if not check(self.root, 0, is_root=True):
            return False
        return len(set(leaf_depths)) == 1