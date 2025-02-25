# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import datetime
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from django.db.models import Q

from apm_web.models import Application
from bkmonitor.data_source import dict_to_q
from bkmonitor.data_source.unify_query.builder import QueryConfigBuilder, UnifyQuerySet
from bkmonitor.utils.thread_backend import ThreadPool
from constants.data_source import DataSourceLabel, DataTypeLabel

logger = logging.getLogger(__name__)


class MetricHelper:

    TIME_FIELD_ACCURACY = 1000

    # 默认查询近 1h 的数据
    DEFAULT_TIME_DURATION: datetime.timedelta = datetime.timedelta(hours=1)

    # 最多查询近 30d 的数据
    MAX_TIME_DURATION: datetime.timedelta = datetime.timedelta(days=30)

    MAX_OPTION_LIMIT: int = 9999

    MAX_DATA_LIMIT: int = 24 * 60 * 30

    USING: Tuple[str, str] = (DataTypeLabel.TIME_SERIES, DataSourceLabel.CUSTOM)

    TIME_FIELD: str = "time"

    def __init__(self, bk_biz_id: int, app_name: str):
        self.table_id: str = Application.get_metric_table_id(bk_biz_id, app_name)

    @property
    def q(self) -> QueryConfigBuilder:
        return QueryConfigBuilder(self.USING).table(self.table_id).time_field(self.TIME_FIELD)

    def time_range_qs(self, start_time: Optional[int] = None, end_time: Optional[int] = None) -> UnifyQuerySet:
        start_time, end_time = self._get_time_range(start_time, end_time)
        return UnifyQuerySet().start_time(start_time).end_time(end_time)

    def get_field_option_values(
        self,
        metric_field: str,
        field: str,
        filter_dict: Optional[Dict[str, Any]] = None,
        limit: int = MAX_OPTION_LIMIT,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[str]:
        q: QueryConfigBuilder = (
            self.q.filter(dict_to_q(filter_dict or {}) or Q())
            .metric(field=metric_field, method="count")
            .tag_values(field)
        )

        option_values: Set[str] = set()
        qs: UnifyQuerySet = self.time_range_qs(start_time, end_time).add_query(q).limit(limit)
        try:
            for bucket in qs:
                value: Optional[str] = bucket.get(field)
                if value:
                    option_values.add(value)
        except Exception:  # noqa
            logger.exception("[get_field_option_values] failed to get option values")
            pass

        return list(option_values)

    def fetch_field_option_values(
        self, params_list: List[Dict[str, Any]], start_time: Optional[int] = None, end_time: Optional[int] = None
    ) -> Dict[Tuple[str, str], List[str]]:
        def _collect(_metric_field: str, _field: str, _filter_dict: Optional[Dict[str, Any]] = None):
            group_option_values_map[(_metric_field, _field)] = self.get_field_option_values(
                _metric_field, _field, filter_dict=_filter_dict, start_time=start_time, end_time=end_time
            )

        group_option_values_map: Dict[Tuple[str, str], List[str]] = {}
        ThreadPool().map_ignore_exception(
            _collect, [(params["metric_field"], params["field"], params.get("filter_dict")) for params in params_list]
        )
        return group_option_values_map

    def get_field_option_values_by_groups(
        self, params_list: List[Dict[str, Any]], start_time: Optional[int] = None, end_time: Optional[int] = None
    ) -> List[str]:
        option_values: Set[str] = set()
        group_option_values_map: Dict[Tuple[str, str], List[str]] = self.fetch_field_option_values(
            params_list, start_time, end_time
        )
        for params in params_list:
            option_values |= set(group_option_values_map.get((params["metric_field"], params["field"])) or [])
        return list(option_values)

    @classmethod
    def _get_time_range(cls, start_time: Optional[int] = None, end_time: Optional[int] = None):
        now: int = int(datetime.datetime.now().timestamp())
        # 最早查询起始时间
        earliest_start_time: int = now - int(cls.MAX_TIME_DURATION.total_seconds())
        # 默认查询起始时间
        default_start_time: int = now - int(cls.DEFAULT_TIME_DURATION.total_seconds())

        # 开始时间不能小于 earliest_start_time
        start_time = max(earliest_start_time, start_time or default_start_time)

        # 结束时间不能大于 now
        end_time = min(now, end_time or now)
        # 省略最后未完成的一分钟，避免数据不准确引起误解
        end_time = end_time // 60 * 60

        return start_time * cls.TIME_FIELD_ACCURACY, end_time * cls.TIME_FIELD_ACCURACY

    @classmethod
    def get_interval(cls, start_time: Optional[int] = None, end_time: Optional[int] = None):
        start_time, end_time = cls._get_time_range(start_time, end_time)
        return (end_time - start_time) // cls.TIME_FIELD_ACCURACY
