import datetime

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_locals_status_count(model_vars_df: pd.DataFrame) -> None:
    locals_status_df = model_vars_df.rename(
        columns=lambda x: x.replace("status_", "")
    )
    locals_status_df["time"] = locals_status_df["time"] / pd.Timedelta(minutes=1)
    locals_status_df = locals_status_df.melt(
        id_vars=["time"],
        value_vars=["home", "traveling", "activity", "work"],  # 改过
        var_name="status",
        value_name="count",
    )
    sns.relplot(
        x="time",
        y="count",
        data=locals_status_df,
        kind="line",
        hue="status",
        aspect=1.5,
    )
    plt.gca().xaxis.set_major_formatter(
        lambda x, pos: ":".join(str(datetime.timedelta(minutes=x)).split(":")[:2])
    )
    plt.xticks(rotation=90)
    plt.title("Number of locals by status")


def plot_num_happiness(model_vars_df: pd.DataFrame) -> None:
    happiness_df = model_vars_df.rename(columns=lambda x: x.replace("happiness_", ""))
    happiness_df["time"] = happiness_df["time"] / pd.Timedelta(minutes=1)
    happiness_df = happiness_df.melt(
        id_vars=["time"],
        var_name="happiness",
        value_name="count",
    )
    sns.relplot(
        x="time",
        y="count",
        data=happiness_df,
        kind="line",
        hue="happiness",
        aspect=1.5,
    )
    plt.gca().xaxis.set_major_formatter(
        lambda x, pos: ":".join(str(datetime.timedelta(minutes=x)).split(":")[:2])
    )
    plt.xticks(rotation=90)
    plt.title("Number of happiness")


def plot_num_gentrification(model_vars_df: pd.DataFrame) -> None:
    gentrification_df = model_vars_df.rename(columns=lambda x: x.replace("gentrification_", ""))
    gentrification_df["time"] = gentrification_df["time"] / pd.Timedelta(minutes=1)
    gentrification_df = gentrification_df.melt(
        id_vars=["time"],
        var_name="gentrification",
        value_name="count",
    )
    sns.relplot(
        x="time",
        y="count",
        data=gentrification_df,
        kind="line",
        hue="gentrification",
        aspect=1.5,
    )
    plt.gca().xaxis.set_major_formatter(
        lambda x, pos: ":".join(str(datetime.timedelta(minutes=x)).split(":")[:2])
    )
    plt.xticks(rotation=90)
    plt.title("total_gentrification")