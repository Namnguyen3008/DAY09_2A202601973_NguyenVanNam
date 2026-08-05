import sys
import os
import json
import glob

sys.stdout.reconfigure(encoding='utf-8')

VALID_PRIMARY_ISSUES = {
    "canceled_order_paid",
    "unavailable_order_paid",
    "late_delivery_seller",
    "late_delivery_logistics",
    "valid_split_payment",
    "unsupported_late_claim"
}

VALID_SECONDARY_ISSUES = [
    "multi_item_order",
    "multi_seller_order",
    "split_payment",
    "repeat_customer",
    "multiple_categories"
]

VALID_EVIDENCE_PREFIXES = ("order:", "item:", "payment:", "seller:", "policy:")

def validate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    filename = os.path.basename(filepath)
    expected_case_id = filename.replace('.json', '')
    assert data['case_id'] == expected_case_id, f"case_id mismatch in {filename}"

    # case_assessment
    ca = data['case_assessment']
    assert ca['primary_issue'] in VALID_PRIMARY_ISSUES, f"Invalid primary issue in {filename}: {ca['primary_issue']}"
    assert ca['case_status'] in ("action_required", "no_action"), f"Invalid case_status in {filename}"
    assert 0.0 <= ca['confidence'] <= 1.0, f"Invalid confidence in {filename}"
    
    # check secondary_issues order
    prev_idx = -1
    for sec in ca['secondary_issues']:
        assert sec in VALID_SECONDARY_ISSUES, f"Invalid secondary issue in {filename}: {sec}"
        curr_idx = VALID_SECONDARY_ISSUES.index(sec)
        assert curr_idx > prev_idx, f"Secondary issues out of order in {filename}: {ca['secondary_issues']}"
        prev_idx = curr_idx

    # affected_entities
    ae = data['affected_entities']
    assert len(ae['order_ids']) <= 5, f"order_ids exceeds limit in {filename}"
    assert len(ae['item_ids']) <= 5, f"item_ids exceeds limit in {filename}"
    assert len(ae['seller_ids']) <= 3, f"seller_ids exceeds limit in {filename}"
    assert len(ae['payment_ids']) <= 5, f"payment_ids exceeds limit in {filename}"

    # customer_context
    cc = data['customer_context']
    assert isinstance(cc['customer_unique_id'], str), f"Invalid customer_unique_id in {filename}"
    assert len(cc['related_order_ids']) <= 5, f"related_order_ids exceeds limit in {filename}"

    # product_context
    pc = data['product_context']
    assert len(pc['product_ids']) <= 5, f"product_ids exceeds limit in {filename}"
    assert len(pc['category_names']) <= 5, f"category_names exceeds limit in {filename}"

    # delivery_analysis
    da = data['delivery_analysis']
    assert len(da['seller_handoff_analysis']) <= 5
    assert len(da['late_handoff_seller_ids']) <= 3

    # payment_reconciliation
    pr = data['payment_reconciliation']
    assert pr['currency'] == 'BRL'

    # root_cause_analysis
    rca = data['root_cause_analysis']
    assert len(rca['ranked_causes']) <= 3
    assert len(rca['responsible_parties']) <= 3

    # evidence_ids
    evs = data['evidence_ids']
    assert len(evs) <= 20, f"evidence_ids exceeds limit in {filename}"
    for ev in evs:
        assert ev.startswith(VALID_EVIDENCE_PREFIXES), f"Invalid evidence ID format in {filename}: {ev}"

    # financial_resolution
    fr = data['financial_resolution']
    assert fr['currency'] == 'BRL'
    assert fr['recommended_refund_brl'] >= 0.0

    # resolution_actions
    ra = data['resolution_actions']
    assert len(ra) <= 5, f"resolution_actions exceeds limit in {filename}"

    return True

if __name__ == '__main__':
    files = sorted(glob.glob('output/EC_*.json'))
    print(f"Validating {len(files)} files in output/...")
    assert len(files) == 50, f"Expected 50 files, got {len(files)}"

    for f in files:
        validate_file(f)

    print("ALL 50 OUTPUT FILES PASSED COMPREHENSIVE VALIDATION!")
