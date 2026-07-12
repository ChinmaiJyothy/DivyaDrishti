from divyadrishti.learning import AuditAction, AuditLogger


def test_audit_logger():
    logger = AuditLogger()
    entry = logger.log(
        AuditAction.RULE_APPROVED,
        user="admin",
        reason="Verified against source",
        affected_objects=["BPHS_7TH_001"],
    )
    assert entry.action == AuditAction.RULE_APPROVED
    assert len(logger.logs) == 1


def test_audit_for_object():
    logger = AuditLogger()
    logger.log(AuditAction.RULE_CREATED, affected_objects=["RULE_1"])
    logger.log(AuditAction.BOOK_IMPORTED, affected_objects=["BOOK_1"])
    results = logger.for_object("RULE_1")
    assert len(results) == 1
