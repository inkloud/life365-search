from typing import Any


def build_product_index_mapping() -> dict[str, Any]:
    return {
        "settings": {"number_of_shards": 1, "number_of_replicas": 0},
        "mappings": {
            "properties": {
                "product_id": {"type": "integer"},
                "title_it": {"type": "text", "analyzer": "italian"},
                "title_en": {"type": "text", "analyzer": "english"},
                "title_cn": {"type": "text", "analyzer": "smartcn"},
                "description_it": {"type": "text", "analyzer": "italian"},
                "description_en": {"type": "text", "analyzer": "english"},
                "description_cn": {"type": "text", "analyzer": "smartcn"},
                "keywords_it": {"type": "text", "analyzer": "italian"},
                "keywords_en": {"type": "text", "analyzer": "english"},
                "keywords_cn": {"type": "text", "analyzer": "smartcn"},
                "brand": {"type": "keyword"},
                "category_level_1_id": {"type": "integer"},
                "category_level_2_id": {"type": "integer"},
                "category_level_3_id": {"type": "integer"},
                "category_level_1_title_it": {"type": "text", "analyzer": "italian"},
                "category_level_1_title_en": {"type": "text", "analyzer": "english"},
                "category_level_1_title_cn": {"type": "text", "analyzer": "smartcn"},
                "category_level_2_title_it": {"type": "text", "analyzer": "italian"},
                "category_level_2_title_en": {"type": "text", "analyzer": "english"},
                "category_level_2_title_cn": {"type": "text", "analyzer": "smartcn"},
                "category_level_3_title_it": {"type": "text", "analyzer": "italian"},
                "category_level_3_title_en": {"type": "text", "analyzer": "english"},
                "category_level_3_title_cn": {"type": "text", "analyzer": "smartcn"},
                "is_available": {"type": "boolean"},
                "is_visible": {"type": "boolean"},
                "is_outlet": {"type": "boolean"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
    }
