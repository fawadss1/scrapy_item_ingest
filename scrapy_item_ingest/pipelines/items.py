"""
Items pipeline for storing scraped items.
"""
import logging

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from .base import BasePipeline
from ..utils.serialization import serialize_item_data
from ..utils.time import get_current_datetime

logger = logging.getLogger(__name__)


class ItemsPipeline(BasePipeline):
    """Pipeline for handling scraped items"""

    def process_item(self, item, spider):
        """Process and store item in database"""
        job_id = self.settings.get_identifier_value(spider)

        adapter = ItemAdapter(item)
        item_dict = adapter.asdict()
        created_at = get_current_datetime(self.settings)

        # Store everything as JSON in the item column
        try:
            sql = f"INSERT INTO {self.settings.db_items_table} (job_id, item, created_at) VALUES (%s, %s, %s)"
            json_data = serialize_item_data(item_dict)

            self.db.execute(sql, (job_id, json_data, created_at))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise DropItem(f"DB insert error: {e}")

        return item
