import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from mysql_autoxtrabackup.backup_backup import BackupBuilderChecker
from mysql_autoxtrabackup.utils import helpers

logger = logging.getLogger(__name__)


@dataclass
class BackupTags:
    tag: Optional[str]
    builder_obj: BackupBuilderChecker

    def add_tag(
        self, backup_type: str, backup_size: Optional[str], backup_status: Optional[str]
    ) -> bool:
        """
        Method for adding backup tags
        :param backup_type: The backup type - Full/Inc
        :param backup_size: The size of the backup in human-readable format
        :param backup_status: Status: OK or Status: Failed
        :return: True if no exception
        """
        # skip tagging unless self.tag
        if not self.tag:
            logger.info("TAGGING SKIPPED")
            return True

        # Currently, only support Inc and Full types, calculate name based on this
        assert backup_type in {
            "Full",
            "Inc",
        }, f"add_tag(): backup_type {backup_type}: must be 'Full' or 'Inc'"

        backup_name = (
            helpers.get_latest_dir_name(
                str(self.builder_obj.backup_options.get("full_dir"))
            )
            if backup_type == "Full"
            else helpers.get_latest_dir_name(
                str(self.builder_obj.backup_options.get("inc_dir"))
            )
        )

        # Calculate more tag fields, create string
        backup_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_tag_str = (
            "{bk_name}\t{bk_type}\t{bk_status}\t{bk_timestamp}\t{bk_size}\t'{bk_tag}'\n"
        )

        # Apply tag
        with open(
            f'{self.builder_obj.backup_options.get("backup_dir")}/backup_tags.txt', "a"
        ) as backup_tags_file:
            backup_tag_final = backup_tag_str.format(
                bk_name=backup_name,
                bk_type=backup_type,
                bk_status=backup_status,
                bk_timestamp=backup_timestamp,
                bk_size=backup_size,
                bk_tag=self.tag,
            )

            backup_tags_file.write(backup_tag_final)
        return True

    @staticmethod
    def show_tags(backup_dir: str, tag_file: Optional[str] = None) -> Optional[bool]:
        tag_file = tag_file or f"{backup_dir}/backup_tags.txt"
        if os.path.isfile(tag_file):
            with open(f"{backup_dir}/backup_tags.txt", "r") as backup_tags:
                from_file = backup_tags.read()
            column_names = "{0}\t{1}\t{2}\t{3}\t{4}\tTAG\n".format(
                "Backup".ljust(19),
                "Type".ljust(4),
                "Status".ljust(2),
                "Completion_time".ljust(19),
                "Size",
            )
            extra_str = "{}\n".format("-" * (len(column_names) + 21))
            print(column_names + extra_str + from_file)
            logger.info(column_names + extra_str + from_file)
            return True
        else:
            logger.warning(
                "Could not find backup_tags.txt inside given backup directory. Can't print tags."
            )
            print(
                "WARNING: Could not find backup_tags.txt inside given backup directory. Can't print tags."
            )
        return None
