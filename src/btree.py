class BTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.child = []
        self.rids = []

class BTree:
    def __init__(self, d):
        self.d = d
        self.root = BTreeNode(leaf=True)
        self.split_count = 0
        self.node_count = 1

    def search(self, key):
        node = self.root
        while True:
            i = 0
            while i < len(node.keys) and key > node.keys[i]: # node.keys에서 key가 위치 찾기
                i += 1
            if i < len(node.keys) and key == node.keys[i]:
                return node.rids[i]  # key가 있으면 RID 반환
            if node.leaf:
                return None # leaf면 None 반환
            node = node.child[i] # 아니면 child로 이동

    def insert(self, key, rid):
        if self.search(key) is not None: # check key is unique
            return
        root = self.root
        if len(root.keys) == 2 * self.d - 1: # root가 가득 찼으면 split
            new_root = BTreeNode(leaf=False)
            new_root.child.append(root)
            self.root = new_root
            self.node_count += 1
            self._split_children(new_root, 0)
            self._insert_non_full(new_root, key, rid) # non_full node에 insert
        else:
            self._insert_non_full(root, key, rid)

    def _insert_non_full(self, node, key, rid):
        i = len(node.keys) - 1
        if node.leaf: # leaf인 경우 key가 들어갈 위치 찾아 삽입
            node.keys.append(None)
            node.rids.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.rids[i + 1] = node.rids[i]
                i -= 1
            node.keys[i + 1] = key
            node.rids[i + 1] = rid
        else: # internal node인 경우 내려갈 child 찾기, child가 full이면 split, 다시 child로 이동
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.child[i].keys) == 2 * self.d - 1:
                self._split_children(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.child[i], key, rid)

    def _split_children(self, parent, child_index):
        d = self.d
        full_child = parent.child[child_index] # full child를 둘로 나누기
        new_child = BTreeNode(leaf=full_child.leaf)
        middle_key = full_child.keys[d - 1] # 중간 key를 parent로 올림
        middle_rid = full_child.rids[d - 1]
    
        new_child.keys = full_child.keys[d:] # 오른쪽 절반을 new_child로 이동
        new_child.rids = full_child.rids[d:]
        full_child.keys = full_child.keys[:d - 1] # 왼쪽 절반은 full_child에 남김
        full_child.rids = full_child.rids[:d - 1]

        if not full_child.leaf: # internal node면 child도 둘로 나누기
            new_child.child = full_child.child[d:]
            full_child.child = full_child.child[:d]

        parent.keys.insert(child_index, middle_key) 
        parent.rids.insert(child_index, middle_rid)
        parent.child.insert(child_index + 1, new_child)
        self.split_count += 1
        self.node_count += 1

    def calculate_utilization(self): # 전체 node의 # of key / 전체 node capacity
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
    
    def range_query(self, start_key, end_key):
        result_rids = []
        def inorder(node):
            i = 0
            while i < len(node.keys):
                if not node.leaf:
                    inorder(node.child[i])
                if start_key <= node.keys[i] <= end_key:
                    result_rids.append(node.rids[i])
                if node.keys[i] > end_key:
                    return
                i += 1
            if not node.leaf:
                inorder(node.child[i])
        inorder(self.root)
        return result_rids
    
    def delete(self, key):
        self._delete(self.root, key)
        if len(self.root.keys) == 0 and not self.root.leaf: # root가 비었고 child가 있으면 height를 줄임
            self.root = self.root.child[0]
            self.node_count -= 1

    def _delete(self, node, key):
        d = self.d
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and node.keys[i] == key: # case 1: key가 현재 node에 있는 경우
            if node.leaf:
                node.keys.pop(i)
                node.rids.pop(i)
            else:
                self._delete_internal_node(node, i)
            return
        
        if node.leaf: # case 2: key가 현재 node에 없는 경우
            return
        
        if len(node.child[i].keys) == d - 1: # 내려갈 child가 최소 key 개수만 가지고 있으면 먼저 fill
            self._fill_children(node, i)
            if i > len(node.keys):
                i -= 1
        self._delete(node.child[i], key)

    def _delete_internal_node(self, node, idx):
        d = self.d
        key = node.keys[idx]
        left_child = node.child[idx]
        right_child = node.child[idx + 1]
        
        if len(left_child.keys) >= d: # 왼쪽 child에 여유가 있으면 predecessor 사용
            pred_key, pred_rid = self._get_predecessor(left_child)
            node.keys[idx] = pred_key
            node.rids[idx] = pred_rid
            self._delete(left_child, pred_key)
        
        elif len(right_child.keys) >= d: # 오른쪽 child에 여유가 있으면 successor 사용
            succ_key, succ_rid = self._get_successor(right_child)
            node.keys[idx] = succ_key
            node.rids[idx] = succ_rid
            self._delete(right_child, succ_key)
        
        else: # 둘 다 최소 개수이면 merge 후 삭제
            self._merge_children(node, idx)
            self._delete(left_child, key)

    def _get_predecessor(self, node):
        while not node.leaf:
            node = node.child[-1]
        return node.keys[-1], node.rids[-1]

    def _get_successor(self, node):
        while not node.leaf:
            node = node.child[0]
        return node.keys[0], node.rids[0]

    def _fill_children(self, parent, idx):
        d = self.d
        if idx > 0 and len(parent.child[idx - 1].keys) >= d:
            self._borrow_from_left(parent, idx)
        elif idx < len(parent.child) - 1 and len(parent.child[idx + 1].keys) >= d:
            self._borrow_from_right(parent, idx)
        else:
            if idx < len(parent.child) - 1:
                self._merge_children(parent, idx)
            else:
                self._merge_children(parent, idx - 1)

    def _borrow_from_left(self, parent, idx):
        child = parent.child[idx]
        sibling = parent.child[idx - 1]
        child.keys.insert(0, parent.keys[idx - 1])
        child.rids.insert(0, parent.rids[idx - 1])
        parent.keys[idx - 1] = sibling.keys.pop()
        parent.rids[idx - 1] = sibling.rids.pop()
        if not sibling.leaf:
            child.child.insert(0, sibling.child.pop())

    def _borrow_from_right(self, parent, idx):
        child = parent.child[idx]
        sibling = parent.child[idx + 1]
        child.keys.append(parent.keys[idx])
        child.rids.append(parent.rids[idx])
        parent.keys[idx] = sibling.keys.pop(0)
        parent.rids[idx] = sibling.rids.pop(0)
        if not sibling.leaf:
            child.child.append(sibling.child.pop(0))

    def _merge_children(self, parent, idx):
        child = parent.child[idx]
        sibling = parent.child[idx + 1]
        child.keys.append(parent.keys.pop(idx))
        child.rids.append(parent.rids.pop(idx))
        child.keys.extend(sibling.keys)
        child.rids.extend(sibling.rids)
        if not sibling.leaf:
            child.child.extend(sibling.child)
        parent.child.pop(idx + 1)
        self.node_count -= 1

    def validate(self):
        leaf_depths = []
        def check(node, min_key=None, max_key=None, depth=0, is_root=False):
            # 1. key 정렬
            if any(node.keys[i - 1] >= node.keys[i] for i in range(1, len(node.keys))):
                return False
            # 2. key 범위
            if any((min_key is not None and key <= min_key) or
                (max_key is not None and key >= max_key)
                for key in node.keys):
                return False
            # 3. key 개수 조건
            if len(node.keys) > 2 * self.d - 1:
                return False
            if not is_root and len(node.keys) < self.d - 1:
                return False
            # 4. leaf 처리
            if node.leaf:
                leaf_depths.append(depth)
                return True
            # 5. internal node child 개수
            if len(node.child) != len(node.keys) + 1:
                return False
            # 6. child 범위 재귀 확인
            for i, child in enumerate(node.child):
                child_min = min_key if i == 0 else node.keys[i - 1]
                child_max = max_key if i == len(node.keys) else node.keys[i]
                if not check(child, child_min, child_max, depth + 1):
                    return False
            return True
        return check(self.root, is_root=True) and len(set(leaf_depths)) == 1