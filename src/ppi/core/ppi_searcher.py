import datetime

import pandas as pd
import re
from typing import List, Dict, Optional, Union, Tuple
from fuzzywuzzy import fuzz, process
from .ppi_data_manager import PPIDataManager


class PPISearcher:
    """
    Search functionality to help users discover relevant PPI series.
    Provides various methods for searching by keywords, categories, and attributes,
    as well as fuzzy matching to handle approximate searches.
    """

    def __init__(self, data_manager: PPIDataManager):
        self.data_manager = data_manager
        self._refresh_metadata_cache()

    def _refresh_metadata_cache(self):
        self.metadata_cache = self.data_manager.get_series_metadata()

        if len(self.metadata_cache) > 0:
            self.metadata_cache['title_lower'] = self.metadata_cache['series_title'].str.lower()

            self.metadata_cache['major_category'] = self.metadata_cache['series_id'].str[3:5]
            self.metadata_cache['is_seasonal'] = self.metadata_cache['seasonal'] == 'S'

    def search_by_keyword(self,
                          keywords: Union[str, List[str]],
                          match_all: bool = False,
                          min_score: int = 80) -> pd.DataFrame:
        """
        Search for series containing specified keywords in their titles.

        Args:
            keywords: String or list of keywords to search for
            match_all: if True, requires all keywords to match; if False any keyword match is sufficient
            min_score: Minimum similarity score (0-100) for fuzzy matching

        Returns:
            Dataframe containing matching series_metadata
        """
        if len(self.metadata_cache) == 0:
            return pd.DataFrame()

        if isinstance(keywords, str):
            keywords = [keywords]

        keywords = [k.lower() for k in keywords]

        all_scores = {}
        for series_id in self.metadata_cache['series_id']:
            title = self.metadata_cache.loc[
                self.metadata_cache['series_id'] == series_id,
                'title_lower'
            ].iloc[0]

            keyword_scores = [fuzz.partial_ratio(kw, title) for kw in keywords]

            if match_all and all(score >= min_score for score in keyword_scores):
                all_scores[series_id] = sum(keyword_scores) / len(keyword_scores)
            elif not match_all and any(score >= min_score for score in keyword_scores):
                all_scores[series_id] = max(keyword_scores)

        matching_series_ids = [
            series_id for series_id, score in all_scores.items()
            if score >= min_score
        ]

        if not matching_series_ids:
            return pd.DataFrame()

        sorted_series = sorted(
            matching_series_ids,
            key=lambda sid: all_scores[sid],
            reverse=True
        )

        return self.metadata_cache[
            self.metadata_cache['series_id'].isin(sorted_series)
        ].sort_values(
            by=['series_id'],
            key=lambda x: pd.Series([sorted_series.index(s) for s in x])
        )

    def search_by_category(self,
                           category_code: str,
                           include_subcategories: bool = True) -> pd.DataFrame:
        """
        Search for series within a specific category code.

        Args:
            category_code: Category code to search for (e.g. '01' for Farm Products)
            include_subcategories: If true, include all series with the category prefix

        Returns:
            DataFrame containing matching series metadata
        """

        if len(self.metadata_cache) == 0:
            return pd.DataFrame()

        if include_subcategories:
            matches = self.metadata_cache[
                self.metadata_cache['group_code'].str.startswith(category_code)
            ]
        else:
            matches = self.metadata_cache[
                self.metadata_cache['group_code'] == category_code
                ]

        return matches.sort_values('series_id')

    def search_by_date_range(self,
                             min_year: Optional[int] = None,
                             max_year: Optional[int] = None,
                             active_only: bool = True) -> pd.DataFrame:
        """
        Search for series with data available in a specific time range.

        Args:
             min_year: Minimum year of data to search over
             max_year: Maximum year of data to search over
             active_only: If True, only include currently active series

            Returns:
                Dataframe containing matching series metadata
        """
        if len(self.metadata_cache) == 0:
            return pd.DataFrame()

        result = self.metadata_cache.copy()

        if min_year is not None:
            result = result[(result['begin_year'] <= min_year) & (result['end_year'] >= min_year)]

        # Similarly for max_year
        if max_year is not None:
            result = result[(result['begin_year'] <= max_year) & (result['end_year'] >= max_year)]

        if active_only:
            current_year = datetime.datetime.now().year
            result = result[result['end_year'] >= current_year]

        return result.sort_values('series_id')

    def get_seasonal_status(self, seasonal: Optional[bool] = None) -> pd.DataFrame:
        """
        Get series filtered by seasonal adjustment status.

        Args:
            seasonal: If true, return seasonally adjusted series;
            if False, return unadjusted series;
            if None, return all series.

        Returns:
            Dataframe containing matching series metadata
        """

        if len(self.metadata_cache) == 0:
            return pd.DataFrame()

        if seasonal is None:
            return self.metadata_cache

        expected_seasonal = 'S' if seasonal else 'U'
        return self.metadata_cache[
            self.metadata_cache['seasonal'] == expected_seasonal
            ]

    def suggest_similar_series(self,
                               series_id: str,
                               n: int = 5,
                               same_category: bool = True) -> pd.DataFrame:
        """
        Suggest similar series to the given series_id based on title similarity.

        Args:
            series_id: Reference series ID
            n: Number of suggestions to return
            same_category: If true, suggest all series with the same category prefix

        Returns:
            Dataframe containing similar series metadata
        """
        if len(self.metadata_cache) == 0:
            return pd.DataFrame()

        ref_series = self.metadata_cache[
            self.metadata_cache['series_id'] == series_id
            ]

        if len(ref_series) == 0:
            return pd.DataFrame()

        ref_title = ref_series['series_title'].iloc[0]
        ref_category = ref_series['group_code'].iloc[0]

        if same_category:
            potential_matches = self.metadata_cache[
                (self.metadata_cache['group_code'] == ref_category) &
                (self.metadata_cache['series_id'] != series_id)
                ]
        else:
            potential_matches = self.metadata_cache[
                self.metadata_cache['series_id'] != series_id
                ]

        if len(potential_matches) == 0:
            return pd.DataFrame()

        titles = potential_matches['series_title'].tolist()
        matches = process.extract(
            ref_title,
            titles,
            limit=n,
            scorer=fuzz.token_sort_ratio
        )

        matching_titles = [match[0] for match in matches]
        similar_series = potential_matches[
            potential_matches['series_title'].isin(matching_titles)
        ]

        similar_series['similarity_score'] = similar_series['series_title'].apply(
            lambda title: fuzz.token_sort_ratio(title, ref_title)
        )

        similar_series = similar_series.sort_values(
            'similarity_score', ascending=False
        )

        return similar_series

    def get_category_map(self) -> Dict[str, str]:
        """
        Returns a mapping of category codes to descriptions
        """
        return {
            '01': 'Farm Products',
            '02': 'Processed Foods and Feeds',
            '03': 'Textile Products and Apparel',
            '04': 'Hides, Skins, Leather, and Related Products',
            '05': 'Fuels and Related Products and Power',
            '06': 'Chemicals and Allied Products',
            '07': 'Rubber and Plastic Products',
            '08': 'Lumber and Wood Products',
            '09': 'Pulp, Paper, and Allied Products',
            '10': 'Metals and Metal Products',
            '11': 'Machinery and Equipment',
            '12': 'Furniture and Household Durables',
            '13': 'Nonmetallic Mineral Products',
            '14': 'Transportation Equipment',
            '15': 'Miscellaneous Products',
        }

    def get_summary_statistics(self) -> Dict[str, int]:
        """
        Return summary statistics about available series.
        """
        if len(self.metadata_cache) == 0:
            return {'total_series': 0}

        stats = {
            'total_series': len(self.metadata_cache),
            'seasonally_adjusted': len(self.metadata_cache[
                self.metadata_cache['seasonal'] == 'S'
                                       ]),
            'non_seasonally_adjusted': len(self.metadata_cache[
                self.metadata_cache['seasonal'] == 'U'
                                           ]),
        }

        category_map = self.get_category_map()
        for code, name in category_map.items():
            stats[f'category_{code}_{name}'] = len(self.metadata_cache[
                self.metadata_cache['group_code'].str.startswith(code)
                                                   ])

        return stats
