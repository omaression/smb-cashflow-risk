import csv
import io
from pathlib import Path

from app.ml.adapters.ibm import IBMInvoiceAdapter
from app.ml.adapters.skywalker import SkywalkerInvoiceAdapter
from app.ml.training.runner import split_dataset_rows


def test_ibm_adapter_normalizes_expected_columns() -> None:
    path = Path('/root/.openclaw/workspace/uploads/20260319_091134_AgADHAcAArMx4EU.csv')
    with path.open(newline='', encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle))[:25]
    frame = IBMInvoiceAdapter().normalize_rows(rows).frame

    assert 'invoice_id' in frame.columns
    assert 'customer_id' in frame.columns
    assert 'is_late_15' in frame.columns
    assert frame['invoice_date'].notna().all()
    assert (frame['invoice_date'] <= frame['due_date']).all()


def test_skywalker_adapter_normalizes_expected_columns() -> None:
    sample = io.StringIO(
        'business_code,cust_number,name_customer,clear_date,buisness_year,doc_id,posting_date,document_create_date,due_in_date,invoice_currency,document type,posting_id,area_business,total_open_amount,baseline_create_date,cust_payment_terms,invoice_id,isOpen\n'
        'U001,0200315290,KWI in,2019-03-07 00:00:00,2019,1928826755,2019-02-20,20190220,20190307.0,USD,RV,1,,21227.05,20190220.0,NAA8,1928826755,0\n'
        'U001,0200769623,WAL-MAR foundation,2020-01-16 00:00:00,2020,1930350280,2020-01-04,20200104,20200119.0,USD,RV,1,,5669.72,20200104.0,NAH4,1930350280,0\n'
    )
    rows = list(csv.DictReader(sample))
    frame = SkywalkerInvoiceAdapter().normalize_rows(rows).frame

    assert 'days_late' in frame.columns
    assert 'is_late_15' in frame.columns
    assert frame['settled_date'].notna().all()
    assert frame['amount'].gt(0).all()


def test_temporal_split_falls_back_without_tiny_first_year() -> None:
    path = Path('/root/.openclaw/workspace/uploads/20260319_091134_AgADHAcAArMx4EU.csv')
    with path.open(newline='', encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle))
    frame = IBMInvoiceAdapter().normalize_rows(rows).frame
    train, val, test = split_dataset_rows(frame, 0.2, 0.2)

    assert len(train) > 0
    assert len(val) > 0
    assert len(test) > 0
    assert train['invoice_date'].max() <= val['invoice_date'].min()
    assert val['invoice_date'].max() <= test['invoice_date'].min()
