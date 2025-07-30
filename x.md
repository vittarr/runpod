# Data-Lineage Cheat-Sheet (MD)

| # | Table | Role | Data delivered to SELECT list | Pre-processing before final result | Transaction id column (guess) |
|---|-------|------|-------------------------------|------------------------------------|-------------------------------|
| **1** | **ENTRY** | **MAIN** | `entry_id`, `posting_date`, `amount`, `fee_amount`, `end_balance`, `contract_for` | date-range filter `:v_FromDate … :v_ToDate`; join to ITEM | **entry.id** |
| **2** | **M_TRANSACTION** | **MAIN** | `service_class`, `trans_amount`, `trans_curr`, `trans_code`, `posting_db_date`, `target_account` | decode / nvl for amount & currency; filter on service_class & trans_code | **m_transaction.id** |
| **3** | **DOC** | **MAIN** | `trans_date`, `trans_amount`, `trans_curr`, `trans_type`, `trans_details`, `sic_code`, `trans_country`, `trans_city`, `auth_code`, `ret_ref_number`, `source_reg_num`, `add_info` | CASE expression → Russian narrative; REGEXP filters on `source_reg_num` & `trans_details` | **doc.id** |
| 4 | TAB (CTE) | INLINE | contract id list | UNION ALL driven by `:IN_CARDID` | — |
| 5 | ACNT_CONTRACT | LOOKUP | — | link TAB → all child contracts; outer joins to dimensions | `acnt_contract.id` |
| 6 | ACCOUNT | LOOKUP | `curr`, `account_type`, `is_am_available`, `code` (P%,F3,P7) | filters on TECHNICAL group | `account.id` |
| 7 | ACCOUNT (alias MA) | LOOKUP | `account_name`, `code` | outer join via `m_transaction.target_account = ma.id` | `ma.id` |
| 8 | CLIENT | LOOKUP | — | join `client.id = acnt_contract.client_id` | — |
| 9 | CURRENCY (multiple aliases) | LOOKUP | currency code & name | outer joins to resolve curr, acc_curr, doc_curr, trans_curr; `amnd_state = 'A'` | — |
| 10 | ACCOUNT_TYPE | LOOKUP | `group_name` | filter TECHNICAL vs non-TECHNICAL | — |
| 11 | SERV_PACK | LOOKUP | — | outer join to `acnt_contract.serv_pack_id` | — |
| 12 | ACC_SCHEME | LOOKUP | — | outer join to `acnt_contract.acc_scheme_id` | — |
| 13 | CONTR_SUBTYPE | LOOKUP | — | outer join to `acnt_contract.contr_subtype_id` | — |
| 14 | TRANS_SUBTYPE | LOOKUP | `name` (for `tr_type`) | outer join to `m_transaction.trans_subtype` | — |
| 15 | DICT | LOOKUP | `name` (fallback trans type) | scalar sub-query by `trans_code` | — |
| 16 | V_LISTBOXES (alias RC) | LOOKUP | `displ_col` (request category text) | outer join on `request_cat`; filter `name = 'Request Category'` & `data_col <> 'p'` | — |
| 17 | ITEM | FILTER | — | bridges ACCOUNT → ENTRY; no columns selected | `item.id` |

> In card statements the **document id (`doc.id`)** or **retrieval reference number (`doc.ret_ref_number`)** is what the customer usually sees as the **transaction id**.


┌─────────────────────────────────────────────────────────────────────────────┐
│                                INLINE (CTE)                                 │
│                              ┌────────────┐                                 │
│                              │    TAB     │   UNION ALL list of contracts   │
│                              └────┬───────┘                                 │
└───────────────────────────────────┼──────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┼──────────────────────────────────────────┐
│                                   │                                          │
│  ┌──────────────┐     ┌──────────┴──────────┐    ┌──────────────────┐      │
│  │   CLIENT     │────→│   ACNT_CONTRACT     │←───┤  SERV_PACK (+)   │      │
│  └──────────────┘     │        (lookup)     │    └──────────────────┘      │
│                        │          id          │    ┌──────────────────┐      │
│                        └──────────┬──────────┘←───┤ ACC_SCHEME (+)   │      │
│                                   │               └──────────────────┘      │
│                                   │               ┌──────────────────┐      │
│                                   │               │CONTR_SUBTYPE (+) │      │
│                                   │               └──────────────────┘      │
│                                   │                                          │
│                                   │◄──currency.code(+), amnd_state='A'──────┤
│                                   │                                          │
│                        ┌──────────┴──────────┐                              │
│                        │     ACCOUNT         │                              │
│                        │   (card sub-acc)    │                              │
│                        │   acnt_contract_oid │                              │
│                        └──────────┬──────────┘                              │
│                                   │                                          │
│                        ┌──────────┴──────────┐                              │
│                        │   ACCOUNT_TYPE      │                              │
│                        │   (filter TECHNICAL)│                              │
│                        └──────────┬──────────┘                              │
│                                   │                                          │
│                                   │                                          │
│                        ┌──────────┴──────────┐                              │
│                        │       ITEM          │   FILTER only                │
│                        │   account_oid       │                              │
│                        └──────────┬──────────┘                              │
│                                   │                                          │
│  ┌──────────────────────────────┐ │                                          │
│  │        MAIN CHAIN            │ │                                          │
│  │   ENTRY (fact)               │ │                                          │
│  │   ├─ m_transaction_id ───────┼─┘                                          │
│  │   │                          │                                             │
│  │   │  ┌──────────────────┐   │                                             │
│  │   └──┤ M_TRANSACTION    │   │                                             │
│  │      │   (fact)         │   │                                             │
│  │      │   id             │   │                                             │
│  │      └────┬─────────────┘   │                                             │
│  │           │                 │                                             │
│  │      ┌────┴─────────────┐   │                                             │
│  │      │   DOC (fact)     │   │                                             │
│  │      │   doc_oid        │   │                                             │
│  │      └────┬─────────────┘   │                                             │
│  │           │                 │                                             │
│  │      ┌────┴─────────────┐   │                                             │
│  │      │ ACCOUNT MA (+)   │   │                                             │
│  │      └──────────────────┘   │                                             │
│  └──────────────────────────────┘                                             │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │             LOOKUP / DIMENSION TABLES (outer joined)                    │ │
│  │  CURRENCY (multiple aliases: acc_curr, doc_curr, trans_curr, tc)        │ │
│  │  TRANS_SUBTYPE                                                          │ │
│  │  V_LISTBOXES (alias RC)                                                 │ │
│  │  DICT (scalar lookup)                                                   │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘