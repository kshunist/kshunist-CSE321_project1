import os
import pandas as pd
import matplotlib.pyplot as plt

RESULT_PATH = "results/results.csv"
ADDITIONAL_RESULT_PATH = "results/additional_results.csv"
FIGURE_DIR = "figures"

def ensure_figure_dir():
    os.makedirs(FIGURE_DIR, exist_ok=True)

def load_results():
    df = pd.read_csv(RESULT_PATH)

    numeric_columns = [
        "d", "num_records",
        #insertion
        "insert_time", "split_count", "node_count", "utilization", "height",
        #search
        "avg_search_time",
        #range query
        "range_time",
        #deletion
        "delete_count", "delete_time",
        #b*-tree specific
        "redistribution_count", "split_2to3_count"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def load_additional_results():
    df = pd.read_csv(ADDITIONAL_RESULT_PATH)
    numeric_columns = [
        "d",
        "num_records",
        "insert_time",
        "split_count",
        "node_count",
        "utilization",
        "height",
        "redistribution_count",
        "split_2to3_count"
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def plot_line_by_d(df, metric, ylabel, title, filename):
    plt.figure(figsize=(8, 5))

    for tree_type in df["tree_type"].unique():
        subset = df[df["tree_type"] == tree_type].sort_values("d")
        plt.plot(
            subset["d"],
            subset[metric],
            marker="o",
            label=tree_type
        )

    plt.xlabel("Tree order d")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(os.path.join(FIGURE_DIR, filename), dpi=300)
    plt.close()

def plot_bstar_specific(df): # B*-Tree의 특성 (redistribution이 split 보다 자주 발생)
    bstar = df[df["tree_type"] == "B*-tree"].sort_values("d")
    if bstar.empty:
        return

    plt.figure(figsize=(8, 5))

    plt.plot(
        bstar["d"],
        bstar["redistribution_count"],
        marker="o",
        label="Redistribution Count"
    )

    plt.plot(
        bstar["d"],
        bstar["split_2to3_count"],
        marker="o",
        label="2-to-3 Split Count"
    )

    plt.xlabel("Tree order d")
    plt.ylabel("Count")
    plt.title("B*-tree Specific Operations")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(os.path.join(FIGURE_DIR, "9. bstar_specific.png"), dpi=300)
    plt.close()

def plot_insertion_order_metric(df, metric, ylabel, title, filename):
    subset = df[df["d"] == 10]
    if subset.empty:
        return
    order_names = ["sorted", "reverse_sorted", "random"]
    pivot = subset.pivot_table(
        index="tree_type",
        columns="insertion_order",
        values=metric,
        aggfunc="mean"
    )
    existing_orders = [order for order in order_names if order in pivot.columns]
    pivot = pivot[existing_orders]
    ax = pivot.plot(
        kind="bar",
        figsize=(8, 5),
        rot=0
    )
    ax.set_xlabel("Tree Type")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{title} (d={10})")
    ax.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, filename), dpi=300)
    plt.close()

def main():
    ensure_figure_dir()
    df = load_results()

    plot_line_by_d( # insertion: order d 에 따른 insert_time 비교 (order d 커질수록 insert_time 증가, B*-Tree가 overhead 큼)
        df,
        metric="insert_time",
        ylabel="Insertion Time (seconds)",
        title="Insertion Time by Tree Order",
        filename="1. insertion_time.png"
    )

    plot_line_by_d( # insertion: tree type에 따른 split_count 비교 (B*-Tree의 장점)
        df,
        metric="split_count",
        ylabel="Split Count",
        title="Split Count by Tree Order",
        filename="2. split_count.png"
    )

    plot_line_by_d( # insertion: tree type에 따른 node_count 비교 (B*-Tree의 장점)
        df,
        metric="node_count",
        ylabel="Node Count",
        title="Node Count by Tree Order",
        filename="3. node_count.png"
    )

    plot_line_by_d( # insertion: tree type에 따른 utilization 비교 (B*-Tree의 장점)
        df,
        metric="utilization",
        ylabel="Utilization",
        title="Space Utilization by Tree Order",
        filename="4. utilization.png"
    )

    plot_line_by_d( # insertion: tree type에 따른 height 비교 (차수가 커질수록 차이 없다)
        df,
        metric="height",
        ylabel="Tree Height",
        title="Tree Height by Tree Order",
        filename="5. tree_height.png"
    )

    plot_line_by_d( # search: tree type에 따른 avg_search_time 비교 (차이 없다)
        df,
        metric="avg_search_time",
        ylabel="Average Search Time (seconds)",
        title="Average Point Search Time by Tree Order",
        filename="6. avg_search_time.png"
    )

    plot_line_by_d( # range query: tree type에 따른 range_time 비교 (B+-Tree의 장점)
        df,
        metric="range_time",
        ylabel="Range Query Time (seconds)",
        title="Range Query Time by Tree Order",
        filename="7. range_query_time.png"
    )

    plot_line_by_d( # deletion: tree type에 따른 delete_time 비교 (B*-Tree의 한계)
        df,
        metric="delete_time",
        ylabel="Deletion Time (seconds)",
        title="Deletion Time by Tree Order",
        filename="8. delete_time.png"
    )

    plot_bstar_specific(df)

    additional_df = load_additional_results()
    plot_insertion_order_metric( # insertion order에 따른 split_count 비교
        additional_df,
        metric="split_count",
        ylabel="Split Count",
        title="Split Count by Insertion Order",
        filename="10. additional_insertion_order_split_count_d10.png"
    )

    plot_insertion_order_metric( # insertion order에 따른 utilization 비교
        additional_df,
        metric="utilization",
        ylabel="Utilization",
        title="Space Utilization by Insertion Order",
        filename="11. additional_insertion_order_utilization_d10.png"
    )

    print(f"Figures saved to '{FIGURE_DIR}/'")

if __name__ == "__main__":
    main()