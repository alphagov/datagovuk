from datetime import datetime

from django.urls import reverse


def format_date(date_string):
    return datetime.fromisoformat(date_string).strftime("%d/%m/%Y")


def resource_table_row_data(resource, document_id, document_name):
    resource_format = resource["format"].strip().strip(".").upper() if resource["format"] else ""
    date = resource["last_modified"] or resource["created"]
    return {
        "url": resource["url"],
        "name": resource["name"],
        "file_size": format_file_size(resource["size"]) if resource["size"] else None,
        "format": resource_format,
        "is_csv": resource_format == "CSV",
        "preview_url": reverse(
            "directory:preview",
            kwargs={"dataset_uuid": document_id, "name": document_name, "datafile_uuid": resource["id"]},
        )
        if resource_format == "CSV"
        else None,
        "date": format_date(date) if date else "",
    }


def format_file_size(file_size):
    binary_multiplier = 1024
    for unit in ("KB", "MB", "GB"):
        file_size /= binary_multiplier
        if file_size < binary_multiplier:
            return f"{file_size:.0f} {unit}"
    return f"{file_size:.0f} GB"
