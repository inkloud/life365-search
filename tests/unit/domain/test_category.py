from app.domain.category import (
    CategoryNode,
    CategoryPath,
    CategoryTitle,
    CategoryTree,
    extract_level_3_paths,
)


def test_extract_level_3_paths():
    tree: CategoryTree = [
        CategoryNode(
            id=1,
            title=CategoryTitle(it="L1"),
            children=[
                CategoryNode(
                    id=2,
                    title=CategoryTitle(it="L2"),
                    children=[
                        CategoryNode(id=3, title=CategoryTitle(it="L3"), children=[]),
                        CategoryNode(id=4, title=CategoryTitle(it="L4"), children=[]),
                    ],
                )
            ],
        )
    ]

    paths: list[CategoryPath] = extract_level_3_paths(tree)

    assert len(paths) == 2
    path: CategoryPath = paths[1]

    assert path.level_1_id == 1
    assert path.level_2_id == 2
    assert path.level_3_id == 4
