import sys
import os
import json
import glob
import pandas as pd
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Load datasets
orders = pd.read_csv('data/olist_orders_dataset.csv')
customers = pd.read_csv('data/olist_customers_dataset.csv')
items = pd.read_csv('data/olist_order_items_dataset.csv')
payments = pd.read_csv('data/olist_order_payments_dataset.csv')
products = pd.read_csv('data/olist_products_dataset.csv')
sellers = pd.read_csv('data/olist_sellers_dataset.csv')

def parse_dt(val):
    if pd.isna(val) or not val:
        return None
    return str(val)

def calc_hours_diff(dt_str1, dt_str2):
    if not dt_str1 or not dt_str2:
        return None
    d1 = datetime.strptime(dt_str1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.strptime(dt_str2, '%Y-%m-%d %H:%M:%S')
    return round((d1 - d2).total_seconds() / 3600.0, 2)

def process_case(case_file):
    with open(case_file, 'r', encoding='utf-8') as f:
        c = json.load(f)
    
    cid = c['case_id']
    oid = c['customer_request']['claimed_order_id']
    
    o_row = orders[orders['order_id'] == oid].iloc[0]
    cust_row = customers[customers['customer_id'] == o_row['customer_id']].iloc[0]
    cust_uniq = cust_row['customer_unique_id']
    
    # Related orders for customer_unique_id
    all_cust_customer_ids = customers[customers['customer_unique_id'] == cust_uniq]['customer_id']
    all_cust_orders = orders[orders['customer_id'].isin(all_cust_customer_ids)]
    # Filter out claimed order
    rel_orders = [r for r in all_cust_orders['order_id'].tolist() if r != oid][:5]
    
    # Items
    it_rows = items[items['order_id'] == oid]
    it_list = it_rows.to_dict('records')
    
    item_ids = [f"{oid}:{it['order_item_id']}" for it in it_list][:5]
    seller_ids = list(dict.fromkeys([it['seller_id'] for it in it_list]))[:3]
    
    prod_ids = list(dict.fromkeys([it['product_id'] for it in it_list]))[:5]
    cat_names = []
    for pid in prod_ids:
        p_row = products[products['product_id'] == pid]
        if len(p_row) > 0 and not pd.isna(p_row.iloc[0]['product_category_name']):
            cn = str(p_row.iloc[0]['product_category_name'])
            if cn not in cat_names:
                cat_names.append(cn)
    cat_names = cat_names[:5]
    
    # Dates & delivery
    del_at = parse_dt(o_row['order_delivered_customer_date'])
    est_at = parse_dt(o_row['order_estimated_delivery_date'])
    car_at = parse_dt(o_row['order_delivered_carrier_date'])
    del_var = calc_hours_diff(del_at, est_at)
    
    seller_handoff_analysis = []
    late_seller_ids = []
    if len(it_list) > 0:
        for sid in seller_ids:
            s_items = [it for it in it_list if it['seller_id'] == sid]
            min_ship_limit = min([it['shipping_limit_date'] for it in s_items])
            h_var = calc_hours_diff(car_at, min_ship_limit)
            late = (h_var is not None and h_var > 0)
            seller_handoff_analysis.append({
                'seller_id': sid,
                'shipping_limit_at': min_ship_limit,
                'handoff_variance_hours': h_var,
                'late_handoff': late
            })
            if late:
                late_seller_ids.append(sid)
                
    # Payments
    pay_rows = payments[payments['order_id'] == oid].to_dict('records')
    payment_ids = [f"{oid}:{p['payment_sequential']}" for p in pay_rows][:5]
    pay_types = list(dict.fromkeys([p['payment_type'] for p in pay_rows]))
    pay_total = round(sum([p['payment_value'] for p in pay_rows]), 2)
    
    if len(it_list) > 0:
        item_tot = round(sum([it['price'] for it in it_list]), 2)
        freight_tot = round(sum([it['freight_value'] for it in it_list]), 2)
        exp_tot = round(item_tot + freight_tot, 2)
        diff_brl = round(pay_total - exp_tot, 2)
        reconciled = abs(diff_brl) <= 0.10
    else:
        item_tot = None
        freight_tot = None
        exp_tot = None
        diff_brl = None
        reconciled = None
        
    status = o_row['order_status']
    
    # Primary issue determination
    if status == 'canceled' and pay_total > 0:
        primary = 'canceled_order_paid'
        cause_code = 'ORDER_CANCELED_AFTER_PAYMENT'
        resp_parties = [{'party_type': 'platform', 'party_id': 'OLIST_PLATFORM'}]
        refund = pay_total
        main_action = 'issue_full_refund'
    elif status == 'unavailable' and pay_total > 0:
        primary = 'unavailable_order_paid'
        cause_code = 'ORDER_UNAVAILABLE_AFTER_PAYMENT'
        resp_parties = [{'party_type': 'platform', 'party_id': 'OLIST_PLATFORM'}]
        refund = pay_total
        main_action = 'issue_full_refund'
    elif del_var is not None and del_var > 0 and len(late_seller_ids) > 0:
        primary = 'late_delivery_seller'
        cause_code = 'SELLER_HANDOFF_AFTER_LIMIT'
        resp_parties = [{'party_type': 'seller', 'party_id': sid} for sid in late_seller_ids[:3]]
        refund = freight_tot
        main_action = 'refund_freight'
    elif del_var is not None and del_var > 0 and len(late_seller_ids) == 0:
        primary = 'late_delivery_logistics'
        cause_code = 'CARRIER_DELIVERED_AFTER_ESTIMATE'
        resp_parties = [{'party_type': 'logistics_provider', 'party_id': 'LOGISTICS_PROVIDER'}]
        refund = freight_tot
        main_action = 'refund_freight'
    elif len(pay_rows) >= 2 and reconciled == True:
        primary = 'valid_split_payment'
        cause_code = 'MULTIPLE_PAYMENTS_RECONCILED'
        resp_parties = []
        refund = 0.0
        main_action = 'explain_valid_split_payment'
    elif del_var is not None and del_var <= 0 and reconciled == True:
        primary = 'unsupported_late_claim'
        cause_code = 'DELIVERY_WITHIN_ESTIMATE'
        resp_parties = []
        refund = 0.0
        main_action = 'reject_late_refund'
    else:
        raise ValueError(f"Case {cid} (order {oid}) did not match any policy rule!")

    # Secondary issues
    secondary = []
    if len(it_list) >= 2:
        secondary.append('multi_item_order')
    if len(seller_ids) >= 2:
        secondary.append('multi_seller_order')
    if len(pay_rows) >= 2:
        secondary.append('split_payment')
    if len(rel_orders) >= 1:
        secondary.append('repeat_customer')
    if len(cat_names) >= 2:
        secondary.append('multiple_categories')
        
    case_st = 'action_required' if refund > 0 else 'no_action'
    
    # Actions
    actions = [main_action]
    if primary == 'late_delivery_seller':
        actions.append('review_seller_handoff')
    elif primary == 'late_delivery_logistics':
        actions.append('review_carrier_delay')
        
    if refund > 0:
        actions.append('verify_refund_completion')
        
    if 'multi_seller_order' in secondary:
        actions.append('coordinate_multi_seller_case')
        
    if 'split_payment' in secondary and primary != 'valid_split_payment':
        actions.append('verify_payment_allocation')
        
    actions = actions[:5]
    
    # Evidence IDs
    evidence_ids = [f'order:{oid}']
    for item_id in item_ids:
        evidence_ids.append(f'item:{item_id}')
    for pay_id in payment_ids:
        evidence_ids.append(f'payment:{pay_id}')
    for rp in resp_parties:
        if rp['party_type'] == 'seller':
            evidence_ids.append(f'seller:{rp["party_id"]}')
    evidence_ids.append(f'policy:{cause_code}')
    evidence_ids = evidence_ids[:20]
    
    output = {
        'case_id': cid,
        'case_assessment': {
            'primary_issue': primary,
            'secondary_issues': secondary,
            'case_status': case_st,
            'confidence': 0.95
        },
        'affected_entities': {
            'order_ids': [oid],
            'item_ids': item_ids,
            'seller_ids': seller_ids,
            'payment_ids': payment_ids
        },
        'customer_context': {
            'customer_unique_id': cust_uniq,
            'related_order_ids': rel_orders
        },
        'product_context': {
            'product_ids': prod_ids,
            'category_names': cat_names
        },
        'delivery_analysis': {
            'delivered_at': del_at,
            'estimated_delivery_at': est_at,
            'carrier_handoff_at': car_at,
            'delivery_variance_hours': del_var,
            'seller_handoff_analysis': seller_handoff_analysis,
            'late_handoff_seller_ids': late_seller_ids
        },
        'payment_reconciliation': {
            'currency': 'BRL',
            'item_total_brl': item_tot,
            'freight_total_brl': freight_tot,
            'expected_total_brl': exp_tot,
            'payment_total_brl': pay_total,
            'difference_brl': diff_brl,
            'reconciled': reconciled,
            'payment_types': pay_types
        },
        'root_cause_analysis': {
            'ranked_causes': [{'cause_code': cause_code, 'rank': 1}],
            'responsible_parties': resp_parties
        },
        'evidence_ids': evidence_ids,
        'financial_resolution': {
            'currency': 'BRL',
            'recommended_refund_brl': refund
        },
        'resolution_actions': actions
    }
    return output

if __name__ == '__main__':
    files = sorted(glob.glob('input/EC_*.json'))
    print(f"Processing {len(files)} files...")
    out_dir = 'output'
    os.makedirs(out_dir, exist_ok=True)
    for f in files:
        res = process_case(f)
        out_name = os.path.basename(f)
        with open(os.path.join(out_dir, out_name), 'w', encoding='utf-8') as out_f:
            json.dump(res, out_f, indent=2, ensure_ascii=False)
    print("Done generating 50 output files in output/")
