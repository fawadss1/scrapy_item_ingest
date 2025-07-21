"""
Main pipeline that combines items and requests functionality.
"""
import logging
from .items import ItemsPipeline
from .requests import RequestsPipeline

logger = logging.getLogger(__name__)


class DbInsertPipeline(ItemsPipeline, RequestsPipeline):
    """
    Main pipeline that combines item processing and request tracking.
    Inherits from both ItemsPipeline and RequestsPipeline.
    """

    def __init__(self, settings):
        # Initialize both parent classes
        ItemsPipeline.__init__(self, settings)
        RequestsPipeline.__init__(self, settings)

    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler"""
        # Use RequestsPipeline's from_crawler to get signal connections
        return RequestsPipeline.from_crawler.__func__(cls, crawler)

    def open_spider(self, spider):
        """Called when spider is opened"""
        # Use the base class implementation
        super().open_spider(spider)

    def close_spider(self, spider):
        """Called when spider is closed"""
        # Use the base class implementation
        super().close_spider(spider)

    def process_item(self, item, spider):
        """Process and store item in database"""
        # Use ItemsPipeline's process_item method
        return ItemsPipeline.process_item(self, item, spider)
