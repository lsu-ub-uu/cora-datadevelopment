from typing import Literal, cast

RelationType = Literal["constituent", "related"]


class OutputRelation:
    type: RelationType
    pid: str

    def __init__(self, type: RelationType, pid: str):
        self.type = type
        self.pid = pid


OutputMigrationStatus = Literal[
    "SUCCESS",
    "CLASSIC_QUALITY",
    "FAILED",
    "SKIPPED",
    "INPUT_VALIDATION_FAILED",
]


class OutputMigrationResult:
    pid: str
    publication_type: str
    status: OutputMigrationStatus
    errors: list[str] | None
    cora_id: str | None
    relations: list[OutputRelation]

    def __init__(
        self,
        pid: str,
        publication_type: str | None = None,
        status: OutputMigrationStatus | None = None,
        errors: list[str] | None = None,
        cora_id: str | None = None,
        relations: list[OutputRelation] | None = None,
    ):
        if status is None and isinstance(publication_type, str):
            valid_statuses = {
                "SUCCESS",
                "CLASSIC_QUALITY",
                "FAILED",
                "SKIPPED",
                "INPUT_VALIDATION_FAILED",
            }
            if publication_type in valid_statuses:
                status = cast(OutputMigrationStatus, publication_type)
                publication_type = "UNKNOWN"

        assert status is not None

        self.pid = pid
        self.publication_type = publication_type if publication_type else "UNKNOWN"
        self.status = status
        self.errors = errors
        self.cora_id = cora_id
        self.relations = relations if relations else []
