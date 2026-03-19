import csv
import io

from app.ml.adapters.ibm import IBMInvoiceAdapter
from app.ml.adapters.skywalker import SkywalkerInvoiceAdapter
from app.ml.training.runner import split_dataset_rows


IBM_SAMPLE_TEXT = (
    'countryCode,customerID,PaperlessDate,invoiceNumber,InvoiceDate,DueDate,InvoiceAmount,Disputed,SettledDate,PaperlessBill,DaysToSettle,DaysLate\n'
    '391,0379-NEVHP,4/6/2013,611365,1/2/2013,2/1/2013,55.94,No,1/15/2013,Paper,13,0\n'
    '406,8976-AMJEO,3/3/2012,7900770,1/26/2013,2/25/2013,61.74,Yes,3/20/2013,Electronic,53,23\n'
    '391,2820-XGXSB,1/26/2012,9231909,7/3/2013,8/2/2013,65.88,No,8/25/2013,Electronic,53,23\n'
)

SKYWALKER_SAMPLE_TEXT = (
    'business_code,cust_number,name_customer,clear_date,buisness_year,doc_id,posting_date,document_create_date,due_in_date,invoice_currency,document type,posting_id,area_business,total_open_amount,baseline_create_date,cust_payment_terms,invoice_id,isOpen\n'
    'U001,0200315290,KWI in,2019-03-07 00:00:00,2019,1928826755,2019-02-20,20190220,20190307.0,USD,RV,1,,21227.05,20190220.0,NAA8,1928826755,0\n'
    'U001,0200769623,WAL-MAR foundation,2020-01-16 00:00:00,2020,1930350280,2020-01-04,20200104,20200119.0,USD,RV,1,,5669.72,20200104.0,NAH4,1930350280,0\n'
)


def test_ibm_adapter_normalizes_expected_columns() -> None:
    rows = list(csv.DictReader(io.StringIO(IBM_SAMPLE_TEXT)))
    frame = IBMInvoiceAdapter().normalize_rows(rows).frame

    assert 'invoice_id' in frame.columns
    assert 'customer_id' in frame.columns
    assert 'is_late_15' in frame.columns
    assert frame['invoice_date'].notna().all()
    assert (frame['invoice_date'] <= frame['due_date']).all()
    assert int(frame['is_late_15'].sum()) == 2


def test_skywalker_adapter_normalizes_expected_columns() -> None:
    rows = list(csv.DictReader(io.StringIO(SKYWALKER_SAMPLE_TEXT)))
    frame = SkywalkerInvoiceAdapter().normalize_rows(rows).frame

    assert 'days_late' in frame.columns
    assert 'is_late_15' in frame.columns
    assert frame['settled_date'].notna().all()
    assert frame['amount'].gt(0).all()


def test_temporal_split_keeps_ordering() -> None:
    rows = list(csv.DictReader(io.StringIO(IBM_SAMPLE_TEXT)))
    frame = IBMInvoiceAdapter().normalize_rows(rows).frame
    train, val, test = split_dataset_rows(frame, 0.2, 0.2)

    combined = [len(train), len(val), len(test)]
    assert sum(combined) == len(frame)
    if not train.empty and not val.empty:
        assert train['invoice_date'].max() <= val['invoice_date'].min()
    if not val.empty and not test.empty:
        assert val['invoice_date'].max() <= test['invoice_date'].min()
