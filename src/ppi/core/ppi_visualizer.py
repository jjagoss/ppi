import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Optional, List, Tuple, Union
import numpy as np
from pathlib import Path

from .ppi_data_manager import PPIDataManager
from .ppi_analyzer import PPIAnalyzer


class PPIVisualizer:
    def __init__(self, data_manager: PPIDataManager, analyzer: Optional[PPIAnalyzer] = None):
        """
        Args:
            data_manager: PPI DataManager instance for data access
            analyzer: Optional PPIAnalyzer instance (will create one if not provided).
        """
        self.data_manager = data_manager
        self.analyzer = analyzer or PPIAnalyzer(data_manager)

        plt.style.use('seaborn-v0_8-whitegrid')
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                       '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    def plot_price_trend(self,
                         series_id: str,
                         title: Optional[str] = None,
                         start_year: Optional[int] = None,
                         end_year: Optional[int] = None,
                         figsize: Tuple[int, int] = (10, 6),
                         save_path: Optional[str] = None) -> plt.Figure:
        """
        Creates a line plot showing price trends for a specific series.
        Args:
            series_id: PPI series identifier
            title: Optional title (defaults to series title from metadata)
            start_year/end_year: Optional date range filters
            figsize: Figure dimensions
            save_path: Optional path to save the figure

        Returns:
            Matplotlib Figure object
        """
        series_data = self.data_manager.get_series_data(series_id,
                                                   start_year=start_year,
                                                   end_year=end_year)
        metadata = self.data_manager.get_series_metadata(series_id)
        series_title = metadata['series_title'].iloc[0] if len(metadata) > 0 else series_id

        series_data['date'] = pd.to_datetime(
            series_data['year'].astype(str) +
            series_data['period'].str[1:].str.zfill(2) +
            '01',
            format='%Y%m%d'
        )

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(series_data['date'], series_data['value'],
                linewidth=2, marker='o', markersize=4, color=self.colors[0])

        chart_title = title or f"Price Index: {series_title}"
        ax.set_title(chart_title, fontsize=14, pad=20)
        ax.set_ylabel("Price Index Value", fontsize=12)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        plt.xticks(rotation=45)

        if len(metadata) > 0 and 'base_date' in metadata.columns:
            base_year = metadata["base_date"].iloc[0][:4]
            ax.axhline(y=100, color='gray', linestyle='--', alpha=0.7)
            ax.text(series_data["date"].iloc[0], 100, f"Base: {base_year}=100",
                    verticalalignment='bottom', fontsize=10, color='gray')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def plot_inflation_rates(self,
                             series_id: str,
                             periods: List[str] = ['one_month', 'twelve_month'],
                             start_year: Optional[int] = None,
                             end_year: Optional[int] = None,
                             figsize: Tuple[int, int] = (10, 6),
                             save_path: Optional[str] = None) -> plt.Figure:
        """
        Args:
            series_id: PPI series identifier
            periods: List of periods to plot ('one_month', 'three_month', etc.)
            start_year/end_year: Optional date range filters
            figsize: Figure dimensions
            save_path: Optional path to save the figure

        Returns:
            Matplotlib Figure object
        """
        series_data = self.data_manager.get_series_data(series_id,
                                                        start_year=start_year,
                                                        end_year=end_year)
        metadata = self.data_manager.get_series_metadata(series_id)
        series_title = metadata['series_title'].iloc[0] if len(metadata) > 0 else series_id

        series_data['date'] = pd.to_datetime(
            series_data['year'].astype(str) +
            series_data['period'].str[1:].str.zfill(2) +
            '01',
            format='%Y%m%d'
        )
        series_data = series_data.sort_values('date')

        inflation_data = {'date': []}
        for period in periods:
            inflation_data[period] = []

        if len(series_data) >= 12:
            for i in range(12, len(series_data)):
                end_idx = i
                end_date = series_data.iloc[end_idx]['date']
                end_year = series_data.iloc[end_idx]['year']
                end_period = series_data.iloc[end_idx]['period']

                rates = self.analyzer.calculate_rolling_changes(
                    series_id,
                    end_year=end_year,
                    end_period=end_period
                )

                inflation_data['date'].append(end_date)
                for period in periods:
                    inflation_data[period].append(rates[period])

        inflation_df = pd.DataFrame(inflation_data)
        fig, ax = plt.subplots(figsize=figsize)

        period_labels = {
            'one_month': '1-Month (Annualized)',
            'three_month': '3-Month (Annualized)',
            'six_month': '6-Month (Annualized)',
            'twelve_month': '12-Month'
        }

        for i, period in enumerate(periods):
            ax.plot(inflation_df['date', inflation_df[period]],
                    label=period_labels.get(period, period),
                    color=self.colors[i % len(self.colors)],
                    linewidth=2)

        chart_title = f"Inflation Rates: {series_title}"
        ax.set_title(chart_title, fontsize=14, pad=20)
        ax.set_ylabel("Percent Change (Annualized)", fontsize=12)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        plt.xticks(rotation=45)

        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)

        ax.legend(loc='best')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def plot_series_comparison(self,
                               series_ids: List[str],
                               normalization: Optional[str] = 'first',
                               start_year: Optional[int] = None,
                               end_year: Optional[int] = None,
                               figsize: Tuple[int, int] = (12, 7),
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        Compare multiple PPI series on the same chart.

        Args:
            series_ids: List of PPI series identifiers to compare
            normalization: How to normalize series for comparison:
                           'first' - normalize to first value
                           'percent_change' - show percent change from start
                           None - show raw values
            start_year/end_year: Optional date range filters
            figsize: Figure dimensions
            save_path: Optional path to save the figure

        Returns:
            Matplotlib Figure object
        """
        # Get metadata for all series
        all_metadata = {}
        for series_id in series_ids:
            metadata = self.data_manager.get_series_metadata(series_id)
            if len(metadata) > 0:
                all_metadata[series_id] = metadata['series_title'].iloc[0]
            else:
                all_metadata[series_id] = series_id

        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)

        # Get and plot each series
        for i, series_id in enumerate(series_ids):
            series_data = self.data_manager.get_series_data(series_id,
                                                            start_year=start_year,
                                                            end_year=end_year)

            # Format date
            series_data['date'] = pd.to_datetime(
                series_data['year'].astype(str) +
                series_data['period'].str[1:].str.zfill(2) +
                '01',
                format='%Y%m%d'
            )
            series_data = series_data.sort_values('date')

            # Apply normalization if requested
            values = series_data['value']
            if normalization == 'first' and len(values) > 0:
                values = values / values.iloc[0] * 100
                ylabel = 'Index (First Period = 100)'
            elif normalization == 'percent_change' and len(values) > 0:
                values = (values / values.iloc[0] - 1) * 100
                ylabel = 'Percent Change from Start'
            else:
                ylabel = 'Price Index Value'

            # Plot the series
            ax.plot(series_data['date'], values,
                    label=all_metadata[series_id],
                    color=self.colors[i % len(self.colors)],
                    linewidth=2)

        # Format the plot
        chart_title = "PPI Series Comparison"
        ax.set_title(chart_title, fontsize=14, pad=20)
        ax.set_ylabel(ylabel, fontsize=12)

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        plt.xticks(rotation=45)

        # Add reference line for normalized plots
        if normalization in ['first', 'percent_change']:
            reference_value = 100 if normalization == 'first' else 0
            ax.axhline(y=reference_value, color='gray', linestyle='--', alpha=0.7)

        # Add legend
        if len(series_ids) > 1:
            ax.legend(loc='best')

        plt.tight_layout()

        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def create_heatmap(self,
                       series_ids: List[str],
                       metric: str = 'twelve_month',
                       start_year: Optional[int] = None,
                       end_year: Optional[int] = None,
                       figsize: Tuple[int, int] = (12, 8),
                       save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a heatmap showing inflation across multiple series over time.

        Args:
            series_ids: List of PPI series to include
            metric: Which inflation metric to use ('one_month', 'twelve_month', etc)
            start_year/end_year: Optional date range filters
            figsize: Figure dimensions
            save_path: Optional path to save the figure

        Returns:
            Matplotlib Figure object
        """
        # Get metadata for all series
        labels = []
        for series_id in series_ids:
            metadata = self.data_manager.get_series_metadata(series_id)
            if len(metadata) > 0:
                labels.append(metadata['series_title'].iloc[0])
            else:
                labels.append(series_id)

        # Collect data for each series and time period
        all_data = {}
        date_range = set()

        for series_id in series_ids:
            series_data = self.data_manager.get_series_data(series_id,
                                                            start_year=start_year,
                                                            end_year=end_year)

            # Skip if insufficient data
            if len(series_data) < 12:
                continue

            # Format date
            series_data['date'] = pd.to_datetime(
                series_data['year'].astype(str) +
                series_data['period'].str[1:].str.zfill(2) +
                '01',
                format='%Y%m%d'
            )
            series_data = series_data.sort_values('date')

            # Calculate inflation for each point in time
            inflation_values = {}

            for i in range(12, len(series_data)):
                end_idx = i
                end_date = series_data.iloc[end_idx]['date']
                end_year = series_data.iloc[end_idx]['year']
                end_period = series_data.iloc[end_idx]['period']

                # Format date for display
                date_str = end_date.strftime('%Y-%m')
                date_range.add(date_str)

                # Get inflation rates
                rates = self.analyzer.calculate_rolling_changes(
                    series_id,
                    end_year=end_year,
                    end_period=end_period
                )

                inflation_values[date_str] = rates[metric]

            all_data[series_id] = inflation_values

        # Convert to a matrix for heatmap
        sorted_dates = sorted(list(date_range))
        matrix_data = np.zeros((len(series_ids), len(sorted_dates)))

        for i, series_id in enumerate(series_ids):
            if series_id in all_data:
                for j, date in enumerate(sorted_dates):
                    if date in all_data[series_id]:
                        matrix_data[i, j] = all_data[series_id][date]
                    else:
                        matrix_data[i, j] = np.nan

        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)

        # Define custom colormap for inflation (blue for negative, white for zero, red for positive)
        from matplotlib.colors import LinearSegmentedColormap
        max_abs_value = np.nanmax(np.abs(matrix_data))
        bounds = np.linspace(-max_abs_value, max_abs_value, 21)
        cmap = LinearSegmentedColormap.from_list(
            'inflation_cmap', ['#1a53ff', '#ffffff', '#ff3333']
        )

        # Create heatmap
        im = ax.imshow(matrix_data, cmap=cmap, aspect='auto',
                       vmin=-max_abs_value, vmax=max_abs_value)

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label(f'{metric.replace("_", " ").title()} Inflation Rate (%)')

        # Format axes
        ax.set_yticks(np.arange(len(labels)))
        ax.set_yticklabels(labels)

        # Only show a subset of dates for readability
        date_indices = np.linspace(0, len(sorted_dates) - 1, min(10, len(sorted_dates))).astype(int)
        ax.set_xticks(date_indices)
        ax.set_xticklabels([sorted_dates[i] for i in date_indices], rotation=45)

        metric_labels = {
            'one_month': '1-Month (Annualized)',
            'three_month': '3-Month (Annualized)',
            'six_month': '6-Month (Annualized)',
            'twelve_month': '12-Month'
        }
        metric_label = metric_labels.get(metric, metric)

        # Add title
        plt.title(f"Heatmap of {metric_label} Inflation Rates", fontsize=14, pad=20)

        plt.tight_layout()

        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig
