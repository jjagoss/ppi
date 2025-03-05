import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")



def plot_annualized_trends(
        df,
        series_id=None,
        series_title=None,  # <-- new
        title=None,
        show=True,
        save_path=None
):
    """
    Plots the annualized 1m, 3m, 6m, and 12m changes from a DataFrame that
    includes columns: "date", "ann_1m", "ann_3m", "ann_6m", "ann_12m".
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))

    # Plot columns if they exist
    if "ann_1m" in df.columns:
        ax.plot(df["date"], df["ann_1m"], label="1m Annualized")
    if "ann_3m" in df.columns:
        ax.plot(df["date"], df["ann_3m"], label="3m Annualized")
    if "ann_6m" in df.columns:
        ax.plot(df["date"], df["ann_6m"], label="6m Annualized")
    if "ann_12m" in df.columns:
        ax.plot(df["date"], df["ann_12m"], label="12m Annualized")

    ax.set_xlabel("Date")
    ax.set_ylabel("Annualized % Change")
    ax.legend()

    # Build a default title if not provided
    if not title:
        if series_title:
            title = f"Annualized PPI Changes for {series_title}"
        elif series_id:
            title = f"Annualized PPI Changes for {series_id}"
        else:
            title = "Annualized PPI Changes"
    ax.set_title(title)

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")

    if show:
        plt.show()

    return fig, ax
