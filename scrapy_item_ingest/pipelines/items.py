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

        logger.info(f"Processing item for job_id {job_id}: {item}")
        adapter = ItemAdapter(item)
        item_dict = adapter.asdict()
        created_at = get_current_datetime(self.settings)

        logger.info(f"Item dict prepared: {item_dict}")

        # Store everything as JSON in the item column
        try:
            sql = f"INSERT INTO {self.settings.db_items_table} (job_id, item, created_at) VALUES (%s, %s, %s)"
            json_data = serialize_item_data(item_dict)
            logger.info(f"Executing SQL: {sql} with JSON data")

            self.db.execute(sql, (job_id, json_data, created_at))
            self.db.commit()
            logger.info(f"Successfully inserted item for job_id {job_id}")
        except Exception as e:
            logger.error(f"Failed to insert item: {e}")
            self.db.rollback()
            raise DropItem(f"DB insert error: {e}")

        return item
