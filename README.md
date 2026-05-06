# CSE321 Project 1

## 1. Overview

This project implements and compares three tree-based index structures:

- B-tree
- B+-tree
- B*-tree

The dataset contains student records.  
The `Student ID` is used as the search key, and the RID is represented by the position of each record in the loaded dataset.

The implemented index structures are evaluated using:

- insertion
- point search
- range query
- deletion experiments

In addition, several structural metrics are analyzed, including:

- split count
- node count
- tree height
- space utilization
- redistribution frequency

The project also includes an additional experiment that analyzes how insertion order affects index structure performance.

---

# 2. Current Progress

## Implemented Features

### B-tree
- Search
- Insert
- Split
- Range query
- Delete
- Tree validation
- Utilization calculation
- Height calculation

---

### B+-tree
- Leaf-node linked structure
- Search
- Insert
- Split
- Efficient range query
- Delete
- Underflow handling
- Tree validation

---

### B*-tree
- Redistribution between sibling nodes
- 2-to-3 split
- B*-specific metrics
- Insert
- Search
- Range query
- Simplified delete

---

### Experiment System
- CSV dataset loader
- Automated experiment pipeline
- Result CSV generation
- Figure generation using matplotlib
- Validation and correctness checking

---

## Generated Experimental Metrics

### Insertion
- insertion time
- split count
- node count
- utilization
- tree height

### Point Search
- average search time
- correctness verification

### Range Query
- range query time
- result count
- average GPA

### Deletion
- deletion time
- tree validity

### B* Tree Specific
- redistribution count
- 2-to-3 split count

---

# 3. How To Run

## 3.1 Move to the project directory

```bash
cd CSE321_Assignment1
```

---

## 3.2 Run the experiment

```bash
python3 src/main.py
```

---

## 3.3 Experiment Output

After running `main.py`, the experimental results are saved to:

```bash
results/results.csv
```

Additional experiment results are saved to:

```bash
results/insertion_order_results.csv
```

---

## 3.4 Generating Figures

To generate figures from the result CSV files, run:

```bash
python3 src/plot_results.py
```

After running `plot_results.py`, generated figures are saved to:

```bash
figures/
```

---

## 3.5 Requirements

Make sure:

- dataset exists in `data/`
- results folder exists
- figures folder exists

Environment:

```text
My Python Version : 3.14.3
```

Required Python packages:

```text
pandas
matplotlib
```

Install packages:

```bash
python3 -m pip install pandas matplotlib
```

---

# 4. Repository Structure

```text
.
├── data/
│   └── students.csv
├── figures/
│   ├── 1. insertion_time.png
│   ├── 2. split_count.png
│   ├── 3. node_count.png
│   ├── 4. utilization.png
│   ├── 5. tree_height.png
│   ├── 6. avg_search_time.png
│   ├── 7. range_query_time.png
│   ├── 8. delete_time.png
│   ├── 9. bstar_specific_operations.png
│   ├── 10. insertion_order_split.png
│   └── 11. insertion_order_utilization.png
├── results/
│   ├── results.csv
│   └── insertion_order_results.csv
├── src/
│   ├── _test.py
│   ├── btree.py
│   ├── bplustree.py
│   ├── bstartree.py
│   ├── loader.py
│   ├── main.py
│   └── plot_results.py
└── README.md
```

---

# 5. Experiment Configuration

## Dataset

- File: `data/student.csv`
- Key: `student_id`
- Value: RID (record index)

The dataset contains:

- student ID
- name
- gender
- GPA
- height
- weight

---

## Tree Parameters

Each tree is tested with different orders:

```python
d = [3, 5, 10, 20, 50]
```

---

## Tested Structures

```python
("B-tree", BTree)
("B+-tree", BPlusTree)
("B*-tree", BStarTree)
```

---

# 6. Experiment Pipeline

For each `(tree type, d)` pair, the following experiments are executed.

---

## 6.1 Insertion Experiment

```python
tree.insert(student_id, rid)
```

Student records are sequentially inserted into each tree structure.

Measured:

- Total insertion time
- Split count
- Node count
- Tree height
- Space utilization

Purpose:

- Compare insertion efficiency
- Analyze node management behavior
- Observe the effect of B* redistribution

---

## 6.2 Point Search Experiment

```python
tree.search(key)
```

Random student IDs are repeatedly searched.

Configuration:

- Up to 20,000 random queries
- Verified against `key_to_rid`

Measured:

- Average search time
- Error count

Purpose:

- Compare lookup efficiency
- Verify search correctness

---

## 6.3 Range Query Experiment

```python
tree.range_query(start_key, end_key)
```

The result records are filtered with:

```python
gender == "Male"
height <= 170
weight >= 80
```

Measured:

- Result count
- Query execution time
- Average GPA of filtered records

Purpose:

- Compare sequential access efficiency
- Evaluate B+-tree range search advantage

---

## 6.4 Deletion Experiment

```python
tree.delete(key)
```

Steps:

1. Randomly delete keys (5,000 records)
2. Validate correctness:
   - Deleted keys should not exist
   - Remaining keys should still be searchable

Measured:

- Delete time
- Tree validity

Purpose:

- Compare underflow handling
- Analyze merge and redistribution behavior

---

## 6.5 B* Tree Specific Metrics

```text
redistribution_count
split_2to3_count
```

These metrics measure:

- Frequency of redistribution
- Frequency of 2-to-3 splits

Purpose:

- Analyze how B* Tree improves utilization
- Observe structural balancing behavior

---

# 7. Additional Experiment

## Insertion Order Experiment

This additional experiment analyzes how insertion order affects tree structure and performance.

Two insertion methods are compared:

- Random insertion
- Sequential insertion (sorted order & reverse sorted order)

The same dataset is used for both experiments.

Measured:

- Split count
- Utilization

Purpose:

- Analyze the impact of input order
- Compare structural stability
- Observe how sequential insertion changes node distribution

Generated Figures:

```text
10. insertion_order_split.png
11. insertion_order_utilization.png
```

---

# 8. Experimental Observations

## B-tree
- Simpler structure
- Good overall performance
- Lower range query efficiency compared to B+-tree

---

## B+-tree
- Better range query performance
- Leaf-node linked structure improves sequential access
- Slightly better search performance

---

## B*-tree
- Higher utilization due to redistribution
- Fewer node splits in many cases
- More complex insertion and deletion logic

---

# 9. Limitations of B* Tree Implementation

This project includes a simplified B* Tree implementation with several practical limitations.

---

## 9.1 Partial Redistribution Logic

- Redistribution is implemented only between local sibling nodes
- Does not fully cover all theoretical B* Tree cases

---

## 9.2 Simplified 2-to-3 Split

- Only basic 2-to-3 split cases are implemented
- Cascading multi-level optimization is limited

---

## 9.3 Simplified Deletion

- Deletion partially reuses B-tree deletion logic
- May fall back to merge instead of optimal redistribution
- Strict 2/3 occupancy is not always guaranteed

---

# 10. Future Improvements

Possible future improvements include:

- Fully optimized B* Tree deletion
- Better redistribution strategies
- Disk-based page simulation
- Buffer manager simulation
- Concurrent operations
- Visualization of tree structures
- Larger-scale benchmarking

---