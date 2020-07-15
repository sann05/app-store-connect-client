from datetime import datetime
from urllib.parse import urlparse

from dateutil.relativedelta import relativedelta

from .dataclass import frequency
from .exceptions import AppStoreConnectValueError


class Query(object):
    def __init__(self, app_id):
        self.config = {
            "startTime": None,
            "endTime": None,
            "adamId": [app_id],
            "group": None,
            "frequency": frequency.days,
            "dimensionFilters": [],
        }
        self.type = None
        self._api_url = "https://analytics.itunes.apple.com/analytics/api/v1"
        self._end_point = None

    @property
    def analytics_url(self):
        return urlparse(self._api_url + self._end_point).geturl()

    def _clean_config(self, keys):
        for key in keys:
            if key in self.config:
                del self.config[key]

    def metrics(self, config):
        """
        Set request configuration to Query
        Required param: measures
        optional params:
         group
         dimensionFilters
        """
        self.type = "metrics"
        self._end_point = "/data/time-series"
        self._clean_config(["limit", "dimension"])
        if config.get("group"):
            self.config["group"] = config["group"]
        if config.get("dimensionFilters"):
            self.config["dimensionFilters"] = config["dimensionFilters"]
        if config.get("measures"):
            self.config["measures"] = config["measures"]
        else:
            raise AppStoreConnectValueError(
                "The 'measures' param is required in the config")
        return self

    def app_list(self, config):
        self.type = "app_list"
        self._end_point = "/data/app-list"
        self._clean_config(["adamId", "dimension", "dimensionFilters", "group"])
        if config.get("measures"):
            self.config["measures"] = config["measures"]
        else:
            raise AppStoreConnectValueError(
                "The 'measures' param is required in the config")

        if config.get("adamId"):
            self.config["adamId"] = config["adamId"]
        else:
            raise AppStoreConnectValueError(
                "The 'adamId' param is required in the config")
        return self

    def dimension_values(self, config):
        """
        Set request configuration to Query for dimension_value request
        Required param: dimensions
        optional params:
         measure
         dimensionFilters
        """
        self.type = "dim_values"
        self._end_point = "/data/dimension-values"
        self._clean_config(["limit", "dimension", "group"])
        if config.get("dimensionFilters"):
            self.config["dimensionFilters"] = config["dimensionFilters"]
        if config.get("dimensions"):
            self.config["dimensions"] = config["dimensions"]
        else:
            raise AppStoreConnectValueError(
                "The 'dimensions' param is required in the config")
        if config.get("measure"):
            self.config["measure"] = config["measure"]

        return self

    def set_frequency(self, value=frequency.days):
        if value in list(frequency):
            self.config['frequency'] = value
        else:
            raise AppStoreConnectValueError(
                "'frequency' param should be on of the allowed values")
        return self

    def sources(self, config=None):
        # needs: dimension and measures
        # do not: group
        self.type = "sources"
        self._end_point = "/data/sources/list"
        if not self.config.get("limit"):
            self.config["limit"] = 200
        if not self.config.get("dimension"):
            self.config["dimension"] = "domainReferer"
        if config:
            self.config.update(config)
        return self

    def _validate_date(self, start, end):
        try:
            datetime.strptime(start, "%Y-%m-%d")
            if end:
                datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            raise AppStoreConnectValueError(
                "Incorrect format, should be YYYY-MM-DD.")

    def date_range(self, start, end=None):
        self._validate_date(start, end)
        self.config["startTime"] = start + "T00:00:000Z"
        if end is None:
            # Only get start date.
            self.config["endTime"] = start + "T00:01:000Z"
        else:
            self.config["endTime"] = end + "T00:00:000Z"
        return self

    def time_ago(self, value, freq=frequency.days):
        now = datetime.now()
        if freq == frequency.days:
            start = now - relativedelta(days=value)
        elif freq == frequency.weekly:
            value *= 7
            start = now - relativedelta(days=value)
        elif freq == frequency.monthly:
            start = now - relativedelta(months=value)
        else:
            raise AppStoreConnectValueError(
                "'freq' param should be on of the allowed values")
        self.config["startTime"] = start.strftime("%Y-%m-%d") + "%00:00:000Z"
        self.config["endTime"] = now.strftime("%Y-%m-%d") + "T00:00:000Z"
        return self
