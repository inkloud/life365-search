from dataclasses import dataclass


@dataclass(frozen=True)
class CategoryTitle:
    it: str | None = None
    en: str | None = None
    cn: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "CategoryTitle":
        return cls(it=data.get("it"), en=data.get("en"), cn=data.get("cn"))


type CategoryTree = list["CategoryNode"]


@dataclass(frozen=True)
class CategoryNode:
    id: int
    title: CategoryTitle
    children: CategoryTree


@dataclass(frozen=True)
class CategoryPath:
    level_1_id: int
    level_1_title: CategoryTitle

    level_2_id: int
    level_2_title: CategoryTitle

    level_3_id: int
    level_3_title: CategoryTitle


def extract_level_3_paths(roots: CategoryTree) -> list[CategoryPath]:
    res: list[CategoryPath] = []

    for level_1 in roots:
        for level_2 in level_1.children:
            for level_3 in level_2.children:
                res.append(
                    CategoryPath(
                        level_1_id=level_1.id,
                        level_1_title=level_1.title,
                        level_2_id=level_2.id,
                        level_2_title=level_2.title,
                        level_3_id=level_3.id,
                        level_3_title=level_3.title,
                    )
                )

    return res
